"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SchemaTable(Base):
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("dbconnection.id"), nullable=False)
    table_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ui_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    connection = relationship("DBConnection", back_populates="tables")
    columns = relationship("SchemaColumn", back_populates="table", cascade="all, delete-orphan")
    source_relationships = relationship("SchemaRelationship", 
                                       foreign_keys="[SchemaRelationship.source_table_id]",
                                       back_populates="source_table")
    target_relationships = relationship("SchemaRelationship", 
                                       foreign_keys="[SchemaRelationship.target_table_id]",
                                       back_populates="target_table")
