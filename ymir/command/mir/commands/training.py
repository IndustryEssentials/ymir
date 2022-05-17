import argparse
import logging
import os
import time
import subprocess
from subprocess import CalledProcessError
import traceback
from typing import Any, List, Optional, Set, Tuple

from tensorboardX import SummaryWriter
import yaml

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, context, data_exporter, mir_storage_ops, revs_parser
from mir.tools import settings as mir_settings, utils as mir_utils
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.code import MirCode
from mir.tools.errors import MirContainerError, MirRuntimeError


# private: post process
def _process_model_storage(out_root: str, model_upload_location: str, executor_config: dict,
                           task_context: dict) -> Tuple[str, float]:
    """
    find and save models
    Returns:
        model hash, model mAP and ModelStorage
    """
    out_model_dir = os.path.join(out_root, "models")
    model_paths, model_mAP = _find_models(out_model_dir)
    if not model_paths:
        # if have no models
        return '', model_mAP

    model_storage = mir_utils.ModelStorage(executor_config=executor_config,
                                           task_context=dict(**task_context,
                                                             mAP=model_mAP,
                                                             type=mirpb.TaskType.TaskTypeTraining),
                                           models=[os.path.basename(model_path) for model_path in model_paths])
    model_sha1 = mir_utils.pack_and_copy_models(model_storage=model_storage,
                                                model_dir_path=out_model_dir,
                                                model_location=model_upload_location)

    return model_sha1, model_mAP


def _find_models(model_root: str) -> Tuple[List[str], float]:
    """
    find models in `model_root`, and returns model names and mAP

    Args:
        model_root (str): model root

    Returns:
        Tuple[List[str], float]: list of model names and map
    """
    model_names = []
    model_mAP = 0.0

    result_yaml_path = os.path.join(model_root, "result.yaml")
    try:
        with open(result_yaml_path, "r") as f:
            yaml_obj = yaml.safe_load(f.read())
            model_names = yaml_obj["model"]
            model_mAP = float(yaml_obj["map"])
    except FileNotFoundError:
        logging.warning(traceback.format_exc())
        return [], 0.0

    return ([os.path.join(model_root, os.path.basename(name)) for name in model_names], model_mAP)


# private: process
def _run_train_cmd(cmd: List[str], out_log_path: str) -> int:
    """
    invoke training command

    Args:
        cmd (str): command
        out_log_path (str): path of log file

    Returns:
        int: MirCode.RC_OK if success

    Raises:
        Exception: if out_log_path can not open for append, or cmd returned non-zero code
    """
    logging.info(f"training with cmd: {cmd}")
    logging.info(f"out log path: {out_log_path}")
    with open(out_log_path, 'a') as f:
        # run and wait, if non-zero value returned, raise
        subprocess.run(cmd, check=True, stdout=f, stderr=f, text=True)

    return MirCode.RC_OK


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


def _get_shm_size(executor_config: dict) -> str:
    if 'shm_size' not in executor_config:
        return '16G'
    return executor_config['shm_size']


def _prepare_pretrained_models(model_location: str, model_hash: str, dst_model_dir: str) -> List[str]:
    """
    prepare pretrained models
    * extract models to dst_model_dir
    * returns model file names

    Args:
        model_location (str): model location
        model_hash (str): model package hash
        dst_model_dir (str): dir where you want to extract model files to

    Returns:
        List[str]: model names
    """
    if not model_hash:
        return []
    model_storage = mir_utils.prepare_model(model_location=model_location,
                                            model_hash=model_hash,
                                            dst_model_path=dst_model_dir)

    return model_storage.models


def _get_task_parameters(config: dict) -> str:
    return config.get(mir_settings.TASK_CONTEXT_KEY, {}).get(mir_settings.TASK_CONTEXT_PARAMETERS_KEY, '')


