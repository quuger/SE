from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, base
from app.database import engine, Base
import asyncio

app = FastAPI(
    title="User Authentication API",
    description="A simple authentication API with registration and login endpoints",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"], 
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


@app.get("/")
async def root():
    return {"message": "Welcome to the Authentication API"}
