#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 16:44
# @Author  : CongPeiQiang
# @File    : documents.py
# @Software: PyCharm
import os
import traceback

from app.core.file_processor.document_processor import DocumentManagerFactory
from app.schemas.notebook.document import InsertResponse
from app.utils.calculate_resource_hash import calculate_resource_hash
from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class DocumentService:
    @classmethod
    async def find_by_file_from_mongdb(cls, file_hash_add_filename, file_content, doc_manager, collection_name="test_db"):

        try:
            # Check if filename already exists in doc_status storage
            existing_doc_data, info = await doc_manager.find_by_file_hash(collection_name=collection_name,
                                                                          file_hash=file_hash_add_filename)
            if existing_doc_data:
                # Get document status and track_id from existing document
                status = existing_doc_data.get("status", "unknown")
                # Use `or ""` to handle both missing key and None value (e.g., legacy rows without track_id)
                existing_track_id = existing_doc_data.get("track_id") or ""
                return InsertResponse(
                    status="duplicated",
                    message=f"File '{file_hash_add_filename}' already exists in document storage (Status: {status}).",
                    track_id=existing_track_id,
                )
            else:
                return InsertResponse(
                    status="failure",
                    message=info,
                    track_id="",
                )

            file_path = doc_manager.input_dir / filename
            # Check if file already exists in file system
            if file_path.exists():
                return InsertResponse(
                    status="duplicated",
                    message=f"File '{safe_filename}' already exists in the input directory.",
                    track_id="",
                )

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            track_id = generate_track_id("upload")

            # Add to background tasks and get track_id
            background_tasks.add_task(pipeline_index_file, rag, file_path, track_id)

            return InsertResponse(
                status="success",
                message=f"File '{safe_filename}' uploaded successfully. Processing will continue in background.",
                track_id=track_id,
            )

        except Exception as e:
            logger.error(f"Error /documents/upload: {file.filename}: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def find_by_file_from_local(cls, file_hash_add_filename, file_content):
        file_save_dir="./upload"
        file_save_path = os.path.join(file_save_dir, file_hash_add_filename)
        if os.path.exists(file_save_path):
            return InsertResponse(
                status="duplicated",
                message=f"存在相同文件: {file_save_path}",
                track_id="",
            )
        else:
            return InsertResponse(
                status="success",
                message="",
                track_id=""
            )

    @classmethod
    async def is_supported_file(cls, filename: str) -> InsertResponse:
        doc_manager = None
        # 初始化documents处理器实例
        try:
            doc_manager = DocumentManagerFactory.get_document_instance()
        except Exception as e:
            error_info = traceback.format_exc()
            error_info_ = f"初始化documents处理器实例 异常: {error_info}"
            logger.error(error_info_)
            return InsertResponse(
                status="failure",
                message=error_info_,
                track_id="",
            )
        result, supported_extensions = doc_manager.is_supported_file(filename)
        if result:
            return InsertResponse(
                status="failure",
                message=f"不支持的文件类型{filename.lower()},支持的文件类型列表为{supported_extensions}",
                track_id="",
            )
        else:
            return InsertResponse(
                    status="success",
                    message=f"支持的文件类型{filename.lower()},支持的文件类型列表为{supported_extensions}",
                    track_id="",
                )
