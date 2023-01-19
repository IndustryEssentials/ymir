import asyncio
import logging

import sentry_sdk
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi_socketio import SocketManager

from fastapi_health import health
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.api.api_v1.api import api_router
from app.api.errors import errors
from app.config import settings
from app.libs.redis_stream import RedisStream
from app.libs.tasks import batch_update_task_status

app = FastAPI(
    docs_url=None,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)
app.add_api_route("/health", health([]))

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN)  # type: ignore
    app.add_middleware(SentryAsgiMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    allow_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    socket_manager = SocketManager(app=app, cors_allowed_origins=allow_origins)
else:
    socket_manager = SocketManager(app=app)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


redis_stream = RedisStream(settings.BACKEND_REDIS_URL)


@app.on_event("startup")
async def startup() -> None:
    if settings.REDIS_TESTING:
        return
    asyncio.create_task(redis_stream.consume(batch_update_task_status))


@app.on_event("shutdown")
async def shutdown() -> None:
    if settings.REDIS_TESTING:
        return
    asyncio.create_task(redis_stream.disconnect())


app.include_router(api_router, prefix=settings.API_V1_STR)

app.add_exception_handler(HTTPException, errors.http_error_handler)
app.add_exception_handler(RequestValidationError, errors.http422_error_handler)

logging.basicConfig(level=logging.INFO)
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
logging.getLogger("multipart").setLevel(logging.WARNING)


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for filter_key in ["/health", "/metrics"]:
            if record.getMessage().find(filter_key) != -1:
                return False
        return True


uvicorn_access_logger.addFilter(EndpointFilter())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
