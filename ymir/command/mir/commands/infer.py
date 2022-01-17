import argparse
import json
import logging
import os
import subprocess
import time
from typing import Any, Tuple, Optional

import yaml

from mir.commands import base
from mir.tools import utils as mir_utils
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


class CmdInfer(base.BaseCommand):
    """
    infer command

    Steps:
        a. prepare_env: make dirs
        b. prepare_assets: copy assets in orig index.tsv into work_dir/in/candidate, and make candidate index.tsv
        c. prepare_model: copy model to work_dir/in/model and unpack
        d. prepare_config_file: generate work_dir/in/config.yaml
        e. run_docker_cmd: bind paths and run docker cmd

    About path mappings:
        a. work_dir/in/candidate -> /in/candidate
        b. work_dir/in/model -> /in/model
        c: work_dir/out -> out
        d: work_dir/in/candidate/index.tsv -> /in/candidate/index.tsv
        e: work_dir/in/config.yaml -> /in/config.yaml
    """
    def run(self) -> int:
        logging.debug("command infer: %s", self.args)

        return CmdInfer.run_with_args(work_dir=self.args.work_dir,
                                      media_path=self.args.work_dir,
                                      model_location=self.args.model_location,
                                      model_hash=self.args.model_hash,
                                      index_file=self.args.index_file,
                                      config_file=self.args.config_file,
                                      executor=self.args.executor,
                                      executor_instance=self.args.executor_instance,
                                      run_infer=True,
                                      run_mining=False)

    @staticmethod
    def run_with_args(work_dir: str,
                      media_path: str,
                      model_location: str,
                      model_hash: str,
                      index_file: str,
                      config_file: str,
                      executor: str,
                      executor_instance: str,
                      task_id: str = f"default-infer-{time.time()}",
                      shm_size: str = None,
                      run_infer: bool = False,
                      run_mining: bool = False) -> int:
        """run infer command

        This function can be called from cmd infer, or as part of minig cmd

        Args:
            work_dir (str): work directory, in which the command generates tmp files
            media_path (str): media path, all medias in `index_file` should all in this `media_path`
                in cmd infer, set it to work_dir, in cmd mining, set it to media_cache or work_dir
            model_location (str): model location
            model_hash (str): model package hash (or model package name)
            index_file (str): index file, each line means an image abs path
            config_file (str): configuration file passed to infer executor
            executor (str): docker image name used to infer
            executor_instance (str): docker container name
            task_id (str, optional): id of this infer (or mining) task. Defaults to 'default-infer' + timestamp.
            shm_size (str, optional): shared memory size used to start the infer docker. Defaults to None.
            run_infer (bool, optional): run or not run infer. Defaults to False.
            run_mining (bool, optional): run or not run mining, Defaults to False.

        Returns:
            int: [description]
        """
        # check args
        if not work_dir:
            logging.error('empty --work-dir, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not model_location:
            logging.error('empty --model-location, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not model_hash:
            logging.error('empty --model-hash, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        if not index_file or not os.path.isfile(index_file):
            logging.error(f"invalid --index-file: {index_file}, abort")
            return MirCode.RC_CMD_INVALID_ARGS

        if not config_file:
            logging.error("empty --config-file")
            return MirCode.RC_CMD_INVALID_ARGS
        if not os.path.isfile(config_file):
            logging.error(f"invalid --config-file {config_file}, not a file, abort")
            return MirCode.RC_CMD_INVALID_ARGS

        if not run_infer and not run_mining:
            logging.warning('invalid run_infer and run_mining: both false')
            return MirCode.RC_OK

        if not executor:
            logging.error('empty --executor, abort')
            return MirCode.RC_CMD_INVALID_ARGS

        if not executor_instance:
            executor_instance = task_id

        _, work_model_path, work_out_path = _prepare_env(work_dir)
        work_index_file = os.path.join(work_dir, 'in', 'candidate', 'index.tsv')
        work_config_file = os.path.join(work_dir, 'in', 'config.yaml')

        _prepare_assets(index_file=index_file, work_index_file=work_index_file, media_path=media_path)

        model_storage = mir_utils.prepare_model(model_location, model_hash, work_model_path)
        model_names = model_storage.models
        class_names = model_storage.class_names
        if not class_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_FILE,
                                  error_message=f"empty class names in model: {model_hash}")
        prepare_config_file(config_file=config_file,
                            dst_config_file=work_config_file,
                            class_names=class_names,
                            task_id=task_id,
                            model_params_path=[os.path.join('/in/model', name) for name in model_names],
                            run_infer=run_infer,
                            run_mining=run_mining)

        run_docker_cmd(asset_path=media_path,
                       index_file_path=work_index_file,
                       model_path=work_model_path,
                       config_file_path=work_config_file,
                       out_path=work_out_path,
                       executor=executor,
                       executor_instance=executor_instance,
                       shm_size=shm_size,
                       task_type=task_id)

        if run_infer:
            _process_infer_results(infer_result_file=os.path.join(work_out_path, 'infer-result.json'),
                                   max_boxes=_get_max_boxes(config_file))

        return MirCode.RC_OK


def _prepare_env(work_dir: str) -> Tuple[str, str, str]:
    """
    make the following dir structures:
    * work_dir
            * in
                    * candidate
                    * model
            * out

    if work_dir already exists, do nothing

    Args:
        work_dir (str): work dir root
    """
    os.makedirs(os.path.join(work_dir, 'in'), exist_ok=True)
    work_assets_path = os.path.join(work_dir, 'in', 'candidate')
    work_model_path = os.path.join(work_dir, 'in', 'model')
    work_out_path = os.path.join(work_dir, 'out')
    os.makedirs(work_assets_path, exist_ok=True)
    os.makedirs(work_model_path, exist_ok=True)
    os.makedirs(work_out_path, exist_ok=True)

    return work_assets_path, work_model_path, work_out_path


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
            f.write(f"/in/candidate/{media_key}\n")

    if not media_keys_set:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='no assets to infer, abort',
                              needs_new_commit=False)


def _process_infer_results(infer_result_file: str, max_boxes: int) -> None:
    if not os.path.isfile(infer_result_file):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_FILE,
                              error_message=f"can not find result file: {infer_result_file}")

    with open(infer_result_file, 'r') as f:
        results = json.loads(f.read())

    if 'detection' in results:
        names_annotations_dict = results['detection']
        for _, annotations_dict in names_annotations_dict.items():
            if 'annotations' in annotations_dict and isinstance(annotations_dict['annotations'], list):
                annotations_dict['annotations'].sort(key=(lambda x: x['score']), reverse=True)
                annotations_dict['annotations'] = annotations_dict['annotations'][:max_boxes]

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
def prepare_config_file(config_file: str, dst_config_file: str, **kwargs: Any) -> None:
    with open(config_file, 'r') as f:
        infer_config = yaml.safe_load(f)

    for k, v in kwargs.items():
        infer_config[k] = v

    logging.debug(f"infer_config: {infer_config}")

    with open(dst_config_file, 'w') as f:
        yaml.dump(infer_config, f)


