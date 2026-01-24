#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 12:15
# @Author  : CongPeiQiang
# @File    : document_processor.py
# @Software: PyCharm
import os
import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Union

from bson import ObjectId
from pymongo import UpdateOne
from app.core.mongodb_processor.mongodb_manager import MongoDBConfig, MongoDBManager
from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()


class DocumentManager(MongoDBManager):
    def __init__(
        self,
        input_dir: str,
        workspace: str = "",  # New parameter for workspace isolation
        supported_extensions: tuple = (
            ".txt",
            ".md",
            ".mdx",  # MDX (Markdown + JSX)
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".rtf",  # Rich Text Format
            ".odt",  # OpenDocument Text
            ".tex",  # LaTeX
            ".epub",  # Electronic Publication
            ".html",  # HyperText Markup Language
            ".htm",  # HyperText Markup Language
            ".csv",  # Comma-Separated Values
            ".json",  # JavaScript Object Notation
            ".xml",  # eXtensible Markup Language
            ".yaml",  # YAML Ain't Markup Language
            ".yml",  # YAML
            ".log",  # Log files
            ".conf",  # Configuration files
            ".ini",  # Initialization files
            ".properties",  # Java properties files
            ".sql",  # SQL scripts
            ".bat",  # Batch files
            ".sh",  # Shell scripts
            ".c",  # C source code
            ".cpp",  # C++ source code
            ".py",  # Python source code
            ".java",  # Java source code
            ".js",  # JavaScript source code
            ".ts",  # TypeScript source code
            ".swift",  # Swift source code
            ".go",  # Go source code
            ".rb",  # Ruby source code
            ".php",  # PHP source code
            ".css",  # Cascading Style Sheets
            ".scss",  # Sassy CSS
            ".less",  # LESS CSS
        ),
        # config = None,
        # manager_name=None,
        # mongdb_manager = None
    ):
        # # 初始化 MongoDB 管理器
        # if config is None:
        #     config = MongoDBConfig(
        #         host="47.120.44.223",
        #         port=27017,
        #         database="test_db"
        #     )
        # if manager_name is None:
        #     manager_name = "test-2026-01-22"
        # if mongdb_manager is None:
        #     factory = MongoDBManagerFactory()
        #     self.mongdb_manager = factory.create_manager(
        #         config=config,
        #         manager_name=manager_name
        #     )

        # Store the base input directory and workspace
        self.base_input_dir = Path(input_dir)
        self.workspace = workspace
        self.supported_extensions = supported_extensions
        self.indexed_files = set()

        # Create workspace-specific input directory
        # If workspace is provided, create a subdirectory for data isolation
        if workspace:
            self.input_dir = self.base_input_dir / workspace
        else:
            self.input_dir = self.base_input_dir

        # Create input directory if it doesn't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)

    async def scan_directory_for_new_files(self) -> List[Path]:
        """Scan input directory for new files"""
        new_files = []
        for ext in self.supported_extensions:
            logger.debug(f"Scanning for {ext} files in {self.input_dir}")
            for file_path in self.input_dir.glob(f"*{ext}"):
                if file_path not in self.indexed_files:
                    new_files.append(file_path)
        return new_files

    async def mark_as_indexed(self, file_path: Path):
        self.indexed_files.add(file_path)

    async def is_supported_file(self, filename: str) -> Tuple[bool, tuple]:
        check_result = any(filename.lower().endswith(ext) for ext in self.supported_extensions)
        return check_result, self.supported_extensions

    async def create_one(self, collection_name, document) -> str:
        """创建单个资源"""
        try:
            doc = document(exclude={"id"}, by_alias=True)
            result = super().insert_one(collection_name, doc)
            logger.debug(f"资源已创建: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"创建资源失败: {error_info}")
            raise Exception(f"创建资源失败: {error_info}")

    async def create_batch(self, collection_name, documents) -> List[str]:
        """批量创建资源（性能优化）"""
        if not documents:
            return []
        try:
            docs = [r.dict(exclude={"id"}, by_alias=True) for r in documents]
            result = super().insert_many(collection_name, docs)
            logger.info(f"批量创建资源: {len(result.inserted_ids)} 条")
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"批量创建document资源失败: {error_info}")
            raise Exception(f"批量创建document资源失败: {error_info}")

    async def find_by_resource_id(self, collection_name: str, resource_id: str) -> Optional[Dict]:
        """按资源ID查询"""
        try:
            doc = super().find_one(collection_name, {"resource_id": ObjectId(resource_id)})
            return doc
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"单个查询资源失败: {error_info}")
            raise Exception(f"单个查询资源失败: {error_info}")

    async def find_by_ids(self,
                    collection_name: str,
                    resource_ids: List[str],
                    projection: Optional[Dict] = None,
                    sort: Optional[List[tuple]] = None,
                    skip: int = 0,
                    limit: int = 0
                    ) -> List[Dict]:
        """按资源ID列表批量查询"""
        if not resource_ids:
            return []
        try:
            docs = super().find_many(collection_name, {"resource_id": {"$in": resource_ids}}, projection, sort, skip, limit)
            return docs
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"批量查询资源失败: {error_info}")
            raise Exception(f"批量查询资源失败: {error_info}")

    async def find_by_user_id(self,
                        collection_name: str,
                        user_id: str,
                        projection: Optional[Dict] = None
                        ) -> Dict:
        """按用户ID查询"""
        try:
            doc = super().find_one(collection_name, {"user_id": user_id}, projection)
            return doc
        except Exception as e:
            logger.error(f"查询用户资源失败: {e}")
            raise

    async def find_by_type(self, collection_name: str, resource_type:str, projection: Optional[Dict] = None) -> Optional[Dict]:
        """按资源类型查询"""
        try:
            doc = super().find_one(collection_name, {"resource_type": resource_type}, projection)
            return doc
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"查询资源类型失败: {error_info}")
            raise Exception(f"查询资源类型失败: {error_info}")

    async def find_by_status(self, collection_name: str, status: str, projection: Optional[Dict] = None) -> Dict:
        """按处理状态查询"""
        try:
            doc = super().find_one(collection_name, {"processing.status": status}, projection)
            return doc
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"查询处理状态失败: {error_info}")
            raise Exception(f"查询处理状态失败: {error_info}")

    async def find_by_file_hash(self, collection_name, file_hash: str, projection: Optional[Dict] = None) -> Tuple[Optional[Dict],str]:
        """按文件哈希查询（用于去重）"""
        try:
            doc = super().find_one(collection_name, {"metadata.file_hash": file_hash}, projection)
            return doc, ""
        except Exception as e:
            error_info = traceback.format_exc()
            error_info_ = f"查询文件哈希失败: {error_info}"
            logger.error(error_info_)
            return None, error_info_

    async def find_by_file_hashes(self,
                            collection_name: str,
                            file_hashes: List[str],
                            projection: Optional[Dict] = None,
                            sort: Optional[List[tuple]] = None,
                            skip: int = 0,
                            limit: int = 0
                            ) -> Dict[str, Dict]:
        """按文件哈希列表批量查询（性能优化）"""
        if not file_hashes:
            return {}
        try:
            result = {}
            docs = super().find_many(collection_name, {"resource_id": {"$in": file_hashes}}, projection, sort, skip,
                                     limit)
            for doc in docs:
                file_hash = doc.get("metadata", {}).get("file_hash")
                result[file_hash] = doc
            return result
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"批量查询文件哈希失败: {error_info}")
            raise Exception(f"批量查询文件哈希失败: {error_info}")

    def find_by_user_and_file_hashes(self,
                                     collection_name: str,
                                     user_id: str,
                                     file_hashes: List[str],
                                     projection: Optional[Dict] = None,
                                     sort: Optional[List[tuple]] = None,
                                     skip: int = 0,
                                     limit: int = 0
                                     ) -> Dict[str, Dict]:
        """按用户ID和文件哈希列表批量查询（性能优化）"""
        if not file_hashes:
            return {}

        try:
            result = {}
            docs = super().find_many(collection_name,
                                     {"user_id": user_id,"metadata.file_hash": {"$in": file_hashes}}, projection, sort, skip,
                                     limit
                                     )
            for doc in docs:
                file_hash = doc.get("metadata", {}).get("file_hash")
                result[file_hash] = doc
            return result
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"按用户和文件哈希批量查询失败: {error_info}")
            raise Exception(f"按用户和文件哈希批量查询失败: {error_info}")

    def update_status(self,
                      collection_name: str,
                      resource_id: str,
                      status: str,
                      error_message: Optional[str] = None
                      ):
        """更新处理状态"""
        try:
            update_data = {
                "processing.status": status,
                "updated_at": datetime.utcnow()
            }
            if error_message:
                update_data["processing.error_message"] = error_message

            super().update_one(
                collection_name,
                {"resource_id": resource_id},
                {"$set": update_data}
            )
            logger.debug(f"资源状态已更新: {resource_id} -> {status}")
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"更新资源状态失败: {error_info}")
            raise Exception(f"更新资源状态失败: {error_info}")

    def update_batch_status(self,
                            collection_name: str,
                            updates: List[Tuple[str, str, Optional[str]]]
                            ):
        """批量更新处理状态（性能优化）"""
        if not updates:
            return

        try:
            operations = []
            for resource_id, status, error_message in updates:
                update_data = {
                    "processing.status": status,
                    "updated_at": datetime.utcnow()
                }
                if error_message:
                    update_data["processing.error_message"] = error_message

                operations.append(
                    UpdateOne({"resource_id": resource_id}, {"$set": update_data})
                )

            if operations:
                result = super().bulk_write(collection_name, operations)
                logger.info(f"批量更新资源状态: {result["modified_count"]} 条")
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"批量更新资源状态失败: {error_info}")
            raise Exception(f"批量更新资源状态失败: {error_info}")

    def delete(self,
               collection_name: str,
               resource_id: str
               ):
        """删除资源"""
        try:
            result = super().delete_one(collection_name, {"resource_id": resource_id})
            logger.debug(f"资源已删除: {resource_id}")
            return result.deleted_count > 0
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"删除资源失败: {error_info}")
            raise

    def count_by_user(self,
                      collection_name: str,
                      user_id: str
                      ) -> int:
        """统计用户的资源数量"""
        try:
            count = super().count_documents(collection_name, {"user_id": user_id})
            return count
        except Exception as e:
            error_info = traceback.format_exc()
            logger.error(f"统计用户资源失败: {error_info}")
            return 0


class DocumentManagerFactory:
    """动态配置单例管理器"""
    _instance: Optional[DocumentManager] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_document_instance(cls, input_dir: str="", workspace: str = "") -> DocumentManager:
        """获取配置单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = DocumentManager(input_dir, workspace)
        return cls._instance