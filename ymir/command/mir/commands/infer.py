import argparse
import json
import logging
import os
import time
from typing import Any

import yaml

from mir.commands import base
from mir.tools import checker, class_ids, models
from mir.tools import settings as mir_settings
from mir.tools import env_config
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.executant import prepare_executant_env, run_docker_executant


class CmdInfer(base.BaseCommand):
    """
    infer command

    Steps:
        a. prepare_env: make dirs
        b. prepare_assets: copy assets in orig index.tsv into work_dir/in/candidate, and make candidate index.tsv
        c. prepare_model: copy model to work_dir/in/models and unpack
        d. prepare_config_file: generate work_dir/in/config.yaml
        e. _execute_locally/_execute_in_openpai: bind paths and run docker cmd

    About path bindings:
        a. work_dir/in/assets or cache -> /in/assets
        b. work_dir/in/models -> /in/models
        c. work_dir/in/candidate-index.tsv -> /in/candidate-index.tsv
        d. work_dir/in/config.yaml -> /in/config.yaml
        e. work_dir/out -> out
    """
    def run(self) -> int:
        logging.debug("command infer: %s", self.args)

        work_dir_in_model = os.path.join(self.args.work_dir, 'in', 'models')
        model_hash, stage_name = models.parse_model_hash_stage(self.args.model_hash_stage)
        model_storage = models.prepare_model(model_location=self.args.model_location,
                                             model_hash=model_hash,
                                             stage_name=stage_name,
                                             dst_model_path=work_dir_in_model)

        return CmdInfer.run_with_args(work_dir=self.args.work_dir,
                                      mir_root=self.args.mir_root,
                                      media_path=os.path.join(self.args.work_dir, 'assets'),
                                      model_storage=model_storage,
                                      index_file=self.args.index_file,
                                      config_file=self.args.config_file,
                                      executor=self.args.executor,
                                      executant_name=self.args.executant_name,
                                      run_as_root=self.args.run_as_root,
                                      run_infer=True,
                                      run_mining=False)

    @staticmethod
    def run_with_args(work_dir: str,
                      mir_root: str,
                      media_path: str,
                      model_storage: models.ModelStorage,
                      index_file: str,
                      config_file: str,
                      executor: str,
                      executant_name: str,
                      run_as_root: bool,
                      task_id: str = f"default-infer-{time.time()}",
                      run_infer: bool = False,
                      run_mining: bool = False) -> int:
        """run infer command

        This function can be called from cmd infer, or as part of minig cmd

        Args:
            work_dir (str): work directory, in which the command generates tmp files
            media_path (str): media path, all medias in `index_file` should all in this `media_path`
                in cmd infer, set it to work_dir, in cmd mining, set it to media_cache or work_dir
            model_location (str): model location
            model_hash_stage (str): model_hash@stage_name
            index_file (str): index file, each line means an image abs path
            config_file (str): configuration file passed to infer executor
            executor (str): docker image name used to infer
            executant_name (str): docker container name
            task_id (str, optional): id of this infer (or mining) task. Defaults to 'default-infer' + timestamp.
            shm_size (str, optional): shared memory size used to start the infer docker. Defaults to None.
            run_infer (bool, optional): run or not run infer. Defaults to False.
            run_mining (bool, optional): run or not run mining, Defaults to False.

        Returns:
            int: [description]
        """
        # check args
        if not mir_root:
            mir_root = '.'
        if not work_dir:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty --work-dir')
        if not index_file or not os.path.isfile(index_file):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"invalid --index-file: {index_file}")
        if not config_file or not os.path.isfile(config_file):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"invalid --task-config-file: {config_file}")
        if not run_infer and not run_mining:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='invalid run_infer and run_mining: both false')
        if not executor:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty --executor')

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            raise MirRuntimeError(error_code=return_code, error_message=f"check failed: {return_code}")

        if not executant_name:
            executant_name = task_id

        work_dir_in = os.path.join(work_dir, "in")
        work_dir_out = os.path.join(work_dir, "out")
        prepare_executant_env(work_dir_in=work_dir_in, work_dir_out=work_dir_out, asset_cache_dir=media_path)

        work_index_file = os.path.join(work_dir_in, 'candidate-index.tsv')
        work_config_file = os.path.join(work_dir_in, 'config.yaml')
        work_env_config_file = os.path.join(work_dir_in, 'env.yaml')

        _prepare_assets(index_file=index_file, work_index_file=work_index_file, media_path=media_path)

        class_names = model_storage.class_names
        if not class_names:
            raise MirRuntimeError(
                error_code=MirCode.RC_CMD_INVALID_FILE,
                error_message=f"empty class names in model: {model_storage.model_hash}@{model_storage.stage_name}")

        model_names = model_storage.stages[model_storage.stage_name].files
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        prepare_config_file(
            config=config,
            dst_config_file=work_config_file,
            class_names=class_names,
            task_id=task_id,
            model_params_path=[os.path.join('/in/models', model_storage.stage_name, name) for name in model_names],
            run_infer=run_infer,
            run_mining=run_mining)

        env_config.generate_mining_infer_env_config_file(task_id=task_id,
                                                         run_mining=run_mining,
                                                         run_infer=run_infer,
                                                         env_config_file_path=work_env_config_file)

        task_config = config.get(mir_settings.TASK_CONTEXT_KEY, {})
        run_docker_executant(
            work_dir_in=work_dir_in,
            work_dir_out=work_dir_out,
            executor=executor,
            executant_name=executant_name,
            executor_config=config[mir_settings.EXECUTOR_CONFIG_KEY],
            gpu_id=task_config.get('available_gpu_id', ""),
            run_as_root=run_as_root,
            task_config=task_config,
        )

        if run_infer:
            _process_infer_results(infer_result_file=os.path.join(work_dir_out, 'infer-result.json'),
                                   max_boxes=_get_max_boxes(config_file),
                                   mir_root=mir_root)

        return MirCode.RC_OK


