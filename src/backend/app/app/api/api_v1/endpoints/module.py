from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Module, ModuleCreate, ModuleOut, ModuleUpdate


router = APIRouter()

# basic CRUD operations for module

@router.get("/", response_model=list[ModuleOut])
def read_moduel(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve moduel.
    """
    statement = select(Module).offset(skip).limit(limit)
    return session.exec(statement).all()

@router.get("/{id}", response_model=ModuleOut)
def read_module(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get Module by ID.
    """
    module = session.get(Module, id)
    if not module:
        raise HTTPException(status_code=404, detail="module not found")
    return module

@router.post("/", response_model=ModuleOut)
def create_module(
    *, session: SessionDep, current_user: CurrentUser, module_in: ModuleCreate
) -> Any:
    """
    Create new module.
    """
    module = module.from_orm(module_in, update={"user_id": current_user.id})
    session.add(module)
    session.commit()
    session.refresh(module)
    return module

# @router.put("/{id}", response_model=RoomOut)
# def update_room(
#     *, session: SessionDep, current_user: CurrentUser, id: int, room_in: RoomUpdate
# ) -> Any:
#     """
#     Update a room.
#     """
#     room = session.get(Room, id)
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     if room.user_id != current_user.id:
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     room = room.copy(update=room_in.dict(exclude_unset=True))
#     session.add(room)
#     session.commit()
#     session.refresh(room)
#     return room

@router.delete("/{id}", response_model=Message)
def delete_module(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Delete a module.
    """
    module = session.get(module, id)
    if not module:
        raise HTTPException(status_code=404, detail="module not found")
    if module.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(module)
    session.commit()
    return Message(message="module deleted")

