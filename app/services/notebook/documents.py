#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 16:44
# @Author  : CongPeiQiang
# @File    : documents.py
# @Software: PyCharm
import os
import traceback

from app.core.file_processor.document_processor import DocumentManagerFactory, DocumentManager
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
                return InsertResponse(
                    status="duplicated",
                    message=f"File '{file_hash_add_filename}' already exists in document storage (Status: {status}).",
                    file_id=file_hash_add_filename,
                    code=400,
                )
            else:
                return InsertResponse(
                    status="success",
                    message=info,
                    file_id=""
                )

            # file_path = doc_manager.input_dir / filename
            # # Check if file already exists in file system
            # if file_path.exists():
            #     return InsertResponse(
            #         status="duplicated",
            #         message=f"File '{safe_filename}' already exists in the input directory.",
            #         file_id="",
            #     )
            #
            # with open(file_path, "wb") as buffer:
            #     shutil.copyfileobj(file.file, buffer)
            #
            # track_id = generate_track_id("upload")
            #
            # # Add to background tasks and get track_id
            # background_tasks.add_task(pipeline_index_file, rag, file_path, track_id)
            #
            # return InsertResponse(
            #     status="success",
            #     message=f"File '{safe_filename}' uploaded successfully. Processing will continue in background.",
            #     file_id=track_id,
            # )

        except Exception as e:
            logger.error(f"Error /documents/upload: {traceback.format_exc()}")
            return InsertResponse(
                status="failure",
                message=traceback.format_exc(),
                file_id="",
                code=400,
            )

    @classmethod
    async def find_by_file_from_local(cls, file_hash_add_filename, file_content):
        file_save_dir="./upload"
        file_save_path = os.path.join(file_save_dir, file_hash_add_filename)
        if os.path.exists(file_save_path):
            return InsertResponse(
                status="duplicated",
                message=f"存在相同文件: {file_save_path}",
                file_id="",
            )
        else:
            return InsertResponse(
                status="success",
                message="",
                file_id=""
            )

    @classmethod
    async def is_supported_file(cls, doc_manager: DocumentManager,  filename: str) -> InsertResponse:
        result, supported_extensions = await doc_manager.is_supported_file(filename)
        if result:
            return InsertResponse(
                status="success",
                message=f"支持的文件类型{filename.lower()},支持的文件类型列表为{supported_extensions}",
                file_id=""
            )
        else:
            return InsertResponse(
                    status="failure",
                    message=f"不支持的文件类型{filename.lower()},支持的文件类型列表为{supported_extensions}",
                    file_id="",
                )
