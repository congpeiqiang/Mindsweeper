#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 11:02
# @Author  : CongPeiQiang
# @File    : config.py
# @Software: PyCharm
"""
Milvus配置管理器
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging
import os


@dataclass
class MilvusConfig:
    """Milvus配置类"""

    # 服务器配置
    milvus_uri: str = "http://localhost:19530"
    ollama_uri: str = "http://localhost:11434"
    timeout: float = 30.0

    # 数据库配置
    default_db: str = "milvus_database"

    # 集合配置
    default_collection: str = "default_collection"
    enable_dynamic_field: bool = True

    # 数据分块配置
    chunk_size: int = 800
    chunk_overlap: int = 100
    batch_size: int = 50

    # 嵌入模型配置
    embedding_model: str = "qwen3-embedding:0.6b"
    embedding_dim: int = 1024

    # 搜索配置
    default_search_limit: int = 10
    bm25_k1: float = 1.2
    bm25_b: float = 0.75

    # 日志配置
    log_level: str = "INFO"
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

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

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }


class ConfigManager:
    """配置管理器"""

    @staticmethod
    def load_from_env() -> MilvusConfig:
        """从环境变量加载配置"""
        config = MilvusConfig()

        # 从环境变量读取配置
        env_mapping = {
            'MILVUS_URI': 'milvus_uri',
            'OLLAMA_URI': 'ollama_uri',
            'MILVUS_TIMEOUT': 'timeout',
            'MILVUS_DEFAULT_DB': 'default_db',
            'MILVUS_DEFAULT_COLLECTION': 'default_collection',
            'MILVUS_CHUNK_SIZE': 'chunk_size',
            'MILVUS_BATCH_SIZE': 'batch_size',
            'MILVUS_LOG_LEVEL': 'log_level',
        }

        for env_key, config_key in env_mapping.items():
            if env_value := os.getenv(env_key):
                # 类型转换
                current_type = type(getattr(config, config_key))
                try:
                    if current_type == int:
                        setattr(config, config_key, int(env_value))
                    elif current_type == float:
                        setattr(config, config_key, float(env_value))
                    elif current_type == bool:
                        setattr(config, config_key, env_value.lower() in ['true', '1', 'yes'])
                    else:
                        setattr(config, config_key, env_value)
                except ValueError:
                    logging.warning(f"无法将环境变量 {env_key}={env_value} 转换为 {current_type}")

        config.validate()
        return config

    @staticmethod
    def load_from_json(file_path: str) -> MilvusConfig:
        """从JSON文件加载配置"""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        config = MilvusConfig()
        config.update_from_dict(config_dict)
        config.validate()
        return config