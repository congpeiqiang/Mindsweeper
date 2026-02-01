#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 14:27
# @Author  : CongPeiQiang
# @File    : calculate_resource_hash.py
# @Software: PyCharm
import hashlib
import io
import os
import uuid
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import Any

from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

def calculate_resource_hash(data: Any) -> str:
    """计算资源的哈希值用于去重"""
    try:
        if isinstance(data, bytes):
            return hashlib.md5(data).hexdigest()
        elif isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        elif isinstance(data, dict):
            # 对于字典类型（如知识库），使用关键字段计算哈希
            key_str = str(sorted(data.items()))
            return hashlib.md5(key_str.encode()).hexdigest()
        elif isinstance(data, SpooledTemporaryFile):
            return _hash_file_object(data)
        else:
            return hashlib.md5(str(data).encode()).hexdigest()
    except Exception as e:
        logger.warning(f"计算资源哈希失败: {e}")
        return str(uuid.uuid4())  # 返回唯一ID避免误判重复


def _hash_file_object(file_obj, buffer_size=65536) -> str:
    """
    计算文件对象的哈希值

    Args:
        file_obj: 支持read()方法的文件对象
        buffer_size: 读取缓冲区大小

    Returns:
        MD5哈希字符串
    """
    md5_hash = hashlib.md5()

    # 保存原始位置
    original_position = file_obj.tell() if hasattr(file_obj, 'tell') else 0

    try:
        # 重置到文件开头
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0, io.SEEK_SET)

        # 读取并计算哈希
        while True:
            data = file_obj.read(buffer_size)
            if not data:
                break
            md5_hash.update(data)

        # 恢复原始位置（如果支持）
        if hasattr(file_obj, 'seek'):
            file_obj.seek(original_position, io.SEEK_SET)

        return md5_hash.hexdigest()

    except Exception as e:
        # 发生错误时尝试恢复位置
        if hasattr(file_obj, 'seek'):
            try:
                file_obj.seek(original_position, io.SEEK_SET)
            except:
                pass
        raise e

def generate_track_id(prefix: str = "upload") -> str:
    """Generate a unique tracking ID with timestamp and UUID

    Args:
        prefix: Prefix for the track ID (e.g., 'upload', 'insert')

    Returns:
        str: Unique tracking ID in format: {prefix}_{timestamp}_{uuid}
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    return f"{prefix}_{timestamp}_{unique_id}"