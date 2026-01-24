#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 14:37
# @Author  : CongPeiQiang
# @File    : mongodb_factory.py
# @Software: PyCharm
# mongodb_factory.py
from typing import Dict, Optional
from threading import Lock
from mongodb_manager import MongoDBConfig, MongoDBConnection, MongoDBManager


class MongoDBManagerFactory:
    """MongoDB管理器工厂（单例模式）"""

    _instance: Optional['MongoDBManagerFactory'] = None
    _lock: Lock = Lock()

    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_managers'):
            self._managers: Dict[str, MongoDBManager] = {}
            self._configs: Dict[str, MongoDBConfig] = {}
            self._connections: Dict[str, MongoDBConnection] = {}

    def create_manager(self, config: MongoDBConfig,
                       manager_name: str = "default") -> MongoDBManager:
        """
        创建MongoDB管理器

        Args:
            config: MongoDB配置
            manager_name: 管理器名称

        Returns:
            MongoDB管理器实例
        """
        if manager_name in self._managers:
            return self._managers[manager_name]

        # 创建连接
        connection = MongoDBConnection(config)
        if not connection.connect():
            raise ConnectionError(f"无法为管理器'{manager_name}'创建MongoDB连接")

        # 创建管理器
        manager = MongoDBManager(connection)

        # 保存引用
        self._configs[manager_name] = config
        self._connections[manager_name] = connection
        self._managers[manager_name] = manager

        return manager

    def get_manager(self, manager_name: str = "default") -> Optional[MongoDBManager]:
        """
        获取管理器实例

        Args:
            manager_name: 管理器名称

        Returns:
            MongoDB管理器实例，如果不存在则返回None
        """
        return self._managers.get(manager_name)

    def get_all_managers(self) -> Dict[str, MongoDBManager]:
        """
        获取所有管理器

        Returns:
            所有管理器实例字典
        """
        return self._managers.copy()

    def remove_manager(self, manager_name: str) -> bool:
        """
        移除管理器

        Args:
            manager_name: 管理器名称

        Returns:
            是否成功移除
        """
        if manager_name in self._managers:
            # 断开连接
            if manager_name in self._connections:
                self._connections[manager_name].disconnect()

            # 清理引用
            del self._managers[manager_name]
            del self._connections[manager_name]
            if manager_name in self._configs:
                del self._configs[manager_name]

            return True
        return False

    def shutdown_all(self):
        """关闭所有管理器连接"""
        for manager_name, connection in list(self._connections.items()):
            connection.disconnect()
            self.remove_manager(manager_name)

    def __del__(self):
        self.shutdown_all()