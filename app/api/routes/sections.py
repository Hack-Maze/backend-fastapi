from fastapi import APIRouter
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
)
from app.models import (
    Message,
    Section,
    SectionCreate,
    SectionOut,
    SectionsOut,
    SectionUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=SectionsOut,
)
def read_sections(session: SessionDep, skip: int = 0, limit: int = 100):
    """
    Retrieve sections.
    """

    count_statement = select(func.count()).select_from(Section)
    count = session.exec(count_statement).one()

    statement = select(Section).offset(skip).limit(limit)
    sections = session.exec(statement).all()    

    return SectionsOut(data=sections, count=count)


@router.post("/", response_model=SectionOut)
def create_section(*, session: SessionDep, section_in: SectionCreate):
    """
    Create new section.
    """

    section = crud.create_section(session=session, section_in=section_in)
    return section


@router.get("/{section_id}", response_model=SectionOut)
def read_section_by_id(section_id: int, session: SessionDep, current_user: CurrentUser):
    """
    Get a specific section by id.
    """
    section = crud.get_section_by_id(session=session, section_id=section_id)
    return section


@router.patch(
    "/{section_id}",
    response_model=SectionOut,
)
def update_section(
    *,
    session: SessionDep,
    section_id: int,
    section_in: SectionUpdate,
):
    """
    Update a section.
    """
    section = crud.update_section(
        session=session, section_id=section_id, section_in=section_in
    )
    return section


@router.delete("/{section_id}")
def delete_section(
    session: SessionDep, current_user: CurrentUser, section_id: int
) -> Message:
    """
    Delete a section.
    """
    section = crud.delete_section(session=session, section_id=section_id)  # noqa
    return {"message": f"Section {section_id} deleted"}
