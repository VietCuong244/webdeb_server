from pydantic import BaseModel


class ChatSearchRequest(BaseModel):
    question: str
    limit: int = 8


class ChatSearchResponse(BaseModel):
    answer: str
    chunks: list[str]