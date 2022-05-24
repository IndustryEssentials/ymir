from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


@router.post("/")
async def create_task(
    task_in: Body,
):
    return {}
