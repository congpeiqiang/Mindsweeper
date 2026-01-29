#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 12:02
# @Author  : CongPeiQiang
# @File    : config.py
# @Software: PyCharm
"""
Milvus配置管理器
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import logging
import os


@dataclass
class MilvusConfig:

    def __init__(self, milvus_uri:str, ollama_uri:str, timeout:float, default_db:str, default_collection:str, enable_dynamic_field:bool, chunk_size:int, chunk_overlap:int, batch_size:int, embedding_model:str, embedding_dim:int, default_search_limit:int, bm25_k1:float, bm25_b:float):
        """Milvus配置类"""
        # 服务器配置
        self.milvus_uri: str = milvus_uri
        self.ollama_uri: str = ollama_uri
        self.timeout: float = timeout

        # 数据库配置
        self.default_db: str = default_db

        # 集合配置
        self.default_collection: str = default_collection
        self.enable_dynamic_field: bool = enable_dynamic_field

        # 数据分块配置
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.batch_size: int = batch_size

        # 嵌入模型配置
        self.embedding_model: str = embedding_model
        self.embedding_dim: int = embedding_dim

        # 搜索配置
        self.default_search_limit: int = default_search_limit
        self.bm25_k1: float = bm25_k1
        self.bm25_b: float = bm25_b
    def validate(self) -> bool:
        """验证配置"""
        if not self.milvus_uri:
            raise ValueError("Milvus URI不能为空")
        if not self.ollama_uri:
            raise ValueError("Ollama URI不能为空")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size必须大于0")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap不能为负数")
        if self.batch_size <= 0:
            raise ValueError("batch_size必须大于0")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# class ConfigManager:
#     """配置管理器"""
#
#     @staticmethod
#     def load_from_env() -> MilvusConfig:
#         """从环境变量加载配置"""
#         config = MilvusConfig()
#
#         # 从环境变量读取配置
#         env_mapping = {
#             'MILVUS_URI': 'milvus_uri',
#             'OLLAMA_URI': 'ollama_uri',
#             'MILVUS_TIMEOUT': 'timeout',
#             'MILVUS_DEFAULT_DB': 'default_db',
#             'MILVUS_DEFAULT_COLLECTION': 'default_collection',
#             'MILVUS_CHUNK_SIZE': 'chunk_size',
#             'MILVUS_BATCH_SIZE': 'batch_size',
#             'MILVUS_LOG_LEVEL': 'log_level',
#         }
#
#         for env_key, config_key in env_mapping.items():
#             if env_value := os.getenv(env_key):
#                 # 类型转换
#                 current_type = type(getattr(config, config_key))
#                 try:
#                     if current_type == int:
#                         setattr(config, config_key, int(env_value))
#                     elif current_type == float:
#                         setattr(config, config_key, float(env_value))
#                     elif current_type == bool:
#                         setattr(config, config_key, env_value.lower() in ['true', '1', 'yes'])
#                     else:
#                         setattr(config, config_key, env_value)
#                 except ValueError:
#                     logging.warning(f"无法将环境变量 {env_key}={env_value} 转换为 {current_type}")
#
#         config.validate()
#         return config
#
#     @staticmethod
#     def load_from_json(file_path: str) -> MilvusConfig:
#         """从JSON文件加载配置"""
#         import json
#         with open(file_path, 'r', encoding='utf-8') as f:
#             config_dict = json.load(f)
#
#         config = MilvusConfig()
#         config.update_from_dict(config_dict)
#         config.validate()
#         return config