class CmdTrain(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command train: %s", self.args)

        return CmdTrain.run_with_args(work_dir=self.args.work_dir,
                                      asset_cache_dir=self.args.asset_cache_dir,
                                      model_upload_location=self.args.model_path,
                                      pretrained_model_hash=self.args.model_hash,
                                      src_revs=self.args.src_revs,
                                      dst_rev=self.args.dst_rev,
                                      mir_root=self.args.mir_root,
                                      media_location=self.args.media_location,
                                      tensorboard_dir=self.args.tensorboard_dir,
                                      executor=self.args.executor,
                                      executant_name=self.args.executant_name,
                                      config_file=self.args.config_file)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str,
                      asset_cache_dir: Optional[str],
                      model_upload_location: str,
                      pretrained_model_hash: str,
                      executor: str,
                      executant_name: str,
                      src_revs: str,
                      dst_rev: str,
                      config_file: Optional[str],
                      tensorboard_dir: str,
                      mir_root: str = '.',
                      media_location: str = '') -> int:
        if not model_upload_location:
            logging.error("empty --model-location, abort")
            return MirCode.RC_CMD_INVALID_ARGS
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
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
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if return_code != MirCode.RC_OK:
            return return_code

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        task_parameters = _get_task_parameters(config)
        if not isinstance(task_parameters, str):
            raise MirRuntimeError(
                error_code=MirCode.RC_CMD_INVALID_ARGS,
                error_message=f"invalid {mir_settings.TASK_CONTEXT_PARAMETERS_KEY} in config: {config}")
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
        if not tensorboard_dir:
            tensorboard_dir = os.path.join(work_dir, 'out', 'tensorboard')
        asset_dir = asset_cache_dir or os.path.join(work_dir, 'in', 'assets')

        # if have model_hash, export model
        pretrained_model_names = _prepare_pretrained_models(model_location=model_upload_location,
                                                            model_hash=pretrained_model_hash,
                                                            dst_model_dir=os.path.join(work_dir, 'in', 'models'))

        # get train_ids and val_ids
        train_ids = set()  # type: Set[str]
        val_ids = set()  # type: Set[str]
        unused_ids = set()  # type: Set[str]
        mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root,
            mir_branch=src_typ_rev_tid.rev,
            mir_task_id=src_typ_rev_tid.tid,
            ms=mirpb.MirStorage.MIR_METADATAS)
        for asset_id, asset_attr in mir_metadatas.attributes.items():
            if asset_attr.tvt_type == mirpb.TvtTypeTraining:
                train_ids.add(asset_id)
            elif asset_attr.tvt_type == mirpb.TvtTypeValidation:
                val_ids.add(asset_id)
            else:
                unused_ids.add(asset_id)
        if not train_ids:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no training set')
        if not val_ids:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no validation set')

        if not unused_ids:
            logging.info(f"training: {len(train_ids)}, validation: {len(val_ids)}")
        else:
            logging.warning(f"training: {len(train_ids)}, validation: {len(val_ids)}" f"unused: {len(unused_ids)}")

        # export
        logging.info("exporting assets")

        os.makedirs(work_dir, exist_ok=True)

        work_dir_in = os.path.join(work_dir, "in")
        work_dir_annotations = os.path.join(work_dir_in, 'annotations')
        os.makedirs(work_dir_annotations, exist_ok=True)

        work_dir_out = os.path.join(work_dir, "out")
        os.makedirs(work_dir_out, exist_ok=True)
        out_model_dir = os.path.join(work_dir, 'out', 'models')
        os.makedirs(out_model_dir, exist_ok=True)

        os.makedirs(asset_dir, exist_ok=True)
        os.makedirs(tensorboard_dir, exist_ok=True)

        # type names to type ids
        # ['cat', 'person'] -> [4, 2]
        cls_mgr = class_ids.ClassIdManager(mir_root=mir_root)
        type_ids_list, unknown_names = cls_mgr.id_for_names(class_names)
        if not type_ids_list:
            logging.info(f"type ids empty, please check config file: {config_file}")
            return MirCode.RC_CMD_INVALID_ARGS
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknown class names: {unknown_names}")

        if not context.check_class_ids(mir_root=mir_root, current_class_ids=type_ids_list):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='user class ids mismatch')

        type_id_idx_mapping = {type_id: index for (index, type_id) in enumerate(type_ids_list)}

        # export train set
        data_exporter.export(mir_root=mir_root,
                             assets_location=media_location,
                             class_type_ids=type_id_idx_mapping,
                             asset_ids=train_ids,
                             asset_dir=asset_dir,
                             annotation_dir=work_dir_annotations,
                             need_ext=True,
                             need_id_sub_folder=True,
                             base_branch=src_typ_rev_tid.rev,
                             base_task_id=src_typ_rev_tid.tid,
                             format_type=data_exporter.ExportFormat.EXPORT_FORMAT_ARK,
                             index_file_path=os.path.join(work_dir_in, 'train-index.tsv'),
                             index_assets_prefix='/in/assets',
                             index_annotations_prefix='/in/annotations')

        # export validation set
        data_exporter.export(mir_root=mir_root,
                             assets_location=media_location,
                             class_type_ids=type_id_idx_mapping,
                             asset_ids=val_ids,
                             asset_dir=asset_dir,
                             annotation_dir=work_dir_annotations,
                             need_ext=True,
                             need_id_sub_folder=True,
                             base_branch=src_typ_rev_tid.rev,
                             base_task_id=src_typ_rev_tid.tid,
                             format_type=data_exporter.ExportFormat.EXPORT_FORMAT_ARK,
                             index_file_path=os.path.join(work_dir_in, 'val-index.tsv'),
                             index_assets_prefix='/in/assets',
                             index_annotations_prefix='/in/annotations')

        logging.info("starting train docker container")

        available_gpu_id = config.get(mir_settings.TASK_CONTEXT_KEY, {}).get('available_gpu_id', '')

        # generate configs
        out_config_path = os.path.join(work_dir_in, "config.yaml")
        executor_config = _generate_config(
            executor_config=executor_config,
            out_config_path=out_config_path,
            task_id=task_id,
            pretrained_model_params=[os.path.join('/in/models', name) for name in pretrained_model_names])
        mir_utils.generate_training_env_config_file(task_id=task_id,
                                                    env_config_file_path=os.path.join(work_dir_in, 'env.yaml'))

        # start train docker and wait
        path_binds = []
        path_binds.append(f"-v{work_dir_in}:/in")  # annotations, models, train-index.tsv, val-index.tsv, config.yaml
        path_binds.append(f"-v{asset_dir}:/in/assets:ro")  # assets
        path_binds.append(f"-v{work_dir_out}:/out")
        path_binds.append(f"-v{tensorboard_dir}:/out/tensorboard")

        cmd = ['nvidia-docker', 'run', '--rm', f"--shm-size={_get_shm_size(executor_config=executor_config)}"]
        cmd.extend(path_binds)
        if available_gpu_id:
            cmd.extend(['--gpus', f"\"device={available_gpu_id}\""])
        cmd.extend(['--user', f"{os.getuid()}:{os.getgid()}"])  # run as current user
        cmd.extend(['--name', f"{executant_name}"])  # executor name used to stop executor
        cmd.append(executor)

        task_code = MirCode.RC_OK
        return_msg = ''
        try:
            _run_train_cmd(cmd, out_log_path=os.path.join(work_dir_out, mir_settings.EXECUTOR_OUTLOG_NAME))
        except CalledProcessError as e:
            logging.warning(f"training exception: {e}")
            # don't exit, proceed if model exists
            task_code = MirCode.RC_CMD_CONTAINER_ERROR
            return_msg = mir_utils.collect_executor_outlog_tail(work_dir=work_dir)

            # write executor tail to tensorboard
            if return_msg:
                with SummaryWriter(logdir=tensorboard_dir) as tb_writer:
                    tb_writer.add_text(tag='executor tail', text_string=f"```\n{return_msg}\n```", walltime=time.time())

        # gen task_context
        task_context = {
            'src_revs': src_revs,
            'dst_rev': dst_rev,
            'executor': executor,
            mir_settings.PRODUCER_KEY: mir_settings.PRODUCER_NAME,
            mir_settings.TASK_CONTEXT_PARAMETERS_KEY: task_parameters
        }

        # save model
        logging.info("saving models")
        model_sha1, model_mAP = _process_model_storage(out_root=work_dir_out,
                                                       model_upload_location=model_upload_location,
                                                       executor_config=executor_config,
                                                       task_context=task_context)

        # commit task
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeTraining,
                                           task_id=dst_typ_rev_tid.tid,
                                           message='training',
                                           model_mAP=model_mAP,
                                           model_hash=model_sha1,
                                           return_code=task_code,
                                           return_msg=return_msg,
                                           serialized_task_parameters=task_parameters,
                                           serialized_executor_config=yaml.safe_dump(executor_config),
                                           executor=executor,
                                           src_revs=src_revs,
                                           dst_rev=dst_rev)

        if task_code != MirCode.RC_OK:
            raise MirContainerError(error_message='container error occured', task=task)

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tid.rev,
                                                      mir_datas={},
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
                                  dest='model_hash',
                                  type=str,
                                  required=False,
                                  help='model hash to be used')
    train_arg_parser.add_argument("-w", required=True, dest="work_dir", type=str, help="work place for training")
    train_arg_parser.add_argument('--asset-cache-dir',
                                  required=False,
                                  dest='asset_cache_dir',
                                  type=str,
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
                                  help="rev@bid: source rev and base task id")
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
    train_arg_parser.set_defaults(func=CmdTrain)
