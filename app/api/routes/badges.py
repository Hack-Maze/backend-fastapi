from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select
from app import crud
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.utils import generate_new_account_email, send_email

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Badge,
    BadgeCreate,
    BadgeOut,
    BadgesOut,
    BadgeUpdate,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserCreateOpen,
    UserOut,
    UsersOut,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter()


@router.get(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=BadgesOut
)
def read_badges(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve badges.
    """

    count_statement = select(func.count()).select_from(Badge)
    count = session.exec(count_statement).one()

    statement = select(Badge).offset(skip).limit(limit)
    badges = session.exec(statement).all()

    return BadgesOut(data=badges, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=BadgeOut
)
def create_badge(*, session: SessionDep, badge_in: BadgeCreate) -> Any:
    """
    Create new badge.
    """
    badge = crud.get_badge_by_name(session=session, name=badge_in.name)
    if badge:
        raise HTTPException(
            status_code=400,
            detail="The badge with this name already exists in the system.",
        )

    badge = crud.create_badge(session=session, badge_create=badge_in)
    return badge


@router.patch("/{badge_id}", response_model=BadgeOut)
def update_badge(
    *,
    session: SessionDep,
    badge_id: int,
    badge_in: BadgeUpdate,
) -> Any:
    """
    Update a badge.
    """

    db_badge = session.get(Badge, badge_id)
    if not db_badge:
        raise HTTPException(
            status_code=404,
            detail="The badge with this id does not exist in the system",
        )
    if badge_in.name:
        existing_badge = crud.get_badge_by_name(session=session, name=badge_in.name)
        if existing_badge and existing_badge.id != badge_id:
            raise HTTPException(
                status_code=409, detail="Badge with this name already exists"
            )

    db_badge = crud.update_badge(session=session, db_badge=db_badge, badge_in=badge_in)
    return db_badge


@router.delete("/{badge_id}")
def delete_badge(
    session: SessionDep, current_user: CurrentUser, badge_id: int
) -> Message:
    """
    Delete a badge.
    """
    badge = session.get(Badge, badge_id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    elif badge != current_user and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )

    session.delete(badge)
    session.commit()
    return Message(message="Badge deleted successfully")
