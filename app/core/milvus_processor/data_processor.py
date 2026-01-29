#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 10:43
# @Author  : CongPeiQiang
# @File    : data_processor.py
# @Software: PyCharm
"""
Milvus数据处理器
"""
import os

from langchain_ollama import OllamaEmbeddings
from typing import List, Dict, Any, Optional, Tuple
import logging
import random
import time
import json
from tqdm import tqdm
from .config import MilvusConfig
from .collection_manager import CollectionManager
from ...logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class DataProcessor:
    """Milvus数据处理器"""

    def __init__(self, collection_manager: CollectionManager, config: MilvusConfig):
        """
        初始化数据处理器

        Args:
            collection_manager: 集合管理器
            config: Milvus配置
        """
        self.collection_manager = collection_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.embeddings = None
        self.client = collection_manager.client

        # 初始化嵌入模型
        self._init_embeddings()

    def _init_embeddings(self):
        """初始化嵌入模型"""
        try:
            self.logger.info(f"初始化嵌入模型: {self.config.embedding_model}")
            self.embeddings = OllamaEmbeddings(
                model=self.config.embedding_model,
                base_url=self.config.ollama_uri
            )
            self.logger.info("嵌入模型初始化成功")
        except Exception as e:
            self.logger.error(f"初始化嵌入模型失败: {e}")
            raise

    def generate_embedding(self, text: str, max_retries: int = 3) -> List[float]:
        """
        生成文本嵌入向量

        Args:
            text: 输入文本
            max_retries: 最大重试次数

        Returns:
            List[float]: 嵌入向量
        """
        if not text or not isinstance(text, str):
            self.logger.warning("输入文本为空，返回零向量")
            return [0.0] * self.config.embedding_dim

        for attempt in range(max_retries):
            try:
                embedding = self.embeddings.embed_query(text)
                return embedding

            except Exception as e:
                self.logger.warning(f"生成嵌入向量失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    self.logger.error("生成嵌入向量最终失败，返回随机向量")
                    return [random.random() for _ in range(self.config.embedding_dim)]

    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
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
                self.logger.warning("输入文本为空或非字符串")
                return []

            # 使用配置或参数
            chunk_size = chunk_size or self.config.chunk_size
            overlap = overlap or self.config.chunk_overlap

            if chunk_size <= 0:
                raise ValueError("chunk_size必须大于0")

            if overlap < 0:
                raise ValueError("overlap不能为负数")

            if overlap >= chunk_size:
                overlap = chunk_size // 2

            # 如果文本长度小于等于chunk_size，直接返回
            if len(text) <= chunk_size:
                return [text.strip()]

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

            return chunks

        except Exception as e:
            self.logger.error(f"文本分块失败: {e}")
            return [text.strip()] if text else []

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
        field_limits = {
            'doc_id': 100,
            'title': 1000,
            'url': 500,
            'author': 100,
            'source': 100,
            'category': 100,
            'publish_date': 100,
        }

        for field, max_len in field_limits.items():
            if field in doc and len(str(doc[field])) > max_len:
                errors.append(f"字段 '{field}' 长度超过 {max_len}")

        return len(errors) == 0, errors

    def prepare_document_chunks(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        准备文档分块数据

        Args:
            doc: 文档数据

        Returns:
            List[Dict[str, Any]]: 分块数据列表
        """
        try:
            # 验证文档
            is_valid, errors = self.validate_document(doc)
            if not is_valid:
                self.logger.error(f"文档验证失败: {errors}")
                return []

            # 分块
            content_chunks = self.chunk_text(doc['content'])

            if not content_chunks:
                self.logger.warning("文档分割后无有效块")
                return []

            chunks_data = []

            for idx, chunk in enumerate(content_chunks):
                # 生成嵌入
                embedding = self.generate_embedding(chunk)

                # 构建块数据
                chunk_data = {
                    "doc_id": str(doc['doc_id']),
                    "chunk_index": idx,
                    "title": str(doc['title']),
                    "content": chunk,
                    "content_dense": embedding,
                    "url": str(doc.get('url', '')),
                    "author": str(doc.get('author', '')),
                    "source": str(doc.get('source', '')),
                    "category": str(doc.get('category', '')),
                    "publish_date": str(doc.get('publish_date', '')),
                }

                chunks_data.append(chunk_data)

            self.logger.debug(f"文档 '{doc['doc_id']}' 分割为 {len(chunks_data)} 个块")
            return chunks_data

        except Exception as e:
            self.logger.error(f"准备文档分块失败: {e}")
            return []

    def insert_documents(self,
                         collection_name: str,
                         documents: List[Dict[str, Any]],
                         show_progress: bool = True) -> Dict[str, Any]:
        """
        插入文档到集合

        Args:
            collection_name: 集合名称
            documents: 文档列表
            show_progress: 是否显示进度条

        Returns:
            Dict[str, Any]: 插入结果统计
        """
        try:
            # 检查集合是否存在
            if not self.collection_manager.collection_exists(collection_name):
                raise ValueError(f"集合 '{collection_name}' 不存在")

            if not documents or not isinstance(documents, list):
                return {
                    "success": True,
                    "message": "没有文档需要插入",
                    "total_documents": 0,
                    "inserted_chunks": 0
                }

            # 准备所有分块
            all_chunks = []
            stats = {
                "total_documents": len(documents),
                "valid_documents": 0,
                "invalid_documents": [],
                "total_chunks": 0,
            }

            # 处理文档
            doc_iter = tqdm(documents, desc="处理文档") if show_progress else documents

            for doc_idx, doc in enumerate(doc_iter):
                try:
                    chunks = self.prepare_document_chunks(doc)

                    if chunks:
                        all_chunks.extend(chunks)
                        stats["valid_documents"] += 1
                    else:
                        stats["invalid_documents"].append({
                            "index": doc_idx,
                            "doc_id": doc.get('doc_id', f'doc_{doc_idx}'),
                            "reason": "分块失败"
                        })

                except Exception as e:
                    self.logger.error(f"处理文档 {doc_idx} 失败: {e}")
                    stats["invalid_documents"].append({
                        "index": doc_idx,
                        "doc_id": doc.get('doc_id', f'doc_{doc_idx}'),
                        "reason": str(e)
                    })

            stats["total_chunks"] = len(all_chunks)

            if not all_chunks:
                return {
                    **stats,
                    "success": False,
                    "message": "没有有效的文档块",
                    "inserted_chunks": 0,
                    "failed_batches": []
                }

            # 批量插入
            batch_size = self.config.batch_size
            inserted_count = 0
            failed_batches = []

            batch_iter = range(0, len(all_chunks), batch_size)
            batch_iter = tqdm(batch_iter, desc="插入数据") if show_progress else batch_iter

            for i in batch_iter:
                batch_data = all_chunks[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                try:
                    self.client.insert(
                        collection_name=collection_name,
                        data=batch_data
                    )
                    inserted_count += len(batch_data)

                except Exception as e:
                    self.logger.error(f"批次 {batch_num} 插入失败: {e}")
                    failed_batches.append(batch_num)

            # 构建结果
            result = {
                **stats,
                "inserted_chunks": inserted_count,
                "failed_batches": failed_batches,
                "success": len(failed_batches) == 0,
                "message": f"成功插入 {inserted_count}/{stats['total_chunks']} 个块"
            }

            self.logger.info(f"插入完成: {result['message']}")
            return result

        except Exception as e:
            self.logger.error(f"插入文档失败: {e}")
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
            self.logger.info(f"从文件读取文档: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 确保是列表格式
            if isinstance(data, dict):
                documents = [data]
            elif isinstance(data, list):
                documents = data
            else:
                raise ValueError("JSON数据必须是字典或列表")

            self.logger.info(f"读取到 {len(documents)} 个文档")
            return self.insert_documents(collection_name, documents, **kwargs)

        except Exception as e:
            error_msg = f"读取文件失败: {e}"
            self.logger.error(error_msg)
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
            stats = self.client.get_collection_stats(collection_name)
            return stats.get('row_count', 0) if stats else 0
        except Exception as e:
            self.logger.error(f"获取文档数量失败: {e}")
            return None