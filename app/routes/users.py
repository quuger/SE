from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth
from app.database import get_db
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    new_user = await crud.create_user(db=db, user=user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login_user(
    user_credentials: schemas.UserLogin, db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    # Authenticate user
    user = await auth.authenticate_user(
        db, user_credentials.username, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
