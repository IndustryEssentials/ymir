import os
import time

from tensorboardX import SummaryWriter

from ymir_exc import env

TASK_STATE_RUNNING = 2


def write_monitor_logger(percent: float) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{TASK_STATE_RUNNING}\n")


def write_tensorboard_text(text: str, tb_log_file: str = 'tensorboard_text.log',
                           tag: str = "", global_step: int = -1) -> None:
    """
    donot call this function too often, it may overwrite history log text with the same `tag` and `global_step`
    """
    env_config = env.get_current_env()
    tb_log_file = os.path.join(env_config.output.tensorboard_dir, tb_log_file)
    writer = SummaryWriter(tb_log_file)

    now = int(round(time.time() * 1000))
    tag = tag if tag else str(now)
    global_step = global_step if global_step >= 0 else now
    writer.add_text(tag=tag, text_string=text, global_step=global_step)
    writer.close()


def write_final_executor_log(tb_log_file: str = 'tensorboard_text.log',
                             tag: str = "", global_step: int = -1) -> None:
    env_config = env.get_current_env()
    exe_log_file = env_config.output.executor_log_file
    with open(exe_log_file) as f:
        # use the raw text format instead of markdown
        text = "```\n" + f.read() + "\n```"
        write_tensorboard_text(text, tb_log_file=tb_log_file, tag=tag, global_step=global_step)
