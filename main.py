from feature.auth.router import router
import models
from database import SessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio  
from fastapi import FastAPI, APIRouter, Depends 
from database import engine, Base
import models

app = FastAPI()
app.include_router(router)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()
    print("Database initialized!")

@app.get("/")
async def root():
    return {"message": "Hello World"}


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Hello World"}

