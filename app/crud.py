from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    Profile,
    ProfileCreate,
    User,
    UserCreate,
    UserUpdate,
    Section,
    SectionCreate,
    SectionUpdate,
    Badge,
    BadgeCreate,
    Question,
    QuestionCreate,
    QuestionUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    create_profile(
        session=session,
        profile_create=ProfileCreate(full_name=db_obj.full_name),
        user_id=db_obj.id,
    )
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_profile_by_user_id(*, session: Session, user_id: int) -> Profile | None:
    statement = select(Profile).where(Profile.user_id == user_id)
    return session.exec(statement).first()


def create_profile(
    *, session: Session, profile_create: ProfileCreate, user_id: int
) -> Profile:
    db_profile = Profile.model_validate(profile_create, update={"user_id": user_id})
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


def create_section(*, session: Session, section_in: SectionCreate) -> Section:
    db_section = Section.model_validate(section_in)
    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


def get_section_by_id(*, session: Session, section_id: int) -> Section | None:
    statement = select(Section).where(Section.id == section_id)
    return session.exec(statement).first()


def update_section(
    *, session: Session, section_id: int, section_in: SectionUpdate
) -> Any:
    db_section = get_section_by_id(session=session, section_id=section_id)
    if not db_section:
        return None
    db_section.sqlmodel_update(section_in)
    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


def delete_section(*, session: Session, section_id: int) -> None:
    statement = select(Section).where(Section.id == section_id)
    db_section = session.exec(statement).first()
    session.delete(db_section)
    session.commit()
    return None


def get_badge_by_name(*, session: Session, name: str) -> Badge | None:
    statement = select(Badge).where(Badge.name == name)
    return session.exec(statement).first()


def create_badge(*, session: Session, badge_create: BadgeCreate) -> Badge:
    db_badge = Badge.model_validate(badge_create)
    session.add(db_badge)
    session.commit()
    session.refresh(db_badge)
    return db_badge


def update_badge(*, session: Session, db_badge: Badge, badge_in: BadgeCreate) -> Any:
    badge_data = badge_in.model_dump(exclude_unset=True)
    db_badge.sqlmodel_update(badge_data)
    session.add(db_badge)
    session.commit()
    session.refresh(db_badge)
    return db_badge


def get_question_by_name(*, session: Session, name: str) -> Question | None:
    statement = select(Question).where(Question.name == name)
    return session.exec(statement).first()


def create_question(*, session: Session, question_in: QuestionCreate) -> Question:
    db_question = Question.model_validate(question_in)
    session.add(db_question)
    session.commit()
    session.refresh(db_question)
    return db_question


def update_question(
    *, session: Session, db_question: Question, question_in: QuestionUpdate
) -> Any:
    question_data = question_in.model_dump(exclude_unset=True)
    db_question.sqlmodel_update(question_data)
    session.add(db_question)
    session.commit()
    session.refresh(db_question)
    return db_question


def delete_question(*, session: Session, question_id: int) -> None:
    statement = select(Question).where(Question.id == question_id)
    db_question = session.exec(statement).first()
    session.delete(db_question)
    session.commit()
    return None
