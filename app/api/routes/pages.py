from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Pages, PagesCreate, PagesOut, PagessOut, PagesUpdate

router = APIRouter()


@router.get("/", response_model=PagessOut)
def read_pages(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve pages.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Pages)
        count = session.exec(count_statement).one()
        statement = select(Pages).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Pages)
            .where(Pages.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Pages)
            .where(Pages.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    pagess = session.exec(statement).all()
    return PagessOut(data=pagess, count=count)


@router.get("/{id}", response_model=PagesOut)
def read_page(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get Page by ID.
    """
    pages = session.get(Pages, id)
    if not pages:
        raise HTTPException(status_code=404, detail="Page not found")
    if not current_user.is_superuser and (pages.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return pages


@router.post("/", response_model=PagesOut)
def create_page(
    *, session: SessionDep, current_user: CurrentUser, pages_in: PagesCreate
) -> Any:
    """
    Create a new Page.
    """
    pages = Pages.model_validate(pages_in, update={"owner_id": current_user.id})
    session.add(pages)
    session.commit()
    session.refresh(pages)
    return pages

@router.put("/{id}", response_model=PagesOut)
def update_page(
    *, session: SessionDep, current_user: CurrentUser, id: int, pages_in: PagesUpdate
) -> Any:
    """
    Update a page.
    """
    pages = session.get(Pages, id)
    if not pages:
        raise HTTPException(status_code=404, detail="Page not found")
    if not current_user.is_superuser and (pages.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = pages_in.model_dump(exclude_unset=True)
    pages_in.sqlmodel_update(update_dict)
    session.add(pages)
    session.commit()
    session.refresh(pages_in)
    return pages_in


@router.delete("/{id}", response_model=Message)
def delete_page(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a page.
    """
  # Correct indentation
    pages = session.get(Pages, id)
    if not pages:
        raise HTTPException(status_code=404, detail="Page not found")
    if pages.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(pages)
    session.commit()
    return Message(message="Page deleted successfully")
