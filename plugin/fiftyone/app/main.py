import uvicorn
from fastapi import FastAPI, requests
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import ErrorResponse
from app.routes.api import router as api_router
from app.worker import create_celery
from conf.configs import conf
from conf.logger import init_logging
from utils.errors import FiftyOneResponseCode


def get_application() -> FastAPI:
    init_logging()
    _app: FastAPI = FastAPI()
    _app.celery_app = create_celery()  # type: ignore

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: requests.Request, exc: RequestValidationError
    ) -> JSONResponse:
        res = ErrorResponse()
        res.code, res.error = (
            FiftyOneResponseCode.REQUEST_VALIDATION_ERROR,
            exc.__str__(),
        )
        return JSONResponse(res.dict(), status_code=200)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=conf.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(api_router)
    _app.router.redirect_slashes = False
    return _app


app = get_application()
celery = app.celery_app  # type: ignore

if __name__ == "__main__":
    # in docker start by >>> uvicorn --host=0.0.0.0 --port={FIFTYONE_PORT} app.main:app
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
