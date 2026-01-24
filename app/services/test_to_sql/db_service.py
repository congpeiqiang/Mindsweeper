"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import urllib.parse
from typing import Dict, Any, List, Optional

import sqlalchemy
from sqlalchemy import create_engine

from app.models.db_connection import DBConnection


def get_db_engine(connection: DBConnection, password: str = None):
    """
    Create a SQLAlchemy engine for the given database connection.
    """
    try:
        # 直接使用明文密码，不进行加密/解密处理
        # 在实际应用中，应该对密码进行适当的加密和解密

        # 如果是从配置文件读取的连接信息
        if hasattr(connection, 'password') and connection.password:
            actual_password = connection.password
        # 如果是从数据库读取的连接信息
        elif password:
            actual_password = password
        # 如果是使用已加密的密码
        else:
            # 这里我们假设password_encrypted存储的是明文密码
            # 在实际应用中，应该进行解密
            actual_password = connection.password_encrypted

        # Encode password for URL safety
        encoded_password = urllib.parse.quote_plus(actual_password)

        if connection.db_type.lower() == "mysql":
            conn_str = (
                f"mysql+pymysql://{connection.username}:"
                f"{encoded_password}@"
                f"{connection.host}:{connection.port}/{connection.database_name}"
            )
            print(f"Connecting to MySQL database: {connection.host}:{connection.port}/{connection.database_name}")
            return create_engine(conn_str)

        elif connection.db_type.lower() == "postgresql":
            conn_str = (
                f"postgresql://{connection.username}:"
                f"{encoded_password}@"
                f"{connection.host}:{connection.port}/{connection.database_name}"
            )
            print(f"Connecting to PostgreSQL database: {connection.host}:{connection.port}/{connection.database_name}")
            return create_engine(conn_str)

        elif connection.db_type.lower() == "sqlite":
            # For SQLite, the database_name is treated as the file path
            conn_str = f"sqlite:///{connection.database_name}"
            print(f"Connecting to SQLite database: {connection.database_name}")
            return create_engine(conn_str)

        else:
            raise ValueError(f"Unsupported database type: {connection.db_type}")
    except Exception as e:
        print(f"Error creating database engine: {str(e)}")
        raise

def test_db_connection(connection: DBConnection) -> bool:
    """
    Test if a database connection is valid.
    """
    try:
        print(f"Testing connection to {connection.db_type} database at {connection.host}:{connection.port}/{connection.database_name}")
        engine = get_db_engine(connection)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print(f"Connection test successful: {result.fetchone()}")
        return True
    except Exception as e:
        error_msg = f"Connection test failed: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

def execute_query(connection: DBConnection, query: str) -> List[Dict[str, Any]]:
    """
    Execute a SQL query on the target database and return the results.
    """
    try:
        engine = get_db_engine(connection)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        raise Exception(f"Query execution failed: {str(e)}")

def get_db_connection_by_id(connection_id: int) -> Optional[DBConnection]:
    """
    根据连接ID获取数据库连接对象
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        connection = db.query(DBConnection).filter(DBConnection.id == connection_id).first()
        return connection
    finally:
        db.close()


def execute_query_with_connection(connection: DBConnection, query: str) -> List[Dict[str, Any]]:
    """
    使用指定的数据库连接执行查询
    """
    return execute_query(connection, query)
