from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.AuthRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists by email
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Check if username already exists
    if user.username:
        db_user = await crud.get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    # Create new user
    user_create = schemas.UserCreate(
        username=user.username or user.email.split('@')[0],
        email=user.email,
        password=user.password
    )
    new_user = await crud.create_user(db=db, user=user_create)
    
    # Create tokens
    access_token, refresh_token = auth.create_token_pair(str(new_user.id))
    
    return schemas.AuthResponse(
        user=new_user,
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=schemas.AuthResponse)
async def login_user(
    user_credentials: schemas.AuthRequest, db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    # Authenticate user
    user = await auth.authenticate_user(
        db, user_credentials.email, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token, refresh_token = auth.create_token_pair(str(user.id))
    
    return schemas.AuthResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token
    )