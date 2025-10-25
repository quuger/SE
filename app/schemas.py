from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.models import AccountType, BookmarkStatus, AccessLevel


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class User(UserBase):
    id: UUID
    account_type: AccountType
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Auth schemas
class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: Optional[str] = Field(None, min_length=3)


class AuthResponse(BaseModel):
    user: User
    access_token: str
    refresh_token: str


# Bookmark schemas
class BookmarkBase(BaseModel):
    url: HttpUrl = Field(..., max_length=2000)
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    access_level: AccessLevel = AccessLevel.PRIVATE


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    url: Optional[HttpUrl] = Field(None, max_length=2000)
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    access_level: Optional[AccessLevel] = None


class Bookmark(BookmarkBase):
    id: UUID
    status: BookmarkStatus = BookmarkStatus.ACTIVE
    owner_id: UUID
    sync_version: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Bookmark list response
class BookmarkListResponse(BaseModel):
    bookmarks: List[Bookmark]
    total_count: int
    has_more: bool


# Import/Export schemas
class ImportRequest(BaseModel):
    format: str = Field(..., pattern="^(json|html|csv)$")
    data: str  # Base64 encoded file content or JSON data


class ImportResponse(BaseModel):
    imported_count: int
    failed_count: int
    errors: List[str] = []


# Sync schemas
class SyncRequest(BaseModel):
    last_sync: Optional[datetime] = None
    sync_version: Optional[int] = Field(None, ge=0)


class SyncResponse(BaseModel):
    bookmarks: List[Bookmark]
    deleted_bookmarks: List[UUID] = []
    deleted_collections: List[UUID] = []
    server_version: int
    has_conflicts: bool = False


class ConflictResolution(BaseModel):
    bookmark_id: UUID
    resolution: str = Field(..., pattern="^(client|server)$")
    client_data: Optional[Bookmark] = None
    server_data: Optional[Bookmark] = None


class SyncResolveRequest(BaseModel):
    resolutions: List[ConflictResolution]


class SyncResolveResponse(BaseModel):
    resolved_count: int
    sync_version: int


# Error schema
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class Error(BaseModel):
    error: ErrorDetail


# Legacy schemas for backward compatibility
class UserResponse(User):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
