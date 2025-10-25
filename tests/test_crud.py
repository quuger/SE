"""
Тестовые CRUD операции для SQLite совместимости
"""
import sys
import os
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_models import TestUser as User, TestBookmark as Bookmark
from app.schemas import UserCreate, BookmarkCreate, BookmarkUpdate


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Получить пользователя по ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Создать пользователя"""
    import uuid
    from app.auth import get_password_hash
    
    db_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)  # Хешируем пароль
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_bookmarks(db: AsyncSession, owner_id: str, skip: int = 0, limit: int = 100) -> List[Bookmark]:
    """Получить закладки пользователя"""
    result = await db.execute(
        select(Bookmark)
        .filter(Bookmark.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_user_bookmarks(db: AsyncSession, owner_id: str, skip: int = 0, limit: int = 100, offset: int = 0) -> List[Bookmark]:
    """Получить закладки пользователя (алиас для совместимости)"""
    # Используем offset если передан, иначе skip
    actual_offset = offset if offset > 0 else skip
    return await get_bookmarks(db, owner_id, actual_offset, limit)


async def get_bookmarks_count(db: AsyncSession, owner_id: str) -> int:
    """Получить количество закладок пользователя"""
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(Bookmark.id))
        .filter(Bookmark.owner_id == owner_id)
    )
    return result.scalar() or 0


async def get_bookmark(db: AsyncSession, bookmark_id: str, owner_id: str) -> Optional[Bookmark]:
    """Получить закладку по ID"""
    result = await db.execute(
        select(Bookmark)
        .filter(Bookmark.id == bookmark_id)
        .filter(Bookmark.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def create_bookmark(db: AsyncSession, bookmark: BookmarkCreate, owner_id: str) -> Bookmark:
    """Создать закладку"""
    from app.models import BookmarkStatus
    import uuid
    db_bookmark = Bookmark(
        id=str(uuid.uuid4()),  # Генерируем UUID
        url=str(bookmark.url),  # Конвертируем HttpUrl в строку
        title=bookmark.title,
        description=bookmark.description,
        status=BookmarkStatus.ACTIVE,  # По умолчанию активная
        access_level=bookmark.access_level,
        owner_id=owner_id,
        sync_version=1  # Начальная версия синхронизации
    )
    db.add(db_bookmark)
    await db.commit()
    await db.refresh(db_bookmark)
    return db_bookmark


async def update_bookmark(db: AsyncSession, bookmark_id, bookmark_update: BookmarkUpdate = None, owner_id: str = None, **kwargs) -> Optional[Bookmark]:
    """Обновить закладку"""
    # Конвертируем bookmark_id в строку если это UUID
    bookmark_id_str = str(bookmark_id)
    owner_id_str = str(owner_id) if owner_id else None
    
    db_bookmark = await get_bookmark(db, bookmark_id_str, owner_id_str)
    if not db_bookmark:
        return None
    
    # Обновляем поля из kwargs (переданные из routes)
    for field, value in kwargs.items():
        if hasattr(db_bookmark, field):
            setattr(db_bookmark, field, value)
    
    # Увеличиваем версию синхронизации при обновлении
    db_bookmark.sync_version += 1
    
    await db.commit()
    await db.refresh(db_bookmark)
    return db_bookmark


async def delete_bookmark(db: AsyncSession, bookmark_id, owner_id: str = None) -> bool:
    """Удалить закладку"""
    # Конвертируем bookmark_id в строку если это UUID
    bookmark_id_str = str(bookmark_id)
    owner_id_str = str(owner_id) if owner_id else None
    
    db_bookmark = await get_bookmark(db, bookmark_id_str, owner_id_str)
    if not db_bookmark:
        return False
    
    await db.delete(db_bookmark)
    await db.commit()
    return True
