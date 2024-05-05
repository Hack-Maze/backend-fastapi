from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Collection, CollectionCreate, CollectionOut, CollectionsOut, CollectionUpdate

router = APIRouter()


@router.get("/", response_model=CollectionsOut)
def read_collections(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Collections.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Collection)
        count = session.exec(count_statement).one()
        statement = select(Collection).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Collection)
            .where(Collection.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Collection)
            .where(Collection.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    collections = session.exec(statement).all()
    return CollectionsOut(data=collections, count=count)


@router.get("/{id}", response_model=CollectionOut)
def read_collection(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get collection by ID.
    """
    collection = session.get(Collection, id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if not current_user.is_superuser and (collection.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return collection


@router.post("/", response_model=CollectionOut)
def create_collection(
    *, session: SessionDep, current_user: CurrentUser, Collection_in: CollectionCreate
) -> Any:
    """
    Create new collection.
    """
    collection = Collection.model_validate(collection_in, update={"owner_id": current_user.id})
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection





@router.put("/{id}", response_model=CollectionOut)
def update_room(
    *, session: SessionDep, current_user: CurrentUser, id: int, room_in: CollectionUpdate
) -> Any:
    """
    Update a Collection.
    """
    collection = session.get(Collection, id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if not current_user.is_superuser and (collection.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = collection_in.model_dump(exclude_unset=True)
    collection.sqlmodel_update(update_dict)
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


@router.delete("/{id}", response_model=Message)
def delete_collection(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a collection.
    """
    collection = session.get(Collection, id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(collection)
    session.commit()
    return Message(message="Collection deleted successfully")
