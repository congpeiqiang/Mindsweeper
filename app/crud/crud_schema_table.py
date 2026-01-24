"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.schema_table import SchemaTable
from app.schemas.test_to_sql.schema_table import SchemaTableCreate, SchemaTableUpdate


class CRUDSchemaTable(CRUDBase[SchemaTable, SchemaTableCreate, SchemaTableUpdate]):
    def get_by_connection(
        self, db: Session, *, connection_id: int, skip: int = 0, limit: int = 100
    ) -> List[SchemaTable]:
        return (
            db.query(SchemaTable)
            .filter(SchemaTable.connection_id == connection_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name_and_connection(
        self, db: Session, *, table_name: str, connection_id: int
    ) -> Optional[SchemaTable]:
        return (
            db.query(SchemaTable)
            .filter(
                SchemaTable.table_name == table_name,
                SchemaTable.connection_id == connection_id
            )
            .first()
        )


schema_table = CRUDSchemaTable(SchemaTable)
