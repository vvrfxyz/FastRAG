from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    file_path = Column(String(255))
    content_type = Column(String(50))  # e.g., "pdf", "txt"
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联到文档的嵌入
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    text_chunk = Column(Text)  # 被嵌入的文本块
    chunk_index = Column(Integer)  # 文档中文本块的索引
    vector_id = Column(String(255))  # 向量数据库中的ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    document = relationship("Document", back_populates="embeddings")