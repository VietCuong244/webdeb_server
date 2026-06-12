from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from feature.rag.service import generate_answer_async, hybrid_search
from models.document import Document, Embedding
from models.novel import Novel


async def get_document_ids_by_novel(db: AsyncSession, novel_id: UUID) -> list[UUID]:
    result = await db.execute(
        select(Document.doc_id).where(Document.doc_novel_id == novel_id)
    )
    return list(result.scalars().all())


async def chat_with_novel(
    db: AsyncSession,
    novel_id: UUID,
    question: str,
    history: list[str],
    top_k: int,
) -> tuple[Novel, str, list[Embedding]]:
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    document_ids = await get_document_ids_by_novel(db, novel_id)
    if not document_ids:
        raise HTTPException(status_code=404, detail="No document found for this novel")

    chunks = await hybrid_search(db, question, top_k, doc_ids=document_ids)
    answer = await generate_answer_async(question, chunks, history)

    return novel, answer, chunks
