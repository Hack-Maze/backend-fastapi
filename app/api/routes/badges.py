from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Badges, BadgesCreate, BadgesOut, BadgessOut, BadgesUpdate

router = APIRouter()


@router.get("/", response_model=BadgessOut)
def read_all_badges(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Badges.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Badges)
        count = session.exec(count_statement).one()
        statement = select(Badges).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Badges)
            .where(Badges.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Badges)
            .where(Badges.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    badgess = session.exec(statement).all()
    return BadgessOut(data=badgess, count=count)


@router.get("/{id}", response_model=BadgesOut)
def read_user_badges(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get badges by ID.
    """
    badges = session.get(Badges, id)
    if not badges:
        raise HTTPException(status_code=404, detail="Badge not found")
    if not current_user.is_superuser and (badges.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return badges


@router.post("/", response_model=BadgesOut)
def create_badge(
    *, session: SessionDep, current_user: CurrentUser, badges_in: BadgesCreate
) -> Any:
    """
    Create a new badge.
    """
    badge = Badges.model_validate(badges_in, update={"owner_id": current_user.id})
    session.add(badge)
    session.commit()
    session.refresh(badge)
    return badge





@router.put("/{id}", response_model=BadgesOut)
def update_badge(
    *, session: SessionDep, current_user: CurrentUser, id: int, badges_in: BadgesUpdate
) -> Any:
    """
    Update a badge.
    """
    badge = session.get(Badges, id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    if not current_user.is_superuser and (badge.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = badges_in.model_dump(exclude_unset=True)
    badge.sqlmodel_update(update_dict)
    session.add(badge)
    session.commit()
    session.refresh(badge)
    return badge


@router.delete("/{id}", response_model=Message)
def delete_badge(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a badge.
    """
    badge = session.get(Badges, id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    if badge.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(badge)
    session.commit()
    return Message(message="Badge deleted successfully")
