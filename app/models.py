from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class AccountType(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"


class BookmarkStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class AccessLevel(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.FREE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="owner", cascade="all, delete-orphan")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(BookmarkStatus), default=BookmarkStatus.ACTIVE, nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.PRIVATE, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sync_version = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="bookmarks")
