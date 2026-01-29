#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 10:14
# @Author  : CongPeiQiang
# @File    : milvus_manager.py
# @Software: PyCharm
"""
Milvus向量数据库管理器
整合了数据库、集合、数据插入和搜索的完整功能
"""
import os

from pymilvus import MilvusClient, DataType, Function, FunctionType
from langchain_ollama import OllamaEmbeddings
from typing import Optional, List, Dict, Any, Union, Tuple
import logging
import time
import json
import random
from tqdm import tqdm
from datetime import datetime

from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class MilvusManager:
    """Milvus向量数据库管理器"""

    def __init__(self,
                 milvus_uri: str = "http://localhost:19530",
                 ollama_uri: str = "http://localhost:11434",
                 default_db: str = "milvus_database",
                 default_collection: str = "default_collection",
                 timeout: float = 30.0):
        """
        初始化Milvus管理器

        Args:
            milvus_uri: Milvus服务器地址
            ollama_uri: Ollama服务器地址（用于嵌入）
            default_db: 默认数据库名称
            default_collection: 默认集合名称
            timeout: 超时时间（秒）
        """
        self.milvus_uri = milvus_uri
        self.ollama_uri = ollama_uri
        self.default_db = default_db
        self.default_collection = default_collection
        self.timeout = timeout

        # 客户端连接
        self.milvus_client = None
        self.embeddings = None

    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

    def initialize(self, db_name: Optional[str] = None) -> bool:
        """
        初始化Milvus连接和嵌入模型

        Args:
            db_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("初始化Milvus管理器...")

            # 初始化嵌入模型
            logger.info(f"连接Ollama嵌入模型: {self.ollama_uri}")
            self.embeddings = OllamaEmbeddings(
                model="qwen3-embedding:0.6b",
                base_url=self.ollama_uri
            )

            # 初始化Milvus客户端
            db_to_use = db_name or self.default_db
            logger.info(f"连接Milvus: {self.milvus_uri}, 数据库: {db_to_use}")

            self.milvus_client = MilvusClient(
                uri=self.milvus_uri,
                db_name=db_to_use,
                timeout=self.timeout
            )

            # 测试连接
            try:
                collections = self.milvus_client.list_collections()
                logger.info(f"连接成功！当前集合数量: {len(collections)}")
                return True
            except Exception as e:
                logger.warning(f"连接测试失败，可能数据库不存在: {e}")
                return False

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False

    # ==================== 数据库管理 ====================

    def create_database(self, db_name: str,
                        check_exists: bool = True) -> bool:
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
            if not db_name or not isinstance(db_name, str):
                raise ValueError("数据库名称不能为空且必须是字符串类型")

            if not db_name.replace('_', '').replace('-', '').isalnum():
                raise ValueError("数据库名称只能包含字母、数字、下划线和连字符")

            if db_name[0].isdigit():
                raise ValueError("数据库名称不能以数字开头")

            # 创建客户端（不指定数据库）
            client = MilvusClient(uri=self.milvus_uri, timeout=self.timeout)

            # 检查数据库是否已存在
            if check_exists:
                existing_dbs = client.list_databases()
                if db_name in existing_dbs:
                    logger.warning(f"数据库 '{db_name}' 已存在")
                    return True

            # 创建数据库
            client.create_database(db_name=db_name)
            logger.info(f"数据库 '{db_name}' 创建成功")

            # 验证创建
            updated_dbs = client.list_databases()
            if db_name not in updated_dbs:
                raise RuntimeError(f"数据库 '{db_name}' 创建失败")

            logger.info(f"当前数据库列表: {updated_dbs}")
            return True

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
            client = MilvusClient(uri=self.milvus_uri, timeout=self.timeout)
            databases = client.list_databases()
            logger.info(f"数据库列表: {databases}")
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

    def delete_database(self, db_name: str,
                        force: bool = False) -> bool:
        """
        删除数据库

        Args:
            db_name: 数据库名称
            force: 是否强制删除（即使不存在）

        Returns:
            bool: 操作是否成功
        """
        try:
            # 检查数据库是否存在
            if not self.database_exists(db_name):
                if force:
                    logger.warning(f"数据库 '{db_name}' 不存在，无需删除")
                    return True
                else:
                    raise ValueError(f"数据库 '{db_name}' 不存在")

            # 删除数据库
            client = MilvusClient(uri=self.milvus_uri, timeout=self.timeout)
            client.drop_database(db_name=db_name)
            logger.info(f"数据库 '{db_name}' 删除成功")
            return True

        except Exception as e:
            logger.error(f"删除数据库失败: {e}")
            return False

    # ==================== 集合管理 ====================

    def create_collection_schema(self,
                                 enable_dynamic_field: bool = True) -> Optional[Any]:
        """
        创建集合Schema

        Args:
            enable_dynamic_field: 是否启用动态字段

        Returns:
            Optional[Any]: Schema对象，失败时返回None
        """
        try:
            logger.info("创建集合Schema...")

            # 创建Schema
            schema = self.milvus_client.create_schema(
                enable_dynamic_field=enable_dynamic_field
            )

            # 定义字段
            analyzer_params = {"type": "chinese"}

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

            # 3. 标题字段（支持全文搜索）
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
                field_name="title_sparse",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
                description="标题稀疏向量（BM25自动生成）"
            )

            # 4. 内容字段
            schema.add_field(
                field_name="content",
                datatype=DataType.VARCHAR,
                max_length=5000,
                analyzer_params=analyzer_params,
                enable_match=True,
                enable_analyzer=True,
                description="文档内容"
            )

            schema.add_field(
                field_name="content_dense",
                datatype=DataType.FLOAT_VECTOR,
                dim=1024,  # 注意：需要与嵌入模型维度匹配
                description="内容密集向量"
            )

            schema.add_field(
                field_name="content_sparse",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
                description="内容稀疏向量（BM25自动生成）"
            )

            # 5. 其他元数据字段
            schema.add_field(
                field_name="url",
                datatype=DataType.VARCHAR,
                max_length=500,
                description="原文链接"
            )

            schema.add_field(
                field_name="publish_date",
                datatype=DataType.VARCHAR,
                max_length=100,
                description="发布日期"
            )

            schema.add_field(
                field_name="author",
                datatype=DataType.VARCHAR,
                max_length=100,
                description="作者"
            )

            schema.add_field(
                field_name="source",
                datatype=DataType.VARCHAR,
                max_length=100,
                description="来源"
            )

            schema.add_field(
                field_name="category",
                datatype=DataType.VARCHAR,
                max_length=100,
                description="分类"
            )

            logger.info("Schema创建成功")
            return schema

        except Exception as e:
            logger.error(f"创建Schema失败: {e}")
            return None

    def add_bm25_functions(self, schema: Any) -> bool:
        """
        为Schema添加BM25函数

        Args:
            schema: Schema对象

        Returns:
            bool: 操作是否成功
        """
        try:
            logger.info("添加BM25函数...")

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

            logger.info("BM25函数添加成功")
            return True

        except Exception as e:
            logger.error(f"添加BM25函数失败: {e}")
            return False

    def create_index_params(self) -> Optional[Any]:
        """
        创建索引参数

        Returns:
            Optional[Any]: 索引参数对象，失败时返回None
        """
        try:
            logger.info("创建索引参数...")

            index_params = self.milvus_client.prepare_index_params()

            # 主键索引
            index_params.add_index(
                field_name="id",
                index_type="AUTOINDEX"
            )

            # 文档ID索引
            index_params.add_index(
                field_name="doc_id",
                index_type="AUTOINDEX"
            )

            # 稀疏向量索引 - 标题
            index_params.add_index(
                field_name="title_sparse",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    "bm25_k1": 1.2,
                    "bm25_b": 0.75
                }
            )

            # 稀疏向量索引 - 内容
            index_params.add_index(
                field_name="content_sparse",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    "bm25_k1": 1.2,
                    "bm25_b": 0.75
                }
            )

            # 密集向量索引
            index_params.add_index(
                field_name="content_dense",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            logger.info("索引参数创建成功")
            return index_params

        except Exception as e:
            logger.error(f"创建索引参数失败: {e}")
            return None

    def create_collection(self,
                          collection_name: str,
                          schema: Optional[Any] = None,
                          index_params: Optional[Any] = None,
                          drop_existing: bool = False,
                          wait_for_load: bool = True,
                          load_timeout: int = 60) -> bool:
        """
        创建集合

        Args:
            collection_name: 集合名称
            schema: Schema对象，如果为None则创建默认Schema
            index_params: 索引参数，如果为None则创建默认参数
            drop_existing: 是否删除已存在的集合
            wait_for_load: 是否等待集合加载完成
            load_timeout: 加载超时时间（秒）

        Returns:
            bool: 操作是否成功
        """
        try:
            logger.info(f"创建集合: {collection_name}")

            # 验证集合名称
            if not collection_name or not isinstance(collection_name, str):
                raise ValueError("集合名称不能为空且必须是字符串类型")

            # 检查集合是否已存在
            if self.milvus_client.has_collection(collection_name):
                if drop_existing:
                    logger.warning(f"集合 '{collection_name}' 已存在，正在删除...")
                    self.milvus_client.drop_collection(collection_name)
                    logger.info(f"集合 '{collection_name}' 删除成功")
                    time.sleep(2)  # 等待删除完成
                else:
                    logger.warning(f"集合 '{collection_name}' 已存在，跳过创建")
                    return True

            # 创建Schema（如果需要）
            if schema is None:
                schema = self.create_collection_schema()
                if schema is None:
                    raise RuntimeError("Schema创建失败")

                # 添加BM25函数
                if not self.add_bm25_functions(schema):
                    raise RuntimeError("BM25函数添加失败")

            # 创建索引参数（如果需要）
            if index_params is None:
                index_params = self.create_index_params()
                if index_params is None:
                    raise RuntimeError("索引参数创建失败")

            # 创建集合
            self.milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )

            logger.info(f"集合 '{collection_name}' 创建成功")

            # 等待集合加载
            if wait_for_load:
                self.wait_for_collection_load(collection_name, load_timeout)

            return True

        except Exception as e:
            logger.error(f"创建集合失败: {e}")
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
            logger.info(f"等待集合 '{collection_name}' 加载...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    load_state = self.milvus_client.get_load_state(
                        collection_name=collection_name
                    )

                    state_name = load_state['state'].name

                    if state_name == 'Loaded':
                        logger.info("集合加载完成")
                        return True
                    elif state_name == 'Loading':
                        logger.info("集合正在加载中...")
                        time.sleep(2)
                    else:
                        logger.warning(f"集合状态异常: {state_name}")
                        time.sleep(2)

                except Exception as e:
                    logger.warning(f"获取加载状态失败: {e}")
                    time.sleep(2)

            logger.warning(f"集合加载超时（{timeout}秒）")
            return False

        except Exception as e:
            logger.error(f"等待集合加载失败: {e}")
            return False

    def list_collections(self) -> Optional[List[str]]:
        """
        列出所有集合

        Returns:
            Optional[List[str]]: 集合列表，失败时返回None
        """
        try:
            collections = self.milvus_client.list_collections()
            logger.info(f"集合列表: {collections}")
            return collections
        except Exception as e:
            logger.error(f"列出集合失败: {e}")
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
            return self.milvus_client.has_collection(collection_name)
        except Exception as e:
            logger.error(f"检查集合存在性失败: {e}")
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
                logger.error(f"集合 '{collection_name}' 不存在")
                return None

            # 获取加载状态
            load_state = self.milvus_client.get_load_state(
                collection_name=collection_name
            )

            # 获取集合描述
            collection_info = self.milvus_client.describe_collection(
                collection_name=collection_name
            )

            # 获取集合统计
            try:
                stats = self.milvus_client.get_collection_stats(
                    collection_name=collection_name
                )
            except Exception as e:
                logger.warning(f"获取集合统计失败: {e}")
                stats = None

            info = {
                "collection_name": collection_name,
                "load_state": load_state,
                "collection_info": collection_info,
                "stats": stats,
                "exists": True
            }

            logger.info(f"集合 '{collection_name}' 信息获取成功")
            return info

        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return None

    def delete_collection(self, collection_name: str,
                          force: bool = False) -> bool:
        """
        删除集合

        Args:
            collection_name: 集合名称
            force: 是否强制删除（即使不存在）

        Returns:
            bool: 操作是否成功
        """
        try:
            # 检查集合是否存在
            if not self.collection_exists(collection_name):
                if force:
                    logger.warning(f"集合 '{collection_name}' 不存在，无需删除")
                    return True
                else:
                    raise ValueError(f"集合 '{collection_name}' 不存在")

            # 删除集合
            self.milvus_client.drop_collection(collection_name)
            logger.info(f"集合 '{collection_name}' 删除成功")
            return True

        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            return False

    # ==================== 数据管理 ====================

    def generate_embedding(self,
                           text: str,
                           max_retries: int = 3) -> List[float]:
        """
        生成文本嵌入向量

        Args:
            text: 输入文本
            max_retries: 最大重试次数

        Returns:
            List[float]: 嵌入向量
        """
        if not text or not isinstance(text, str):
            logger.warning("输入文本为空或非字符串，返回零向量")
            return [0.0] * 1024  # 默认维度

        for attempt in range(max_retries):
            try:
                logger.info(f"生成嵌入向量 (尝试 {attempt + 1}/{max_retries})")
                embedding = self.embeddings.embed_query(text)
                logger.info(f"生成 {len(embedding)} 维向量")
                return embedding

            except Exception as e:
                logger.warning(f"生成嵌入向量失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error("生成嵌入向量最终失败，返回随机向量")
                    return [random.random() for _ in range(1024)]

    def chunk_text(self,
                   text: str,
                   chunk_size: int = 800,
                   overlap: int = 100) -> List[str]:
        """
        将文本分块

        Args:
            text: 输入文本
            chunk_size: 块大小
            overlap: 重叠大小

        Returns:
            List[str]: 文本块列表
        """
        try:
            if not text or not isinstance(text, str):
                logger.warning("输入文本为空或非字符串")
                return []

            if chunk_size <= 0:
                raise ValueError("chunk_size必须大于0")

            if overlap < 0:
                raise ValueError("overlap不能为负数")

            if overlap >= chunk_size:
                logger.warning("overlap过大，调整为chunk_size的一半")
                overlap = chunk_size // 2

            # 如果文本长度小于等于chunk_size，直接返回
            if len(text) <= chunk_size:
                return [text]

            chunks = []
            start = 0

            while start < len(text):
                end = start + chunk_size

                # 如果不是最后一块，尝试在标点处断句
                if end < len(text):
                    search_end = min(end + 100, len(text))

                    # 寻找合适的断句点
                    sentence_end = max(
                        text.rfind('。', end - 100, search_end),
                        text.rfind('！', end - 100, search_end),
                        text.rfind('？', end - 100, search_end),
                        text.rfind('\n', end - 100, search_end),
                        text.rfind('.', end - 100, search_end),
                        text.rfind('!', end - 100, search_end),
                        text.rfind('?', end - 100, search_end)
                    )

                    if sentence_end > end - 100:
                        end = sentence_end + 1

                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)

                # 设置下一块的起始位置
                start = max(start + chunk_size - overlap, end)

                if start >= len(text):
                    break

            logger.info(f"文本分割完成，共生成 {len(chunks)} 个块")
            return chunks

        except Exception as e:
            logger.error(f"文本分块失败: {e}")
            return [text] if text else []

    def validate_document(self, doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证文档数据

        Args:
            doc: 文档数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []

        # 必需字段
        required_fields = ['doc_id', 'title', 'content']

        for field in required_fields:
            if field not in doc:
                errors.append(f"缺少必需字段: {field}")
            elif not doc[field]:
                errors.append(f"字段 '{field}' 为空")

        # 字段长度验证
        if 'doc_id' in doc and len(str(doc['doc_id'])) > 100:
            errors.append("doc_id长度超过100")

        if 'title' in doc and len(str(doc['title'])) > 1000:
            errors.append("title长度超过1000")

        if 'url' in doc and len(str(doc['url'])) > 500:
            errors.append("url长度超过500")

        if 'author' in doc and len(str(doc['author'])) > 100:
            errors.append("author长度超过100")

        return len(errors) == 0, errors

    def prepare_document_chunks(self,
                                doc: Dict[str, Any],
                                chunk_size: int = 800,
                                overlap: int = 100) -> List[Dict[str, Any]]:
        """
        准备文档分块数据

        Args:
            doc: 文档数据
            chunk_size: 块大小
            overlap: 重叠大小

        Returns:
            List[Dict[str, Any]]: 分块数据列表
        """
        try:
            # 验证文档
            is_valid, errors = self.validate_document(doc)
            if not is_valid:
                logger.error(f"文档验证失败: {errors}")
                return []

            # 分块
            content_chunks = self.chunk_text(
                doc['content'],
                chunk_size=chunk_size,
                overlap=overlap
            )

            if not content_chunks:
                logger.warning("文档分割后无有效块")
                return []

            chunks_data = []

            for idx, chunk in enumerate(content_chunks):
                # 生成嵌入
                embedding = self.generate_embedding(chunk)

                # 构建块数据
                chunk_data = {
                    "doc_id": str(doc['doc_id']),
                    "chunk_index": idx,
                    "title": str(doc.get('title', ''))[:1000],
                    "content": chunk,
                    "content_dense": embedding,
                    "url": str(doc.get('url', ''))[:500],
                    "publish_date": str(doc.get('publish_date', ''))[:100],
                    "author": str(doc.get('author', ''))[:100],
                    "source": str(doc.get('source', ''))[:100],
                    "category": str(doc.get('category', ''))[:100],
                    "original_doc": json.dumps(doc, ensure_ascii=False)[:50000]  # 原始文档副本
                }

                # 添加可选字段
                if 'keywords' in doc:
                    chunk_data['keywords'] = str(doc['keywords'])[:500]

                if 'summary' in doc:
                    chunk_data['summary'] = str(doc['summary'])[:1000]

                chunks_data.append(chunk_data)

            logger.info(f"文档 '{doc['doc_id']}' 分割为 {len(chunks_data)} 个块")
            return chunks_data

        except Exception as e:
            logger.error(f"准备文档分块失败: {e}")
            return []

    def insert_documents(self,
                         collection_name: str,
                         documents: List[Dict[str, Any]],
                         chunk_size: int = 800,
                         overlap: int = 100,
                         batch_size: int = 50,
                         show_progress: bool = True) -> Dict[str, Any]:
        """
        插入文档到集合

        Args:
            collection_name: 集合名称
            documents: 文档列表
            chunk_size: 块大小
            overlap: 重叠大小
            batch_size: 批处理大小
            show_progress: 是否显示进度条

        Returns:
            Dict[str, Any]: 插入结果统计
        """
        try:
            # 参数验证
            if not collection_name:
                raise ValueError("集合名称不能为空")

            if not documents or not isinstance(documents, list):
                logger.warning("没有文档需要插入")
                return {"success": True, "message": "没有文档需要插入"}

            # 检查集合是否存在
            if not self.collection_exists(collection_name):
                raise ValueError(f"集合 '{collection_name}' 不存在")

            all_chunks = []
            stats = {
                "total_documents": len(documents),
                "valid_documents": 0,
                "invalid_documents": [],
                "total_chunks": 0,
                "failed_chunks": 0,
                "document_stats": {}
            }

            logger.info(f"开始处理 {len(documents)} 个文档...")

            # 处理文档
            doc_iter = tqdm(documents, desc="处理文档") if show_progress else documents

            for doc_idx, doc in enumerate(doc_iter):
                try:
                    # 准备分块
                    chunks = self.prepare_document_chunks(
                        doc,
                        chunk_size=chunk_size,
                        overlap=overlap
                    )

                    if chunks:
                        all_chunks.extend(chunks)
                        stats["valid_documents"] += 1
                        stats["document_stats"][doc.get('doc_id', f'doc_{doc_idx}')] = len(chunks)
                    else:
                        stats["invalid_documents"].append({
                            "index": doc_idx,
                            "doc_id": doc.get('doc_id', f'doc_{doc_idx}'),
                            "reason": "分块失败或无内容"
                        })

                except Exception as e:
                    logger.error(f"处理文档 {doc_idx} 失败: {e}")
                    stats["invalid_documents"].append({
                        "index": doc_idx,
                        "doc_id": doc.get('doc_id', f'doc_{doc_idx}'),
                        "reason": str(e)
                    })

            stats["total_chunks"] = len(all_chunks)

            if not all_chunks:
                logger.error("没有有效的文档块需要插入")
                return {
                    **stats,
                    "inserted_chunks": 0,
                    "failed_batches": 0,
                    "success": False,
                    "message": "没有有效的文档块"
                }

            # 批量插入
            logger.info(f"开始批量插入 {len(all_chunks)} 个文档块...")

            inserted_count = 0
            failed_batches = []

            batch_iter = range(0, len(all_chunks), batch_size)
            batch_iter = tqdm(batch_iter, desc="插入数据") if show_progress else batch_iter

            for i in batch_iter:
                batch_data = all_chunks[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                try:
                    self.milvus_client.insert(
                        collection_name=collection_name,
                        data=batch_data
                    )
                    inserted_count += len(batch_data)
                    logger.debug(f"批次 {batch_num}: 成功插入 {len(batch_data)} 个块")

                except Exception as e:
                    logger.error(f"批次 {batch_num} 插入失败: {e}")
                    failed_batches.append(batch_num)
                    stats["failed_chunks"] += len(batch_data)

            # 构建结果
            result = {
                **stats,
                "inserted_chunks": inserted_count,
                "failed_batches": failed_batches,
                "success": len(failed_batches) == 0,
                "message": f"插入完成: {inserted_count}/{stats['total_chunks']} 个块"
            }

            # 输出统计信息
            logger.info("=" * 50)
            logger.info("插入统计:")
            logger.info(f"  文档总数: {stats['total_documents']}")
            logger.info(f"  有效文档: {stats['valid_documents']}")
            logger.info(f"  无效文档: {len(stats['invalid_documents'])}")
            logger.info(f"  总块数: {stats['total_chunks']}")
            logger.info(f"  插入块数: {inserted_count}")
            logger.info(f"  失败批次: {len(failed_batches)}")
            logger.info("=" * 50)

            return result

        except Exception as e:
            logger.error(f"插入文档失败: {e}")
            return {
                "success": False,
                "message": str(e),
                "total_documents": len(documents) if documents else 0,
                "inserted_chunks": 0,
                "failed_batches": []
            }

    def insert_from_json_file(self,
                              collection_name: str,
                              file_path: str,
                              **kwargs) -> Dict[str, Any]:
        """
        从JSON文件插入文档

        Args:
            collection_name: 集合名称
            file_path: JSON文件路径
            **kwargs: 传递给insert_documents的参数

        Returns:
            Dict[str, Any]: 插入结果
        """
        try:
            logger.info(f"从文件读取文档: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            if not isinstance(documents, list):
                documents = [documents]

            logger.info(f"读取到 {len(documents)} 个文档")
            return self.insert_documents(collection_name, documents, **kwargs)

        except FileNotFoundError:
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

        except Exception as e:
            error_msg = f"读取文件失败: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    def get_document_count(self, collection_name: str) -> Optional[int]:
        """
        获取集合中的文档数量

        Args:
            collection_name: 集合名称

        Returns:
            Optional[int]: 文档数量，失败时返回None
        """
        try:
            stats = self.milvus_client.get_collection_stats(collection_name)
            if stats and 'row_count' in stats:
                return stats['row_count']
            return 0
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return None

    # ==================== 搜索功能 ====================

    def semantic_search(self,
                        collection_name: str,
                        query: str,
                        limit: int = 10,
                        filter_condition: Optional[str] = None,
                        output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        语义搜索（密集向量搜索）

        Args:
            collection_name: 集合名称
            query: 查询文本
            limit: 返回结果数量
            filter_condition: 过滤条件
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果，失败时返回None
        """
        try:
            # 生成查询向量
            query_vector = self.generate_embedding(query)

            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url"]

            # 执行搜索
            search_params = {"metric_type": "COSINE"}

            results = self.milvus_client.search(
                collection_name=collection_name,
                anns_field="content_dense",
                data=[query_vector],
                limit=limit,
                filter=filter_condition,
                search_params=search_params,
                output_fields=output_fields
            )

            # 格式化结果
            formatted_results = []
            if results and len(results) > 0:
                for result in results[0]:
                    entity = result["entity"]
                    formatted_results.append({
                        "id": entity.get("id"),
                        "score": result["distance"],
                        "title": entity.get("title", ""),
                        "content": entity.get("content", ""),
                        "author": entity.get("author", ""),
                        "source": entity.get("source", ""),
                        "url": entity.get("url", ""),
                        "doc_id": entity.get("doc_id", ""),
                        "chunk_index": entity.get("chunk_index", 0)
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return None

    def keyword_search(self,
                       collection_name: str,
                       query: str,
                       limit: int = 10,
                       search_field: str = "content",
                       output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        关键词搜索（稀疏向量/全文搜索）

        Args:
            collection_name: 集合名称
            query: 查询文本
            limit: 返回结果数量
            search_field: 搜索字段（content或title）
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果，失败时返回None
        """
        try:
            # 确定稀疏向量字段
            if search_field == "title":
                anns_field = "title_sparse"
            else:
                anns_field = "content_sparse"

            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url"]

            # 执行搜索
            search_params = {'params': {'drop_ratio_search': 0.2}}

            results = self.milvus_client.search(
                collection_name=collection_name,
                anns_field=anns_field,
                data=[query],
                limit=limit,
                search_params=search_params,
                output_fields=output_fields
            )

            # 格式化结果
            formatted_results = []
            if results and len(results) > 0:
                for result in results[0]:
                    entity = result["entity"]
                    formatted_results.append({
                        "id": entity.get("id"),
                        "score": result["distance"],
                        "title": entity.get("title", ""),
                        "content": entity.get("content", ""),
                        "author": entity.get("author", ""),
                        "source": entity.get("source", ""),
                        "url": entity.get("url", ""),
                        "doc_id": entity.get("doc_id", ""),
                        "chunk_index": entity.get("chunk_index", 0)
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"关键词搜索失败: {e}")
            return None

    def hybrid_search(self,
                      collection_name: str,
                      query: str,
                      limit: int = 10,
                      weights: List[float] = None,
                      filter_condition: Optional[str] = None,
                      output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        混合搜索（结合语义和关键词搜索）

        Args:
            collection_name: 集合名称
            query: 查询文本
            limit: 返回结果数量
            weights: 权重列表 [语义权重, 关键词权重]
            filter_condition: 过滤条件
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果，失败时返回None
        """
        try:
            from pymilvus import AnnSearchRequest

            # 设置默认权重
            if weights is None:
                weights = [0.5, 0.5]

            # 生成语义查询向量
            semantic_vector = self.generate_embedding(query)

            # 创建语义搜索请求
            semantic_request = AnnSearchRequest(
                data=[semantic_vector],
                anns_field="content_dense",
                param={"metric_type": "COSINE"},
                limit=limit * 2  # 获取更多结果用于混合
            )

            # 创建关键词搜索请求
            keyword_request = AnnSearchRequest(
                data=[query],
                anns_field="content_sparse",
                param={"drop_ratio_search": 0.2},
                limit=limit * 2
            )

            # 创建加权排序器
            weight_ranker = Function(
                name="weight",
                input_field_names=[],
                function_type=FunctionType.RERANK,
                params={
                    "reranker": "weighted",
                    "weights": weights,
                    "norm_score": True
                }
            )

            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url"]

            # 执行混合搜索
            results = self.milvus_client.hybrid_search(
                collection_name=collection_name,
                reqs=[semantic_request, keyword_request],
                ranker=weight_ranker,
                limit=limit,
                output_fields=output_fields
            )

            # 格式化结果
            formatted_results = []
            if results:
                for result in results:
                    entity = result["entity"]
                    formatted_results.append({
                        "id": entity.get("id"),
                        "score": result.get("distance", 0),
                        "title": entity.get("title", ""),
                        "content": entity.get("content", ""),
                        "author": entity.get("author", ""),
                        "source": entity.get("source", ""),
                        "url": entity.get("url", ""),
                        "doc_id": entity.get("doc_id", ""),
                        "chunk_index": entity.get("chunk_index", 0)
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"混合搜索失败: {e}")
            return None

    def text_match_search(self,
                          collection_name: str,
                          query: str,
                          search_field: str = "content",
                          limit: int = 10,
                          output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        文本匹配搜索（使用TEXT_MATCH函数）

        Args:
            collection_name: 集合名称
            query: 查询文本
            search_field: 搜索字段
            limit: 返回结果数量
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果，失败时返回None
        """
        try:
            # 构建TEXT_MATCH过滤条件
            filter_condition = f'TEXT_MATCH({search_field}, "{query}")'

            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url"]

            # 执行查询
            results = self.milvus_client.query(
                collection_name=collection_name,
                filter=filter_condition,
                output_fields=output_fields,
                limit=limit
            )

            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.get("id"),
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "author": result.get("author", ""),
                    "source": result.get("source", ""),
                    "url": result.get("url", ""),
                    "doc_id": result.get("doc_id", ""),
                    "chunk_index": result.get("chunk_index", 0)
                })

            return formatted_results

        except Exception as e:
            logger.error(f"文本匹配搜索失败: {e}")
            return None

    def get_by_ids(self,
                   collection_name: str,
                   ids: List[int],
                   output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        根据ID获取文档

        Args:
            collection_name: 集合名称
            ids: ID列表
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 文档列表，失败时返回None
        """
        try:
            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url"]

            # 获取文档
            results = self.milvus_client.get(
                collection_name=collection_name,
                ids=ids,
                output_fields=output_fields
            )

            return results

        except Exception as e:
            logger.error(f"根据ID获取文档失败: {e}")
            return None

    def query_with_filter(self,
                          collection_name: str,
                          filter_condition: str,
                          limit: int = 100,
                          output_fields: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        使用过滤条件查询文档

        Args:
            collection_name: 集合名称
            filter_condition: 过滤条件
            limit: 返回结果数量
            output_fields: 返回字段

        Returns:
            Optional[List[Dict[str, Any]]]: 查询结果，失败时返回None
        """
        try:
            # 设置输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id"]

            # 执行查询
            results = self.milvus_client.query(
                collection_name=collection_name,
                filter=filter_condition,
                output_fields=output_fields,
                limit=limit
            )

            return results

        except Exception as e:
            logger.error(f"查询文档失败: {e}")
            return None

    # ==================== 实用功能 ====================

    def clear_collection(self, collection_name: str) -> bool:
        """
        清空集合中的所有数据

        Args:
            collection_name: 集合名称

        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取所有文档的ID
            results = self.milvus_client.query(
                collection_name=collection_name,
                output_fields=["id"],
                limit=10000
            )

            if not results:
                logger.info(f"集合 '{collection_name}' 为空，无需清空")
                return True

            ids = [doc["id"] for doc in results]

            # 删除所有文档
            self.milvus_client.delete(
                collection_name=collection_name,
                ids=ids
            )

            logger.info(f"集合 '{collection_name}' 清空成功，删除了 {len(ids)} 个文档")
            return True

        except Exception as e:
            logger.error(f"清空集合失败: {e}")
            return False

    def backup_collection(self,
                          collection_name: str,
                          backup_path: str,
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
            # 查询所有数据
            results = self.milvus_client.query(
                collection_name=collection_name,
                output_fields=["*"],
                limit=limit
            )

            if not results:
                logger.warning(f"集合 '{collection_name}' 为空，没有数据可备份")
                return True

            # 保存到文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"集合 '{collection_name}' 备份成功，保存了 {len(results)} 个文档到 {backup_path}")
            return True

        except Exception as e:
            logger.error(f"备份集合失败: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        获取Milvus管理器状态

        Returns:
            Dict[str, Any]: 状态信息
        """
        try:
            status = {
                "milvus_uri": self.milvus_uri,
                "ollama_uri": self.ollama_uri,
                "default_db": self.default_db,
                "default_collection": self.default_collection,
                "connected": self.milvus_client is not None,
                "embeddings_initialized": self.embeddings is not None,
                "timestamp": datetime.now().isoformat()
            }

            # 如果已连接，获取更多信息
            if self.milvus_client:
                try:
                    collections = self.milvus_client.list_collections()
                    status["collections"] = collections
                    status["collection_count"] = len(collections)
                except Exception as e:
                    status["collection_error"] = str(e)

            return status

        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {"error": str(e)}

    def close(self):
        """关闭连接"""
        try:
            if self.milvus_client:
                # MilvusClient通常不需要显式关闭，但可以在这里添加清理逻辑
                logger.info("Milvus管理器关闭")
        except Exception as e:
            logger.warning(f"关闭连接时出现警告: {e}")


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    # 1. 初始化管理器
    manager = MilvusManager(
        milvus_uri="http://localhost:19530",
        ollama_uri="http://localhost:11434"
    )

    # 2. 初始化连接
    if not manager.initialize():
        print("初始化失败")
        return

    # 3. 创建数据库（如果需要）
    if not manager.database_exists("milvus_database"):
        manager.create_database("milvus_database")

    # 4. 创建集合
    collection_name = "my_collection"
    manager.create_collection(
        collection_name=collection_name,
        drop_existing=True,  # 如果已存在则删除
        wait_for_load=True
    )

    # 5. 插入文档
    documents = [
        {
            "doc_id": "doc_001",
            "title": "人工智能的未来",
            "content": "人工智能正在快速发展，将在各个领域产生深远影响...",
            "author": "张三",
            "source": "科技日报",
            "url": "http://example.com/doc1",
            "category": "科技"
        },
        {
            "doc_id": "doc_002",
            "title": "机器学习入门",
            "content": "机器学习是人工智能的重要分支，包括监督学习、无监督学习等...",
            "author": "李四",
            "source": "计算机世界",
            "url": "http://example.com/doc2",
            "category": "教育"
        }
    ]

    insert_result = manager.insert_documents(
        collection_name=collection_name,
        documents=documents,
        chunk_size=500,
        overlap=50,
        batch_size=10
    )

    print(f"插入结果: {insert_result}")

    # 6. 搜索示例
    # 语义搜索
    semantic_results = manager.semantic_search(
        collection_name=collection_name,
        query="人工智能发展",
        limit=5
    )

    print(f"语义搜索结果: {len(semantic_results)} 条")

    # 关键词搜索
    keyword_results = manager.keyword_search(
        collection_name=collection_name,
        query="机器学习",
        limit=5
    )

    print(f"关键词搜索结果: {len(keyword_results)} 条")

    # 混合搜索
    hybrid_results = manager.hybrid_search(
        collection_name=collection_name,
        query="人工智能与机器学习",
        limit=5,
        weights=[0.7, 0.3]  # 语义搜索权重0.7，关键词搜索权重0.3
    )

    print(f"混合搜索结果: {len(hybrid_results)} 条")

    # 7. 获取集合信息
    collection_info = manager.get_collection_info(collection_name)
    print(f"集合信息: {collection_info}")

    # 8. 获取状态
    status = manager.get_status()
    print(f"管理器状态: {status}")

    # 9. 清理
    manager.close()


if __name__ == "__main__":
    example_usage()