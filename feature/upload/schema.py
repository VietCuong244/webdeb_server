from pydantic import BaseModel, Field
from fastapi import Form

class PDFUploadRequest(BaseModel):
    novel_title: str = Field(..., description="The title of the novel")
    novel_author: str = Field(..., description="The author of the novel")
    novel_descriptionurl: str | None = Field(None, description="Optional URL for the novel description")
    novel_series: str | None = Field(None, description="Optional series name")
    novel_isprivate: bool = Field(False, description="Whether the novel is private")
    doc_source: str = Field("novel", description="The source of the document")

    @classmethod
    def as_form(
        cls,
        novel_title: str = Form(..., description="The title of the novel"),
        novel_author: str = Form(..., description="The author of the novel"),
        novel_descriptionurl: str | None = Form(None, description="Optional URL for the novel description"),
        novel_series: str | None = Form(None, description="Optional series name"),
        novel_isprivate: bool = Form(False, description="Whether the novel is private"),
        doc_source: str = Form("novel", description="The source of the document"),
    ):
        return cls(
            novel_title=novel_title,
            novel_author=novel_author,
            novel_descriptionurl=novel_descriptionurl,
            novel_series=novel_series,
            novel_isprivate=novel_isprivate,
            doc_source=doc_source,
        )
