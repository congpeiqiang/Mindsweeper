#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 13:29
# @Author  : CongPeiQiang
# @File    : milvus_manager.py
# @Software: PyCharm
"""
Milvus向量数据库管理器 - 主入口
使用模块化设计，集成各个功能模块
"""
import json
import os
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from app.logger.logger import AppLogger
from app.config.settings import settings

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

# 导入各个模块
try:
    from .config import MilvusConfig
    from .database_manager import DatabaseManager
    from .collection_manager import CollectionManager
    from .data_processor import DataProcessor
    from .search_engine import SearchEngine
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from config import MilvusConfig
    from database_manager import DatabaseManager
    from collection_manager import CollectionManager
    from data_processor import DataProcessor
    from search_engine import SearchEngine


class MilvusManager:
    """Milvus向量数据库管理器（主入口）"""

    def __init__(self, config: Optional[MilvusConfig] = None):
        """
        初始化Milvus管理器

        Args:
            config: Milvus配置，如果为None则使用默认配置
        """
        self.config = config

        # 初始化各个管理器
        self.db_manager = None
        self.collection_manager = None
        self.data_processor = None
        self.search_engine = None

        # 状态
        self.initialized = False
        self.current_collection = None

    def initialize(self, db_name: Optional[str] = None) -> bool:
        """
        初始化Milvus管理器

        Args:
            db_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("初始化Milvus管理器...")

            # 验证配置
            self.config.validate()

            # 初始化数据库管理器
            self.db_manager = DatabaseManager(self.config)

            # 切换到指定数据库或默认数据库
            target_db = db_name or self.config.default_db

            # 如果数据库不存在，则创建
            if not self.db_manager.database_exists(target_db):
                logger.info(f"数据库 '{target_db}' 不存在，正在创建...")
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
            logger.info("Milvus管理器初始化成功")
            return True

        except Exception as e:
            logger.error(f"初始化失败: {e}")
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

    def switch_database(self, db_name: str) -> bool:
        """切换数据库"""
        if not self.db_manager:
            raise RuntimeError("管理器未初始化")

        success = self.db_manager.switch_database(db_name)
        if success:
            # 重新初始化集合管理器和相关组件
            self.collection_manager = CollectionManager(self.db_manager, self.config)
            self.data_processor = DataProcessor(self.collection_manager, self.config)
            self.search_engine = SearchEngine(self.data_processor, self.config)
            self.current_collection = None
        return success

    # ==================== 集合操作代理 ====================

    def create_collection(self,
                          collection_name: str,
                          drop_existing: bool = False,
                          wait_for_load: bool = True) -> bool:
        """创建集合"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")

        success = self.collection_manager.create_collection(
            collection_name=collection_name,
            drop_existing=drop_existing,
            wait_for_load=wait_for_load
        )

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

        success = self.collection_manager.delete_collection(collection_name)
        if success and collection_name == self.current_collection:
            self.current_collection = None
        return success

    def clear_collection(self, collection_name: str) -> bool:
        """清空集合数据"""
        if not self.collection_manager:
            raise RuntimeError("管理器未初始化")
        return self.collection_manager.clear_collection(collection_name)

    # ==================== 数据操作代理 ====================

    def insert_documents(self,
                         collection_name: str,
                         documents: List[Dict[str, Any]],
                         show_progress: bool = True) -> Dict[str, Any]:
        """插入文档到集合"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.insert_documents(
            collection_name=collection_name,
            documents=documents,
            show_progress=show_progress
        )

    def insert_from_json_file(self,
                              collection_name: str,
                              file_path: Union[str, Path],
                              **kwargs) -> Dict[str, Any]:
        """从JSON文件插入文档"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.insert_from_json_file(
            collection_name=collection_name,
            file_path=str(file_path),
            **kwargs
        )

    def get_document_count(self, collection_name: str) -> Optional[int]:
        """获取集合中的文档数量"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.get_document_count(collection_name)

    def generate_embedding(self, text: str, max_retries: int = 3) -> List[float]:
        """生成文本嵌入向量"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.generate_embedding(text, max_retries)

    def chunk_text(self,
                   text: str,
                   chunk_size: int = None,
                   overlap: int = None) -> List[str]:
        """将文本分块"""
        if not self.data_processor:
            raise RuntimeError("管理器未初始化")
        return self.data_processor.chunk_text(text, chunk_size, overlap)

    # ==================== 搜索操作代理 ====================

    def search(self,
               collection_name: str,
               query: str,
               search_type: str = "semantic",
               **kwargs) -> Optional[List[Dict[str, Any]]]:
        """
        搜索文档

        Args:
            collection_name: 集合名称
            query: 查询文本
            search_type: 搜索类型（semantic/keyword/hybrid/text_match）
            **kwargs: 其他搜索参数

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")

        search_types = {
            "semantic": self.search_engine.semantic_search,
            "keyword": self.search_engine.keyword_search,
            "hybrid": self.search_engine.hybrid_search,
            "text_match": self.search_engine.text_match_search,
        }

        if search_type not in search_types:
            logger.error(f"不支持的搜索类型: {search_type}")
            return None

        method = search_types[search_type]
        return method(collection_name, query, **kwargs)

    def semantic_search(self,
                        collection_name: str,
                        query: str,
                        **kwargs) -> Optional[List[Dict[str, Any]]]:
        """语义搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.semantic_search(collection_name, query, **kwargs)

    def keyword_search(self,
                       collection_name: str,
                       query: str,
                       **kwargs) -> Optional[List[Dict[str, Any]]]:
        """关键词搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.keyword_search(collection_name, query, **kwargs)

    def hybrid_search(self,
                      collection_name: str,
                      query: str,
                      **kwargs) -> Optional[List[Dict[str, Any]]]:
        """混合搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.hybrid_search(collection_name, query, **kwargs)

    def text_match_search(self,
                          collection_name: str,
                          query: str,
                          **kwargs) -> Optional[List[Dict[str, Any]]]:
        """文本匹配搜索"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.text_match_search(collection_name, query, **kwargs)

    def get_by_ids(self,
                   collection_name: str,
                   ids: List[int],
                   output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """根据ID获取文档"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.get_by_ids(collection_name, ids, output_fields)

    def query_with_filter(self,
                          collection_name: str,
                          filter_condition: str,
                          limit: int = 100,
                          output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """使用过滤条件查询文档"""
        if not self.search_engine:
            raise RuntimeError("管理器未初始化")
        return self.search_engine.query_with_filter(
            collection_name, filter_condition, limit, output_fields
        )

    # ==================== 实用方法 ====================

    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        status = {
            "initialized": self.initialized,
            "config": self.config.to_dict(),
            "current_database": self.db_manager.config.default_db if self.db_manager else None,
            "current_collection": self.current_collection,
        }

        if self.db_manager:
            try:
                status["databases"] = self.db_manager.list_databases()
            except Exception as e:
                status["database_error"] = str(e)

        if self.collection_manager:
            try:
                status["collections"] = self.collection_manager.list_collections()
            except Exception as e:
                status["collection_error"] = str(e)

        return status

    def backup_collection(self,
                          collection_name: str,
                          backup_path: Union[str, Path],
                          limit: int = 10000) -> bool:
        """
        备份集合数据到JSON文件

        Args:
            collection_name: 集合名称
            backup_path: 备份文件路径
            limit: 最大备份数量

        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return False

            # 查询所有数据
            results = self.query_with_filter(
                collection_name=collection_name,
                filter_condition="",
                limit=limit,
                output_fields=["*"]
            )

            if not results:
                logger.warning(f"集合 '{collection_name}' 为空")
                return True

            # 保存到文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"集合 '{collection_name}' 备份成功，保存了 {len(results)} 个文档到 {backup_path}")
            return True

        except Exception as e:
            logger.error(f"备份集合失败: {e}")
            return False

    def close(self):
        """关闭管理器"""
        logger.info("关闭Milvus管理器")
        self.initialized = False
        # 注意：MilvusClient通常不需要显式关闭


# ==================== 简化使用函数 ====================
from threading import Lock
from typing import Optional


class MilvusManagerSingleton:
    """
    Milvus管理器单例包装类
    """
    _instance: Optional['MilvusManager'] = None
    _lock: Lock = Lock()
    _initialized: bool = False

    @classmethod
    def get_instance(cls) -> 'MilvusManager':
        """
        获取Milvus管理器单例实例

        Returns:
            MilvusManager: 单例管理器实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查锁定
                    cls._instance = create_manager()
                    cls._initialized = True
        elif not cls._initialized:
            # 如果实例存在但未初始化，重新初始化
            with cls._lock:
                if not cls._initialized:
                    cls._instance = create_manager()
                    cls._initialized = True

        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        重置单例实例（主要用于测试）
        """
        with cls._lock:
            if cls._instance:
                cls._instance.cleanup()
                cls._instance = None
                cls._initialized = False


# 使用示例
def get_milvus_manager(singleton: bool = True) -> 'MilvusManager':
    """
    获取Milvus管理器的统一入口

    Args:
        singleton: 是否使用单例模式

    Returns:
        MilvusManager: 管理器实例
    """
    if singleton:
        return MilvusManagerSingleton.get_instance()
    else:
        return create_manager()

def create_manager() -> MilvusManager:
    """
    快速创建Milvus管理器

    Returns:
        MilvusManager: 初始化好的管理器实例
    """
    config = MilvusConfig(settings.MILVUS_URI, settings.OLLAMA_URI, settings.MILVUS_TIMEOUT, settings.MILVUS_DATABASE,
                          settings.MILVUS_COLLECTION_NAME, settings.MILVUS_ENABLE_DYNAMIC_FIELD,
                          settings.CHUNK_SIZE, settings.CHUNK_OVERLAP, settings.MILVUS_BATCH_SIZE, settings.EMBEDDING_MODEL,
                          settings.EMBEDDING_DIMENSION, settings.MILVUS_LIMIT,
                          settings.MILVUS_BM25_K1, settings.MILVUS_BM25_B)

    manager = MilvusManager(config)
    if not manager.initialize():
        raise RuntimeError("Milvus管理器初始化失败")

    return manager