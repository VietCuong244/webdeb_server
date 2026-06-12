import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from feature.rag.service import clean_extracted_text, gemini_client, hybrid_search, CHAT_MODEL
from models.novel import Novel


async def search_novels_by_text(db: AsyncSession, query: str, limit: int | None = None) -> list[Novel]:
    title_stmt = select(Novel).where(Novel.novel_title.ilike(f"%{query}%"))
    if limit is not None:
        title_stmt = title_stmt.limit(limit)

    result = await db.execute(title_stmt)
    novels = result.scalars().all()

    if novels:
        return novels

    author_stmt = select(Novel).where(Novel.novel_author.ilike(f"%{query}%"))
    if limit is not None:
        author_stmt = author_stmt.limit(limit)

    result = await db.execute(author_stmt)
    return result.scalars().all()


def extract_search_query(question: str, chunk_texts: list[str]) -> str:
    context = "\n\n---\n\n".join(chunk_texts)
    prompt = f"""
You are a search query extractor for a novel library.

The user is trying to find a novel. Use the retrieved CONTEXT to infer the most likely novel title.
Return only one short search query, preferably the exact novel title.
If the title is unclear, return the best distinctive keyword, character name, faction name, or author-like phrase.
Do not explain.
Do not use quotes.

USER QUESTION:
{question}

RETRIEVED CONTEXT:
{context}
"""

    response = gemini_client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
    )
    return response.text.strip().strip('"').strip("'")


async def extract_search_query_async(question: str, chunk_texts: list[str]) -> str:
    return await asyncio.to_thread(extract_search_query, question, chunk_texts)


async def ai_search_novels(db: AsyncSession, question: str, limit: int = 10, top_k: int = 8):
    chunks = await hybrid_search(db, question, top_k)
    chunk_texts = [clean_extracted_text(chunk.emb_chunk) for chunk in chunks]
    extracted_query = await extract_search_query_async(question, chunk_texts)

    novels = await search_novels_by_text(db, extracted_query, limit)

    return extracted_query, novels, chunk_texts
