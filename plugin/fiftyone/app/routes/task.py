from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from app.models.schemas import Task, TaskCreateResponse
from app.service.task_service import task_create

router = APIRouter()


@router.post("/", response_model=TaskCreateResponse)
async def create_task(task: Task):
    logger.info(f"task: {task}")
    res = await task_create(task)
    return JSONResponse(content=res)
