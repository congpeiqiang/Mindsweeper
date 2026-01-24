# 应用配置

import os
import threading
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

class Settings(BaseSettings):
    """
    应用配置类

    从 YAML 文件加载所有配置参数，支持环境变量覆盖
    """

    # Pydantic v2 配置
    # 获取项目根目录（config 目录的父目录）
    _config_file = Path(__file__).parent.parent / "config.yaml"

    model_config = SettingsConfigDict(
        yaml_file=str(_config_file),
        case_sensitive=True,
        extra="ignore"  # 忽略 YAML 中的额外字段
    )

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库URL"""
        return self.database.url

    @property
    def MILVUS_HOST(self) -> str:
        """获取Milvus主机地址"""
        return self.milvus.host

    @property
    def CORS_ORIGINS_LIST(self) -> list:
        """
        获取CORS允许的源列表

        Returns:
            list: 源列表
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def ALLOWED_HOSTS_LIST(self) -> list:
        """
        获取允许的主机列表

        Returns:
            list: 主机列表
        """
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @property
    def ALLOWED_EXTENSIONS_LIST(self) -> list:
        """
        获取允许的文件扩展名列表

        Returns:
            list: 扩展名列表
        """
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def MILVUS_URI(self) -> str:
        """
        获取Milvus连接URI

        Returns:
            str: Milvus连接字符串
        """
        return f"http://{self.MILVUS_HOST}:{self.MILVUS_PORT}"


# ==================== 单例模式实现 ====================

class SettingsSingleton:
    """
    Settings单例管理器

    使用线程安全的双重检查锁定（Double-Checked Locking）模式
    确保在多线程环境下只创建一个Settings实例
    """

    _instance: Optional[Settings] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> Settings:
        """
        获取Settings单例实例

        使用双重检查锁定模式确保线程安全：
        1. 第一次检查：无锁检查，提高性能
        2. 获取锁：确保线程安全
        3. 第二次检查：有锁检查，防止竞态条件
        4. 创建实例：只在第一次调用时创建

        Returns:
            Settings: 全局唯一的Settings实例

        Example:
            settings = SettingsSingleton.get_instance()
            print(settings.APP_NAME)
        """
        # 第一次检查（无锁）- 提高性能
        if cls._instance is None:
            # 获取锁
            with cls._lock:
                # 第二次检查（有锁）- 防止竞态条件
                if cls._instance is None:
                    cls._instance = Settings()

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        重置单例实例

        仅用于测试环境，生产环境不应调用此方法

        Example:
            SettingsSingleton.reset()  # 用于单元测试
        """
        with cls._lock:
            cls._instance = None


def get_settings() -> Settings:
    """
    获取应用配置实例（单例模式）

    这是推荐的获取Settings实例的方式，用于FastAPI依赖注入

    Returns:
        Settings: 全局唯一的Settings实例

    Example:
        from config.settings import get_settings
        from fastapi import Depends

        @app.get("/config/")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"app_name": settings.APP_NAME}
    """
    return SettingsSingleton.get_instance()


# 导出全局配置实例
settings = get_settings()
