from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Computed, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"
    doc_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_title     = Column(String, nullable=False)
    doc_source    = Column(String, nullable=True)   # "novel" | "upload"
    doc_content   = Column(Text, nullable=False)
    doc_fts       = Column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('simple', coalesce(doc_title, '')), 'A') || "
            "setweight(to_tsvector('simple', coalesce(doc_content, '')), 'B')",
            persisted=True,
        ),
    )
    doc_createdat = Column(DateTime(timezone=True), server_default=text("now()"))

    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_doc_fts", "doc_fts", postgresql_using="gin"),
    )

class Embedding(Base):
    __tablename__ = "embeddings"
    emb_id     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id     = Column(UUID(as_uuid=True), ForeignKey("documents.doc_id"), nullable=False)
    emb_vector = Column(Vector(768))
    emb_chunk  = Column(Text, nullable=False)

    document = relationship("Document", back_populates="embeddings")
