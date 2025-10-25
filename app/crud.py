from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, desc, func
from app.models import User, Bookmark, BookmarkStatus, AccessLevel
from app.schemas import UserCreate, BookmarkCreate, BookmarkUpdate
from app.auth import get_password_hash
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime


# User CRUD operations
async def get_user(db: AsyncSession, user_id: UUID):
    """Get a user by ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str):
    """Get a user by username"""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    """Get a user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user"""
    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create the user object
    db_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )

    # Add to database
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


# Bookmark CRUD operations
async def get_bookmark(db: AsyncSession, bookmark_id: UUID, owner_id: UUID):
    """Get a bookmark by ID for a specific owner"""
    result = await db.execute(
        select(Bookmark).filter(
            and_(Bookmark.id == bookmark_id, Bookmark.owner_id == owner_id)
        )
    )
    return result.scalar_one_or_none()


async def get_user_bookmarks(
    db: AsyncSession, 
    owner_id: UUID, 
    limit: int = 50, 
    offset: int = 0
):
    """Get bookmarks for a user"""
    result = await db.execute(
        select(Bookmark)
        .filter(Bookmark.owner_id == owner_id)
        .order_by(desc(Bookmark.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_bookmarks_count(
    db: AsyncSession, 
    owner_id: UUID
):
    """Get total count of bookmarks for a user"""
    result = await db.execute(
        select(func.count(Bookmark.id)).filter(Bookmark.owner_id == owner_id)
    )
    return result.scalar()


async def create_bookmark(db: AsyncSession, bookmark: BookmarkCreate, owner_id: UUID):
    """Create a new bookmark"""
    db_bookmark = Bookmark(
        url=str(bookmark.url),
        title=bookmark.title,
        description=bookmark.description,
        access_level=bookmark.access_level,
        owner_id=owner_id
    )
    db.add(db_bookmark)
    await db.commit()
    await db.refresh(db_bookmark)
    return db_bookmark


async def update_bookmark(db: AsyncSession, bookmark_id: UUID, owner_id: UUID, **kwargs):
    """Update a bookmark"""
    bookmark = await get_bookmark(db, bookmark_id, owner_id)
    if not bookmark:
        return None
    
    for key, value in kwargs.items():
        if hasattr(bookmark, key) and value is not None:
            setattr(bookmark, key, value)
    
    bookmark.sync_version += 1
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


async def delete_bookmark(db: AsyncSession, bookmark_id: UUID, owner_id: UUID):
    """Delete a bookmark"""
    bookmark = await get_bookmark(db, bookmark_id, owner_id)
    if not bookmark:
        return False
    
    await db.delete(bookmark)
    await db.commit()
    return True


# Sync operations
async def get_sync_data(
    db: AsyncSession, 
    owner_id: UUID, 
    last_sync: Optional[datetime] = None,
    sync_version: Optional[int] = None
):
    """Get data for synchronization"""
    query = select(Bookmark).filter(Bookmark.owner_id == owner_id)
    
    if last_sync:
        query = query.filter(Bookmark.updated_at > last_sync)
    
    if sync_version is not None:
        query = query.filter(Bookmark.sync_version > sync_version)
    
    result = await db.execute(query.order_by(Bookmark.updated_at))
    return result.scalars().all()


async def get_server_version(db: AsyncSession, owner_id: UUID):
    """Get current server version for user"""
    result = await db.execute(
        select(func.max(Bookmark.sync_version))
        .filter(Bookmark.owner_id == owner_id)
    )
    return result.scalar() or 0
