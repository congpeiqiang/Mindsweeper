"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class ValueMappingBase(BaseModel):
    nl_term: str
    db_value: str

# Properties to receive on mapping creation
class ValueMappingCreate(ValueMappingBase):
    column_id: int


# Properties to receive on mapping update
class ValueMappingUpdate(BaseModel):
    nl_term: Optional[str] = None
    db_value: Optional[str] = None

# Properties shared by models stored in DB
class ValueMappingInDBBase(ValueMappingBase):
    id: int
    column_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class ValueMapping(ValueMappingInDBBase):
    pass
