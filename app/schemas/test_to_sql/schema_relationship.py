"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# 关系类型常量
RELATIONSHIP_TYPES = {
    "ONE_TO_ONE": "1-to-1",
    "ONE_TO_MANY": "1-to-N",
    "MANY_TO_ONE": "N-to-1",  # 添加多对一关系类型
    "MANY_TO_MANY": "N-to-M"
}

# Shared properties
class SchemaRelationshipBase(BaseModel):
    connection_id: int
    source_table_id: int
    source_column_id: int
    target_table_id: int
    target_column_id: int
    relationship_type: Optional[str] = None
    description: Optional[str] = None

# Properties to receive on relationship creation
class SchemaRelationshipCreate(SchemaRelationshipBase):
    pass


# Properties to receive on relationship update
class SchemaRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    description: Optional[str] = None


# Properties shared by models stored in DB
class SchemaRelationshipInDBBase(SchemaRelationshipBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class SchemaRelationship(SchemaRelationshipInDBBase):
    pass


# Properties with detailed information
class SchemaRelationshipDetailed(SchemaRelationship):
    source_table_name: str
    source_column_name: str
    target_table_name: str
    target_column_name: str
