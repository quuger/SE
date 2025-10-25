from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth
from app.database import get_db
from app.models import User, BookmarkStatus, AccessLevel
from typing import List
from uuid import UUID
import json
import base64
import re
from datetime import datetime

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/{format}", response_model=schemas.ImportResponse)
async def import_bookmarks(
    format: str,
    import_request: schemas.ImportRequest,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import bookmarks from specified format"""
    
    # Check import limits for free users
    if current_user.account_type.value == "free":
        bookmark_count = await crud.get_bookmarks_count(db, current_user.id)
        if bookmark_count >= 100:  # Free tier limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Import limit exceeded for free account"
            )
    
    try:
        if format == "json":
            return await import_json(import_request, current_user, db)
        elif format == "html":
            return await import_html(import_request, current_user, db)
        elif format == "csv":
            return await import_csv(import_request, current_user, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported import format"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}"
        )


async def import_json(import_request: schemas.ImportRequest, current_user: User, db: AsyncSession):
    """Import bookmarks from JSON format"""
    try:
        # Decode base64 data if needed
        if import_request.data.startswith('data:'):
            # Remove data URL prefix
            data = import_request.data.split(',')[1]
            decoded_data = base64.b64decode(data).decode('utf-8')
        else:
            decoded_data = import_request.data
        
        bookmarks_data = json.loads(decoded_data)
        
        # Handle different JSON structures
        if isinstance(bookmarks_data, dict) and 'bookmarks' in bookmarks_data:
            bookmarks_list = bookmarks_data['bookmarks']
        elif isinstance(bookmarks_data, list):
            bookmarks_list = bookmarks_data
        else:
            bookmarks_list = [bookmarks_data]
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        for bookmark_data in bookmarks_list:
            try:
                bookmark_create = schemas.BookmarkCreate(
                    url=bookmark_data['url'],
                    title=bookmark_data.get('title', bookmark_data['url']),
                    description=bookmark_data.get('description'),
                    access_level=AccessLevel(bookmark_data.get('access_level', 'private'))
                )
                
                await crud.create_bookmark(db, bookmark_create, current_user.id)
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to import bookmark {bookmark_data.get('title', 'Unknown')}: {str(e)}")
        
        return schemas.ImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )


async def import_html(import_request: schemas.ImportRequest, current_user: User, db: AsyncSession):
    """Import bookmarks from HTML format (browser bookmarks)"""
    try:
        # Decode base64 data if needed
        if import_request.data.startswith('data:'):
            data = import_request.data.split(',')[1]
            decoded_data = base64.b64decode(data).decode('utf-8')
        else:
            decoded_data = import_request.data
        
        # Parse HTML to extract links
        link_pattern = r'<A HREF="([^"]*)"[^>]*>([^<]*)</A>'
        matches = re.findall(link_pattern, decoded_data, re.IGNORECASE)
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        for url, title in matches:
            try:
                bookmark_create = schemas.BookmarkCreate(
                    url=url,
                    title=title.strip()
                )
                
                await crud.create_bookmark(db, bookmark_create, current_user.id)
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to import bookmark {title}: {str(e)}")
        
        return schemas.ImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse HTML: {str(e)}"
        )


async def import_csv(import_request: schemas.ImportRequest, current_user: User, db: AsyncSession):
    """Import bookmarks from CSV format"""
    try:
        import csv
        from io import StringIO
        
        # Decode base64 data if needed
        if import_request.data.startswith('data:'):
            data = import_request.data.split(',')[1]
            decoded_data = base64.b64decode(data).decode('utf-8')
        else:
            decoded_data = import_request.data
        
        csv_reader = csv.DictReader(StringIO(decoded_data))
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                bookmark_create = schemas.BookmarkCreate(
                    url=row['URL'],
                    title=row.get('Title', row['URL']),
                    description=row.get('Description', ''),
                    access_level=AccessLevel(row.get('Access Level', 'private'))
                )
                
                await crud.create_bookmark(db, bookmark_create, current_user.id)
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to import bookmark {row.get('Title', 'Unknown')}: {str(e)}")
        
        return schemas.ImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(e)}"
        )
