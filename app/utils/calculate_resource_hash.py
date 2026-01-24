#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 14:27
# @Author  : CongPeiQiang
# @File    : calculate_resource_hash.py
# @Software: PyCharm
import hashlib
import os
import uuid
from datetime import datetime
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
        else:
            return hashlib.md5(str(data).encode()).hexdigest()
    except Exception as e:
        logger.warning(f"计算资源哈希失败: {e}")
        return str(uuid.uuid4())  # 返回唯一ID避免误判重复

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