def _prepare_assets(index_file: str, work_index_file: str, media_path: str) -> None:
    """
    generates in container index file

    Args:
        index_file (str): path to source index file
        work_index_file (str): path to destination index file used in container
        media_path (str): path for all medias

    Raise:
        FileNotFoundError: if index_file not found, or assets in index_file not found
    """
    with open(index_file, 'r') as f:
        asset_files = f.readlines()

    # copy assets (and also generate in-container index file)
    media_keys_set = set()  # detect dumplicate media keys
    with open(work_index_file, 'w') as f:
        for src_asset_file in asset_files:
            # skip blank lines
            src_asset_file = src_asset_file.strip()
            if not src_asset_file:
                continue

            # check rel path
            if not src_asset_file.startswith('/'):
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message=f"rel path not allowed: {src_asset_file}",
                                      needs_new_commit=False)

            # check repeat
            media_key = os.path.relpath(path=src_asset_file, start=media_path)
            if media_key in media_keys_set:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message=f"dumplicate image name: {media_key}, abort",
                                      needs_new_commit=False)
            media_keys_set.add(media_key)

            # write in-container index file
            f.write(f"/in/assets/{media_key}\n")

    if not media_keys_set:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='no assets to infer, abort',
                              needs_new_commit=False)


def _process_infer_results(infer_result_file: str, max_boxes: int, mir_root: str) -> None:
    if not os.path.isfile(infer_result_file):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_NO_RESULT,
                              error_message=f"can not find result file: {infer_result_file}")

    with open(infer_result_file, 'r') as f:
        results = json.loads(f.read())

    class_id_mgr = class_ids.load_or_create_userlabels(mir_root=mir_root)

    for _, annotations_dict in results.get('detection', {}).items():
        # Compatible with previous version of format.
        annotations = annotations_dict.get('boxes') or annotations_dict.get('annotations')
        if not isinstance(annotations, list):
            continue

        annotations.sort(key=(lambda x: x['score']), reverse=True)
        annotations = [a for a in annotations if class_id_mgr.has_name(a['class_name'])]
        annotations_dict['boxes'] = annotations[:max_boxes]

    with open(infer_result_file, 'w') as f:
        f.write(json.dumps(results, indent=4))


def _get_max_boxes(config_file: str) -> int:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f.read())

    max_boxes = config.get('max_boxes', 50)
    if not isinstance(max_boxes, int) or max_boxes <= 0:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"invalid max_boxes: {max_boxes}")

    return max_boxes


# might used both by mining and infer
# public: general
def prepare_config_file(config: dict, dst_config_file: str, **kwargs: Any) -> None:
    executor_config = config[mir_settings.EXECUTOR_CONFIG_KEY]

    for k, v in kwargs.items():
        executor_config[k] = v

    logging.info(f"container config: {executor_config}")

    with open(dst_config_file, 'w') as f:
        yaml.dump(executor_config, f)


# public: cli bind
def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    infer_arg_parser = subparsers.add_parser('infer',
                                             parents=[parent_parser],
                                             description='use this command to inference images',
                                             help='inference images')
    infer_arg_parser.add_argument('--index-file', dest='index_file', type=str, required=True, help='path to index file')
    infer_arg_parser.add_argument('-w',
                                  required=True,
                                  dest='work_dir',
                                  type=str,
                                  help='work place for this command, all images should put to <work_dir>/assets')
    infer_arg_parser.add_argument('--model-location',
                                  required=True,
                                  dest='model_location',
                                  type=str,
                                  help='model storage location for models')
    infer_arg_parser.add_argument('--model-hash',
                                  dest='model_hash_stage',
                                  type=str,
                                  required=True,
                                  help='model hash@stage to be used')
    infer_arg_parser.add_argument('--task-config-file',
                                  dest='config_file',
                                  type=str,
                                  required=True,
                                  help='path to executor config file')
    infer_arg_parser.add_argument('--executor',
                                  required=True,
                                  dest='executor',
                                  type=str,
                                  help="docker image name for infer or mining")
    infer_arg_parser.add_argument('--executant-name',
                                  required=False,
                                  dest='executant_name',
                                  type=str,
                                  help='docker container name for infer or mining')
    infer_arg_parser.add_argument("--run-as-root",
                                  dest="run_as_root",
                                  action='store_true',
                                  help="run executor as root user")
    infer_arg_parser.set_defaults(func=CmdInfer)
