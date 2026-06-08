from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from feature.common.response import NovelInfoResponse
from feature.search.schema import ChatSearchRequest, ChatSearchResponse
from models.novel import Novel, Tag
from feature.rag.service import clean_extracted_text, generate_answer, hybrid_search

router_search = APIRouter(prefix="/search", tags=["search"])

@router_search.get("/{query}", response_model=list[NovelInfoResponse])
async def search_novels(query: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Novel).where(Novel.novel_title.ilike(f"%{query}%"))
    result = await db.execute(stmt)
    novels = result.scalars().all()
    
    if not novels:
        stmt = select(Novel).where(Novel.novel_author.ilike(f"%{query}%"))
        result = await db.execute(stmt)
        novels = result.scalars().all()
    
    if not novels:
        raise HTTPException(status_code=404, detail="No novels found matching the query")
    
    response = []
    for novel in novels:
        tag_result = await db.execute(select(Tag).join(Novel.tags).where(Novel.novel_id == novel.novel_id))
        tags = tag_result.scalars().all()
        response.append({
            "novel_id": novel.novel_id,
            "novel_title": novel.novel_title,
            "novel_author": novel.novel_author,
            "novel_description": novel.novel_description,
            "novel_coverurl": novel.novel_coverurl,
            "novel_series": novel.novel_series,
            "tags": tags,
        })

    return response

@router_search.post("/chat", response_model=ChatSearchResponse)
async def chat_search(data: ChatSearchRequest, db: AsyncSession = Depends(get_db)):
    chunks = await hybrid_search(db, data.question, data.limit)
    answer = generate_answer(data.question, chunks)

    return {
        "answer": answer,
        "chunks": [clean_extracted_text(chunk.emb_chunk) for chunk in chunks],
    }
