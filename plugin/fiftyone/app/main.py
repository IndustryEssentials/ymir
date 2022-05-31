import uvicorn  # type: ignore
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import BaseResponseBody
from app.routes.api import router as api_router
from conf.configs import conf
from conf.logger import init_logging


def get_application() -> FastAPI:
    init_logging()
    _app = FastAPI()

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        res = BaseResponseBody()
        res.code = 1010
        res.error = str(exc)
        return JSONResponse(res.dict, status_code=200)

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, debug=True)
