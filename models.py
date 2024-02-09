from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# endpoints for all models

SQLALCHEMY_DATABASE_URL = "mysql://root:ff@127.0.0.1:3306/fastapi_admin"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from fastapi import FastAPI, Request, Response


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def _create_user(db: Session, user: UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


class SUser(UserBase):
    id: int
    is_active: int

    class Config:
        orm_mode = True


@app.get("/users/", response_model=list[SUser])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=SUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return _create_user(db=db, user=user)


@app.get("/")
async def read_root(request: Request):
    return {"message": "Hello World"}


# class Room(Base):
#     __tablename__ = "room"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)

#     class Config:
#         orm_mode = True


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

#     class Config:
#         orm_mode = True


# class Collection(Base):
#     __tablename__ = "collection"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)

#     rooms = relationship(
#         "Room", secondary=association_table, back_populates="collections"
#     )


# class Module(Base):
#     __tablename__ = "module"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     author_id = Column(Integer, ForeignKey("user.id"))
#     level = Column(Integer, index=True)
#     is_active = Column(Boolean, default=False)

#     collections = relationship("Collection", back_populates="modules")

#     author = relationship("User", back_populates="modules")


# def get_room(db: Session, room_id: int):
#     return db.query(Room).filter(Room.id == room_id).first()


# def get_rooms(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Room).offset(skip).limit(limit).all()


# class RoomCreate(BaseModel):
#     title: str
#     description: str


# @app.post("/rooms/", response_model=Room)
# def create_room(db: Session, room: RoomCreate):
#     db_room = Room(**room.dict())
#     db.add(db_room)
#     db.commit()
#     db.refresh(db_room)
#     return db_room


# def get_collection(db: Session, collection_id: int):
#     return db.query(Collection).filter(Collection.id == collection_id).first()


# def get_collections(db: Session, skip: int = 0, limit: int = 100):

#     return db.query(Collection).offset(skip).limit(limit).all()


# class CollectionCreate(BaseModel):
#     title: str
#     description: str


# def create_collection(db: Session, collection: CollectionCreate):
#     db_collection = Collection(**collection.dict())
#     db.add(db_collection)
#     db.commit()
#     db.refresh(db_collection)
#     return db_collection


# def get_module(db: Session, module_id: int):

#     return db.query(Module).filter(Module.id == module_id).first()


# def get_modules(db: Session, skip: int = 0, limit: int = 100):

#     return db.query(Module).offset(skip).limit(limit).all()


# class ModuleCreate(BaseModel):
#     title: str
#     description: str
#     author_id: int
#     level: int
#     is_active: bool


# def create_module(db: Session, module: ModuleCreate):
#     db_module = Module(**module.dict())
#     db.add(db_module)
#     db.commit()
#     db.refresh(db_module)
#     return db_module


# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


# class User(Base):
#     __tablename__ = "user"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     modules = relationship("Module", back_populates="author")


# def get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):

#     return db.query(User).filter(User.email == email).first()


# def create_user(db: Session, user: UserCreate):
#     hashed_password = get_password_hash(user.password)
#     db_user = User(email=user.email, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool

#     class Config:
#         orm_mode = True


# def get_user(db: Session, user_id: int):

#     return db.query(User).filter(User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):

#     return db.query(User).filter(User.email == email).first()


# def create_user(db: Session, user: UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# @app.post("/rooms/", response_model=Room)
# def create_room(room: RoomCreate, db: Session = Depends(get_db)):
#     return create_room(db, room)


# @app.get("/rooms/", response_model=List[Room])
# def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     rooms = get_rooms(db, skip=skip, limit=limit)
#     return rooms


# @app.get("/rooms/{room_id}", response_model=Room)
# def read_room(room_id: int, db: Session = Depends(get_db)):
#     db_room = get_room(db, room_id)
#     if db_room is None:
#         raise HTTPException(status_code=404, detail="Room not found")
#     return db_room


# @app.post("/collections/", response_model=Collection)
# def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
#     return create_collection(db, collection)


# @app.get("/collections/", response_model=List[Collection])
# def read_collections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     collections = get_collections(db, skip=skip, limit=limit)
#     return collections


# @app.get("/collections/{collection_id}", response_model=Collection)
# def read_collection(collection_id: int, db: Session = Depends(get_db)):
#     db_collection = get_collection(db, collection_id)
#     if db_collection is None:
#         raise HTTPException(status_code=404, detail="Collection not found")
#     return db_collection


# @app.post("/modules/", response_model=Module)
# def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
#     return create_module(db, module)


# @app.get("/modules/", response_model=List[Module])
# def read_modules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     modules = get_modules(db, skip=skip, limit=limit)
#     return modules


# @app.get("/modules/{module_id}", response_model=Module)
# def read_module(module_id: int, db: Session = Depends(get_db)):

#     db_module = get_module(db, module_id)
#     if db_module is None:
#         raise HTTPException(status_code=404, detail="Module not found")
#     return db_module
