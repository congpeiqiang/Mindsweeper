"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import logging
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created")


def create_initial_data(db: Session) -> None:
    # Check if we already have connections
    connection = crud.db_connection.get_by_name(db, name="Sample Database")
    if not connection:
        connection_in = schemas.DBConnectionCreate(
            name="chatdb",
            db_type="mysql",
            host="47.120.44.223",
            port=3306,
            username="root",
            password="MySecure@123",
            database_name="chatdb"
        )
        connection = crud.db_connection.create(db=db, obj_in=connection_in)
        logger.info(f"Created sample connection: {connection.name}")


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        init_db(db)
        create_initial_data(db)
    finally:
        db.close()
