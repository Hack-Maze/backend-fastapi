from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserCreateOpen(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    profile: list["Profile"] = Relationship(back_populates="user")
    rooms: list["Room"] = Relationship(back_populates="owner")
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int


class ProfileBase(SQLModel):
    full_name: str
    country: str
    rank: int
    level: int
    bio: str
    github_link: str
    linkedin_link: str
    personal_blog_link: str
    job: str
    active_room: bool
    completed_rooms: str
    friends: str
    badges: str
    created_rooms: str


class ProfileCreate(ProfileBase):
    full_name: str
    country: str
    rank: int
    level: int
    bio: str
    github_link: str
    linkedin_link: str
    personal_blog_link: str
    job: str
    active_room: bool
    completed_rooms: str
    friends: str
    badges: str
    created_rooms: str


class ProfileUpdate(ProfileBase):
    full_name: str | None = None
    country: str | None = None
    rank: int | None = None
    level: int | None = None
    github_link: str | None = None
    linkedin_link: str | None = None
    personal_blog_link: str | None = None
    job: str | None = None
    active_room: bool | None = None
    completed_rooms: str | None = None
    friends: str | None = None
    created_rooms: str | None = None


class Profile(ProfileBase, table=True):
    id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: int = Field(foreign_key="user.id", nullable=False)
    # O-O relationship
    user: User = Relationship(
        sa_relationship_kwargs={
            "uselist": False
        },  # SQLModel is a wrapper around SQLAlchemy, so you can use SQLAlchemy's relationship kwargs
        back_populates="profile",
    )


class ProfileOut(ProfileBase):
    id: UUID
    user_id: int


# do the same for rooms {id, user, description, difficulty, is_active, recommended_video, room_type, title, visibility, created_at, updated_at, deleted_at}
class RoomBase(SQLModel):
    title: str
    description: str | None = None
    difficulty: int
    is_active: bool
    recommended_video: str | None = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class RoomCreate(RoomBase):
    title: str
    description: str | None = None
    difficulty: int
    is_active: bool
    recommended_video: str | None = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class RoomUpdate(RoomBase):
    title: str | None = None
    description: str | None = None
    difficulty: int | None = None
    is_active: bool | None = None
    recommended_video: str | None = None
    room_type: str | None = None
    visibility: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    deleted_at: str | None = None


class Room(RoomBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="rooms")


class RoomOut(RoomBase):
    id: int
    owner_id: int | None = None


class RoomsOut(SQLModel):
    data: list[RoomOut]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str

# Shared properties
class ItemBase(SQLModel):
    title: str
    description: str | None = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemOut(ItemBase):
    id: int
    owner_id: int


class ItemsOut(SQLModel):
    data: list[ItemOut]
    count: int
