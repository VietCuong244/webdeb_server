from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SearchNovelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    novel_id: UUID
    novel_title: str
    novel_author: str
    novel_description: str | None = None
    novel_coverurl: str | None = None
    novel_series: str | None = None


class ChatSearchRequest(BaseModel):
    question: str
    limit: int = Field(default=10, ge=1, le=50)
    top_k: int = Field(default=8, ge=1, le=20)


class ChatSearchResponse(BaseModel):
    query: str
    extracted_query: str
    novels: list[SearchNovelResponse]
    chunks: list[str]
