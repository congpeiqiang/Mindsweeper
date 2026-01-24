#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 14:36
# @Author  : CongPeiQiang
# @File    : mongodb_manager.py
# @Software: PyCharm
# mongodb_manager.py
import logging
import os
import traceback
from typing import Any, Dict, List, Optional, Union
from pymongo import MongoClient, InsertOne, UpdateOne, UpdateMany, DeleteOne, DeleteMany, ReplaceOne
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError, BulkWriteError
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
from bson import ObjectId, json_util

from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class MongoDBOperation(Enum):
    """MongoDB操作类型枚举"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    FIND = "find"
    AGGREGATE = "aggregate"


@dataclass
class MongoDBConfig:
    """MongoDB配置类"""
    host: str = "localhost"
    port: int = 27017
    username: str = ""
    password: str = ""
    database: str = "default_db"
    auth_source: str = "admin"
    max_pool_size: int = 100
    min_pool_size: int = 10
    timeout_ms: int = 5000
    use_tls: bool = False
    replica_set: Optional[str] = None


class MongoDBConnection:
    """MongoDB连接类"""

    def __init__(self, config: MongoDBConfig):
        self.config = config
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self.is_connected = False

    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            connection_string = self._build_connection_string()

            self._client = MongoClient(
                connection_string,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
                serverSelectionTimeoutMS=self.config.timeout_ms
            )

            # 测试连接
            self._client.admin.command('ping')
            self._database = self._client[self.config.database]
            self.is_connected = True

            logger.info(f"成功连接到MongoDB: {self.config.host}:{self.config.port}")
            return True

        except ConnectionFailure as e:
            logger.error(f"MongoDB连接失败: {e}")
            self._cleanup()
            return False
        except Exception as e:
            logger.error(f"连接时发生未知错误: {e}")
            self._cleanup()
            return False

    def _build_connection_string(self) -> str:
        """构建连接字符串"""
        auth_part = ""
        if self.config.username and self.config.password:
            auth_part = f"{self.config.username}:{self.config.password}@"

        host_part = self.config.host
        if self.config.replica_set:
            host_part = f"{self.config.host}/?replicaSet={self.config.replica_set}"

        connection_string = f"mongodb://{auth_part}{host_part}:{self.config.port}/"

        if self.config.auth_source:
            connection_string += f"?authSource={self.config.auth_source}"

        return connection_string

    def get_database(self) -> Optional[Database]:
        """获取数据库实例"""
        if self.is_connected and self._database:
            return self._database
        return None

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """获取集合实例"""
        if self.is_connected and self._database:
            return self._database[collection_name]
        return None

    def disconnect(self):
        """断开数据库连接"""
        self._cleanup()
        logger.info("MongoDB连接已关闭")

    def _cleanup(self):
        """清理资源"""
        if self._client:
            self._client.close()
        self._client = None
        self._database = None
        self.is_connected = False

    def __del__(self):
        self.disconnect()


class MongoDBManager:
    """MongoDB管理器基类"""

    def __init__(self, connection: MongoDBConnection):
        self.connection = connection
        self._ensure_connection()

    def _ensure_connection(self):
        """确保连接正常"""
        if not self.connection.is_connected:
            if not self.connection.connect():
                raise ConnectionError("无法连接到MongoDB数据库")

    def _handle_exception(self, operation: MongoDBOperation,
                          collection_name: str, error: Exception) -> str:
        """统一异常处理"""
        return (
            f"MongoDB操作失败 - 操作: {operation.value}, "
            f"集合: {collection_name}, 错误: {error}"
        )

    def _convert_objectid(self, document: Dict) -> Dict:
        """转换ObjectId为字符串"""
        if document and '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
        return document

    def _convert_documents(self, documents: List[Dict]) -> List[Dict]:
        """批量转换ObjectId为字符串"""
        return [self._convert_objectid(doc) for doc in documents]

    def insert_one(self, collection_name: str, document: Dict) -> Optional[str]:
        """
        插入单个文档

        Args:
            collection_name: 集合名称
            document: 要插入的文档

        Returns:
            插入文档的ID（字符串形式）
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.insert_one(document)
            return str(result.inserted_id)

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.INSERT, collection_name, e)
            return None

    def insert_many(self, collection_name: str,
                    documents: List[Dict]) -> Optional[List[str]]:
        """
        批量插入文档

        Args:
            collection_name: 集合名称
            documents: 要插入的文档列表

        Returns:
            插入文档的ID列表
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.INSERT, collection_name, e)
            return None


    def find_one(self, collection_name: str,
                 query: Optional[Dict] = None,
                 projection: Optional[Dict] = None) -> Optional[Dict]:
        """
        查询单个文档

        Args:
            collection_name: 集合名称
            query: 查询条件
            projection: 投影条件

        Returns:
            查询到的文档
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            query = query or {}
            document = collection.find_one(query, projection)

            if document:
                return self._convert_objectid(document)
            return None

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.FIND, collection_name, e)
            return None

    def find_many(self, collection_name: str,
                  query: Optional[Dict] = None,
                  projection: Optional[Dict] = None,
                  sort: Optional[List[tuple]] = None,
                  skip: int = 0,
                  limit: int = 0) -> List[Dict]:
        """
        查询多个文档

        Args:
            collection_name: 集合名称
            query: 查询条件
            projection: 投影条件
            sort: 排序条件
            skip: 跳过文档数
            limit: 限制文档数

        Returns:
            文档列表
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return []

            query = query or {}
            cursor = collection.find(query, projection)

            if sort:
                cursor = cursor.sort(sort)
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)

            documents = list(cursor)
            return self._convert_documents(documents)

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.FIND, collection_name, e)
            return []

    def update_one(self, collection_name: str,
                   query: Dict,
                   update: Dict,
                   upsert: bool = False) -> Optional[Dict]:
        """
        更新单个文档

        Args:
            collection_name: 集合名称
            query: 查询条件
            update: 更新操作
            upsert: 如果不存在是否插入

        Returns:
            更新结果信息
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.update_one(query, update, upsert=upsert)

            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None
            }

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.UPDATE, collection_name, e)
            return None

    def update_many(self, collection_name: str,
                    query: Dict,
                    update: Dict,
                    upsert: bool = False) -> Optional[Dict]:
        """
        批量更新文档

        Args:
            collection_name: 集合名称
            query: 查询条件
            update: 更新操作
            upsert: 如果不存在是否插入

        Returns:
            更新结果信息
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.update_many(query, update, upsert=upsert)

            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None
            }

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.UPDATE, collection_name, e)
            return None

    def bulk_write(self, collection_name: str,
                   operations: List[Union[InsertOne, UpdateOne, UpdateMany, DeleteOne, DeleteMany, ReplaceOne]],
                   ordered: bool = True) -> Optional[Dict]:
        """
        批量写操作（替代多个update_many）

        Args:
            collection_name: 集合名称
            operations: 批量操作列表
            ordered: 是否按顺序执行

        Returns:
            批量写结果统计

        Examples:
            # 使用示例
            operations = [
                InsertOne({"name": "张三", "age": 25}),
                UpdateOne({"name": "李四"}, {"$set": {"age": 30}}),
                UpdateMany({"status": "active"}, {"$inc": {"score": 10}}),
                DeleteOne({"name": "王五"}),
                ReplaceOne({"name": "赵六"}, {"name": "赵六", "age": 35, "status": "vip"})
            ]

            result = manager.bulk_write("users", operations)
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection or not operations:
                return None

            # 执行批量操作
            result = collection.bulk_write(operations, ordered=ordered)

            return {
                'inserted_count': result.inserted_count,
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'deleted_count': result.deleted_count,
                'upserted_count': result.upserted_count,
                'bulk_api_result': result.bulk_api_result if hasattr(result, 'bulk_api_result') else None
            }

        except BulkWriteError as e:
            # 批量操作部分失败的情况
            error_result = {
                'error': True,
                'error_details': str(e.details),
                'inserted_count': e.details.get('nInserted', 0),
                'matched_count': e.details.get('nMatched', 0),
                'modified_count': e.details.get('nModified', 0),
                'deleted_count': e.details.get('nRemoved', 0),
                'upserted_count': len(e.details.get('upserted', []))
            }
            logger.error(f"批量操作部分失败: {e.details}")
            return error_result

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.BULK_WRITE, collection_name, e)
            return None

    def delete_one(self, collection_name: str, query: Dict) -> Optional[int]:
        """
        删除单个文档

        Args:
            collection_name: 集合名称
            query: 查询条件

        Returns:
            删除的文档数量
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.delete_one(query)
            return result.deleted_count

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.DELETE, collection_name, e)
            return None

    def delete_many(self, collection_name: str, query: Dict) -> Optional[int]:
        """
        批量删除文档

        Args:
            collection_name: 集合名称
            query: 查询条件

        Returns:
            删除的文档数量
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            result = collection.delete_many(query)
            return result.deleted_count

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.DELETE, collection_name, e)
            return None

    def aggregate(self, collection_name: str,
                  pipeline: List[Dict]) -> List[Dict]:
        """
        聚合查询

        Args:
            collection_name: 集合名称
            pipeline: 聚合管道

        Returns:
            聚合结果
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return []

            cursor = collection.aggregate(pipeline)
            results = list(cursor)
            return self._convert_documents(results)

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.AGGREGATE, collection_name, e)
            return []

    def count_documents(self, collection_name: str,
                        query: Optional[Dict] = None) -> int:
        """
        统计文档数量

        Args:
            collection_name: 集合名称
            query: 查询条件

        Returns:
            文档数量
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return 0

            query = query or {}
            return collection.count_documents(query)

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.FIND, collection_name, e)
            return 0

    def create_index(self, collection_name: str,
                     keys: List[tuple],
                     **kwargs) -> Optional[str]:
        """
        创建索引

        Args:
            collection_name: 集合名称
            keys: 索引键列表
            **kwargs: 其他索引参数

        Returns:
            创建的索引名称
        """
        try:
            self._ensure_connection()
            collection = self.connection.get_collection(collection_name)

            if not collection:
                return None

            return collection.create_index(keys, **kwargs)

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.INSERT, collection_name, e)
            return None

    def drop_collection(self, collection_name: str) -> bool:
        """
        删除集合

        Args:
            collection_name: 集合名称

        Returns:
            是否成功
        """
        try:
            self._ensure_connection()
            database = self.connection.get_database()

            if not database:
                return False

            collection = database[collection_name]
            collection.drop()
            return True

        except PyMongoError as e:
            self._handle_exception(MongoDBOperation.DELETE, collection_name, e)
            return False