import time

from tensorboardX import SummaryWriter

from ymir_exc import env

TASK_STATE_RUNNING = 2


def write_monitor_logger(percent: float) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{TASK_STATE_RUNNING}\n")


class YmirTensorboardLog:
    def __init__(self) -> None:
        env_config = env.get_current_env()
        self.writer = SummaryWriter(env_config.output.tensorboard_dir)

    def __del__(self) -> None:
        self.writer.close()

    def write_tensorboard_text(self, text: str, tag: str = "") -> None:
        """
        donot call this function too often, tensorboard may
        overwrite history log text with the same `tag` and `global_step`
        """
        now = int(round(time.time() * 1000))
        tag = tag if tag else str(now)
        self.writer.add_text(tag=tag, text_string=text, global_step=now)

    def write_final_executor_log(self,
                                 tag: str = "") -> None:
        env_config = env.get_current_env()
        exe_log_file = env_config.output.executor_log_file
        with open(exe_log_file) as f:
            # use the raw text format instead of markdown
            text = "```\n" + f.read() + "\n```"
            self.write_tensorboard_text(text, tag=tag)
