"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# fmt: off  MC8yOmFIVnBZMlhrdUp2bG43bmx2TG82TUcxU1dRPT06NjlmMzllZjA=

from app.db.base_class import Base


class SchemaRelationship(Base):
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("dbconnection.id"), nullable=False)
    source_table_id = Column(Integer, ForeignKey("schematable.id"), nullable=False)
    source_column_id = Column(Integer, ForeignKey("schemacolumn.id"), nullable=False)
    target_table_id = Column(Integer, ForeignKey("schematable.id"), nullable=False)
    target_column_id = Column(Integer, ForeignKey("schemacolumn.id"), nullable=False)
    relationship_type = Column(String(50), nullable=True)  # e.g., '1-to-1', '1-to-N', 'N-to-M'
    description = Column(Text, nullable=True)  # 关系描述
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    connection = relationship("DBConnection")
    source_table = relationship("SchemaTable", foreign_keys=[source_table_id], back_populates="source_relationships")
    source_column = relationship("SchemaColumn", foreign_keys=[source_column_id], back_populates="source_relationships")
    target_table = relationship("SchemaTable", foreign_keys=[target_table_id], back_populates="target_relationships")
    target_column = relationship("SchemaColumn", foreign_keys=[target_column_id], back_populates="target_relationships")
