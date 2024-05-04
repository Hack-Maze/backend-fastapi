from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Room, RoomCreate, RoomOut, RoomsOut, RoomUpdate

router = APIRouter()


@router.get("/", response_model=RoomsOut)
def read_rooms(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve rooms.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Room)
        count = session.exec(count_statement).one()
        statement = select(Room).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Room)
            .where(Room.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Room)
            .where(Room.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    rooms = session.exec(statement).all()
    return RoomsOut(data=rooms, count=count)


@router.get("/{id}", response_model=RoomOut)
def read_room(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get room by ID.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return room


@router.post("/", response_model=RoomOut)
def create_room(
    *, session: SessionDep, current_user: CurrentUser, room_in: RoomCreate
) -> Any:
    """
    Create new room.
    """
    room = Room.model_validate(room_in, update={"owner_id": current_user.id})
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.post("/{id}/upload/")
def upload_room_file(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    file_name: UploadFile = File(...),
):
    # reference: https://fastapi.tiangolo.com/reference/uploadfile/
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # create file on disk first and then save the file name in the database
    with open(f"files/{file_name.filename}", "wb") as file_object:
        file_object.write(file_name.file.read())
    room.file_name = file_name.filename
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.put("/{id}", response_model=RoomOut)
def update_room(
    *, session: SessionDep, current_user: CurrentUser, id: int, room_in: RoomUpdate
) -> Any:
    """
    Update a room.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = room_in.model_dump(exclude_unset=True)
    room.sqlmodel_update(update_dict)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.delete("/{id}", response_model=Message)
def delete_room(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
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
    return Message(message="Room deleted successfully")
