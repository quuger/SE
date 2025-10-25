from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Base user schema
class UserBase(BaseModel):
    username: str
    email: EmailStr


# Schema for user registration
class UserCreate(UserBase):
    password: str


# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str


# Schema for user response (without password)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for token data
class TokenData(BaseModel):
    username: Optional[str] = None
