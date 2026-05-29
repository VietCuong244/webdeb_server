from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from feature.user.service import require_admin
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import Document
from models.novel import Novel, Tag
from models.user import User
from uuid import UUID

router_novel = APIRouter(prefix="/novel", tags=["novel"])


@router_novel.get("/")
async def novel_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Novel).order_by(Novel.novel_createdat.desc()))
    novels = result.scalars().all()
    return novels


@router_novel.get("/tag/{tag_id}")
async def get_novels_by_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Novel).join(Novel.tags).where(Tag.tag_id == tag_id).order_by(Novel.novel_updatedat.desc()))
    novels = result.scalars().all()
    return novels


@router_novel.get("/info/{novel_id}")
async def get_novel_info(novel_id: UUID, db: AsyncSession = Depends(get_db)):
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return {"novel_title": novel.novel_title,
            "novel_author": novel.novel_author,
            "novel_descriptionurl": novel.novel_descriptionurl,
            "novel_coverurl": novel.novel_coverurl,
            "novel_series": novel.novel_series,}
    
    
@router_novel.get("/{novel_id}")
async def get_novel_by_id(novel_id: UUID, db: AsyncSession = Depends(get_db)):
    result  = await db.execute(select(Novel).where(Novel.novel_id == novel_id))
    novel = result.scalar_one_or_none()
    docresult  = await db.execute(select(Document).where(Document.doc_novel_id == novel_id))
    doc = docresult.scalars().one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return {
        "novel_id": novel.novel_id,
        "novel_title": novel.novel_title,
        "novel_author": novel.novel_author,
        "novel_descriptionurl": novel.novel_descriptionurl,
        "novel_coverurl": novel.novel_coverurl,
        "novel_series": novel.novel_series,
        "documents": 
            {
                "document_id": doc.doc_id,
                "document_title": doc.doc_title,
                "document_data": doc.doc_markdownurl,
                "document_fileurl": doc.doc_fileurl
            }
            if doc else None
    }

