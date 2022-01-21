from typing import Dict

import sentry_sdk
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Depends
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.exceptions import HTTPException

from monitor.config import settings
from monitor.libs.container import Container
from monitor.libs.services import TaskService
from monitor.schemas.task import TaskParameter
from monitor.utils.errors import http_error_handler


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.0.1",
        contact={"name": "ymir"},
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
        },
    )
    sentry_sdk.init(dsn=settings.MONITOR_SENTRY_DSN)
    application.add_middleware(SentryAsgiMiddleware)
    application.add_exception_handler(HTTPException, http_error_handler)

    return application


app = create_app()


@app.post("/api/v1/tasks")
@inject
async def register_task(parameters: TaskParameter, service: TaskService = Depends(Provide[Container.service])) -> Dict:
    service.register_task(parameters)
    return {"result": "Success"}


@app.get("/api/v1/running_tasks")
@inject
async def get_running_task(service: TaskService = Depends(Provide[Container.service])) -> Dict:
    result = service.get_running_task()
    return {"result": result}


@app.get("/api/v1/finished_tasks")
@inject
async def get_finished_task(service: TaskService = Depends(Provide[Container.service])) -> Dict:
    result = service.get_finished_task()
    return {"result": result}


container = Container()
container.wire(modules=[__name__])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080)
