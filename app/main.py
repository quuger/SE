from fastapi import FastAPI
from app.routes import users, base
from app.database import engine, Base
import asyncio

app = FastAPI(
    title="User Authentication API",
    description="A simple authentication API with registration and login endpoints",
    version="1.0.0",
)


# Create tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Include routers
app.include_router(base.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Authentication API"}
