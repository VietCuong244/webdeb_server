from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from feature.search.schema import ChatSearchRequest, ChatSearchResponse, SearchNovelResponse
from feature.search.service import ai_search_novels, search_novels_by_text

router_search = APIRouter(prefix="/search", tags=["search"])

@router_search.get("/{query}", response_model=list[SearchNovelResponse])
async def search_novels(query: str, db: AsyncSession = Depends(get_db)):
    novels = await search_novels_by_text(db, query)
    if not novels:
        raise HTTPException(status_code=404, detail="No novels found matching the query")
    return novels

@router_search.post("/chat", response_model=ChatSearchResponse)
async def ai_search(data: ChatSearchRequest, db: AsyncSession = Depends(get_db)):
    extracted_query, novels, chunk_texts = await ai_search_novels(
        db,
        data.question,
        data.limit,
        data.top_k,
    )
    if not novels:
        raise HTTPException(status_code=404, detail="No novels found matching the AI search query")

    return {
        "query": data.question,
        "extracted_query": extracted_query,
        "novels": novels,
        "chunks": chunk_texts,
    }
