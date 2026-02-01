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
            database="notebook"
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
            file_id="",
            code=400
        )
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    try:
        file_content = file.file
        filename = file.filename
        filename_stem = Path(file.filename).stem # 获取文件后缀(去除后缀)
        filename_suffix = Path(file.filename).suffix # 获取文件后缀
        logger.info(f"解析出文件名: {filename}")
    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(error_info)
        response = InsertResponse(
            status="failure",
            message=error_info,
            file_id="",
            code=400
        )
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    try:
        # 根据文件内容生成哈希
        file_hash = calculate_resource_hash(file_content)
        file_hash_add_filename_stem = file_hash + "_" + filename_stem
        logger.info(f"根据文件内容生成哈希: {file_hash_add_filename_stem}")
    except Exception as e:
        error_info = traceback.format_exc()
        error_info_ = f"根据文件内容生成哈希 异常:{error_info}"
        logger.error(error_info_)
        response = InsertResponse(
            status="failure",
            message=error_info_,
            file_id="",
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
    response = await DocumentService.find_by_file_from_mongdb(file_hash_add_filename_stem, doc_manager, collection_name="mindsweeper")
    if response.status != "success":
        # return response
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 检查存储目录中是否存在上传的文件
    response = await DocumentService.find_by_file_from_local(file_hash_add_filename_stem, doc_manager)
    if response.status != "success":
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response

    # 保存上传文件
    file_path=os.path.join("./upload", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # 异步写入文件
    async with aiofiles.open(file_path, "wb") as buffer:
        # 分块读取和写入，避免内存溢出
        chunk_size = 1024 * 1024  # 1MB
        while chunk := await file.read(chunk_size):
            await buffer.write(chunk)

    # 上传文件记录至mongdb
    # 计算文件大小、文件类型、文件id、文件路径
    try:
        size_bytes = Path(file_path).stat().st_size
    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(error_info)
        response = InsertResponse(
            status="failure",
            message=error_info,
            file_id=file_hash_add_filename_stem,
            code=400
        )
    file_info = {"file_id":file_hash_add_filename_stem,
                 "status":"success",
                 "file_type":filename_suffix,
                 "file_size":size_bytes,
                 "file_path":file_path,
                 "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "update_time":None
                 }
    response = await DocumentService.insert_file_record_to_mongdb(doc_manager, file_info, file_hash_add_filename_stem, collection_name="mindsweeper")
    if response.status != "success":
        fail_response = await ResponseBuilder.fail(data=response)
        return fail_response
    return await ResponseBuilder.success(data=InsertResponse(
        status="success",
        message=f"File '{filename}' uploaded successfully.",
        file_id=file_hash_add_filename_stem,
        code=200,
        file_size=size_bytes,
        file_path=file_path)
    )