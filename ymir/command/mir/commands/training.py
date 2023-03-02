import argparse
import logging
import os
import time
from subprocess import CalledProcessError
from typing import Any, Dict, List, Optional
from mir.version import YMIR_MODEL_VERSION

from tensorboardX import SummaryWriter
import yaml

from mir.commands import base
from mir.commands.merge import merge_with_pb
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, env_config, exporter
from mir.tools import mir_storage_ops, models, revs_parser
from mir.tools import settings as mir_settings
from mir.tools.annotations import make_empty_mir_annotations, MergeStrategy
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.code import MirCode
from mir.tools.errors import MirContainerError, MirRuntimeError
from mir.tools.executant import prepare_executant_env, run_docker_executant


# private: post process
def _get_model_storage(model_root: str, executor_config: dict, task_context: dict) -> models.ModelStorage:
    """
    find models in `model_root`, and returns all model stages and attachments

    Args:
        model_root (str): model root

    Returns:
        models.ModelStorage
    """
    # model_names = []
    # model_mAP = 0.0
    model_stages: Dict[str, models.ModelStageStorage]
    best_stage_name = ''
    attachments: Dict[str, Any] = {}

    result_yaml_path = os.path.join(model_root, "result.yaml")
    try:
        with open(result_yaml_path, "r") as f:
            yaml_obj = yaml.safe_load(f.read())
        if 'model' in yaml_obj:
            # old trainig result file: read models from `model` field
            model_names = yaml_obj["model"]
            model_mAP = float(yaml_obj["map"])

            best_stage_name = 'default_best_stage'
            model_stages = {
                best_stage_name:
                models.ModelStageStorage(stage_name=best_stage_name,
                                         files=model_names,
                                         mAP=model_mAP,
                                         timestamp=int(time.time()))
            }
        elif 'model_stages' in yaml_obj:
            # new training result file: read from model stages
            model_stages = {k: models.ModelStageStorage.parse_obj(v) for k, v in yaml_obj['model_stages'].items()}

            best_stage_name = yaml_obj['best_stage_name']
        if 'attachments' in yaml_obj:
            attachments = yaml_obj['attachments']
    except FileNotFoundError:
        error_message = f"can not find file: {result_yaml_path}, executor may have errors, see ymir-executor-out.log"
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE, error_message=error_message)

    if not model_stages:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='can not find model stages in result.yaml')

    return models.ModelStorage(executor_config=executor_config,
                               task_context=dict(**task_context,
                                                 mAP=model_stages[best_stage_name].mAP,
                                                 type=mirpb.TaskType.TaskTypeTraining),
                               stages=model_stages,
                               best_stage_name=best_stage_name,
                               object_type=int(yaml_obj.get('object_type', models.ModelObjectType.MOT_DET_BOX.value)),
                               attachments=attachments,
                               evaluate_config=yaml_obj.get('evaluate_config', {}),
                               package_version=YMIR_MODEL_VERSION)


# private: pre process
def _generate_config(executor_config: Any, out_config_path: str, task_id: str,
                     pretrained_model_params: List[str]) -> dict:
    executor_config["task_id"] = task_id
    if pretrained_model_params:
        executor_config['pretrained_model_params'] = pretrained_model_params
    elif 'pretrained_model_params' in executor_config:
        del executor_config['pretrained_model_params']

    logging.info("container config: {}".format(executor_config))

    with open(out_config_path, "w") as f:
        yaml.dump(executor_config, f)

    return executor_config


def _prepare_pretrained_models(model_location: str, model_hash_stage: str, dst_model_dir: str) -> List[str]:
    """
    prepare pretrained models
    * extract models to dst_model_dir
    * returns model file names

    Args:
        model_location (str): model location
        model_hash_stage (str): model package hash
        dst_model_dir (str): dir where you want to extract model files to

    Returns:
        List[str]: stage_name/model_names
    """
    if not model_hash_stage:
        return []
    model_hash, stage_name = models.parse_model_hash_stage(model_hash_stage)
    model_storage = models.prepare_model(model_location=model_location,
                                         model_hash=model_hash,
                                         stage_name=stage_name,
                                         dst_model_path=dst_model_dir)

    return [f"{stage_name}/{file_name}" for file_name in model_storage.stages[stage_name].files]


