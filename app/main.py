from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, base, bookmarks, export, import_routes
from app.database import engine, Base
import asyncio

app = FastAPI(
    title="Bookmark Management Service API",
    description="API для управления закладками с поддержкой экспорта и управления доступом",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@bookmarkservice.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Include routers
app.include_router(base.router)
app.include_router(users.router)
app.include_router(bookmarks.router)
app.include_router(export.router)
app.include_router(import_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Bookmark Management Service API"}
