from fastapi import APIRouter

from auth.api.api_v1.endpoints import login, roles, users

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
