from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Room, RoomCreate, RoomOut, RoomUpdate


router = APIRouter()

# basic CRUD operations for rooms

@router.get("/", response_model=list[RoomOut])
def read_rooms(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve rooms.
    """
    statement = select(Room).offset(skip).limit(limit)
    return session.exec(statement).all()

@router.get("/{id}", response_model=RoomOut)
def read_room(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get room by ID.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/", response_model=RoomOut)
def create_room(
    *, session: SessionDep, current_user: CurrentUser, room_in: RoomCreate
) -> Any:
    """
    Create new room.
    """
    room = Room.from_orm(room_in, update={"user_id": current_user.id})
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

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
def delete_room(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Delete a room.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(room)
    session.commit()
    return Message(message="Room deleted")

