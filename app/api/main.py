from fastapi import APIRouter

from app.api.routes import items, login, profiles, mazes, signup, users, utils , pages , question , badges , tags # noqa

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profile", tags=["profile"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(mazes.router, prefix="/mazes", tags=["mazes"])
api_router.include_router(pages.router, prefix="/pages", tags=["pages"])
api_router.include_router(question.router, prefix="/question", tags=["question"])
api_router.include_router(badges.router, prefix="/badges", tags=["badges"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
