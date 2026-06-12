from uuid import UUID

from pydantic import BaseModel, Field


class ChatbotRequest(BaseModel):
    novel_id: UUID
    question: str
    history: list[str] = Field(default_factory=list)
    top_k: int = Field(default=8, ge=1, le=20)


class ChatbotResponse(BaseModel):
    novel_id: UUID
    novel_title: str
    answer: str
    chunks: list[str]
