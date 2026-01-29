#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 11:01
# @Author  : CongPeiQiang
# @File    : __init__.py
# @Software: PyCharm
"""
Milvus向量数据库管理器
主入口模块
"""

import logging
from typing import Optional, Dict, Any, List
from .config import MilvusConfig, ConfigManager
from .database_manager import DatabaseManager
from .collection_manager import CollectionManager
from .data_processor import DataProcessor
from .search_engine import SearchEngine
from .utils import setup_logging


class MilvusManager:
    """Milvus主管理器"""

    def __init__(self, config: MilvusConfig = None):
        """
        初始化Milvus管理器

        Args:
            config: Milvus配置，如果为None则使用默认配置
        """
        # 加载配置
        self.config = config or MilvusConfig()

        # 设置日志
        setup_logging(self.config.log_level, self.config.log_format)
        self.logger = logging.getLogger(__name__)

        # 初始化组件
        self.db_manager = None
        self.collection_manager = None
        self.data_processor = None
        self.search_engine = None

        # 初始化状态
        self.initialized = False
        self.current_collection = None

    def initialize(self, db_name: str = None) -> bool:
        """
        初始化管理器

        Args:
            db_name: 要连接的数据库名称

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("初始化Milvus管理器...")

            # 验证配置
            self.config.validate()

            # 初始化数据库管理器
            self.db_manager = DatabaseManager(self.config)

            # 切换到指定数据库或默认数据库
            target_db = db_name or self.config.default_db

            # 如果数据库不存在，则创建
            if not self.db_manager.database_exists(target_db):
                self.logger.info(f"数据库 '{target_db}' 不存在，正在创建...")
                if not self.db_manager.create_database(target_db):
                    raise RuntimeError(f"创建数据库 '{target_db}' 失败")

            # 切换到目标数据库
            if not self.db_manager.switch_database(target_db):
                raise RuntimeError(f"切换到数据库 '{target_db}' 失败")

            # 初始化集合管理器
            self.collection_manager = CollectionManager(self.db_manager, self.config)

            # 初始化数据处理器
            self.data_processor = DataProcessor(self.collection_manager, self.config)

            # 初始化搜索引擎
            self.search_engine = SearchEngine(self.data_processor, self.config)

            self.initialized = True
            self.logger.info("Milvus管理器初始化成功")
            return True

        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False

    # ==================== 数据库操作代理 ====================

    def create_database(self, db_name: str, check_exists: bool = True) -> bool:
        """创建数据库"""
        if not self.db_manager:
            raise RuntimeError("管理器未初始化")
        return self.db_manager.create_database(db_name, check_exists)

    def list_databases(self) -> Optional[List[str]]:
        """列出所有数据库"""
        if not self.db_manager:
            raise RuntimeError("管理器未初始化")
        return self.db_manager.list_databases()

    def database_exists(self, db_name: str) -> bool:
        """检查数据库是否存在"""
        if not self.db_manager:
            raise RuntimeError("管理器未初始化")
        return self.db_manager.database_exists(db_name)

    def delete_database(self, db_name: str) -> bool:
        """删除数据库"""
        if not self.db_manager:
            raise RuntimeError("管理器未初始化")
        return self.db_manager.delete_database(db_name)

    # ==================== 集合操作代理 ====================

    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """创建集合"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")

        success = self.collection_manager.create_collection(collection_name, **kwargs)
        if success:
            self.current_collection = collection_name
        return success

    def list_collections(self) -> Optional[List[str]]:
        """列出所有集合"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")
        return self.collection_manager.list_collections()

    def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")
        return self.collection_manager.collection_exists(collection_name)

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """获取集合信息"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")
        return self.collection_manager.get_collection_info(collection_name)

    def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")
        return self.collection_manager.delete_collection(collection_name)

    # ==================== 数据操作代理 ====================

    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """插入文档"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.insert_documents(collection_name, documents, **kwargs)

    def insert_from_json_file(self, collection_name: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """从JSON文件插入文档"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.insert_from_json_file(collection_name, file_path, **kwargs)

    def get_document_count(self, collection_name: str) -> Optional[int]:
        """获取文档数量"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.get_document_count(collection_name)

    # ==================== 搜索操作代理 ====================

    def search(self, collection_name: str, query: str, search_type: str = "semantic", **kwargs) -> Optional[
        List[Dict[str, Any]]]:
        """搜索文档"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.search_with_options(collection_name, query, search_type, **kwargs)

    def semantic_search(self, collection_name: str, query: str, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """语义搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.semantic_search(collection_name, query, **kwargs)

    def keyword_search(self, collection_name: str, query: str, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """关键词搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.keyword_search(collection_name, query, **kwargs)

    def hybrid_search(self, collection_name: str, query: str, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """混合搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.hybrid_search(collection_name, query, **kwargs)

    # ==================== 工具方法 ====================

    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        status = {
            "initialized": self.initialized,
            "config": self.config.to_dict(),
            "current_collection": self.current_collection,
        }

        if self.db_manager:
            try:
                status["databases"] = self.db_manager.list_databases()
                status["current_database"] = self.config.default_db
            except Exception as e:
                status["database_error"] = str(e)

        if self.collection_manager:
            try:
                status["collections"] = self.collection_manager.list_collections()
            except Exception as e:
                status["collection_error"] = str(e)

        return status

    def close(self):
        """关闭管理器"""
        self.logger.info("关闭Milvus管理器")
        self.initialized = False


# 导出主要类和函数
__all__ = [
    'MilvusManager',
    'MilvusConfig',
    'ConfigManager',
    'DatabaseManager',
    'CollectionManager',
    'DataProcessor',
    'SearchEngine',
]