import os.path as osp
import time

from pygtail import Pygtail
from tensorboardX import SummaryWriter

from ymir_exc import env

TASK_STATE_RUNNING = 2
_TENSORBOARD_GLOBAL_STEP = 0


def write_monitor_logger(percent: float) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{TASK_STATE_RUNNING}\n")


def write_tensorboard_text() -> None:
    env_config = env.get_current_env()
    tb_log_file = osp.join(env_config.output.tensorboard_dir, 'tensorboard_text.log')
    executor_log_file = env_config.output.executor_log_file
    writer = SummaryWriter(tb_log_file)

    # Pygtail always return the new lines
    for line in Pygtail(executor_log_file):
        writer.add_text(tag='ymir-executor', text_string=line, global_step=_TENSORBOARD_GLOBAL_STEP)
        _TENSORBOARD_GLOBAL_STEP += 1

    writer.close()
