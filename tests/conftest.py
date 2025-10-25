"""
Конфигурация для интеграционных тестов
"""
import sys
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Переопределяем конфигурацию базы данных для тестов
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.database import get_db
from app.auth import get_password_hash
from app.schemas import UserCreate
from tests.test_models import Base, TestUser as User, TestBookmark as Bookmark
from tests.test_crud import get_user, get_user_by_email, create_user, get_bookmarks, get_user_bookmarks, get_bookmarks_count, get_bookmark, create_bookmark, update_bookmark, delete_bookmark


# Тестовая база данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем тестовый движок
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Создаем фабрику сессий для тестов
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создаем event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Создаем тестовую базу данных для каждого теста"""
    # Создаем все таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию
    async with TestSessionLocal() as session:
        yield session
    
    # Очищаем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создаем тестовый клиент"""
    
    def override_get_db():
        return test_db
    
    # Переопределяем CRUD операции для тестов
    import app.crud as crud
    crud.get_user = get_user
    crud.get_user_by_email = get_user_by_email
    crud.create_user = create_user
    crud.get_bookmarks = get_bookmarks
    crud.get_user_bookmarks = get_user_bookmarks
    crud.get_bookmarks_count = get_bookmarks_count
    crud.get_bookmark = get_bookmark
    crud.create_bookmark = create_bookmark
    crud.update_bookmark = update_bookmark
    crud.delete_bookmark = delete_bookmark
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Создаем тестового пользователя"""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="pass123"
    )
    
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def test_user_2(test_db: AsyncSession) -> User:
    """Создаем второго тестового пользователя"""
    user_data = UserCreate(
        username="testuser2",
        email="test2@example.com",
        password="pass123"
    )
    
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Получаем заголовки авторизации для тестового пользователя"""
    login_data = {
        "email": test_user.email,
        "password": "pass123"
    }
    
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_bookmark(test_db: AsyncSession, test_user: User) -> Bookmark:
    """Создаем тестовую закладку"""
    bookmark = Bookmark(
        id=str(uuid.uuid4()),
        url="https://example.com",
        title="Test Bookmark",
        description="Test description",
        owner_id=str(test_user.id)
    )
    
    test_db.add(bookmark)
    await test_db.commit()
    await test_db.refresh(bookmark)
    
    return bookmark


@pytest.fixture
async def multiple_bookmarks(test_db: AsyncSession, test_user: User) -> list[Bookmark]:
    """Создаем несколько тестовых закладок"""
    bookmarks = []
    for i in range(5):
        bookmark = Bookmark(
            id=str(uuid.uuid4()),
            url=f"https://example{i}.com",
            title=f"Test Bookmark {i}",
            description=f"Test description {i}",
            owner_id=str(test_user.id)
        )
        bookmarks.append(bookmark)
        test_db.add(bookmark)
    
    await test_db.commit()
    for bookmark in bookmarks:
        await test_db.refresh(bookmark)
    
    return bookmarks
