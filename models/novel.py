from database import Base
from sqlalchemy import Column, Integer, String, Boolean,  DateTime, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

class Novel(Base):
    __tablename__ = "novels"
    novel_id = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    novel_title = Column(String, nullable=False)
    novel_author = Column(String,nullable=False)
    novel_user = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    novel_descriptionurl = Column(String, nullable=True)
    novel_coverurl = Column(String, nullable=True)
    novel_series = Column(String, nullable=True)
    
    novel_views = Column(Integer, nullable=False, default=0)
    novel_downloads = Column(Integer, nullable=False, default=0)
    
    novel_isprivate = Column(Boolean, nullable=False, default=False)
    novel_createdat = Column(Integer, nullable=True)
    novel_updatedat = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc))

    uploader = relationship("User", back_populates="novels")
    tags = relationship("Tag", secondary="noveltotags", back_populates="novels")
    reports = relationship("Report", back_populates="novel", cascade="all, delete-orphan")
    
    
class Tag(Base):
    __tablename__ = "tags"
    tag_id = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    tag_name = Column(String, nullable=False, unique=True)
    tag_description = Column(String, nullable=True)
    tag_isactive = Column(Boolean, nullable=False, default=True)

    novels = relationship("Novel", secondary="noveltotags", back_populates="tags")
    
    
class NoveltoTags(Base):
    __tablename__ = "noveltotags"
    novel_id = Column(UUID(as_uuid=True), ForeignKey("novels.novel_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.tag_id", ondelete="CASCADE"), nullable=False,primary_key=True)