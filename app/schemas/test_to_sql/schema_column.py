"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class SchemaColumnBase(BaseModel):
    column_name: str
    data_type: str
    description: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False  # 添加唯一标记

# Properties to receive on column creation
class SchemaColumnCreate(SchemaColumnBase):
    table_id: int


# Properties to receive on column update
class SchemaColumnUpdate(BaseModel):
    column_name: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None
    is_primary_key: Optional[bool] = None
    is_foreign_key: Optional[bool] = None
    is_unique: Optional[bool] = None  # 添加唯一标记


# Properties shared by models stored in DB
class SchemaColumnInDBBase(SchemaColumnBase):
    id: int
    table_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class SchemaColumn(SchemaColumnInDBBase):
    pass


# Properties with relationships
class SchemaColumnWithMappings(SchemaColumn):
    value_mappings: List[Any] = []

# Update forward references after all classes are defined
SchemaColumnWithMappings.model_rebuild()
