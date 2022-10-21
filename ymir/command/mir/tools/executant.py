import logging
import os
import subprocess
from typing import Dict, List

from mir.tools import settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from requests.exceptions import ConnectionError, HTTPError, Timeout


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
        task_config=task_config,
    )


def _get_shm_size(executor_config: Dict, shm_size_count: int) -> str:
    """
    shm_size_count: shm_size_count = gpu_count if use_gpu else 1
    """
    # increase share memory according to shm_size_count
    if 'shm_size' in executor_config:
        return executor_config['shm_size']
    else:
        shm_size = 16 * shm_size_count
        return f'{shm_size}G'


def _append_binds(cmd: List, bind_path: str) -> None:
    if os.path.exists(bind_path) and os.path.islink(bind_path):
        actual_bind_path = os.readlink(bind_path)
        cmd.append(f"-v{actual_bind_path}:{actual_bind_path}")


def _get_docker_executable(runtime: str) -> str:
    if runtime == 'nvidia':
        return 'nvidia-docker'
    return 'docker'


def _execute_locally(
    work_dir_in: str,
    work_dir_out: str,
    executor: str,
    executant_name: str,
    executor_config: Dict,
    gpu_id: str,
    run_as_root: bool,
    task_config: dict,
) -> int:
    cmd = [_get_docker_executable(runtime=task_config.get('server_runtime', '')), 'run', '--rm']
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
        shm_size_count = len(gpu_id.split(','))
    else:
        shm_size_count = 1
    cmd.append(f"--shm-size={_get_shm_size(executor_config=executor_config, shm_size_count=shm_size_count)}")
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
    work_dir_pred = os.path.join(work_dir_in, 'predictions')
    os.makedirs(work_dir_pred, exist_ok=True)
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
        logging.info(f"Run executor task {executant_name} on OpenPai.")
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
        logging.info(f"Run executor task {executant_name} locally.")
        return _execute_locally(
            work_dir_in=work_dir_in,
            work_dir_out=work_dir_out,
            executor=executor,
            executant_name=executant_name,
            executor_config=executor_config,
            gpu_id=gpu_id,
            run_as_root=run_as_root,
            task_config=task_config,
        )
