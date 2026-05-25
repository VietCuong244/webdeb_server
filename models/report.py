from database import Base
from sqlalchemy import Column, String, CheckConstraint, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


class Report(Base):
    __tablename__ = "reports"  
     
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_novel_id = Column(UUID(as_uuid=True), ForeignKey("novels.novel_id"), nullable=False)
    report_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    report_type = Column(String, nullable=False)
    report_reason = Column(String, nullable=False)
    report_status = Column(String, nullable=False, default="pending")  # pending, resolved, rejected
    report_comment = Column(String, nullable=True)
    
    report_createdat = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    
    novel = relationship("Novel", back_populates="reports")
    user = relationship("User", back_populates="reports")

    __table_args__ = (
        CheckConstraint("report_type IN ('novel', 'user', 'other')", name="check_report_type"),
        CheckConstraint("report_status IN ('pending', 'resolved', 'rejected')", name="check_report_status"),
    )   
    