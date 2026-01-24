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
class DBConnectionBase(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    username: str
    database_name: str


# Properties to receive on connection creation
class DBConnectionCreate(DBConnectionBase):
    password: str


# Properties to receive on connection update
class DBConnectionUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None


# Properties shared by models stored in DB
class DBConnectionInDBBase(DBConnectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class DBConnection(DBConnectionInDBBase):
    pass


# Properties stored in DB
class DBConnectionInDB(DBConnectionInDBBase):
    password_encrypted: str
