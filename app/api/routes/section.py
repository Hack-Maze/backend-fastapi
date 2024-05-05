from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Section, SectionCreate, SectionOut, SectionsOut, SectionUpdate

router = APIRouter()


@router.get("/", response_model=SectionsOut)
def read_sections(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve sections.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Section)
        count = session.exec(count_statement).one()
        statement = select(Section).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Section)
            .where(Section.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Section)
            .where(Section.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    sections = session.exec(statement).all()
    return SectionsOut(data=sections, count=count)


@router.get("/{id}", response_model=SectionOut)
def read_sections(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get Section by ID.
    """
    section = session.get(Section, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return room


@router.post("/", response_model=SectionOut)
def create_section(
    *, session: SessionDep, current_user: CurrentUser, section_in: SectionCreate
) -> Any:
    """
    Create new Section.
    """
    section = Section.model_validate(section_in, update={"owner_id": current_user.id})
    session.add(section)
    session.commit()
    session.refresh(section)
    return section

@router.put("/{id}", response_model=SectionOut)
def update_room(
    *, session: SessionDep, current_user: CurrentUser, id: int, section_in: SectionUpdate
) -> Any:
    """
    Update a section.
    """
    section = session.get(Section, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    if not current_user.is_superuser and (section.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = section_in.model_dump(exclude_unset=True)
    section_in.sqlmodel_update(update_dict)
    session.add(section)
    session.commit()
    session.refresh(section_in)
    return section_in


@router.delete("/{id}", response_model=Message)
def delete_section(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a section.
    """
  # Correct indentation
    section = session.get(Section, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    if section.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(section)
    session.commit()
    return Message(message="Section deleted successfully")
