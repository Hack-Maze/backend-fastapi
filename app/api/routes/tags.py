from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Tag, TagCreate, TagOut, TagsOut, TagUpdate

router = APIRouter()


@router.get("/", response_model=TagsOut)
def read_tags(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Tags.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Tag)
        count = session.exec(count_statement).one()
        statement = select(Tag).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Tag)
            .where(Tag.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Tag)
            .where(Tag.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    tags = session.exec(statement).all()
    return TagsOut(data=tags, count=count)


@router.get("/{id}", response_model=TagOut)
def read_tag(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get tag by ID.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and (tag.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return tag


@router.post("/", response_model=TagOut)
def create_tag(
    *, session: SessionDep, current_user: CurrentUser, tag_in: TagCreate
) -> Any:
    """
    Create new tag.
    """
    tag = Tag.model_validate(tag_in, update={"owner_id": current_user.id})
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag





@router.put("/{id}", response_model=TagOut)
def update_tag(
    *, session: SessionDep, current_user: CurrentUser, id: int, tag_in: TagUpdate
) -> Any:
    """
    Update a tag.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and (tag.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = tag_in.model_dump(exclude_unset=True)
    tag.sqlmodel_update(update_dict)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{id}", response_model=Message)
def delete_tag(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a tag.
    """
    tag = session.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(tag)
    session.commit()
    return Message(message="Tag deleted successfully")
