import logging
import os
import sys
import time
from typing import List

from executor import dataset_reader as dr, env, monitor, result_writer as rw


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
    trigger_crash: bool = executor_config.get('trigger_crash', False)
    #! use `logging` or `print` to write log to console
    #   notice that logging.basicConfig is invoked at executor.env
    logging.info(f"training config: {executor_config}")

    #! use `dataset_reader.item_paths` to read training or validation dataset items
    #!  note that `dataset_reader.item_paths` is a generator
    for asset_path, annotation_path in dr.item_paths(dataset_type=env.DatasetType.TRAINING):
        logging.info(f"asset: {asset_path}, annotation: {annotation_path}")

    #! use `monitor.write_monitor_logger` to write write task process percent to monitor.txt
    monitor.write_monitor_logger(percent=0.5)

    # suppose we have a long time training, and have saved the final model
    #! use `env_config.output.models_dir` to get model output dir
    with open(os.path.join(env_config.output.models_dir, 'model-0000.params'), 'w') as f:
        f.write('fake params')
    with open(os.path.join(env_config.output.models_dir, 'model-symbols.json'), 'w') as f:
        f.write('fake json')

    #! use `rw.write_training_result` to save training result
    rw.write_training_result(model_names=['model-0000.params', 'model-symbols.json'],
                             mAP=expected_mAP,
                             classAPs={class_name: expected_mAP
                                       for class_name in class_names})

    _dummy_work(idle_seconds=idle_seconds, trigger_crash=trigger_crash)

    #! if task done, write 100% percent log
    logging.info('training done')
    monitor.write_monitor_logger(percent=1.0)


def _run_mining(env_config: env.EnvConfig) -> None:
    #! use `env.get_executor_config` to get config file for training
    #   models are transfered in executor_config's model_params_path
    executor_config = env.get_executor_config()
    idle_seconds: float = executor_config.get('idle_seconds', 60)
    trigger_crash: bool = executor_config.get('trigger_crash', False)
    #! use `logging` or `print` to write log to console
    logging.info(f"mining config: {executor_config}")

    #! use `dataset_reader.item_paths` to read candidate dataset items
    #   note that annotations path will be empty str if there's no annotations in that dataset
    asset_paths = []
    for asset_path, _ in dr.item_paths(dataset_type=env.DatasetType.CANDIDATE):
        logging.info(f"asset: {asset_path}")
        asset_paths.append(asset_path)

    if len(asset_paths) == 0:
        raise ValueError('empty asset paths')

    #! use `monitor.write_monitor_logger` to write task process to monitor.txt
    logging.info(f"assets count: {len(asset_paths)}")
    monitor.write_monitor_logger(percent=0.5)

    _dummy_work(idle_seconds=idle_seconds, trigger_crash=trigger_crash)

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
    trigger_crash: bool = executor_config.get('trigger_crash', False)
    #! use `logging` or `print` to write log to console
    logging.info(f"infer config: {executor_config}")

    #! use `dataset_reader.item_paths` to read candidate dataset items
    #   note that annotations path will be empty str if there's no annotations in that dataset
    asset_paths: List[str] = []
    for asset_path, _ in dr.item_paths(dataset_type=env.DatasetType.CANDIDATE):
        logging.info(f"asset: {asset_path}")
        asset_paths.append(asset_path)

    if len(asset_paths) == 0 or len(class_names) == 0:
        raise ValueError('empty asset paths or class names')

    #! use `monitor.write_monitor_logger` to write log to console and write task process percent to monitor.txt
    logging.info(f"assets count: {len(asset_paths)}")
    monitor.write_monitor_logger(percent=0.5)

    _dummy_work(idle_seconds=idle_seconds, trigger_crash=trigger_crash)

    #! write infer result
    fake_annotation = rw.Annotation(class_name=class_names[0], score=0.9, box=rw.Box(x=50, y=50, w=150, h=150))
    infer_result = {asset_path: [fake_annotation] for asset_path in asset_paths}
    rw.write_infer_result(infer_result=infer_result)

    #! if task done, write 100% percent log
    logging.info('infer done')
    monitor.write_monitor_logger(percent=1.0)


def _dummy_work(idle_seconds: float, trigger_crash: bool = False, gpu_memory_size: int = 0) -> None:
    if idle_seconds > 0:
        time.sleep(idle_seconds)
    if trigger_crash:
        raise RuntimeError('app crashed')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s] %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.INFO)
    sys.exit(start())
