from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Module, ModuleCreate, ModuleOut, ModuelsOut, ModuleUpdate

router = APIRouter()


@router.get("/", response_model=ModuelsOut)
def read_modules(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve modules.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Module)
        count = session.exec(count_statement).one()
        statement = select(Module).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Module)
            .where(Module.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Module)
            .where(Module.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    modules = session.exec(statement).all()
    return ModuelsOut(data=modules, count=count)


@router.get("/{id}", response_model=ModuleOut)
def read_module(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get module by ID.
    """
    module = session.get(Module, id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if not current_user.is_superuser and (module.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return module


@router.post("/", response_model=ModuleOut)
def create_module(
    *, session: SessionDep, current_user: CurrentUser, module_in: ModuleCreate
) -> Any:
    """
    Create new module.
    """
    module = Module.model_validate(module_in, update={"owner_id": current_user.id})
    session.add(module)
    session.commit()
    session.refresh(module)
    return module




@router.put("/{id}", response_model=ModuleOut)
def update_module(
    *, session: SessionDep, current_user: CurrentUser, id: int, module_in: ModuleUpdate
) -> Any:
    """
    Update a module.
    """
    module = session.get(Module, id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if not current_user.is_superuser and (module.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = module_in.model_dump(exclude_unset=True)
    module.sqlmodel_update(update_dict)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


@router.delete("/{id}", response_model=Message)
def delete_module(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a module.
    """
    module = session.get(Module, id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(module)
    session.commit()
    return Message(message="Module deleted successfully")
