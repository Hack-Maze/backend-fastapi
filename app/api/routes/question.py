from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Question, QuestionCreate, QuestionOut, QuestionsOut, QuestionUpdate

router = APIRouter()


@router.get("/", response_model=QuestionsOut)
def read_questions(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve questions.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Question)
        count = session.exec(count_statement).one()
        statement = select(Question).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Question)
            .where(Question.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Question)
            .where(Question.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    questions = session.exec(statement).all()
    return QuestionsOut(data=questions, count=count)


@router.get("/{id}", response_model=QuestionOut)
def read_question(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get Question by ID.
    """
    question = session.get(Question, id)
    if not question:
        raise HTTPException(status_code=404, detail="Questions not found")
    if not current_user.is_superuser and (question.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return question


@router.post("/", response_model=QuestionOut)
def create_question(
    *, session: SessionDep, current_user: CurrentUser, question_in: QuestionCreate
) -> Any:
    """
    Create new question.
    """
    question = Question.model_validate(question_in, update={"owner_id": current_user.id})
    session.add(question)
    session.commit()
    session.refresh(question)
    return question





@router.put("/{id}", response_model=QuestionOut)
def update_question(
    *, session: SessionDep, current_user: CurrentUser, id: int, question_in: QuestionUpdate
) -> Any:
    """
    Update a question.
    """
    question = session.get(Question, id)
    if not question:
        raise HTTPException(status_code=404, detail="question not found")
    if not current_user.is_superuser and (question.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = question_in.model_dump(exclude_unset=True)
    question.sqlmodel_update(update_dict)
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@router.delete("/{id}", response_model=Message)
def delete_Question(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a question.
    """
    question = session.get(Question, id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(question)
    session.commit()
    return Message(message="Question deleted successfully")
