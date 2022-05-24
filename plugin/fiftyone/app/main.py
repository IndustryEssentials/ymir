import logging
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from conf.configs import conf
from conf.log import LogConfig

logger = logging.getLogger("fiftyOne_app")


def get_application() -> FastAPI:
    dictConfig(LogConfig().dict())

    _app = FastAPI()

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=conf.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("FiftyOne app created")

    return _app


app = get_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8888)
