import time

from tensorboardX import SummaryWriter

from ymir_exc import env

TASK_STATE_RUNNING = 2


def write_monitor_logger(percent: float) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{TASK_STATE_RUNNING}\n")


def write_tensorboard_text(text: str, tag: str = None) -> None:
    """
    donot call this function too often, tensorboard may
    overwrite history log text with the same `tag` and `global_step`
    """
    env_config = env.get_current_env()
    tag = tag if tag else "default"

    # show the raw text format instead of markdown
    text = f"```\n {text} \n```"
    with SummaryWriter(env_config.output.tensorboard_dir) as f:
        f.add_text(tag=tag, text_string=text, global_step=round(time.time() * 1000))


def write_final_executor_log(tag: str = None) -> None:
    env_config = env.get_current_env()
    exe_log_file = env_config.output.executor_log_file
    with open(exe_log_file) as f:
        write_tensorboard_text(f.read(), tag=tag)
