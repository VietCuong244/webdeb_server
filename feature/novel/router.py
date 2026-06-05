from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from feature.novel.schema import NovelBase
from feature.user.service import require_novel_owner_or_admin
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import Document
from models.novel import Novel, Tag
from uuid import UUID
from feature.common.response import MessageResponse, NovelContentResponse, NovelInfoResponse, NovelListItemResponse, NovelUpdateResponse

router_novel = APIRouter(prefix="/novel", tags=["novel"])


@router_novel.get("/", response_model=list[NovelListItemResponse])
async def novel_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Novel).order_by(Novel.novel_updatedat.desc()))
    novels = result.scalars().all()
    return novels


@router_novel.get("/tag/{tag_id}", response_model=list[NovelListItemResponse])
async def get_novels_by_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Novel).join(Novel.tags).where(Tag.tag_id == tag_id).order_by(Novel.novel_updatedat.desc()))
    novels = result.scalars().all()
    return novels


@router_novel.get("/info/{novel_id}", response_model=NovelInfoResponse)
async def get_novel_info(novel_id: UUID, db: AsyncSession = Depends(get_db)):
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    tags = await db.execute(select(Tag).join(Novel.tags).where(Novel.novel_id == novel_id))
    tags = tags.scalars().all()
    return {
        "novel_id": novel.novel_id,
        "novel_title": novel.novel_title,
        "novel_author": novel.novel_author,
        "novel_description": novel.novel_description,
        "novel_coverurl": novel.novel_coverurl,
        "novel_series": novel.novel_series,
        "tags": tags,
    }
    
    
@router_novel.get("/content/{novel_id}", response_model=NovelContentResponse)
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
        "novel_description": novel.novel_description,
        "novel_coverurl": novel.novel_coverurl,
        "novel_series": novel.novel_series,
        "document":
            {
                "doc_id": doc.doc_id,
                "doc_title": doc.doc_title,
                "doc_fileurl": doc.doc_fileurl,
                "doc_markdownurl": doc.doc_markdownurl,
                "doc_status": doc.doc_status,
                "doc_error": doc.doc_error,
            }
            if doc else None
    }
    
    
@router_novel.delete("/{novel_id}", response_model=MessageResponse)
async def delete_novel(novel_id: UUID, current_user = Depends(require_novel_owner_or_admin), db: AsyncSession = Depends(get_db)):
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found") 
    
    await db.delete(novel)
    await db.commit()
    return {"message": "Novel deleted successfully"}


@router_novel.put("/{novel_id}", response_model=NovelUpdateResponse)
async def update_novel(novel_id: UUID, novel_data: NovelBase, current_user = Depends(require_novel_owner_or_admin), db: AsyncSession = Depends(get_db)):
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    
    
    novel.novel_title = novel_data.novel_title if novel_data.novel_title is not None else novel.novel_title
    novel.novel_author = novel_data.novel_author if novel_data.novel_author is not None else novel.novel_author
    novel.novel_description = novel_data.novel_description if novel_data.novel_description is not None else novel.novel_description
    novel.novel_coverurl = novel_data.novel_coverurl if novel_data.novel_coverurl is not None else novel.novel_coverurl
    novel.novel_series = novel_data.novel_series if novel_data.novel_series is not None else novel.novel_series
    novel.novel_isprivate = novel_data.novel_isprivate if novel_data.novel_isprivate is not None else novel.novel_isprivate
    
    if novel_data.tags is not None:
        tag_result = await db.execute(
            select(Tag).where(Tag.tag_id.in_(novel_data.tags))
        )
        new_tags = tag_result.scalars().all()
        novel.tags = new_tags
    
     
    
    await db.commit()
    await db.refresh(novel)
    
    return {
        "message": "Novel updated successfully",
        "novel": novel,
    }
