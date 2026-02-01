#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 11:53
# @Author  : CongPeiQiang
# @File    : documents.py
# @Software: PyCharm
import asyncio
import os
import shutil
import traceback
from datetime import datetime, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File

from app.core.file_processor.document_processor import DocumentManagerFactory, DocumentManager
from app.core.mongodb_processor.mongodb_manager import MongoDBConfig
from app.schemas.notebook.document import InsertResponse
from app.schemas.test_to_sql.response import ResponseBuilder
from app.services.notebook.documents import DocumentService
from app.utils.calculate_resource_hash import generate_track_id, calculate_resource_hash
from app.logger.logger import AppLogger
from app.utils.utils import compute_mdhash_id

router = APIRouter()
from fastapi import Request

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

@router.post("/upload", response_model=InsertResponse, summary="文档上传-summary", description="pdf文档上传-description")
async def upload_to_input_dir(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
):
    # 初始化documents处理器实例
    try:
        # 创建主数据库管理器
        mongdb_config = MongoDBConfig(
            host="localhost",
            port=27017,
            database="main_db"
        )
        doc_manager: DocumentManager = DocumentManagerFactory.get_document_instance(mongdb_config)
        logger.info(f"初始化Document Manager成功")
    except Exception as e:
        error_info = traceback.format_exc()
        error_info_ = f"初始化documents处理器实例 异常: {error_info}"
        logger.error(error_info_)
        response = InsertResponse(
            status="failure",
            message=error_info_,
            track_id="",
            code=400
        )
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    try:
        file_content = file.file
        filename = file.filename
        logger.info(f"解析出文件名: {filename}")
    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(error_info)
        response = InsertResponse(
            status="failure",
            message=error_info,
            track_id="",
            code=400
        )
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    try:
        # 根据文件内容生成哈希
        file_hash = calculate_resource_hash(file_content)
        file_hash_add_filename = file_hash + "_" + filename
        logger.info(f"根据文件内容生成哈希: {file_hash_add_filename}")
    except Exception as e:
        error_info = traceback.format_exc()
        error_info_ = f"根据文件内容生成哈希 异常:{error_info}"
        logger.error(error_info_)
        response = InsertResponse(
            status="failure",
            message=error_info_,
            track_id="",
            code=400
        )
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 检查是否支持上传的文件类型
    response = await DocumentService.is_supported_file(doc_manager, filename)
    logger.info(f"检查是否支持上传的文件类型: {response.status}")
    if response.status != "success":
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 基于mongdb检查是否存在文件记录
    response = await DocumentService.find_by_file_from_mongdb(file_hash_add_filename, file_content, doc_manager, collection_name="test_db")
    if response.status != "success":
        # return response
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 检查存储目录中是否存在上传的文件
    response = await DocumentService.find_by_file_from_local(file_hash_add_filename, doc_manager)
    if response.status != "success":
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 保存上传文件(background_tasks)
    track_id = generate_track_id("upload")
    file_path=os.path.join("./", file_hash_add_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    background_tasks.add_task(doc_manager.pipeline_index_file, Path(file_path), track_id, collection_name="test_db")
    return await ResponseBuilder.success(data=InsertResponse(
        status="success",
        message=f"File '{filename}' uploaded successfully. Processing will continue in background.",
        track_id=track_id,
        code=200)
    )