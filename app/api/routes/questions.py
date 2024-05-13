from typing import Any
from fastapi import APIRouter, Depends
from sqlmodel import func, select
from app import crud
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Question,
    QuestionCreate,
    QuestionOut,
    QuestionsOut,
    QuestionUpdate,
)

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=QuestionsOut,
)
def read_questions(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve questions.
    """

    count_statement = select(func.count()).select_from(Question)
    count = session.exec(count_statement).one()

    statement = select(Question).offset(skip).limit(limit)
    questions = session.exec(statement).all()

    return QuestionsOut(data=questions, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=QuestionOut,
)
def create_question(*, session: SessionDep, question_in: QuestionCreate) -> Any:
    """
    Create new question.
    """
    question = crud.get_question_by_name(session=session, name=question_in.name)
    if question:
        raise HTTPException(
            status_code=400,
            detail="The question with this name already exists in the system.",
        )
    question = crud.create_question(session=session, question_create=question_in)
    return question


@router.get("/{question_id}", response_model=QuestionOut)
def read_question_by_id(
    question_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific question by id.
    """
    question = session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.patch(
    "/{question_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=QuestionOut,
)
def update_question(
    *,
    session: SessionDep,
    question_id: int,
    question_in: QuestionUpdate,
) -> Any:
    """
    Update a question.
    """
    db_question = session.get(Question, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question_in.name:
        existing_badge = crud.get_badge_by_name(session=session, name=question_in.name)
        if existing_badge and existing_badge.id != question_id:
            raise HTTPException(
                status_code=409, detail="Badge with this name already exists"
            )

    db_badge = crud.update_badge(
        session=session,
        db_badge=db_badge,
        question_in=question_in,
    )
    return db_badge


@router.delete("/{question_id}")
def delete_question(
    session: SessionDep, current_user: CurrentUser, question_id: int
) -> Message:
    """
    Delete a question.
    """
    question = session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    elif question != current_user and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )

    session.delete(question)
    session.commit()
    return Message(message="Question deleted successfully")
