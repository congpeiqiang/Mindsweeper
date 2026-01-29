#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 10:43
# @Author  : CongPeiQiang
# @File    : collection_manager.py
# @Software: PyCharm
"""
Milvus集合管理器
"""

from pymilvus import MilvusClient, DataType, Function, FunctionType
from typing import Optional, List, Dict, Any
import logging
import time
from .config import MilvusConfig
from .database_manager import DatabaseManager


class CollectionManager:
    """Milvus集合管理器"""

    def __init__(self, db_manager: DatabaseManager, config: MilvusConfig):
        """
        初始化集合管理器

        Args:
            db_manager: 数据库管理器
            config: Milvus配置
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = db_manager.client

    def create_default_schema(self, enable_dynamic_field: bool = None) -> Any:
        """
        创建默认集合Schema

        Args:
            enable_dynamic_field: 是否启用动态字段

        Returns:
            Any: Schema对象
        """
        enable_dynamic = enable_dynamic_field or self.config.enable_dynamic_field

        try:
            self.logger.info("创建默认集合Schema...")

            # 创建Schema
            schema = self.client.create_schema(
                enable_dynamic_field=enable_dynamic
            )

            # 配置分析器参数
            analyzer_params = {"type": "chinese"}

            # 添加字段定义
            # 1. 主键字段
            schema.add_field(
                field_name="id",
                datatype=DataType.INT64,
                auto_id=True,
                is_primary=True,
                description="文档唯一标识"
            )

            # 2. 文档元数据字段
            schema.add_field(
                field_name="doc_id",
                datatype=DataType.VARCHAR,
                max_length=100,
                description="文档ID"
            )

            schema.add_field(
                field_name="chunk_index",
                datatype=DataType.INT64,
                description="文档块索引"
            )

            # 3. 内容字段
            schema.add_field(
                field_name="title",
                datatype=DataType.VARCHAR,
                max_length=1000,
                analyzer_params=analyzer_params,
                enable_match=True,
                enable_analyzer=True,
                description="文章标题"
            )

            schema.add_field(
                field_name="content",
                datatype=DataType.VARCHAR,
                max_length=5000,
                analyzer_params=analyzer_params,
                enable_match=True,
                enable_analyzer=True,
                description="文档内容"
            )

            # 4. 向量字段
            schema.add_field(
                field_name="content_dense",
                datatype=DataType.FLOAT_VECTOR,
                dim=self.config.embedding_dim,
                description="内容密集向量"
            )

            schema.add_field(
                field_name="content_sparse",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
                description="内容稀疏向量（BM25生成）"
            )

            schema.add_field(
                field_name="title_sparse",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
                description="标题稀疏向量（BM25生成）"
            )

            # 5. 元数据字段
            metadata_fields = [
                ("url", 500, "原文链接"),
                ("author", 100, "作者"),
                ("source", 100, "来源"),
                ("category", 100, "分类"),
                ("publish_date", 100, "发布日期"),
            ]

            for field_name, max_len, description in metadata_fields:
                schema.add_field(
                    field_name=field_name,
                    datatype=DataType.VARCHAR,
                    max_length=max_len,
                    description=description
                )

            self.logger.info("默认Schema创建成功")
            return schema

        except Exception as e:
            self.logger.error(f"创建Schema失败: {e}")
            raise

    def add_bm25_functions(self, schema: Any) -> bool:
        """
        为Schema添加BM25函数

        Args:
            schema: Schema对象

        Returns:
            bool: 操作是否成功
        """
        try:
            self.logger.info("添加BM25函数...")

            # 标题BM25函数
            title_bm25_function = Function(
                name="title_bm25_emb",
                input_field_names=["title"],
                output_field_names=["title_sparse"],
                function_type=FunctionType.BM25,
            )

            # 内容BM25函数
            content_bm25_function = Function(
                name="content_bm25_emb",
                input_field_names=["content"],
                output_field_names=["content_sparse"],
                function_type=FunctionType.BM25,
            )

            # 添加函数到Schema
            schema.add_function(title_bm25_function)
            schema.add_function(content_bm25_function)

            self.logger.info("BM25函数添加成功")
            return True

        except Exception as e:
            self.logger.error(f"添加BM25函数失败: {e}")
            return False

    def create_default_index_params(self) -> Any:
        """
        创建默认索引参数

        Returns:
            Any: 索引参数对象
        """
        try:
            self.logger.info("创建默认索引参数...")

            index_params = self.client.prepare_index_params()

            # 1. 标量字段索引
            index_params.add_index(
                field_name="id",
                index_type="AUTOINDEX"
            )

            index_params.add_index(
                field_name="doc_id",
                index_type="AUTOINDEX"
            )

            # 2. 稀疏向量索引（BM25）
            sparse_index_params = {
                "inverted_index_algo": "DAAT_MAXSCORE",
                "bm25_k1": self.config.bm25_k1,
                "bm25_b": self.config.bm25_b
            }

            for field_name in ["title_sparse", "content_sparse"]:
                index_params.add_index(
                    field_name=field_name,
                    index_type="SPARSE_INVERTED_INDEX",
                    metric_type="BM25",
                    params=sparse_index_params
                )

            # 3. 密集向量索引
            index_params.add_index(
                field_name="content_dense",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            self.logger.info("默认索引参数创建成功")
            return index_params

        except Exception as e:
            self.logger.error(f"创建索引参数失败: {e}")
            raise

    def create_collection(self,
                          collection_name: str,
                          schema: Optional[Any] = None,
                          index_params: Optional[Any] = None,
                          drop_existing: bool = False,
                          wait_for_load: bool = True) -> bool:
        """
        创建集合

        Args:
            collection_name: 集合名称
            schema: Schema对象，如果为None则创建默认Schema
            index_params: 索引参数，如果为None则创建默认参数
            drop_existing: 是否删除已存在的集合
            wait_for_load: 是否等待集合加载完成

        Returns:
            bool: 操作是否成功
        """
        try:
            self.logger.info(f"创建集合: {collection_name}")

            # 验证集合名称
            if not collection_name or not isinstance(collection_name, str):
                raise ValueError("集合名称无效")

            # 检查集合是否已存在
            if self.client.has_collection(collection_name):
                if drop_existing:
                    self.logger.warning(f"集合 '{collection_name}' 已存在，正在删除...")
                    self.client.drop_collection(collection_name)
                    self.logger.info(f"集合 '{collection_name}' 删除成功")
                    time.sleep(2)
                else:
                    self.logger.warning(f"集合 '{collection_name}' 已存在")
                    return True

            # 创建Schema（如果需要）
            if schema is None:
                schema = self.create_default_schema()

            # 添加BM25函数
            self.add_bm25_functions(schema)

            # 创建索引参数（如果需要）
            if index_params is None:
                index_params = self.create_default_index_params()

            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )

            self.logger.info(f"集合 '{collection_name}' 创建成功")

            # 等待集合加载
            if wait_for_load:
                self.wait_for_collection_load(collection_name)

            return True

        except Exception as e:
            self.logger.error(f"创建集合失败: {e}")
            return False

    def wait_for_collection_load(self,
                                 collection_name: str,
                                 timeout: int = 60) -> bool:
        """
        等待集合加载完成

        Args:
            collection_name: 集合名称
            timeout: 超时时间（秒）

        Returns:
            bool: 是否加载成功
        """
        try:
            self.logger.info(f"等待集合 '{collection_name}' 加载...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    load_state = self.client.get_load_state(
                        collection_name=collection_name
                    )

                    state_name = load_state['state'].name

                    if state_name == 'Loaded':
                        self.logger.info("集合加载完成")
                        return True
                    elif state_name == 'Loading':
                        self.logger.info("集合正在加载中...")
                        time.sleep(2)
                    else:
                        self.logger.warning(f"集合状态异常: {state_name}")
                        time.sleep(2)

                except Exception as e:
                    self.logger.warning(f"获取加载状态失败: {e}")
                    time.sleep(2)

            self.logger.warning(f"集合加载超时（{timeout}秒）")
            return False

        except Exception as e:
            self.logger.error(f"等待集合加载失败: {e}")
            return False

    def list_collections(self) -> Optional[List[str]]:
        """
        列出所有集合

        Returns:
            Optional[List[str]]: 集合列表，失败时返回None
        """
        try:
            collections = self.client.list_collections()
            self.logger.info(f"当前集合: {collections}")
            return collections
        except Exception as e:
            self.logger.error(f"列出集合失败: {e}")
            return None

    def collection_exists(self, collection_name: str) -> bool:
        """
        检查集合是否存在

        Args:
            collection_name: 集合名称

        Returns:
            bool: 集合是否存在
        """
        try:
            return self.client.has_collection(collection_name)
        except Exception as e:
            self.logger.error(f"检查集合存在性失败: {e}")
            return False

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        获取集合信息

        Args:
            collection_name: 集合名称

        Returns:
            Optional[Dict[str, Any]]: 集合信息，失败时返回None
        """
        try:
            if not self.collection_exists(collection_name):
                self.logger.error(f"集合 '{collection_name}' 不存在")
                return None

            # 获取集合信息
            load_state = self.client.get_load_state(
                collection_name=collection_name
            )

            collection_info = self.client.describe_collection(
                collection_name=collection_name
            )

            # 尝试获取统计信息
            try:
                stats = self.client.get_collection_stats(
                    collection_name=collection_name
                )
            except Exception as e:
                self.logger.warning(f"获取集合统计失败: {e}")
                stats = None

            info = {
                "name": collection_name,
                "load_state": load_state,
                "info": collection_info,
                "stats": stats,
                "exists": True
            }

            return info

        except Exception as e:
            self.logger.error(f"获取集合信息失败: {e}")
            return None

    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合

        Args:
            collection_name: 集合名称

        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.collection_exists(collection_name):
                self.logger.warning(f"集合 '{collection_name}' 不存在")
                return False

            self.client.drop_collection(collection_name)
            self.logger.info(f"集合 '{collection_name}' 删除成功")
            return True

        except Exception as e:
            self.logger.error(f"删除集合失败: {e}")
            return False

    def clear_collection(self, collection_name: str) -> bool:
        """
        清空集合数据

        Args:
            collection_name: 集合名称

        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.collection_exists(collection_name):
                self.logger.error(f"集合 '{collection_name}' 不存在")
                return False

            # 获取所有文档ID
            results = self.client.query(
                collection_name=collection_name,
                output_fields=["id"],
                limit=10000
            )

            if not results:
                self.logger.info(f"集合 '{collection_name}' 为空")
                return True

            ids = [doc["id"] for doc in results]

            # 删除所有文档
            self.client.delete(
                collection_name=collection_name,
                ids=ids
            )

            self.logger.info(f"集合 '{collection_name}' 已清空，删除了 {len(ids)} 个文档")
            return True

        except Exception as e:
            self.logger.error(f"清空集合失败: {e}")
            return False