def run_docker_cmd(asset_path: str, index_file_path: str, model_path: str, config_file_path: str, out_path: str,
                   executor: str, executor_instance: str, shm_size: Optional[str], task_type: str) -> int:
    """ runs infer or mining docker container """
    cmd = ['nvidia-docker', 'run', '--rm']
    # path bindings
    cmd.extend(['-v', f"{asset_path}:/in/candidate"])
    cmd.extend(['-v', f"{model_path}:/in/model"])
    cmd.extend(['-v', f"{index_file_path}:/in/candidate/index.tsv"])
    cmd.extend(['-v', f"{config_file_path}:/in/config.yaml"])
    cmd.extend(['-v', f"{out_path}:/out"])
    # permissions and shared memory
    cmd.extend(['--user', f"{os.getuid()}:{os.getgid()}"])
    if shm_size:
        cmd.append(f"--shm-size={shm_size}")
    cmd.extend(['--name', executor_instance])
    cmd.append(executor)

    out_log_path = os.path.join(out_path, 'ymir-executor-out.log')
    logging.info(f"starting {task_type} docker container with cmd: {' '.join(cmd)}")
    with open(out_log_path, 'a') as f:
        # run and wait, if non-zero value returned, raise
        subprocess.run(cmd, check=True, stdout=f, stderr=f, text=True)

    return MirCode.RC_OK


# public: cli bind
def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    infer_arg_parser = subparsers.add_parser('infer',
                                             description='use this command to inference images',
                                             help='inference images')
    infer_arg_parser.add_argument('--index-file', dest='index_file', type=str, required=True, help='path to index file')
    infer_arg_parser.add_argument('-w',
                                  required=True,
                                  dest='work_dir',
                                  type=str,
                                  help='work place for mining and monitoring')
    infer_arg_parser.add_argument('--model-location',
                                  required=True,
                                  dest='model_location',
                                  type=str,
                                  help='model storage location for models')
    infer_arg_parser.add_argument('--model-hash',
                                  dest='model_hash',
                                  type=str,
                                  required=True,
                                  help='model hash to be used')
    infer_arg_parser.add_argument('--config-file',
                                  dest='config_file',
                                  type=str,
                                  required=True,
                                  help='path to executor config file')
    infer_arg_parser.add_argument('--executor',
                                  required=True,
                                  dest='executor',
                                  type=str,
                                  help="docker image name for infer or mining")
    infer_arg_parser.add_argument('--executor-instance',
                                  required=False,
                                  dest='executor_instance',
                                  type=str,
                                  help='docker container name for infer or mining')
    infer_arg_parser.set_defaults(func=CmdInfer)
