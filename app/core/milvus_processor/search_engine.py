#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 11:00
# @Author  : CongPeiQiang
# @File    : search_engine.py
# @Software: PyCharm
"""
Milvus搜索引擎
"""

from pymilvus import AnnSearchRequest, Function, FunctionType
from typing import Optional, List, Dict, Any
import logging
from .config import MilvusConfig
from .data_processor import DataProcessor
from .collection_manager import CollectionManager


class SearchEngine:
    """Milvus搜索引擎"""

    def __init__(self, data_processor: DataProcessor, config: MilvusConfig):
        """
        初始化搜索引擎

        Args:
            data_processor: 数据处理器
            config: Milvus配置
        """
        self.data_processor = data_processor
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = data_processor.client
        self.embeddings = data_processor.embeddings

    def semantic_search(self,
                        collection_name: str,
                        query: str,
                        limit: int = None,
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
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        try:
            # 生成查询向量
            query_vector = self.data_processor.generate_embedding(query)

            # 使用配置或参数
            limit = limit or self.config.default_search_limit

            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            # 执行搜索
            results = self.client.search(
                collection_name=collection_name,
                anns_field="content_dense",
                data=[query_vector],
                limit=limit,
                filter=filter_condition,
                search_params={"metric_type": "COSINE"},
                output_fields=output_fields
            )

            # 格式化结果
            return self._format_search_results(results, output_fields)

        except Exception as e:
            self.logger.error(f"语义搜索失败: {e}")
            return None

    def keyword_search(self,
                       collection_name: str,
                       query: str,
                       limit: int = None,
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
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        try:
            # 确定稀疏向量字段
            anns_field = f"{search_field}_sparse" if search_field in ["content", "title"] else "content_sparse"

            # 使用配置或参数
            limit = limit or self.config.default_search_limit

            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            # 执行搜索
            results = self.client.search(
                collection_name=collection_name,
                anns_field=anns_field,
                data=[query],
                limit=limit,
                search_params={'params': {'drop_ratio_search': 0.2}},
                output_fields=output_fields
            )

            # 格式化结果
            return self._format_search_results(results, output_fields)

        except Exception as e:
            self.logger.error(f"关键词搜索失败: {e}")
            return None

    def hybrid_search(self,
                      collection_name: str,
                      query: str,
                      limit: int = None,
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
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        try:
            from pymilvus import AnnSearchRequest

            # 默认权重
            if weights is None:
                weights = [0.5, 0.5]

            # 使用配置或参数
            limit = limit or self.config.default_search_limit

            # 生成语义查询向量
            semantic_vector = self.data_processor.generate_embedding(query)

            # 创建搜索请求
            semantic_request = AnnSearchRequest(
                data=[semantic_vector],
                anns_field="content_dense",
                param={"metric_type": "COSINE"},
                limit=limit * 2
            )

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

            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            # 执行混合搜索
            results = self.client.hybrid_search(
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
            self.logger.error(f"混合搜索失败: {e}")
            return None

    def text_match_search(self,
                          collection_name: str,
                          query: str,
                          search_field: str = "content",
                          limit: int = None,
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
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        try:
            # 使用配置或参数
            limit = limit or self.config.default_search_limit

            # 构建TEXT_MATCH过滤条件
            filter_condition = f'TEXT_MATCH({search_field}, "{query}")'

            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            # 执行查询
            results = self.client.query(
                collection_name=collection_name,
                filter=filter_condition,
                output_fields=output_fields,
                limit=limit
            )

            return results

        except Exception as e:
            self.logger.error(f"文本匹配搜索失败: {e}")
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
            Optional[List[Dict[str, Any]]]: 文档列表
        """
        try:
            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            results = self.client.get(
                collection_name=collection_name,
                ids=ids,
                output_fields=output_fields
            )

            return results

        except Exception as e:
            self.logger.error(f"根据ID获取文档失败: {e}")
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
            Optional[List[Dict[str, Any]]]: 查询结果
        """
        try:
            # 默认输出字段
            if output_fields is None:
                output_fields = ["id", "title", "content", "author", "source", "url", "doc_id", "chunk_index"]

            results = self.client.query(
                collection_name=collection_name,
                filter=filter_condition,
                output_fields=output_fields,
                limit=limit
            )

            return results

        except Exception as e:
            self.logger.error(f"查询文档失败: {e}")
            return None

    def _format_search_results(self,
                               results: Any,
                               output_fields: List[str]) -> List[Dict[str, Any]]:
        """
        格式化搜索结果

        Args:
            results: 原始搜索结果
            output_fields: 输出字段列表

        Returns:
            List[Dict[str, Any]]: 格式化结果
        """
        formatted_results = []

        if results and len(results) > 0:
            for result in results[0]:
                entity = result["entity"]
                formatted_result = {
                    "id": entity.get("id"),
                    "score": result["distance"],
                }

                # 添加请求的字段
                for field in output_fields:
                    if field in entity:
                        formatted_result[field] = entity[field]

                formatted_results.append(formatted_result)

        return formatted_results

    def search_with_options(self,
                            collection_name: str,
                            query: str,
                            search_type: str = "semantic",
                            **kwargs) -> Optional[List[Dict[str, Any]]]:
        """
        使用选项进行搜索

        Args:
            collection_name: 集合名称
            query: 查询文本
            search_type: 搜索类型（semantic/keyword/hybrid/text_match）
            **kwargs: 其他搜索参数

        Returns:
            Optional[List[Dict[str, Any]]]: 搜索结果
        """
        search_methods = {
            "semantic": self.semantic_search,
            "keyword": self.keyword_search,
            "hybrid": self.hybrid_search,
            "text_match": self.text_match_search,
        }

        if search_type not in search_methods:
            self.logger.error(f"不支持的搜索类型: {search_type}")
            return None

        method = search_methods[search_type]
        return method(collection_name, query, **kwargs)