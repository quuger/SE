from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserCreate
from app.auth import get_password_hash


async def get_user(db: AsyncSession, user_id: int):
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
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    # Add to database
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user
