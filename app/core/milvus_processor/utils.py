#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 11:00
# @Author  : CongPeiQiang
# @File    : utils.py
# @Software: PyCharm
"""
Milvus工具函数
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from tqdm import tqdm


def setup_logging(log_level: str = "INFO", log_format: str = None):
    """设置日志"""
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format
    )


def format_timestamp(timestamp: float = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def save_to_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """保存数据到JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logging.error(f"保存JSON失败: {e}")
        return False


def load_from_json(file_path: str) -> Optional[Any]:
    """从JSON文件加载数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载JSON失败: {e}")
        return None


def validate_json_structure(data: Any, expected_type: type) -> bool:
    """验证JSON结构"""
    if not isinstance(data, expected_type):
        logging.error(f"数据类型错误: 期望 {expected_type}, 实际 {type(data)}")
        return False
    return True


def batch_process(items: List[Any], batch_size: int = 100, desc: str = "处理"):
    """批处理生成器"""
    for i in tqdm(range(0, len(items), batch_size), desc=desc):
        yield items[i:i + batch_size]


def measure_time(func):
    """测量函数执行时间的装饰器"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logging.info(f"函数 {func.__name__} 执行时间: {end_time - start_time:.2f}秒")
        return result

    return wrapper


class Timer:
    """计时器类"""

    def __init__(self, name: str = "操作"):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logging.info(f"开始 {self.name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if exc_type is None:
            logging.info(f"{self.name} 完成，耗时: {elapsed:.2f}秒")
        else:
            logging.error(f"{self.name} 失败，耗时: {elapsed:.2f}秒")

    def get_elapsed(self) -> float:
        """获取经过的时间"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time