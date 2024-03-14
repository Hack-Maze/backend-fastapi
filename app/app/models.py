from typing import Union

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Union[str, None] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


class UserCreateOpen(SQLModel):
    email: EmailStr
    password: str
    full_name: Union[str, None] = None


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Union[EmailStr, None] = None
    password: Union[str, None] = None


class UserUpdateMe(BaseModel):
    password: Union[str, None] = None
    full_name: Union[str, None] = None
    email: Union[EmailStr, None] = None


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")
    rooms: list["Room"] = Relationship(back_populates="user")
    publicuser: list["PublicUser"] = Relationship(back_populates="user")

# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


# Shared properties
class ItemBase(SQLModel):
    title: str
    description: Union[str, None] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: Union[str, None] = None


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    title: str
    owner_id: Union[int, None] = Field(
        default=None, foreign_key="user.id", nullable=False
    )
    owner: Union[User, None] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemOut(ItemBase):
    id: int


# do the same for rooms {id, user, description, difficulty, is_active, recommended_video, room_type, title, visibility, created_at, updated_at, deleted_at}
class RoomBase(SQLModel):
    title: str
    description: Union[str, None] = None
    difficulty: int
    is_active: bool
    recommended_video: Union[str, None] = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: Union[str, None] = None


class RoomCreate(RoomBase):
    title: str
    description: Union[str, None] = None
    difficulty: int
    is_active: bool
    recommended_video: Union[str, None] = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: Union[str, None] = None


class RoomUpdate(RoomBase):
    title: Union[str, None] = None
    description: Union[str, None] = None
    difficulty: Union[int, None] = None
    is_active: Union[bool, None] = None
    recommended_video: Union[str, None] = None
    room_type: Union[str, None] = None
    visibility: Union[str, None] = None
    created_at: Union[str, None] = None
    updated_at: Union[str, None] = None
    deleted_at: Union[str, None] = None


class Room(RoomBase, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    title: str
    user_id: Union[int, None] = Field(
        default=None, foreign_key="user.id", nullable=False
    )
    user: Union[User, None] = Relationship(back_populates="rooms")


class RoomOut(RoomBase):
    id: int


# do the same for PublicUser {full_name , country , rank, level , bio ,github link ,linkedin link ,personal blog link ,job ,active room , completed rooms ,friends ,badges ,created rooms}
class PublicUserBase(SQLModel):
    full_name : str
    country : str
    rank :int
    level :int
    bio :str
    github_link: str
    linkedin_link : str
    personal_blog_link :str
    job : str
    active_room : bool
    completed_rooms : str
    friends :str
    badges : str
    created_rooms : str


class PublicUserCreate(PublicUserBase):
    full_name : str
    country : str
    rank :int
    level :int
    bio :str
    github_link: str
    linkedin_link : str
    personal_blog_link :str
    job : str
    active_room : bool
    completed_rooms : str
    friends :str
    badges : str
    created_rooms : str

class PublicUserUpdate(PublicUserBase):
    full_name: Union[str, None] = None
    country: Union[str, None] = None
    rank: Union[int, None] = None
    level: Union[int, None] = None
    github_link: Union[str, None] = None
    linkedin_link: Union[str, None] = None
    personal_blog_link: Union[str, None] = None
    job: Union[str, None] = None
    active_room: Union[bool, None] = None
    completed_rooms: Union[str, None] = None
    friends: Union[str, None] = None
    created_rooms: Union[str, None] = None


class PublicUser(PublicUserBase, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    full_name: str
    user_id: Union[int, None] = Field(
        default=None, foreign_key="user.id", nullable=False
    )
    user: Union[User, None] = Relationship(back_populates="publicuser")


class PublicUserOut(PublicUserBase):
    id: int


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Union[int, None] = None


class NewPassword(BaseModel):
    token: str
    new_password: str
