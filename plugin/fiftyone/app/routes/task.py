from fastapi import APIRouter
from loguru import logger

router = APIRouter()


@router.post("/")
async def create_task(
    task_in: str,
):
    logger.info(f"Creating task: {task_in}")

    return {"task": task_in}
