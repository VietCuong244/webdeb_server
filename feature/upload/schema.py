from uuid import UUID
from pydantic import BaseModel, Field
from fastapi import Form

class PDFUploadRequest(BaseModel):
    novel_title: str = Field(..., description="The title of the novel")
    novel_author: str = Field(..., description="The author of the novel")
    novel_description: str | None = Field(None, description="Optional novel description")
    novel_series: str | None = Field(None, description="Optional series name")
    novel_isprivate: bool = Field(False, description="Whether the novel is private")
    doc_source: str = Field("novel", description="The source of the document")
    tag_ids: list[UUID] = Field(default_factory=list, description="Tag IDs assigned to the novel")

    @classmethod
    def as_form(
        cls,
        novel_title: str = Form(..., description="The title of the novel"),
        novel_author: str = Form(..., description="The author of the novel"),
        novel_description: str | None = Form(None, description="Optional novel description"),
        novel_series: str | None = Form(None, description="Optional series name"),
        novel_isprivate: bool = Form(False, description="Whether the novel is private"),
        doc_source: str = Form("novel", description="The source of the document"),
        
        tag_ids: list[str] = Form(default=[], description="Tag IDs assigned to the novel"),
    ):
        
        parsed_tags = []
        if tag_ids:
            for tag in tag_ids:
                tag = tag.strip()
                if not tag:
                    continue
                if "," in tag:
                    parsed_tags.extend([t.strip() for t in tag.split(",") if t.strip()])
                else:
                    parsed_tags.append(tag)

        return cls(
            novel_title=novel_title,
            novel_author=novel_author,
            novel_description=novel_description,
            novel_series=novel_series,
            novel_isprivate=novel_isprivate,
            doc_source=doc_source,
            

            tag_ids=parsed_tags, 
        )
