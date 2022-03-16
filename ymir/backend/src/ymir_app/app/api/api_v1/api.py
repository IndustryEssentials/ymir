from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    datasets,
    graphs,
    images,
    inferences,
    info,
    keywords,
    login,
    models,
    roles,
    stats,
    tasks,
    upload,
    users,
    projects,
    iterations,
    dataset_groups,
    model_groups,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(iterations.router, prefix="/iterations", tags=["iterations"])
api_router.include_router(dataset_groups.router, prefix="/dataset_groups", tags=["dataset_groups"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(model_groups.router, prefix="/model_groups", tags=["model_groups"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(graphs.router, prefix="/graphs", tags=["graphs"])
api_router.include_router(images.router, prefix="/images", tags=["docker_images"])
api_router.include_router(inferences.router, prefix="/inferences", tags=["inference"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(info.router, prefix="/sys_info", tags=["sys"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
