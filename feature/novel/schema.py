from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class NovelBase(BaseModel):
    novel_title: Optional[str] = None
    novel_author: Optional[str] = None
    novel_description: Optional[str] = None
    novel_coverurl: Optional[str] = None
    novel_series: Optional[str] = None
    novel_isprivate: Optional[bool] = None
    tags: list[UUID] | None = None
