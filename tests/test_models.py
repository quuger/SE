"""
Тестовые модели для SQLite совместимости
"""
import sys
import os
from sqlalchemy import Column, String, DateTime, Enum, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.models import AccountType, BookmarkStatus, AccessLevel

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Base = declarative_base()


class TestUser(Base):
    """Тестовая модель пользователя для SQLite"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)  # UUID как строка
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.FREE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TestBookmark(Base):
    """Тестовая модель закладки для SQLite"""
    __tablename__ = "bookmarks"
    
    id = Column(String(36), primary_key=True)  # UUID как строка
    url = Column(Text, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(BookmarkStatus), default=BookmarkStatus.ACTIVE, nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.PRIVATE, nullable=False)
    owner_id = Column(String(36), nullable=False)  # UUID как строка
    sync_version = Column(Integer, default=1, nullable=False)  # Добавляем sync_version
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())