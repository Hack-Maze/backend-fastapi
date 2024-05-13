from fastapi import APIRouter

from app.api.routes import sections, login, profiles, rooms, signup, users, utils 

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profile", tags=["profile"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(sections.router, tags=["sections"])