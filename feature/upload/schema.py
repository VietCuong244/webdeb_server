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
        
        # MẸO 1: Hứng dữ liệu bằng list[str] thay vì list[UUID] để tránh bị FastAPI văng lỗi quá sớm
        tag_ids: list[str] = Form(default=[], description="Tag IDs assigned to the novel"),
    ):
        
        # MẸO 2: Tiền xử lý (Pre-processing) tag_ids trước khi đưa vào BaseModel
        parsed_tags = []
        if tag_ids:
            for tag in tag_ids:
                # Nếu frontend/Swagger gửi nguyên một chuỗi dính liền có dấu phẩy: "uuid1,uuid2"
                if "," in tag:
                    # Cắt chuỗi bằng dấu phẩy và làm sạch khoảng trắng dư thừa
                    parsed_tags.extend([t.strip() for t in tag.split(",") if t.strip()])
                else:
                    # Nếu gửi đúng từng ô, cứ thế đẩy vào
                    parsed_tags.append(tag.strip())

        return cls(
            novel_title=novel_title,
            novel_author=novel_author,
            novel_description=novel_description,
            novel_series=novel_series,
            novel_isprivate=novel_isprivate,
            doc_source=doc_source,
            
            # Pydantic (BaseModel) sẽ tự động nhận mảng parsed_tags (chứa các string sạch),
            # tự động ép kiểu thành list[UUID] an toàn và báo lỗi 422 chuẩn mực nếu UUID sai format!
            tag_ids=parsed_tags, 
        )