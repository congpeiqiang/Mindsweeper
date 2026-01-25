#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 12:15
# @Author  : CongPeiQiang
# @File    : document_processor.py
# @Software: PyCharm
import asyncio
import os
import threading
import traceback
from datetime import datetime, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Union, Any

import aiofiles
from bson import ObjectId
from pymongo import UpdateOne, InsertOne

from app.core.file_processor.document_enum import DocStatus
from app.core.mongodb_processor.mongodb_manager import MongoDBConfig, MongoDBManager, MongoDBConnection
from app.logger.logger import AppLogger
from app.utils.calculate_resource_hash import generate_track_id
from app.utils.utils import compute_mdhash_id

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

# Temporary file prefix
temp_prefix = "__tmp__"

class DocumentManager(MongoDBManager):
    def __init__(
        self,
        mongdb_config: MongoDBConfig,
        input_dir: str,
        workspace: str = "",  # New parameter for workspace isolation
        # supported_extensions: tuple = (
        #     ".txt",
        #     ".md",
        #     ".mdx",  # MDX (Markdown + JSX)
        #     ".pdf",
        #     ".docx",
        #     ".pptx",
        #     ".xlsx",
        #     ".rtf",  # Rich Text Format
        #     ".odt",  # OpenDocument Text
        #     ".tex",  # LaTeX
        #     ".epub",  # Electronic Publication
        #     ".html",  # HyperText Markup Language
        #     ".htm",  # HyperText Markup Language
        #     ".csv",  # Comma-Separated Values
        #     ".json",  # JavaScript Object Notation
        #     ".xml",  # eXtensible Markup Language
        #     ".yaml",  # YAML Ain't Markup Language
        #     ".yml",  # YAML
        #     ".log",  # Log files
        #     ".conf",  # Configuration files
        #     ".ini",  # Initialization files
        #     ".properties",  # Java properties files
        #     ".sql",  # SQL scripts
        #     ".bat",  # Batch files
        #     ".sh",  # Shell scripts
        #     ".c",  # C source code
        #     ".cpp",  # C++ source code
        #     ".py",  # Python source code
        #     ".java",  # Java source code
        #     ".js",  # JavaScript source code
        #     ".ts",  # TypeScript source code
        #     ".swift",  # Swift source code
        #     ".go",  # Go source code
        #     ".rb",  # Ruby source code
        #     ".php",  # PHP source code
        #     ".css",  # Cascading Style Sheets
        #     ".scss",  # Sassy CSS
        #     ".less",  # LESS CSS
        # ),
        supported_extensions: tuple = (".pdf", ".md"),
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
        connection = MongoDBConnection(mongdb_config)
        super().__init__(connection)
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

    def _convert_with_docling(self,file_path: Path) -> str:
        """Convert document using docling (synchronous).

        Args:
            file_path: Path to the document file

        Returns:
            str: Extracted markdown content
        """
        from docling.document_converter import DocumentConverter  # type: ignore

        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()

    def _extract_pdf_pypdf(self,file_bytes: bytes, password: str = None) -> str:
        """Extract PDF content using pypdf (synchronous).

        Args:
            file_bytes: PDF file content as bytes
            password: Optional password for encrypted PDFs

        Returns:
            str: Extracted text content

        Raises:
            Exception: If PDF is encrypted and password is incorrect or missing
        """
        from pypdf import PdfReader  # type: ignore

        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)

        # Check if PDF is encrypted
        if reader.is_encrypted:
            if not password:
                raise Exception("PDF is encrypted but no password provided")

            decrypt_result = reader.decrypt(password)
            if decrypt_result == 0:
                raise Exception("Incorrect PDF password")

        # Extract text from all pages
        content = ""
        for page in reader.pages:
            content += page.extract_text() + "\n"

        return content

    @lru_cache(maxsize=1)
    def _is_docling_available(self,) -> bool:
        """Check if docling is available (cached check).

        This function uses lru_cache to avoid repeated import attempts.
        The result is cached after the first call.

        Returns:
            bool: True if docling is available, False otherwise
        """
        try:
            import docling  # noqa: F401  # type: ignore[import-not-found]

            return True
        except ImportError:
            return False

    async def pipeline_index_file(self, file_path: Path, track_id: str = None, collection_name="test_db"):
        """Index a file with track_id

        Args:
            :param file_path: Path to the saved file
            :param track_id: Optional tracking ID
            :param collection_name:
        """
        try:
            success, returned_track_id = await self.pipeline_enqueue_file(file_path, track_id, collection_name="test_db")
            # if success:
            #     await self.apipeline_process_enqueue_documents()

        except Exception as e:
            logger.error(f"Error indexing file {file_path.name}: {str(e)}")
            logger.error(traceback.format_exc())

    async def apipeline_enqueue_error_documents(self,
            error_files: list[dict[str, Any]],
            track_id: str | None = None,
            collection_name="test_db"
    ) -> None:
        """
        Record file extraction errors in doc_status storage.

        This function creates error document entries in the doc_status storage for files
        that failed during the extraction process. Each error entry contains information
        about the failure to help with debugging and monitoring.

        Args:
            :param error_files: List of dictionaries containing error information for each failed file.
                Each dictionary should contain:
                - file_path: Original file name/path
                - error_description: Brief error description (for content_summary)
                - original_error: Full error message (for error_msg)
                - file_size: File size in bytes (for content_length, 0 if unknown)
            :param track_id: Optional tracking ID for grouping related operations
            :param collection_name:

        Returns:
            None
        """
        if not error_files:
            logger.debug("No error files to record")
            return

        # Generate track_id if not provided
        if track_id is None or track_id.strip() == "":
            track_id = generate_track_id("error")

        error_docs: dict[str, Any] = {}
        current_time = datetime.now(timezone.utc).isoformat()

        for error_file in error_files:
            file_path = error_file.get("file_path", "unknown_file")
            error_description = error_file.get(
                "error_description", "File extraction failed"
            )
            original_error = error_file.get("original_error", "Unknown error")
            file_size = error_file.get("file_size", 0)

            # Generate unique doc_id with "error-" prefix
            doc_id_content = f"{file_path}-{error_description}"
            doc_id = compute_mdhash_id(doc_id_content, prefix="error-")

            error_docs[doc_id] = {
                "status": DocStatus.FAILED,
                "content_summary": error_description,
                "content_length": file_size,
                "error_msg": original_error,
                "chunks_count": 0,  # No chunks for failed files
                "created_at": current_time,
                "updated_at": current_time,
                "file_path": file_path,
                "track_id": track_id,
                "metadata": {
                    "error_type": "file_extraction_error",
                },
            }

        # Store error documents in doc_status
        if error_docs:
            operations = [InsertOne(error_docs)]
            self.bulk_write(collection_name, operations)
            # Log each error for debugging
            for doc_id, error_doc in error_docs.items():
                logger.error(
                    f"File processing error: - ID: {doc_id} {error_doc['file_path']}"
                )

    def get_unique_filename_in_enqueued(self, target_dir: Path, original_name: str) -> str:
        """Generate a unique filename in the target directory by adding numeric suffixes if needed

        Args:
            target_dir: Target directory path
            original_name: Original filename

        Returns:
            str: Unique filename (may have numeric suffix added)
        """
        import time

        original_path = Path(original_name)
        base_name = original_path.stem
        extension = original_path.suffix

        # Try original name first
        if not (target_dir / original_name).exists():
            return original_name

        # Try with numeric suffixes 001-999
        for i in range(1, 1000):
            suffix = f"{i:03d}"
            new_name = f"{base_name}_{suffix}{extension}"
            if not (target_dir / new_name).exists():
                return new_name

        # Fallback with timestamp if all 999 slots are taken
        timestamp = int(time.time())
        return f"{base_name}_{timestamp}{extension}"

    async def pipeline_enqueue_file(self, file_path: Path, track_id: str = None, collection_name="test_db"
    ) -> tuple[bool, str]:
        """Add a file to the queue for processing

        Args:
            :param file_path: Path to the saved file
            :param track_id: Optional tracking ID, if not provided will be generated
            :param collection_name:
        Returns:
            tuple: (success: bool, track_id: str)
        """

        # Generate track_id if not provided
        if track_id is None:
            track_id = generate_track_id("unknown")

        try:
            content = ""
            ext = file_path.suffix.lower() # 后缀
            file_size = 0

            # Get file size for error reporting
            try:
                file_size = file_path.stat().st_size
            except Exception:
                file_size = 0

            file = None
            print(file_path)
            try:
                async with aiofiles.open(file_path, "rb") as f:
                    file = await f.read()
            except PermissionError as e:
                error_files = [
                    {
                        "file_path": str(file_path.name),
                        "error_description": "[File Extraction]Permission denied - cannot read file",
                        "original_error": str(e),
                        "file_size": file_size,
                    }
                ]
                await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                logger.error(
                    f"[File Extraction]Permission denied reading file: {file_path.name}"
                )
                return False, track_id
            except FileNotFoundError as e:
                error_files = [
                    {
                        "file_path": str(file_path.name),
                        "error_description": "[File Extraction]File not found",
                        "original_error": str(e),
                        "file_size": file_size,
                    }
                ]
                await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                logger.error(f"[File Extraction]File not found: {file_path.name}")
                return False, track_id
            except Exception as e:
                error_files = [
                    {
                        "file_path": str(file_path.name),
                        "error_description": "[File Extraction]File reading error",
                        "original_error": str(e),
                        "file_size": file_size,
                    }
                ]
                await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                logger.error(
                    f"[File Extraction]Error reading file {file_path.name}: {str(e)}"
                )
                return False, track_id

            # Process based on file type
            try:
                match ext:
                    case ".pdf":
                        document_loading_engine = "Not DOCLING"
                        try:
                            # Try DOCLING first if configured and available
                            if (
                                    document_loading_engine == "DOCLING"
                                    and self._is_docling_available()
                            ):
                                content = await asyncio.to_thread(
                                    self._convert_with_docling, file_path
                                )
                            else:
                                if (
                                        document_loading_engine == "DOCLING"
                                        and not self._is_docling_available()
                                ):
                                    logger.warning(
                                        f"DOCLING engine configured but not available for {file_path.name}. Falling back to pypdf."
                                    )
                                # Use pypdf (non-blocking via to_thread)
                                content = await asyncio.to_thread(
                                    self._extract_pdf_pypdf,
                                    file,
                                    "pdf_decrypt_password",
                                )
                        except Exception as e:
                            error_files = [
                                {
                                    "file_path": str(file_path.name),
                                    "error_description": "[File Extraction]PDF processing error",
                                    "original_error": f"Failed to extract text from PDF: {str(e)}",
                                    "file_size": file_size,
                                }
                            ]
                            await self.apipeline_enqueue_error_documents(
                                error_files, track_id, collection_name
                            )
                            logger.error(
                                f"[File Extraction]Error processing PDF {file_path.name}: {str(e)}"
                            )
                            return False, track_id

            except Exception as e:
                error_files = [
                    {
                        "file_path": str(file_path.name),
                        "error_description": "[File Extraction]File format processing error",
                        "original_error": f"Unexpected error during file extracting: {str(e)}",
                        "file_size": file_size,
                    }
                ]
                await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                logger.error(
                    f"[File Extraction]Unexpected error during {file_path.name} extracting: {str(e)}"
                )
                return False, track_id

            # Insert into the RAG queue
            if content:
                # Check if content contains only whitespace characters
                if not content.strip():
                    error_files = [
                        {
                            "file_path": str(file_path.name),
                            "error_description": "[File Extraction]File contains only whitespace",
                            "original_error": "File content contains only whitespace characters",
                            "file_size": file_size,
                        }
                    ]
                    await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                    logger.warning(
                        f"[File Extraction]File contains only whitespace characters: {file_path.name}"
                    )
                    return False, track_id

                return True, track_id

                # try:
                #     await self.apipeline_enqueue_documents(
                #         content, file_paths=file_path.name, track_id=track_id
                #     )
                #
                #     logger.info(
                #         f"Successfully extracted and enqueued file: {file_path.name}"
                #     )
                #
                #     # Move file to __enqueued__ directory after enqueuing
                #     try:
                #         enqueued_dir = file_path.parent / "__enqueued__"
                #         enqueued_dir.mkdir(exist_ok=True)
                #
                #         # Generate unique filename to avoid conflicts
                #         unique_filename = self.get_unique_filename_in_enqueued(
                #             enqueued_dir, file_path.name
                #         )
                #         target_path = enqueued_dir / unique_filename
                #
                #         # Move the file
                #         file_path.rename(target_path)
                #         logger.debug(
                #             f"Moved file to enqueued directory: {file_path.name} -> {unique_filename}"
                #         )
                #
                #     except Exception as move_error:
                #         logger.error(
                #             f"Failed to move file {file_path.name} to __enqueued__ directory: {move_error}"
                #         )
                #         # Don't affect the main function's success status
                #
                #     return True, track_id
                #
                # except Exception as e:
                #     error_files = [
                #         {
                #             "file_path": str(file_path.name),
                #             "error_description": "Document enqueue error",
                #             "original_error": f"Failed to enqueue document: {str(e)}",
                #             "file_size": file_size,
                #         }
                #     ]
                #     await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                #     logger.error(f"Error enqueueing document {file_path.name}: {str(e)}")
                #     return False, track_id
            else:
                error_files = [
                    {
                        "file_path": str(file_path.name),
                        "error_description": "No content extracted",
                        "original_error": "No content could be extracted from file",
                        "file_size": file_size,
                    }
                ]
                await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
                logger.error(f"No content extracted from file: {file_path.name}")
                return False, track_id
        except Exception as e:
            # Catch-all for any unexpected errors
            try:
                file_size = file_path.stat().st_size if file_path.exists() else 0
            except Exception:
                file_size = 0

            error_files = [
                {
                    "file_path": str(file_path.name),
                    "error_description": "Unexpected processing error",
                    "original_error": f"Unexpected error: {str(e)}",
                    "file_size": file_size,
                }
            ]
            await self.apipeline_enqueue_error_documents(error_files, track_id, collection_name)
            logger.error(f"Enqueuing file {file_path.name} error: {str(e)}")
            logger.error(traceback.format_exc())
            return False, track_id
        finally:
            if file_path.name.startswith(temp_prefix):
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {str(e)}")
class DocumentManagerFactory:
    """动态配置单例管理器"""
    _instance: Optional[DocumentManager] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_document_instance(cls, mongdb_config: MongoDBConfig, input_dir: str="", workspace: str = "") -> DocumentManager:
        """获取配置单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = DocumentManager(mongdb_config, input_dir, workspace)
        return cls._instance