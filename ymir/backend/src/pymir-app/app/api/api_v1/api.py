from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    datasets,
    graphs,
    inferences,
    keywords,
    login,
    models,
    roles,
    runtimes,
    stats,
    tasks,
    upload,
    users,
    workspaces,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(graphs.router, prefix="/graphs", tags=["graphs"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(runtimes.router, prefix="/runtimes", tags=["runtimes"])
api_router.include_router(inferences.router, prefix="/inferences", tags=["inference"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
