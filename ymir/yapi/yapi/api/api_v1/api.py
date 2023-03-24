from fastapi import APIRouter

from yapi.api.api_v1.endpoints import (
    datasets,
    models,
    predictions,
    projects,
    docker_images,
)

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(
    predictions.router, prefix="/predictions", tags=["predictions"]
)
api_router.include_router(
    docker_images.router, prefix="/docker_images", tags=["docker_images"]
)
