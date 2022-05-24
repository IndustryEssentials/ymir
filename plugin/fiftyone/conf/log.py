from pydantic import BaseModel
import sys


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "fiftyOne_app"
    LOG_FORMAT: str = "%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y%m%d-%H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "fiftyOne_app": {"handlers": ["default"], "level": LOG_LEVEL},
    }
