from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.novel import Novel

router_search = APIRouter(prefix="/search", tags=["search"])
