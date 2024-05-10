from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Maze, MazesCreate, MazesOut, MazeOut ,  MazesUpdate

router = APIRouter()


@router.get("/", response_model=MazesOut)
def read_mazes(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Mazes.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Maze)
        count = session.exec(count_statement).one()
        statement = select(Maze).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Maze)
            .where(Maze.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Maze)
            .where(Maze.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    mazes = session.exec(statement).all()
    return MazesOut(data=mazes, count=count)


@router.get("/{id}", response_model=MazeOut)
def read_maze(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get maze by ID.
    """
    maze = session.get(Maze, id)
    if not maze:
        raise HTTPException(status_code=404, detail="Maze not found")
    if not current_user.is_superuser and (maze.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return maze


@router.post("/", response_model=MazeOut)
def create_maze(
    *, session: SessionDep, current_user: CurrentUser, Mazes_in: MazesCreate
) -> Any:
    """
    Create new maze.
    """
    maze = Maze.model_validate(Mazes_in, update={"owner_id": current_user.id})
    session.add(maze)
    session.commit()
    session.refresh(maze)
    return maze


# @router.post("/{id}/upload/")
# def upload_maze_file(
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: int,
#     file_name: UploadFile = File(...),
# ):
#     # reference: https://fastapi.tiangolo.com/reference/uploadfile/
#     maze = session.get(Maze, id)
#     if not maze:
#         raise HTTPException(status_code=404, detail="Maze not found")
#     if not current_user.is_superuser and (maze.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     # create file on disk first and then save the file name in the database
#     with open(f"files/{file_name.filename}", "wb") as file_object:
#         file_object.write(file_name.file.read())
#     maze.file_name = file_name.filename
#     session.add(maze)
#     session.commit()
#     session.refresh(maze)
#     return maze


@router.put("/{id}", response_model=MazeOut)
def update_maze(
    *, session: SessionDep, current_user: CurrentUser, id: int, Mazes_in: MazesUpdate
) -> Any:
    """
    Update a maze.
    """
    maze = session.get(Maze, id)
    if not maze:
        raise HTTPException(status_code=404, detail="Maze not found")
    if not current_user.is_superuser and (maze.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = Mazes_in.model_dump(exclude_unset=True)
    maze.sqlmodel_update(update_dict)
    session.add(maze)
    session.commit()
    session.refresh(maze)
    return maze


@router.delete("/{id}", response_model=Message)
def delete_maze(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a maze.
    """
    maze = session.get(Maze, id)
    if not maze:
        raise HTTPException(status_code=404, detail="Maze not found")
    if maze.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(maze)
    session.commit()
    return Message(message="Maze deleted successfully")
