#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 11:53
# @Author  : CongPeiQiang
# @File    : documents.py
# @Software: PyCharm
import os
import traceback

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File

from app.core.file_processor.document_processor import DocumentManagerFactory
from app.schemas.notebook.document import InsertResponse
from app.services.notebook.documents import DocumentService
from app.utils.calculate_resource_hash import generate_track_id, calculate_resource_hash
from app.logger.logger import AppLogger

router = APIRouter()
from fastapi import Request

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

@router.post("/upload", response_model=InsertResponse)
async def upload_to_input_dir(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
):
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

    try:
        file_content = file.file
        filename = file.filename
    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(error_info)
        return InsertResponse(
            status="failure",
            message=error_info,
            track_id="",
        )

    try:
        # 根据文件内容生成哈希
        file_hash = calculate_resource_hash(file_content)
        file_hash_add_filename = filename + "_" + file_hash
    except Exception as e:
        error_info = traceback.format_exc()
        error_info_ = f"根据文件内容生成哈希 异常:{error_info}"
        logger.error(error_info_)
        return InsertResponse(
            status="failure",
            message=error_info_,
            track_id="",
        )

    # 检查是否支持上传的文件类型
    response = await DocumentService.is_supported_file(file_hash_add_filename)
    if response.status != "success":
        return response

    # 基于mongdb检查是否存在文件记录
    response = await DocumentService.find_by_file_from_mongdb(file_hash_add_filename, file_content, doc_manager, collection_name="test_db")
    if response.status != "success":
        return response

    # 检查存储目录中是否存在上传的文件
    response = await DocumentService.find_by_file_from_local(file_hash_add_filename, doc_manager)
    if response.status != "success":
        return response

    # 保存上传文件(background_tasks)
    track_id = generate_track_id("upload")
    file_path=os.path.join("./", file_hash_add_filename)
    background_tasks.add_task(pipeline_index_file, rag, file_path, track_id)
    return response