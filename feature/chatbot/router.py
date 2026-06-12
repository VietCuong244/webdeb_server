from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from feature.chatbot.schema import ChatbotRequest, ChatbotResponse
from feature.chatbot.service import chat_with_novel
from feature.rag.service import clean_extracted_text

router_chatbot = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router_chatbot.post("/novel", response_model=ChatbotResponse)
async def chatbot_by_novel(data: ChatbotRequest, db: AsyncSession = Depends(get_db)):
    novel, answer, chunks = await chat_with_novel(
        db=db,
        novel_id=data.novel_id,
        question=data.question,
        history=data.history,
        top_k=data.top_k,
    )

    return {
        "novel_id": novel.novel_id,
        "novel_title": novel.novel_title,
        "answer": answer,
        "chunks": [clean_extracted_text(chunk.emb_chunk) for chunk in chunks],
    }
