#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 10:42
# @Author  : CongPeiQiang
# @File    : database_manager.py
# @Software: PyCharm
"""
Milvus数据库管理器
"""
import os

from pymilvus import MilvusClient
from typing import Optional, List, Dict, Any

from . import MilvusConfig
from ...logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class DatabaseManager:
    """Milvus数据库管理器"""

    def __init__(self, config: MilvusConfig):
        """
        初始化数据库管理器

        Args:
            config: Milvus配置
        """
        self.config = config
        self.client = None

    def _get_root_client(self) -> MilvusClient:
        """获取根客户端（不指定数据库）"""
        return MilvusClient(
            uri=self.config.milvus_uri,
            timeout=self.config.timeout
        )

    def _get_db_client(self, db_name: Optional[str] = None) -> MilvusClient:
        """获取数据库客户端"""
        db_to_use = db_name or self.config.default_db
        return MilvusClient(
            uri=self.config.milvus_uri,
            db_name=db_to_use,
            timeout=self.config.timeout
        )

    def validate_db_name(self, db_name: str) -> bool:
        """验证数据库名称"""
        if not db_name or not isinstance(db_name, str):
            return False

        # 检查名称格式
        if not db_name.replace('_', '').replace('-', '').isalnum():
            return False

        if db_name[0].isdigit():
            return False

        return True

    def create_database(self, db_name: str, check_exists: bool = True) -> bool:
        """
        创建数据库

        Args:
            db_name: 数据库名称
            check_exists: 是否检查数据库已存在

        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证数据库名称
            if not self.validate_db_name(db_name):
                raise ValueError(f"数据库名称 '{db_name}' 无效")

            client = self._get_root_client()

            # 检查数据库是否已存在
            if check_exists:
                existing_dbs = client.list_databases()
                if db_name in existing_dbs:
                    logger.info(f"数据库 '{db_name}' 已存在")
                    return True

            # 创建数据库
            client.create_database(db_name=db_name)
            logger.info(f"数据库 '{db_name}' 创建成功")

            # 验证创建
            updated_dbs = client.list_databases()
            success = db_name in updated_dbs

            if success:
                logger.info(f"数据库列表: {updated_dbs}")
            else:
                logger.error(f"数据库 '{db_name}' 创建失败")

            return success

        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            return False

    def list_databases(self) -> Optional[List[str]]:
        """
        列出所有数据库

        Returns:
            Optional[List[str]]: 数据库列表，失败时返回None
        """
        try:
            client = self._get_root_client()
            databases = client.list_databases()
            logger.info(f"当前数据库: {databases}")
            return databases
        except Exception as e:
            logger.error(f"列出数据库失败: {e}")
            return None

    def database_exists(self, db_name: str) -> bool:
        """
        检查数据库是否存在

        Args:
            db_name: 数据库名称

        Returns:
            bool: 数据库是否存在
        """
        try:
            databases = self.list_databases()
            if databases is None:
                return False
            return db_name in databases
        except Exception as e:
            logger.error(f"检查数据库存在性失败: {e}")
            return False

    def delete_database(self, db_name: str) -> bool:
        """
        删除数据库

        Args:
            db_name: 数据库名称

        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.database_exists(db_name):
                logger.warning(f"数据库 '{db_name}' 不存在")
                return False

            client = self._get_root_client()
            client.drop_database(db_name=db_name)

            logger.info(f"数据库 '{db_name}' 删除成功")
            return True

        except Exception as e:
            logger.error(f"删除数据库失败: {e}")
            return False

    def switch_database(self, db_name: str) -> bool:
        """
        切换当前数据库

        Args:
            db_name: 要切换到的数据库名称

        Returns:
            bool: 切换是否成功
        """
        try:
            if not self.database_exists(db_name):
                logger.error(f"数据库 '{db_name}' 不存在")
                return False

            # 创建新的客户端连接到指定数据库
            self.client = self._get_db_client(db_name)
            self.config.default_db = db_name

            logger.info(f"已切换到数据库: {db_name}")
            return True

        except Exception as e:
            logger.error(f"切换数据库失败: {e}")
            return False

    def get_database_info(self, db_name: str) -> Optional[Dict[str, Any]]:
        """
        获取数据库信息

        Args:
            db_name: 数据库名称

        Returns:
            Optional[Dict[str, Any]]: 数据库信息，失败时返回None
        """
        try:
            if not self.database_exists(db_name):
                logger.error(f"数据库 '{db_name}' 不存在")
                return None

            # 获取数据库的集合列表
            client = self._get_db_client(db_name)
            collections = client.list_collections()

            info = {
                "name": db_name,
                "collections": collections,
                "collection_count": len(collections),
                "exists": True
            }

            return info

        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return None