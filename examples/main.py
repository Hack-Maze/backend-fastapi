import os

import redis.asyncio as redis
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from tortoise.contrib.fastapi import register_tortoise

from examples import settings
from examples.constants import BASE_DIR
from examples.models import Admin
from examples.providers import LoginProvider
from fastapi_admin.app import app as admin_app
from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
    unauthorized_error_exception,
)

fake_db = {"yusuf": {"password": "ff"}}

SECRET = "eb8e081b666a50fd58763f2644abafe1e1a6bd1d4054f080"
manager = LoginManager(SECRET, token_url="/auth/token")

DB = {"users": {"yusuf": {"name": "yusuf", "password": "ff"}}}


def query_user(user_id: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    return DB["users"].get(user_id)


def create_app():
    app = FastAPI()

    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "static")),
        name="static",
    )

    @manager.user_loader()
    def load_user(email: str):  # could also be an asynchronous function
        user = fake_db.get(email)
        return user

    from fastapi import Depends
    from fastapi.security import OAuth2PasswordRequestForm
    from fastapi_login.exceptions import InvalidCredentialsException

    # the python-multipart package is required to use the OAuth2PasswordRequestForm
    @app.post("/auth/token")
    def login(data: OAuth2PasswordRequestForm = Depends()):
        email = data.username
        password = data.password

        user = load_user(email)  # we are using the same function to retrieve the user
        if not user:
            raise InvalidCredentialsException  # you can also use your own HTTPException
        elif password != user["password"]:
            raise InvalidCredentialsException

        access_token = manager.create_access_token(data=dict(sub=email))
        return {"access_token": access_token, "token_type": "bearer"}

    @app.post("/login")
    def login(data: OAuth2PasswordRequestForm = Depends()):
        email = data.username
        password = data.password

        user = query_user(email)
        if not user:
            # you can return any response or error of your choice
            raise InvalidCredentialsException
        elif password != user["password"]:
            raise InvalidCredentialsException

        return {"status": "Success"}

    @app.get("/protected")
    def protected_route(user=Depends(manager)):
        return {"user": user}

    @app.get("/users/me")
    def read_users_me(current_user=Depends(manager)):
        return current_user

    @app.get("/")
    async def index():
        return RedirectResponse(url="/admin")

    admin_app.add_exception_handler(
        HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception
    )
    admin_app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
    admin_app.add_exception_handler(HTTP_403_FORBIDDEN, forbidden_error_exception)
    admin_app.add_exception_handler(HTTP_401_UNAUTHORIZED, unauthorized_error_exception)

    @app.on_event("startup")
    async def startup():
        r = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf8",
        )
        await admin_app.configure(
            logo_url="https://preview.tabler.io/static/logo-white.svg",
            template_folders=[os.path.join(BASE_DIR, "templates")],
            favicon_url="https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
            providers=[
                LoginProvider(
                    login_logo_url="https://preview.tabler.io/static/logo.svg",
                    admin_model=Admin,
                )
            ],
            redis=r,
        )

    app.mount("/admin", admin_app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    register_tortoise(
        app,
        config={
            "connections": {"default": settings.DATABASE_URL},
            "apps": {
                "models": {
                    "models": ["examples.models"],
                    "default_connection": "default",
                }
            },
        },
        generate_schemas=True,
    )
    return app


app_ = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app_", reload=True)
