"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.test_to_sql.schema_relationship import RELATIONSHIP_TYPES

router = APIRouter()


@router.get("/", response_model=Dict[str, Dict[str, str]])
def get_relationship_tips(
    *,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取关系类型的提示信息
    """
    try:
        # 为每种关系类型提供提示信息
        relationship_tips = {
            RELATIONSHIP_TYPES["ONE_TO_ONE"]: {
                "title": "一对一关系 (1:1)",
                "description": "每个源记录对应一个目标记录，反之亦然。例如：一个人只能有一个身份证号，一个身份证号只能属于一个人。",
                "example": "Person.id → IDCard.person_id",
                "when_to_use": "当两个实体之间存在唯一对应关系时使用。"
            },
            RELATIONSHIP_TYPES["ONE_TO_MANY"]: {
                "title": "一对多关系 (1:N)",
                "description": "一个源记录可以对应多个目标记录，但每个目标记录只对应一个源记录。例如：一个部门有多个员工，但每个员工只属于一个部门。",
                "example": "Department.id → Employee.department_id",
                "when_to_use": "当父表中的一条记录对应子表中的多条记录时使用。"
            },
            RELATIONSHIP_TYPES["MANY_TO_ONE"]: {
                "title": "多对一关系 (N:1)",
                "description": "多个源记录对应同一个目标记录，但每个源记录只对应一个目标记录。例如：多个订单可能属于同一个客户，但每个订单只属于一个客户。",
                "example": "Order.customer_id → Customer.id",
                "when_to_use": "当子表中的多条记录引用父表中的同一条记录时使用。"
            },
            RELATIONSHIP_TYPES["MANY_TO_MANY"]: {
                "title": "多对多关系 (N:M)",
                "description": "一个源记录可以对应多个目标记录，一个目标记录也可以对应多个源记录。例如：一个学生可以选修多门课程，一门课程也可以被多个学生选修。",
                "example": "通过关联表实现：Student ↔ StudentCourse ↔ Course",
                "when_to_use": "当两个实体之间存在多对多的关联关系时使用，通常需要通过关联表实现。"
            }
        }
        
        return relationship_tips
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关系类型提示信息失败: {str(e)}")
