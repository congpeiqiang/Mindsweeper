# 文档表模型

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.db.base_class import Base


class Document(Base):
    """
    文档表
    
    存储文件处理后的文档分块信息
    """

    # 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="文档ID")
    
    # 外键
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False, comment="文件ID")
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
    
    # 内容
    content = Column(Text, nullable=False, comment="文档内容")
    chunk_index = Column(Integer, nullable=False, comment="分块索引")

    # 元数据
    doc_metadata = Column(JSONB, nullable=True, comment="额外元数据")

    # Milvus关联
    milvus_id = Column(BigInteger, nullable=True, comment="Milvus中的ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 索引
    __table_args__ = (
        Index("idx_documents_file_id", "file_id"),
        Index("idx_documents_kb_id", "kb_id"),
        Index("idx_documents_milvus_id", "milvus_id"),
        Index("idx_documents_kb_file", "kb_id", "file_id"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, file_id={self.file_id}, chunk_index={self.chunk_index})>"

