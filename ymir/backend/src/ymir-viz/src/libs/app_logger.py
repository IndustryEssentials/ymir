import logging

LOGGER_NAME = "Ymir-viz"


def init_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(processName)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s "
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


logger = init_logger()