class CmdTrain(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command train: %s", self.args)

        return CmdTrain.run_with_args(work_dir=self.args.work_dir,
                                      asset_cache_dir=self.args.asset_cache_dir,
                                      model_upload_location=self.args.model_path,
                                      pretrained_model_hash_stage=self.args.model_hash_stage,
                                      src_revs=self.args.src_revs,
                                      strategy=MergeStrategy(self.args.strategy),
                                      dst_rev=self.args.dst_rev,
                                      mir_root=self.args.mir_root,
                                      label_storage_file=self.args.label_storage_file,
                                      media_location=self.args.media_location,
                                      tensorboard_dir=self.args.tensorboard_dir,
                                      executor=self.args.executor,
                                      executant_name=self.args.executant_name,
                                      run_as_root=self.args.run_as_root,
                                      config_file=self.args.config_file)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str,
                      asset_cache_dir: str,
                      model_upload_location: str,
                      pretrained_model_hash_stage: str,
                      executor: str,
                      executant_name: str,
                      src_revs: str,
                      strategy: MergeStrategy,
                      dst_rev: str,
                      config_file: Optional[str],
                      tensorboard_dir: str,
                      run_as_root: bool,
                      label_storage_file: str,
                      mir_root: str = '.',
                      media_location: str = '') -> int:
        if not model_upload_location:
            logging.error("empty --model-location, abort")
            return MirCode.RC_CMD_INVALID_ARGS

        src_typ_rev_tids = revs_parser.parse_arg_revs(src_revs)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        if not work_dir:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty work_dir')
        if not config_file or not os.path.isfile(config_file):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"invalid --task-config-file: {config_file}")
        if asset_cache_dir and not os.path.isabs(asset_cache_dir):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"invalid --cache {config_file}, not an absolute path for directory")

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        if mir_settings.EXECUTOR_CONFIG_KEY not in config:
            raise MirRuntimeError(
                error_code=MirCode.RC_CMD_INVALID_ARGS,
                error_message=f"invalid config file: {config_file}, needs: {mir_settings.EXECUTOR_CONFIG_KEY}")

        executor_config = config[mir_settings.EXECUTOR_CONFIG_KEY]

        class_names = executor_config.get('class_names', [])
        if not class_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"no class_names in config file: {config_file}")
        if len(set(class_names)) != len(class_names):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"dumplicate class names in class_names: {class_names}")

        task_id = dst_typ_rev_tid.tid
        if not executant_name:
            executant_name = f"default-training-{task_id}"

        # setting up paths.
        os.makedirs(work_dir, exist_ok=True)

        work_dir_in = os.path.join(work_dir, "in")
        work_dir_out = os.path.join(work_dir, "out")
        prepare_executant_env(work_dir_in=work_dir_in,
                              work_dir_out=work_dir_out,
                              asset_cache_dir=asset_cache_dir,
                              tensorboard_dir=tensorboard_dir)

        asset_dir = os.path.join(work_dir_in, 'assets')
        work_dir_pred = os.path.join(work_dir_in, 'predictions')
        work_dir_gt = os.path.join(work_dir_in, 'annotations')
        tensorboard_dir = os.path.join(work_dir_out, 'tensorboard')

        docker_log_dst = os.path.join(tensorboard_dir, "executor.log")
        docker_log_src = os.path.join(work_dir_out, mir_settings.EXECUTOR_OUTLOG_NAME)
        open(docker_log_src, 'w').close()
        os.symlink(docker_log_src, docker_log_dst)

        # if have model_hash_stage, export model
        pretrained_model_stage_and_names = _prepare_pretrained_models(model_location=model_upload_location,
                                                                      model_hash_stage=pretrained_model_hash_stage,
                                                                      dst_model_dir=os.path.join(work_dir_in, 'models'))

        mir_metadatas, mir_annotations = merge_with_pb(mir_root=mir_root,
                                                       src_typ_rev_tids=src_typ_rev_tids,
                                                       ex_typ_rev_tids=[],
                                                       strategy=strategy)

        # export
        logging.info("exporting assets")
        # type names to type ids
        # ['cat', 'person'] -> [4, 2]
        cls_mgr = class_ids.load_or_create_userlabels(label_storage_file=label_storage_file)
        type_ids_list, unknown_names = cls_mgr.id_for_names(class_names)
        if not type_ids_list:
            logging.info(f"type ids empty, please check config file: {config_file}")
            return MirCode.RC_CMD_INVALID_ARGS
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknown class names: {unknown_names}")

        type_id_idx_mapping = {type_id: index for (index, type_id) in enumerate(type_ids_list)}
        anno_format, asset_format = exporter.parse_export_type(type_str=executor_config.get('export_format', ''))
        ec = mirpb.ExportConfig(asset_format=asset_format,
                                asset_dir=asset_dir,
                                asset_index_file=os.path.join(work_dir_in, "idx-assets.tsv"),
                                asset_index_prefix="/in/assets",
                                media_location=media_location,
                                need_sub_folder=True,
                                anno_format=anno_format,
                                gt_dir=work_dir_gt,
                                gt_index_file=os.path.join(work_dir_in, "idx-gt.tsv"),
                                gt_index_prefix="/in/annotations",
                                pred_dir=work_dir_pred,
                                pred_index_file=os.path.join(work_dir_in, "idx-pred.tsv"),
                                pred_index_prefix="/in/predictions",
                                tvt_index_dir=work_dir_in,)
        export_code = exporter.export_mirdatas_to_dir(
            mir_metadatas=mir_metadatas,
            ec=ec,
            mir_annotations=mir_annotations,
            class_ids_mapping=type_id_idx_mapping,
            cls_id_mgr=cls_mgr,
        )
        if export_code != MirCode.RC_OK:
            return export_code
        logging.info("finish exporting, starting train docker container")

        # generate configs
        out_config_path = os.path.join(work_dir_in, "config.yaml")
        executor_config = _generate_config(
            executor_config=executor_config,
            out_config_path=out_config_path,
            task_id=task_id,
            pretrained_model_params=[os.path.join('/in/models', name) for name in pretrained_model_stage_and_names])
        env_config.generate_training_env_config_file(task_id=task_id,
                                                     env_config_file_path=os.path.join(work_dir_in, 'env.yaml'))

        task_config = config.get(mir_settings.TASK_CONTEXT_KEY, {})
        task_code = MirCode.RC_OK
        return_msg = ""
        try:
            run_docker_executant(
                work_dir_in=work_dir_in,
                work_dir_out=work_dir_out,
                executor=executor,
                executant_name=executant_name,
                executor_config=executor_config,
                gpu_id=task_config.get('available_gpu_id', ""),
                run_as_root=run_as_root,
                task_config=task_config,
            )
        except CalledProcessError as e:
            logging.warning(f"training exception: {e}")
            # don't exit, proceed if model exists
            task_code = MirCode.RC_CMD_CONTAINER_ERROR
            return_msg = env_config.collect_executor_outlog_tail(work_dir=work_dir)

            # write executor tail to tensorboard
            if return_msg:
                with SummaryWriter(logdir=tensorboard_dir) as tb_writer:
                    tb_writer.add_text(tag='executor tail', text_string=f"```\n{return_msg}\n```", walltime=time.time())

        # gen task_context
        task_context = task_config
        task_context.update({
            'src_revs': src_revs,
            'dst_rev': dst_rev,
            'executor': executor,
            mir_settings.PRODUCER_KEY: mir_settings.PRODUCER_NAME,
        })

        # save model
        logging.info(f"saving models:\n task_context: {task_context}")
        out_model_dir = os.path.join(work_dir_out, "models")
        model_storage = _get_model_storage(model_root=out_model_dir,
                                           executor_config=executor_config,
                                           task_context=task_context)
        models.pack_and_copy_models(model_storage=model_storage,
                                    model_dir_path=out_model_dir,
                                    model_location=model_upload_location)

        # commit task
        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeTraining,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  message='training',
                                                  model_meta=model_storage.get_model_meta(),
                                                  return_code=task_code,
                                                  return_msg=return_msg,
                                                  serialized_executor_config=yaml.safe_dump(executor_config),
                                                  executor=executor,
                                                  src_revs=src_revs,
                                                  dst_rev=dst_rev)

        if task_code != MirCode.RC_OK:
            raise MirContainerError(error_message='container error occured', task=task)

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tids[0].rev,
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas(),
                                                          mirpb.MirStorage.MIR_ANNOTATIONS:
                                                          make_empty_mir_annotations()
                                                      },
                                                      task=task)

        logging.info("training done")

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    train_arg_parser = subparsers.add_parser("train",
                                             parents=[parent_parser],
                                             description="use this command to train current workspace",
                                             help="train current workspace")
    train_arg_parser.add_argument("--model-location",
                                  required=True,
                                  dest="model_path",
                                  type=str,
                                  help="storage place (upload location) to store packed model")
    train_arg_parser.add_argument("--media-location",
                                  required=True,
                                  dest="media_location",
                                  type=str,
                                  help="media storage location for models")
    train_arg_parser.add_argument('--model-hash',
                                  dest='model_hash_stage',
                                  type=str,
                                  required=False,
                                  help='model hash to be used')
    train_arg_parser.add_argument("-w", required=True, dest="work_dir", type=str, help="work place for training")
    train_arg_parser.add_argument('--asset-cache-dir',
                                  required=False,
                                  dest='asset_cache_dir',
                                  type=str,
                                  default='',
                                  help='asset cache directory')
    train_arg_parser.add_argument("--executor",
                                  required=True,
                                  dest="executor",
                                  type=str,
                                  help="docker image name for training")
    train_arg_parser.add_argument('--executant-name',
                                  required=False,
                                  dest='executant_name',
                                  type=str,
                                  help='docker container name for training')
    train_arg_parser.add_argument("--src-revs",
                                  dest="src_revs",
                                  type=str,
                                  required=True,
                                  help="source tvt types, revs and base task ids, first the host, others the guests, "
                                  "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    train_arg_parser.add_argument("-s",
                                  dest="strategy",
                                  type=str,
                                  default="stop",
                                  choices=["stop", "host", "guest"],
                                  help="conflict resolvation strategy, stop (default): stop when conflict detects; "
                                  "host: use host; guest: use guest")
    train_arg_parser.add_argument("--dst-rev",
                                  dest="dst_rev",
                                  type=str,
                                  required=True,
                                  help="rev@tid: destination branch name and task id")
    train_arg_parser.add_argument("--task-config-file",
                                  dest="config_file",
                                  type=str,
                                  required=True,
                                  help="path to executor config file")
    train_arg_parser.add_argument("--tensorboard-dir",
                                  dest="tensorboard_dir",
                                  type=str,
                                  required=False,
                                  help="tensorboard log directory")
    train_arg_parser.add_argument("--run-as-root",
                                  dest="run_as_root",
                                  action='store_true',
                                  help="run executor as root user")
    train_arg_parser.set_defaults(func=CmdTrain)
