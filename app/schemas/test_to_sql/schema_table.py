"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class SchemaTableBase(BaseModel):
    table_name: str
    description: Optional[str] = None
    ui_metadata: Optional[Dict[str, Any]] = None


# Properties to receive on table creation
class SchemaTableCreate(SchemaTableBase):
    connection_id: int


# Properties to receive on table update
class SchemaTableUpdate(BaseModel):
    table_name: Optional[str] = None
    description: Optional[str] = None
    ui_metadata: Optional[Dict[str, Any]] = None


# Properties shared by models stored in DB
class SchemaTableInDBBase(SchemaTableBase):
    id: int
    connection_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class SchemaTable(SchemaTableInDBBase):
    pass


# Properties with relationships
class SchemaTableWithRelationships(SchemaTable):
    columns: List[Any] = []
    relationships: List[Any] = []

# Update forward references after all classes are defined
SchemaTableWithRelationships.model_rebuild()
