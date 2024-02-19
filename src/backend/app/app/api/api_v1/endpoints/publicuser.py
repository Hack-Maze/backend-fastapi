from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, PublicUser, PublicUserCreate, PublicUserOut, PublicUserUpdate


router = APIRouter()

# basic CRUD operations for publicuser

@router.get("/", response_model=list[PublicUserOut])
def read_publicuser(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve User.
    """
    statement = select(PublicUser).offset(skip).limit(limit)
    return session.exec(statement).all()

@router.get("/{id}", response_model=PublicUserOut)
def read_publicuser(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get publicuser by ID.
    """
    publicuser = session.get(PublicUser, id)
    if not publicuser:
        raise HTTPException(status_code=404, detail="User not found")
    return publicuser

@router.post("/", response_model=PublicUserOut)
def create_publicuser(
    *, session: SessionDep, current_user: CurrentUser, publicuser_in: PublicUserCreate
) -> Any:
    """
    Create new publicuser.
    """
    publicuser = PublicUser.from_orm(publicuser_in, update={"user_id": current_user.id})
    session.add(publicuser)
    session.commit()
    session.refresh(publicuser)
    return publicuser

@router.delete("/{id}", response_model=Message)
def delete_publicuser(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Delete a publicuser.
    """
    publicuser = session.get(PublicUser, id)
    if not publicuser:
        raise HTTPException(status_code=404, detail="publicuser not found")
    if publicuser.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(publicuser)
    session.commit()
    return Message(message="publicuser deleted")