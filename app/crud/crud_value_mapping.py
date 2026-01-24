"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.value_mapping import ValueMapping
from app.schemas.test_to_sql.value_mapping import ValueMappingCreate, ValueMappingUpdate

# fmt: off  MC8yOmFIVnBZMlhrdUp2bG43bmx2TG82WkVoNlZRPT06ZmE5MjRmOWU=

class CRUDValueMapping(CRUDBase[ValueMapping, ValueMappingCreate, ValueMappingUpdate]):
    def get_by_column(
        self, db: Session, *, column_id: int, skip: int = 0, limit: int = 100
    ) -> List[ValueMapping]:
        return (
            db.query(ValueMapping)
            .filter(ValueMapping.column_id == column_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
# pylint: disable  MS8yOmFIVnBZMlhrdUp2bG43bmx2TG82WkVoNlZRPT06ZmE5MjRmOWU=

    def get_by_column_and_term(
        self, db: Session, *, column_id: int, nl_term: str
    ) -> Optional[ValueMapping]:
        return (
            db.query(ValueMapping)
            .filter(
                ValueMapping.column_id == column_id,
                ValueMapping.nl_term == nl_term
            )
            .first()
        )


value_mapping = CRUDValueMapping(ValueMapping)
