from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Badges, BadgesCreate, BadgesOut, BadgessOut, BadgesUpdate

router = APIRouter()


@router.get("/", response_model=BadgessOut)
def read_Badges(
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
def read_badges(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get badges by ID.
    """
    badges = session.get(Badges, id)
    if not badges:
        raise HTTPException(status_code=404, detail="Badges not found")
    if not current_user.is_superuser and (badges.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return badges


@router.post("/", response_model=BadgesOut)
def create_badges(
    *, session: SessionDep, current_user: CurrentUser, badges_in: BadgesCreate
) -> Any:
    """
    Create new badges.
    """
    badges = Badges.model_validate(badges_in, update={"owner_id": current_user.id})
    session.add(badges)
    session.commit()
    session.refresh(badges)
    return badges





@router.put("/{id}", response_model=BadgesOut)
def update_badges(
    *, session: SessionDep, current_user: CurrentUser, id: int, badges_in: BadgesUpdate
) -> Any:
    """
    Update a badges.
    """
    badges = session.get(Badges, id)
    if not badges:
        raise HTTPException(status_code=404, detail="Badges not found")
    if not current_user.is_superuser and (badges.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = badges_in.model_dump(exclude_unset=True)
    badges.sqlmodel_update(update_dict)
    session.add(badges)
    session.commit()
    session.refresh(badges)
    return badges


@router.delete("/{id}", response_model=Message)
def delete_badges(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a badges.
    """
    badges = session.get(Badges, id)
    if not badges:
        raise HTTPException(status_code=404, detail="Badges not found")
    if badges.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(badges)
    session.commit()
    return Message(message="Badges deleted successfully")
