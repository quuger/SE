from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth
from app.database import get_db
from app.models import User
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.get("/", response_model=schemas.BookmarkListResponse)
async def get_bookmarks(
    limit: int = Query(50, ge=1, le=200, description="Number of bookmarks to return"),
    offset: int = Query(0, ge=0, description="Number of bookmarks to skip"),
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmarks"""
    bookmarks = await crud.get_user_bookmarks(
        db=db,
        owner_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    total_count = await crud.get_bookmarks_count(
        db=db,
        owner_id=current_user.id
    )
    
    has_more = (offset + limit) < total_count
    
    return schemas.BookmarkListResponse(
        bookmarks=bookmarks,
        total_count=total_count,
        has_more=has_more
    )


@router.post("/", response_model=schemas.Bookmark, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: schemas.BookmarkCreate,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bookmark"""
    # Check bookmark limits for free users
    if current_user.account_type.value == "free":
        bookmark_count = await crud.get_bookmarks_count(db, current_user.id)
        if bookmark_count >= 100:  # Free tier limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookmark limit exceeded for free account"
            )
    
    new_bookmark = await crud.create_bookmark(
        db=db,
        bookmark=bookmark,
        owner_id=current_user.id
    )
    
    return new_bookmark


@router.put("/{bookmark_id}", response_model=schemas.Bookmark)
async def update_bookmark(
    bookmark_id: UUID,
    bookmark_update: schemas.BookmarkUpdate,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a bookmark"""
    # Get update data, excluding None values
    update_data = bookmark_update.dict(exclude_unset=True)
    
    updated_bookmark = await crud.update_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        owner_id=current_user.id,
        **update_data
    )
    
    if not updated_bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return updated_bookmark


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bookmark"""
    success = await crud.delete_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        owner_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return {"success": True}
