from fastapi import APIRouter

from app.api.routes import items, login, profiles, rooms, signup, users, utils , section , question , collection , module , badges  # noqa

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profile", tags=["profile"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(section.router, prefix="/section", tags=["section"])
api_router.include_router(question.router, prefix="/question", tags=["question"])
api_router.include_router(collection.router, prefix="/collection", tags=["collection"])
api_router.include_router(module.router, prefix="/module", tags=["module"])
api_router.include_router(badges.router, prefix="/badges", tags=["badges"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
