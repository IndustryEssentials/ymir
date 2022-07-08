from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from app.models.schemas import Task, TaskCreateResponse, TaskQueryResponse, TaskDeleteResponse
from app.service.task_service import task_create, task_query, task_delete

router = APIRouter()


@router.post("/", response_model=TaskCreateResponse)
async def create_task(task: Task) -> JSONResponse:
    logger.info(f"task: {task}")
    res = await task_create(task)
    return JSONResponse(content=res)


@router.get("/{tid}", response_model=TaskQueryResponse)
async def query_task(tid: str) -> JSONResponse:
    logger.info(f"tid: {tid}")
    res = await task_query(tid)
    return JSONResponse(content=res)


@router.delete("/{tid}", response_model=TaskDeleteResponse)
async def delete_task(tid: str) -> JSONResponse:
    logger.info(f"tid: {tid}")
    res = await task_delete(tid)
    return JSONResponse(content=res)
