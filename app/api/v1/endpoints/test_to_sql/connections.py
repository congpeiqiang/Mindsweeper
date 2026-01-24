"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.schemas import DBConnection, DBConnectionCreate, DBConnectionUpdate
from app.api.dependencies import get_db

router = APIRouter()


@router.get("", response_model=List[DBConnection], summary="查询数据库连接信息-summary", description="查询数据库连接信息-description")
def read_connections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all database connections.
    """
    connections = crud.db_connection.get_multi(db, skip=skip, limit=limit)
    return connections


@router.post("", response_model=DBConnection, summary="新增数据库连接信息")
def create_connection(
    *,
    db: Session = Depends(get_db),
    connection_in: DBConnectionCreate,
) -> Any:
    """
    Create new database connection.
    """
    connection = crud.db_connection.create(db=db, obj_in=connection_in)
    return connection

@router.post("/{connection_id}/discover-and-save", response_model=Dict[str, Any], summary="分析数据库表结构")
def discover_and_save_schema(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
) -> Any:
    """
    Discover schema from a database connection and save it to the database.
    """
    from app.services.test_to_sql.schema_service import discover_schema, save_discovered_schema

    connection = crud.db_connection.get(db=db, id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    try:
        # Test the connection first
        from app.services.test_to_sql.db_service import test_db_connection
        test_db_connection(connection)

        # Discover schema
        schema_info = discover_schema(connection)

        # Save discovered schema
        tables_data, relationships_data = save_discovered_schema(db, connection_id, schema_info)

        return {
            "status": "success",
            "message": f"Successfully discovered and saved schema for {connection.name}",
            "tables": tables_data,
            "relationships": relationships_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering and saving schema: {str(e)}")


@router.get("/{connection_id}", response_model=DBConnection, summary="根据ID, 查询数据库连接信息")
def read_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
) -> Any:
    """
    Get database connection by ID.
    """
    connection = crud.db_connection.get(db=db, id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection


@router.put("/{connection_id}", response_model=DBConnection, summary="更新数据库连接信息")
def update_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
    connection_in: DBConnectionUpdate,
) -> Any:
    """
    Update a database connection.
    """
    connection = crud.db_connection.get(db=db, id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection = crud.db_connection.update(db=db, db_obj=connection, obj_in=connection_in)
    return connection


@router.delete("/{connection_id}", response_model=DBConnection, summary="删除数据库连接信息")
def delete_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
) -> Any:
    """
    Delete a database connection.
    """
    connection = crud.db_connection.get(db=db, id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection = crud.db_connection.remove(db=db, id=connection_id)
    return connection


@router.post("/{connection_id}/test", response_model=dict, summary="测试数据库连接")
def test_connection(
    *,
    db: Session = Depends(get_db),
    connection_id: int,
) -> Any:
    """
    Test a database connection.
    """
    connection = crud.db_connection.get(db=db, id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Test the connection
    try:
        # Implement connection testing logic
        from app.services.test_to_sql.db_service import test_db_connection
        test_db_connection(connection)
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
