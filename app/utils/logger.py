# 日志配置

import logging
import sys
import os
from typing import Optional


class LoggerManager:
    """
    日志管理器

    提供统一的日志配置和管理接口
    """

    _instance: Optional[logging.Logger] = None
    _configured: bool = False

    @classmethod
    def setup_logging(cls, settings) -> logging.Logger:
        """
        配置应用日志

        Args:
            settings: 应用配置实例

        Returns:
            logging.Logger: 配置后的日志记录器

        Example:
            from config.settings import get_settings
            from app.utils.logger import LoggerManager

            settings = get_settings()
            logger = LoggerManager.setup_logging(settings)
            logger.info("应用启动")
        """
        if cls._configured:
            return cls._instance

        # 创建日志目录
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 配置日志格式
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )

        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format=log_format,
            handlers=[
                logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout),
            ],
        )

        # 获取应用日志记录器
        logger = logging.getLogger(__name__)
        cls._instance = logger
        cls._configured = True

        return logger

    @classmethod
    def get_logger(cls, name: str = __name__) -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称，默认为当前模块名

        Returns:
            logging.Logger: 日志记录器实例

        Example:
            from app.utils.logger import LoggerManager

            logger = LoggerManager.get_logger(__name__)
            logger.info("这是一条日志")
        """
        if not cls._configured:
            raise RuntimeError("日志系统未初始化，请先调用 setup_logging()")

        return logging.getLogger(name)

    @classmethod
    def reset(cls) -> None:
        """
        重置日志配置

        仅用于测试环境
        """
        cls._instance = None
        cls._configured = False


def setup_logging(settings) -> logging.Logger:
    """
    配置应用日志（便捷函数）

    Args:
        settings: 应用配置实例

    Returns:
        logging.Logger: 配置后的日志记录器
    """
    return LoggerManager.setup_logging(settings)


def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器（便捷函数）

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return LoggerManager.get_logger(name)
