from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, utils, rooms , publicuser, signup

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(publicuser.router, prefix="/publicuser", tags=["publicuser"])
