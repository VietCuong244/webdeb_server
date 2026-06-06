from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AuthRegisterResponse(BaseModel):
    message: str
    user_name: str
    user_email: str
    user_id: UUID
    user_role: str | None = None


class RootAdminResponse(BaseModel):
    message: str
    user_name: str | None = None
    user_email: str | None = None
    user_id: UUID | None = None


class UserMeResponse(ORMModel):
    user_id: UUID
    user_name: str
    user_email: str
    user_role: str


class UserAvatarResponse(BaseModel):
    user_name: str
    user_avatar: str | None = None


class NovelListItemResponse(ORMModel):
    novel_id: UUID
    novel_title: str
    novel_author: str
    novel_description: str | None = None
    novel_coverurl: str | None = None
    novel_series: str | None = None
    novel_isprivate: bool = False
    novel_views: int = 0
    novel_downloads: int = 0
    novel_updatedat: datetime | None = None


class TagResponse(ORMModel):
    tag_id: UUID
    tag_name: str
    tag_description: str | None = None
    tag_isactive: bool = True


class TagListResponse(BaseModel):
    tags: list[TagResponse] = Field(default_factory=list)


class TagActionResponse(BaseModel):
    message: str
    tag: TagResponse


class UserProfileResponse(UserMeResponse):
    user_novels: list[NovelListItemResponse] = Field(default_factory=list)


class DocumentResponse(ORMModel):
    doc_id: UUID
    doc_title: str
    doc_fileurl: str | None = None
    doc_markdownurl: str | None = None
    doc_status: str
    doc_error: str | None = None


class NovelInfoResponse(ORMModel):
    novel_id: UUID
    novel_title: str
    novel_author: str
    novel_description: str | None = None
    novel_coverurl: str | None = None
    novel_series: str | None = None
    tags: list[TagResponse] = Field(default_factory=list)


class NovelContentResponse(NovelListItemResponse):
    document: DocumentResponse | None = None


class NovelUpdateResponse(BaseModel):
    message: str
    novel: NovelListItemResponse


class UploadStartResponse(BaseModel):
    message: str
    status: str
    novel_id: UUID
    novel_title: str | None = None
    novel_coverurl: str | None = None
    document_id: UUID
    doc_title: str | None = None
    doc_fileurl: str
    doc_markdownurl: str
    tag_ids: list[UUID] = Field(default_factory=list)


class DocumentStatusResponse(BaseModel):
    document_id: UUID
    status: str
    error: str | None = None
    markdown_url: str | None = None
    can_update_information: bool = False


class UploadUpdateResponse(BaseModel):
    message: str
    novel_id: UUID
    novel_title: str
    novel_author: str
    novel_description: str | None = None
    novel_coverurl: str | None = None
    novel_series: str | None = None
    novel_isprivate: bool = False
    document_id: UUID
    doc_title: str
    tags: list[TagResponse] = Field(default_factory=list)


class ReportResponse(ORMModel):
    report_id: UUID
    report_novel_id: UUID
    report_user_id: UUID
    report_type: str
    report_reason: str
    report_status: str
    report_comment: str | None = None
    report_createdat: datetime | None = None


class ReportCreateResponse(BaseModel):
    message: str
    report_id: UUID


class ReportUpdateResponse(BaseModel):
    message: str
    report: ReportResponse
