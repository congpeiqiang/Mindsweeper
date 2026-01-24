"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SchemaColumn(Base):
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("schematable.id"), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)  # 添加唯一标记
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    table = relationship("SchemaTable", back_populates="columns")
    value_mappings = relationship("ValueMapping", back_populates="column", cascade="all, delete-orphan")
    source_relationships = relationship("SchemaRelationship",
                                       foreign_keys="[SchemaRelationship.source_column_id]",
                                       back_populates="source_column")
    target_relationships = relationship("SchemaRelationship",
                                       foreign_keys="[SchemaRelationship.target_column_id]",
                                       back_populates="target_column")
