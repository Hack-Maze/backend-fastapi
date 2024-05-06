from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Profile, ProfileCreate, ProfileOut, UserOut
from app import crud

router = APIRouter()


@router.get("/", response_model=list[ProfileOut])
def read_Profile(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    List all Profiles.
    """
    statement = select(Profile).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.get("/{profile_id}", response_model=ProfileOut)
def read_Profile_by_id(session: SessionDep, profile_id: UUID) -> Any:
    """
    Get Profile by ID.
    """
    if profile := session.get(Profile, profile_id):
        return profile
    raise HTTPException(status_code=404, detail="User Profile not found")


@router.post("/", response_model=ProfileOut)
def create_or_update_Profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    profile_in: ProfileCreate,
) -> Any:
    """
    Update OR Create a Profile.
    """
    profile = crud.get_profile_by_user_id(
        session=session,
        user_id=current_user.id,
    )
    if not profile:
        return crud.create_profile(
            session=session, profile_create=profile_in, user_id=current_user.id
        )

    if profile.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = profile_in.model_dump(exclude_unset=True)
    profile.sqlmodel_update(update_dict)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.delete("/{profile_id}", response_model=Message)
def delete_Profile(
    session: SessionDep, current_user: CurrentUser, profile_id: UUID
) -> Any:
    """
    Delete a Profile.
    """
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(profile)
    session.commit()
    return Message(message="Profile deleted successfully")
