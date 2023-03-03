import logging
import os
import random
import sys
import time
from typing import List

# view https://github.com/protocolbuffers/protobuf/issues/10051 for detail
os.environ.setdefault('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'python')
from tensorboardX import SummaryWriter
from ymir_exc import dataset_reader as dr
from ymir_exc import env, monitor
from ymir_exc import result_writer as rw
from ymir_exc.code import ExecutorReturnCode, ExecutorState


def start() -> int:
    env_config = env.get_current_env()

    if env_config.run_training:
        _run_training(env_config)
    if env_config.run_mining:
        _run_mining(env_config)
    if env_config.run_infer:
        _run_infer(env_config)

    return 0


def _run_training(env_config: env.EnvConfig) -> None:
    """
    sample function of training, which shows:
    1. how to get config file
    2. how to read training and validation datasets
    3. how to write logs
    4. how to write training result
    """
    #! use `env.get_executor_config` to get config file for training
    executor_config = env.get_executor_config()
    class_names: List[str] = executor_config['class_names']
    expected_mAP: float = executor_config.get('expected_map', 0.6)
    idle_seconds: float = executor_config.get('idle_seconds', 60)
    crash_code: bool = executor_config.get('crash_code', ExecutorReturnCode.RC_EXEC_NO_ERROR)
    #! use `logging` or `print` to write log to console
    #   notice that logging.basicConfig is invoked at executor.env
    logging.info(f"training config: {executor_config}")

    #! use `dataset_reader.item_paths` to read training or validation dataset items
    #!  note that `dataset_reader.item_paths` is a generator
    absent_count = 0
    for asset_path, annotation_path in dr.item_paths(dataset_type=env.DatasetType.TRAINING):
        isfile = os.path.isfile(asset_path)
        if not isfile:
            absent_count += 1
        logging.info(f"asset: {asset_path}, is file: {isfile}; "
                     f"annotation: {annotation_path}, is file: {os.path.isfile(annotation_path)}")
    logging.info(f"absent: {absent_count}")

    #! use `monitor.write_monitor_logger` to write write task process percent to monitor.txt
    monitor.write_monitor_logger(percent=0.5)

    _dummy_work(idle_seconds=idle_seconds, crash_code=crash_code)

    # suppose we have a long time training, and have saved the final model
    #! model output dir: os.path.join(env_config.output.models_dir, your_stage_name)
    stage_dir = os.path.join(env_config.output.models_dir, 'stage_00')
    os.makedirs(stage_dir, exist_ok=True)
    with open(os.path.join(stage_dir, 'model-0000.params'), 'w') as f:
        f.write('fake model-0000.params')
    with open(os.path.join(stage_dir, 'model-symbols.json'), 'w') as f:
        f.write('fake model-symbols.json')
    #! use `rw.write_model_stage` to save training result
    rw.write_model_stage(stage_name='stage_00',
                         files=['model-0000.params', 'model-symbols.json'],
                         evaluation_result={
                             'mAP': expected_mAP / 2,
                             'mAR': 0.35,
                             'tp': 50,
                             'fp': 30,
                             'fn': 20
                         },
                         evaluate_config={
                             'iou_thr': 0.5,
                             'conf_thr': 0.005
                         })

    write_tensorboard_log(env_config.output.tensorboard_dir)

    stage_dir = os.path.join(env_config.output.models_dir, 'stage_10')
    os.makedirs(stage_dir, exist_ok=True)
    with open(os.path.join(stage_dir, 'model-0010.params'), 'w') as f:
        f.write('fake model-0010.params')
    with open(os.path.join(stage_dir, 'model-symbols.json'), 'w') as f:
        f.write('fake model-symbols.json')
    rw.write_model_stage(stage_name='stage_10',
                         files=['model-0010.params', 'model-symbols.json'],
                         evaluation_result={
                             'mAP': expected_mAP,
                             'mAR': 0.35,
                             'tp': 50,
                             'fp': 30,
                             'fn': 20
                         })

    #! if task done, write 100% percent log
    logging.info('training done')
    monitor.write_monitor_logger(percent=1.0)


def _run_mining(env_config: env.EnvConfig) -> None:
    #! use `env.get_executor_config` to get config file for training
    #   models are transfered in executor_config's model_params_path
    executor_config = env.get_executor_config()
    idle_seconds: float = executor_config.get('idle_seconds', 60)
    crash_code: bool = executor_config.get('crash_code', ExecutorReturnCode.RC_EXEC_NO_ERROR)
    #! use `logging` or `print` to write log to console
    logging.info(f"mining config: {executor_config}")

    #! use `dataset_reader.item_paths` to read candidate dataset items
    #   note that annotations path will be empty str if there's no annotations in that dataset
    asset_paths = []
    absent_count = 0
    for asset_path, _ in dr.item_paths(dataset_type=env.DatasetType.CANDIDATE):
        isfile = os.path.isfile(asset_path)
        if not isfile:
            absent_count += 1
        logging.info(f"asset: {asset_path}, is file: {isfile}")
        asset_paths.append(asset_path)

    if len(asset_paths) == 0:
        raise ValueError('empty asset paths')

    #! use `monitor.write_monitor_logger` to write task process to monitor.txt
    logging.info(f"assets count: {len(asset_paths)}, absent: {absent_count}")
    monitor.write_monitor_logger(percent=0.5)

    _dummy_work(idle_seconds=idle_seconds, crash_code=crash_code)

    #! write mining result
    #   here we give a fake score to each assets
    total_length = len(asset_paths)
    mining_result = [(asset_path, index / total_length) for index, asset_path in enumerate(asset_paths)]
    rw.write_mining_result(mining_result=mining_result)

    #! if task done, write 100% percent log
    logging.info('mining done')
    monitor.write_monitor_logger(percent=1.0)


def _run_infer(env_config: env.EnvConfig) -> None:
    #! use `env.get_executor_config` to get config file for training
    #   models are transfered in executor_config's model_params_path
    executor_config = env.get_executor_config()
    class_names = executor_config['class_names']
    idle_seconds: float = executor_config.get('idle_seconds', 60)
    crash_code: bool = executor_config.get('crash_code', ExecutorReturnCode.RC_EXEC_NO_ERROR)
    seed: int = executor_config.get('seed', 15)
    #! use `logging` or `print` to write log to console
    logging.info(f"infer config: {executor_config}")

    #! use `dataset_reader.item_paths` to read candidate dataset items
    #   note that annotations path will be empty str if there's no annotations in that dataset
    asset_paths: List[str] = []
    absent_count = 0
    for asset_path, _ in dr.item_paths(dataset_type=env.DatasetType.CANDIDATE):
        isfile = os.path.isfile(asset_path)
        if not isfile:
            absent_count += 1
        logging.info(f"asset: {asset_path}, is file: {isfile}")
        asset_paths.append(asset_path)

    if len(asset_paths) == 0 or len(class_names) == 0:
        raise ValueError('empty asset paths or class names')

    #! use `monitor.write_monitor_logger` to write log to console and write task process percent to monitor.txt
    logging.info(f"assets count: {len(asset_paths)}, absent: {absent_count}")
    monitor.write_monitor_logger(percent=0.5)

    _dummy_work(idle_seconds=idle_seconds, crash_code=crash_code)

    #! write infer result
    fake_anns = []
    random.seed(seed)
    for class_name in class_names:
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        w = random.randint(50, 100)
        h = random.randint(50, 100)
        ann = rw.Annotation(class_name=class_name, score=random.random(), box=rw.Box(x=x, y=y, w=w, h=h))

        fake_anns.append(ann)

    infer_result = {asset_path: fake_anns for asset_path in asset_paths}
    rw.write_infer_result(infer_result=infer_result)

    #! if task done, write 100% percent log
    logging.info('infer done')
    monitor.write_monitor_logger(percent=1.0)


def _dummy_work(idle_seconds: float, crash_code: ExecutorReturnCode) -> None:
    if idle_seconds > 0:
        time.sleep(idle_seconds)
    if crash_code != ExecutorReturnCode.RC_EXEC_NO_ERROR:
        #! if error, write corresponding return code with monitor.write_monitor_logger
        #! and then raise exception
        monitor.write_monitor_logger(percent=1,
                                     state=ExecutorState.ES_ERROR,
                                     return_code=crash_code)
        raise RuntimeError(f"App crashed with code: {crash_code}")


def write_tensorboard_log(tensorboard_dir: str) -> None:
    tb_log = SummaryWriter(tensorboard_dir)

    total_epoch = 30
    for e in range(total_epoch):
        tb_log.add_scalar("fake_loss", 10 / (1 + e), e)
        time.sleep(1)
        monitor.write_monitor_logger(percent=e / total_epoch)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s] %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.INFO)
    sys.exit(start())
