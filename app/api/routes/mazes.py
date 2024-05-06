from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Mazes, MazesCreate, MazesOut, MazessOut, MazesUpdate

router = APIRouter()


@router.get("/", response_model=MazessOut)
def read_Mazess(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Mazess.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Mazes)
        count = session.exec(count_statement).one()
        statement = select(Mazes).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Mazes)
            .where(Mazes.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Mazes)
            .where(Mazes.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    Mazess = session.exec(statement).all()
    return MazessOut(data=Mazess, count=count)


@router.get("/{id}", response_model=MazesOut)
def read_Mazes(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get mazes by ID.
    """
    mazes = session.get(Mazes, id)
    if not mazes:
        raise HTTPException(status_code=404, detail="Mazes not found")
    if not current_user.is_superuser and (mazes.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return mazes


@router.post("/", response_model=MazesOut)
def create_Mazes(
    *, session: SessionDep, current_user: CurrentUser, Mazes_in: MazesCreate
) -> Any:
    """
    Create new mazes.
    """
    mazes = Mazes.model_validate(Mazes_in, update={"owner_id": current_user.id})
    session.add(mazes)
    session.commit()
    session.refresh(mazes)
    return mazes


@router.post("/{id}/upload/")
def upload_Mazes_file(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    file_name: UploadFile = File(...),
):
    # reference: https://fastapi.tiangolo.com/reference/uploadfile/
    mazes = session.get(Mazes, id)
    if not mazes:
        raise HTTPException(status_code=404, detail="Mazes not found")
    if not current_user.is_superuser and (mazes.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # create file on disk first and then save the file name in the database
    with open(f"files/{file_name.filename}", "wb") as file_object:
        file_object.write(file_name.file.read())
    mazes.file_name = file_name.filename
    session.add(mazes)
    session.commit()
    session.refresh(mazes)
    return mazes


@router.put("/{id}", response_model=MazesOut)
def update_Mazes(
    *, session: SessionDep, current_user: CurrentUser, id: int, Mazes_in: MazesUpdate
) -> Any:
    """
    Update a mazes.
    """
    mazes = session.get(Mazes, id)
    if not mazes:
        raise HTTPException(status_code=404, detail="Mazes not found")
    if not current_user.is_superuser and (mazes.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = Mazes_in.model_dump(exclude_unset=True)
    mazes.sqlmodel_update(update_dict)
    session.add(mazes)
    session.commit()
    session.refresh(mazes)
    return mazes


@router.delete("/{id}", response_model=Message)
def delete_Mazes(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a mazes.
    """
    mazes = session.get(Mazes, id)
    if not mazes:
        raise HTTPException(status_code=404, detail="Mazes not found")
    if mazes.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(mazes)
    session.commit()
    return Message(message="Mazes deleted successfully")
