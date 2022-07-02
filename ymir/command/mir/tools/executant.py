import logging
import os
import subprocess
from requests.exceptions import ConnectionError, HTTPError, Timeout
from typing import Dict, List

from mir.tools import settings as mir_settings
from mir.tools import utils as mir_utils
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def _execute_in_openpai(
    work_dir_in: str,
    work_dir_out: str,
    executor: str,
    executant_name: str,
    executor_config: Dict,
    gpu_id: str,
    run_as_root: bool,
    task_config: Dict,
) -> int:
    # openpai_host = task_config.get("openpai_host", ""),
    # openpai_token = task_config.get("openpai_token", ""),
    # openpai_storage = task_config.get("openpai_storage", ""),
    # openpai_user = task_config.get("openpai_user", ""),

    return _execute_locally(
        work_dir_in=work_dir_in,
        work_dir_out=work_dir_out,
        executor=executor,
        executant_name=executant_name,
        executor_config=executor_config,
        gpu_id=gpu_id,
        run_as_root=run_as_root,
    )


def _get_shm_size(executor_config: Dict) -> str:
    if 'shm_size' not in executor_config:
        return '16G'
    return executor_config['shm_size']


def _append_binds(cmd: List, bind_path: str) -> None:
    if os.path.exists(bind_path) and os.path.islink(bind_path):
        actual_bind_path = os.readlink(bind_path)
        cmd.append(f"-v{actual_bind_path}:{actual_bind_path}")


def _execute_locally(
    work_dir_in: str,
    work_dir_out: str,
    executor: str,
    executant_name: str,
    executor_config: Dict,
    gpu_id: str,
    run_as_root: bool,
) -> int:
    cmd = [mir_utils.get_docker_executable(gpu_ids=gpu_id), 'run', '--rm']
    # path bindings
    cmd.append(f"-v{work_dir_in}:/in:ro")
    cmd.append(f"-v{work_dir_out}:/out")
    # assets and tensorboard dir may be sym-links, check and mount on demands.
    _append_binds(cmd, os.path.join(work_dir_in, 'assets'))
    _append_binds(cmd, os.path.join(work_dir_in, 'models'))
    _append_binds(cmd, os.path.join(work_dir_out, 'tensorboard'))

    # permissions and shared memory
    if not run_as_root:
        cmd.extend(['--user', f"{os.getuid()}:{os.getgid()}"])
    if gpu_id:
        cmd.extend(['--gpus', f"\"device={gpu_id}\""])
    cmd.append(f"--shm-size={_get_shm_size(executor_config=executor_config)}")
    cmd.extend(['--name', executant_name])
    cmd.append(executor)

    out_log_path = os.path.join(work_dir_out, mir_settings.EXECUTOR_OUTLOG_NAME)
    logging.info(f"starting {executant_name} docker container with cmd: {' '.join(cmd)}")
    with open(out_log_path, 'a') as f:
        # run and wait, if non-zero value returned, raise
        subprocess.run(cmd, check=True, stdout=f, stderr=f, text=True)

    return MirCode.RC_OK


def prepare_executant_env(work_dir_in: str,
                          work_dir_out: str,
                          asset_cache_dir: str = None,
                          tensorboard_dir: str = None) -> None:
    os.makedirs(work_dir_in, exist_ok=True)
    # assets folder, fixed location at work_dir_in/assets.
    asset_dir = os.path.join(work_dir_in, 'assets')
    if asset_cache_dir:
        if asset_cache_dir != asset_dir:
            os.symlink(asset_cache_dir, asset_dir)
    else:
        os.makedirs(asset_dir, exist_ok=True)
    work_dir_annotations = os.path.join(work_dir_in, 'annotations')
    os.makedirs(work_dir_annotations, exist_ok=True)
    work_dir_gt = os.path.join(work_dir_in, 'groundtruth')
    os.makedirs(work_dir_gt, exist_ok=True)
    work_dir_in_model = os.path.join(work_dir_in, 'models')
    os.makedirs(work_dir_in_model, exist_ok=True)

    os.makedirs(work_dir_out, exist_ok=True)
    out_model_dir = os.path.join(work_dir_out, 'models')
    os.makedirs(out_model_dir, exist_ok=True)
    # Build tensorbaord folder, fixed location at work_dir_out/tensorboard
    tensorboard_dir_local = os.path.join(work_dir_out, 'tensorboard')
    if tensorboard_dir:
        if tensorboard_dir != tensorboard_dir_local:
            os.system(f"chmod -R 777 {tensorboard_dir}")
            os.symlink(tensorboard_dir, tensorboard_dir_local)
    else:
        os.makedirs(tensorboard_dir_local, exist_ok=True)
    os.system(f"chmod -R 777 {work_dir_out}")


def run_docker_executant(work_dir_in: str,
                         work_dir_out: str,
                         executor: str,
                         executant_name: str,
                         executor_config: Dict,
                         gpu_id: str,
                         run_as_root: bool,
                         task_config: Dict = {}) -> int:
    if task_config.get("openpai_enable", False):
        logging.info("Run executor task on OpenPai.")
        try:
            return _execute_in_openpai(
                work_dir_in=work_dir_in,
                work_dir_out=work_dir_out,
                executor=executor,
                executant_name=executant_name,
                executor_config=executor_config,
                gpu_id=gpu_id,
                run_as_root=run_as_root,
                task_config=task_config,
            )
        except (ConnectionError, HTTPError, Timeout):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_OPENPAI_ERROR, error_message='OpenPai Error')
    else:
        logging.info("Run training task on locally.")
        return _execute_locally(
            work_dir_in=work_dir_in,
            work_dir_out=work_dir_out,
            executor=executor,
            executant_name=executant_name,
            executor_config=executor_config,
            gpu_id=gpu_id,
            run_as_root=run_as_root,
        )
