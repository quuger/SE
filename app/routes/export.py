from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth
from app.database import get_db
from app.models import User
from typing import Optional
from uuid import UUID
import json
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/{format}")
async def export_bookmarks(
    format: str,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export bookmarks in specified format"""
    
    # Get all bookmarks for user
    bookmarks = await crud.get_user_bookmarks(
        db=db,
        owner_id=current_user.id,
        limit=10000  # Large limit for export
    )
    
    if format == "json":
        return export_json(bookmarks)
    elif format == "html":
        return export_html(bookmarks)
    elif format == "csv":
        return export_csv(bookmarks)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format"
        )


def export_json(bookmarks):
    """Export bookmarks as JSON"""
    bookmarks_data = []
    for bookmark in bookmarks:
        bookmarks_data.append({
            "id": str(bookmark.id),
            "url": str(bookmark.url),
            "title": bookmark.title,
            "description": bookmark.description,
            "access_level": bookmark.access_level.value,
            "status": bookmark.status.value,
            "created_at": bookmark.created_at.isoformat(),
            "updated_at": bookmark.updated_at.isoformat() if bookmark.updated_at else None
        })
    
    return {"bookmarks": bookmarks_data}


def export_html(bookmarks):
    """Export bookmarks as HTML"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bookmarks Export</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .bookmark {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }}
            .title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
            .url {{ color: #0066cc; text-decoration: none; }}
            .description {{ color: #666; margin-top: 5px; }}
            .meta {{ font-size: 12px; color: #999; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>Bookmarks Export</h1>
        <p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total bookmarks: {len(bookmarks)}</p>
    """
    
    for bookmark in bookmarks:
        html_content += f"""
        <div class="bookmark">
            <div class="title">{bookmark.title}</div>
            <a href="{bookmark.url}" class="url">{bookmark.url}</a>
            {f'<div class="description">{bookmark.description}</div>' if bookmark.description else ''}
            <div class="meta">
                Status: {bookmark.status.value} | 
                Access: {bookmark.access_level.value} | 
                Created: {bookmark.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=bookmarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"}
    )


def export_csv(bookmarks):
    """Export bookmarks as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Title", "URL", "Description", "Status", "Access Level", 
        "Created At", "Updated At"
    ])
    
    # Write data
    for bookmark in bookmarks:
        writer.writerow([
            bookmark.title,
            str(bookmark.url),
            bookmark.description or "",
            bookmark.status.value,
            bookmark.access_level.value,
            bookmark.created_at.isoformat(),
            bookmark.updated_at.isoformat() if bookmark.updated_at else ""
        ])
    
    output.seek(0)
    
    def generate():
        yield output.getvalue()
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=bookmarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )
