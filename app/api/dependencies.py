# 依赖注入
from functools import lru_cache
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import get_settings as get_settings_instance, DynamicSettings as Settings
# 获取配置
from app.config.settings import settings

from urllib.parse import quote_plus
from app.config.settings import settings
encoded_password = quote_plus(settings.MYSQL_PASSWORD)
# MySQL connection string
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{encoded_password}@"
    f"{settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==================== 依赖注入函数 ====================

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    用于FastAPI依赖注入，确保每个请求都有独立的数据库会话

    Yields:
        Session: SQLAlchemy数据库会话

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置

    使用LRU缓存避免重复创建配置实例

    Returns:
        Settings: 应用配置实例

    Example:
        @app.get("/config/")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"app_name": settings.APP_NAME}
    """
    return get_settings_instance()
