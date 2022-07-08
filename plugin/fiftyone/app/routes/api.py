from fastapi import APIRouter

from app.routes import task

router = APIRouter()

router.include_router(task.router, tags=["task"], prefix="/task")
