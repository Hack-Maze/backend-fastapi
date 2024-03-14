from typing import Any, List # noqa

from app import crud
from app.api.deps import SessionDep
from app.models import UserOut, UserCreate, UserCreateOpen
from fastapi import APIRouter, HTTPException
from app.core.config import settings # noqa

router = APIRouter()


@router.post("/signup", response_model=UserOut)
def signup(session: SessionDep, user_in: UserCreateOpen) -> Any:
    """
    Create new user without the need to be logged in.
    """
    # if not settings.USERS_OPEN_REGISTRATION:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Open user registration is forbidden on this server",
    #     )
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_create = UserCreate.from_orm(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user
