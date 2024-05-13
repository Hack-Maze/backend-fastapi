from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserCreateOpen(SQLModel):
    email: str
    password: str
    full_name: str | None = None


class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


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
    active_rooms: list["Room"] = Relationship(back_populates="owner")
    completed_rooms: list["Room"] = Relationship(back_populates="owner")
    created_rooms: list["Room"] = Relationship(back_populates="owner")
    rooms: list["Room"] = Relationship(back_populates="owner")
    items: list["Item"] = Relationship(back_populates="owner")
    badges: list["Badge"] = Relationship(back_populates="owner")
    friends: list["User"] = Relationship(back_populates="friends")


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
    image: str
    github_link: str
    linkedin_link: str
    personal_blog_link: str
    job: str


class ProfileCreate(ProfileBase):
    full_name: str
    country: str = "Egypt"
    rank: int = 1
    level: int = 1
    bio: str = "I am a software engineer"
    image: str = "https://example.com/image.jpg"
    github_link: str = ""
    linkedin_link: str = ""
    personal_blog_link: str = "" 
    job: str = "Software Engineer"


class ProfileUpdate(ProfileBase):
    full_name: str | None = None
    country: str | None = None
    rank: int | None = None
    level: int | None = None
    github_link: str | None = None
    linkedin_link: str | None = None
    personal_blog_link: str | None = None
    job: str | None = None
    image: str | None = None


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


class RoomBase(SQLModel):
    title: str
    description: str | None = None
    difficulty: int
    level: str  # Added level property
    is_active: bool
    recommended_video: str | None = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None
    file_name: str = None


class RoomCreate(RoomBase):
    title: str
    description: str | None = None
    difficulty: int
    level: str  # Added level property
    is_active: bool
    recommended_video: str | None = None
    room_type: str
    visibility: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None
    file_name: str = None


class RoomUpdate(RoomBase):
    title: str | None = None
    description: str | None = None
    difficulty: int | None = None
    level: str | None = None  # Added level property
    is_active: bool | None = None
    recommended_video: str | None = None
    room_type: str | None = None
    visibility: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    deleted_at: str | None = None
    file_name: str = None


class Room(RoomBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="rooms")
    sections: list["Section"] = Relationship(back_populates="room")


class RoomOut(RoomBase):
    id: int
    owner_id: int | None = None
    sections: list["Section"] = []


class RoomsOut(SQLModel):
    data: list[RoomOut]
    count: int


class SectionBase(SQLModel):
    title: str
    description: str | None = None
    room_id: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class SectionCreate(SectionBase):
    title: str
    description: str | None = None
    room_id: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class SectionUpdate(SectionBase):
    title: str | None = None
    description: str | None = None
    room_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    deleted_at: str | None = None


class Section(SectionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    room_id: int | None = Field(default=None, foreign_key="room.id", nullable=False)
    room: Room | None = Relationship(back_populates="sections")


class SectionOut(SectionBase):
    id: int
    room_id: int | None = None


class SectionsOut(SQLModel):
    data: list[SectionOut]
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


class ItemCreate(ItemBase):
    title: str


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


class BadgeBase(SQLModel):
    title: str
    image: str


class BadgeCreate(BadgeBase):
    title: str
    image: str


class BadgeUpdate(BadgeBase):
    title: str | None = None
    image: str | None = None


class Badge(BadgeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    image: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="badges")


class BadgeOut(BadgeBase):
    id: int
    owner_id: int


class BadgesOut(SQLModel):
    data: list[BadgeOut]
    count: int
