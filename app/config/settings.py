#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/31 14:16
# @Author  : CongPeiQiang
# @File    : settings.py
# @Software: PyCharm
# 应用配置

import os
import threading
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any, ClassVar
from pydantic import ConfigDict, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamicSettings(BaseSettings):
    """
    动态配置类

    核心改进：
    1. 不定义具体的配置字段，完全动态加载
    2. 支持通过环境变量指定配置文件路径
    3. 自动合并环境变量覆盖
    4. 支持热重载（可选）
    """

    # ==================== 配置模型 ====================
    model_config = ConfigDict(
        extra="allow",  # 允许额外字段
        arbitrary_types_allowed=True,
        validate_assignment=True,
        protected_namespaces=()  # 禁用保护命名空间检查
    )

    # ==================== 私有属性 ====================
    _config_path: Optional[str] = PrivateAttr(default=None)
    _yaml_data: Dict[str, Any] = PrivateAttr(default_factory=dict)

    # ==================== 类变量 ====================
    # 配置缓存和锁是类级别的
    _config_cache: ClassVar[Dict[str, Any]] = {}
    _config_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """初始化配置，优先从YAML文件加载"""
        # 确定配置文件路径
        config_path = self._determine_config_path(config_file)

        # 加载YAML配置
        yaml_config = self._load_yaml_config(config_path)

        # 合并配置：YAML配置 < 环境变量 < 直接传入的参数
        merged_config = {}
        merged_config.update(yaml_config)  # YAML基础配置

        # 处理环境变量（自动转换数据类型）
        env_overrides = self._extract_env_overrides(merged_config)
        merged_config.update(env_overrides)  # 环境变量覆盖

        merged_config.update(kwargs)  # 直接传入的参数（最高优先级）

        # 调用父类初始化
        super().__init__(**merged_config)

        # 设置私有属性
        self._config_path = config_path
        self._yaml_data = yaml_config

    def _determine_config_path(self, config_file: Optional[str]) -> str:
        """确定配置文件路径"""
        if config_file:
            return config_file
        elif os.getenv("CONFIG_FILE"):
            return os.getenv("CONFIG_FILE")
        else:
            # 默认路径：项目根目录下的 config/config.yaml
            return str(Path(__file__).parent.parent / "config" / "config.yaml")

    def _load_yaml_config(self, config_path: str) -> Dict[str, Any]:
        """加载YAML配置文件"""
        with self._config_lock:
            # 检查缓存
            if config_path in self._config_cache:
                return self._config_cache[config_path].copy()

            try:
                if not os.path.exists(config_path):
                    print(f"警告: 配置文件不存在: {config_path}，使用空配置")
                    return {}

                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}

                # 处理环境变量占位符
                config_data = self._process_env_placeholders(config_data)

                # 缓存配置
                self._config_cache[config_path] = config_data.copy()
                return config_data

            except yaml.YAMLError as e:
                print(f"警告: YAML配置文件格式错误: {config_path} - {e}，使用空配置")
                return {}
            except Exception as e:
                print(f"警告: 加载配置文件失败: {config_path} - {e}，使用空配置")
                return {}

    def _process_env_placeholders(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理环境变量占位符，如 ${VAR_NAME}"""
        import re

        def process_value(value):
            if isinstance(value, str):
                # 匹配 ${VAR_NAME} 格式的环境变量
                match = re.match(r'^\$\{(.+)\}$', value)
                if match:
                    env_var = match.group(1)
                    env_value = os.getenv(env_var)
                    if env_value is None:
                        print(f"警告: 环境变量 {env_var} 未设置，使用空值")
                        return ""
                    return env_value
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_item(item) for item in value]
            return value

        def process_item(item):
            if isinstance(item, dict):
                return {k: process_value(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [process_item(subitem) for subitem in item]
            elif isinstance(item, str):
                match = re.match(r'^\$\{(.+)\}$', item)
                if match:
                    env_var = match.group(1)
                    env_value = os.getenv(env_var)
                    if env_value is None:
                        print(f"警告: 环境变量 {env_var} 未设置，使用空值")
                        return ""
                    return env_value
            return item

        return {k: process_value(v) for k, v in config_data.items()}

    def _extract_env_overrides(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """从环境变量提取配置覆盖"""
        env_overrides = {}

        # 递归遍历配置结构，生成环境变量名映射
        def _traverse_config(config: Dict[str, Any], prefix: str = ""):
            for key, value in config.items():
                env_key = f"{prefix}{key.upper()}" if prefix else key.upper()

                if isinstance(value, dict):
                    _traverse_config(value, f"{env_key}_")
                else:
                    # 从环境变量获取值
                    env_value = os.getenv(env_key)
                    if env_value is not None:
                        # 转换数据类型
                        converted_value = self._convert_value_type(value, env_value)
                        env_overrides[key] = converted_value

        # 遍历顶级配置
        for top_key, top_value in base_config.items():
            if isinstance(top_value, dict):
                _traverse_config(top_value, f"{top_key.upper()}_")
            else:
                env_key = top_key.upper()
                env_value = os.getenv(env_key)
                if env_value is not None:
                    converted_value = self._convert_value_type(top_value, env_value)
                    env_overrides[top_key] = converted_value

        return env_overrides

    def _convert_value_type(self, original_value: Any, env_value: str) -> Any:
        """将环境变量的字符串值转换为正确的类型"""
        # 根据原始值的类型进行转换
        if isinstance(original_value, bool):
            return env_value.lower() in ("true", "1", "yes", "on", "t")
        elif isinstance(original_value, int):
            try:
                return int(env_value)
            except ValueError:
                return original_value
        elif isinstance(original_value, float):
            try:
                return float(env_value)
            except ValueError:
                return original_value
        elif isinstance(original_value, list):
            # 假设列表元素用逗号分隔
            if env_value.startswith("[") and env_value.endswith("]"):
                # 如果是 JSON 数组格式
                import json
                try:
                    return json.loads(env_value)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in env_value.split(",") if item.strip()]
        else:
            # 默认为字符串
            return env_value

    def reload(self, config_file: Optional[str] = None) -> None:
        """重新加载配置"""
        config_path = config_file or self._config_path
        if config_path and config_path in self._config_cache:
            with self._config_lock:
                del self._config_cache[config_path]

        # 重新加载配置
        if config_path:
            yaml_config = self._load_yaml_config(config_path)
            env_overrides = self._extract_env_overrides(yaml_config)

            # 更新实例属性
            for key, value in yaml_config.items():
                setattr(self, key, value)

            # 应用环境变量覆盖
            for key, value in env_overrides.items():
                setattr(self, key, value)

            self._yaml_data = yaml_config
            self._config_path = config_path

    # ==================== 属性访问器 ====================
    # 提供类型安全的属性访问

    @property
    def APP_NAME(self) -> str:
        return self._get_nested("app", "name", "Mindsweeper")

    @property
    def APP_VERSION(self) -> str:
        return self._get_nested("app", "version", "1.0.0")

    @property
    def DEBUG(self) -> bool:
        return self._get_nested("app", "debug", False)

    @property
    def ENVIRONMENT(self) -> str:
        return self._get_nested("app", "environment", "development")

    @property
    def RELOAD(self) -> bool:
        return self._get_nested("app", "reload", self.ENVIRONMENT == "development")

    @property
    def WORKERS(self) -> int:
        default = 4 if self.ENVIRONMENT == "development" else 8
        return self._get_nested("app", "workers", default)

    @property
    def HOST(self) -> str:
        return self._get_nested("server", "host", "0.0.0.0")

    @property
    def PORT(self) -> int:
        return self._get_nested("server", "port", 8000)

    @property
    def NEO4J_URI(self) -> str:
        env_url = os.getenv("NEO4J_URI")
        if env_url:
            return env_url
        return self._get_nested("neo4j", "uri", "")

    @property
    def NEO4J_DB(self) -> str:
        env_db = os.getenv("NEO4J_DB")
        if env_db:
            return env_db
        return self._get_nested("neo4j", "database", "")

    @property
    def NEO4J_PASSWORD(self) -> str:
        env_password = os.getenv("NEO4J_PASSWORD")
        if env_password:
            return env_password
        return self._get_nested("neo4j", "password", "")

    @property
    def NEO4J_USER(self) -> str:
        env_user = os.getenv("NEO4J_USER")
        if env_user:
            return env_user
        return self._get_nested("neo4j", "username", "")

    @property
    def DATABASE_URL(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        return self._get_nested("database", "url", "")

    @property
    def DATABASE_ECHO(self) -> bool:
        return self._get_nested("database", "echo", self.DEBUG)

    @property
    def DATABASE_POOL_SIZE(self) -> bool:
        return self._get_nested("database", "pool_size", 30)

    @property
    def DATABASE_MAX_OVERFLOW(self) -> bool:
        return self._get_nested("database", "max_overflow", 10)

    @property
    def DATABASE_POOL_RECYCLE(self) -> bool:
        return self._get_nested("database", "pool_recycle", 3600)

    @property
    def MILVUS_HOST(self) -> str:
        return self._get_nested("milvus", "host", "localhost")

    @property
    def MILVUS_PORT(self) -> int:
        return self._get_nested("milvus", "port", 19530)

    @property
    def MILVUS_COLLECTION_NAME(self) -> str:
        return self._get_nested("milvus", "collection_name", "documents")

    @property
    def MILVUS_URI(self) -> str:
        return f"http://{self.MILVUS_HOST}:{self.MILVUS_PORT}"

    @property
    def MILVUS_DATABASE(self) -> str:
        return self._get_nested("milvus", "database", "")

    @property
    def MILVUS_VECTOR_DIM(self) -> int:
        return self._get_nested("milvus", "vector_dim", 0)

    @property
    def MILVUS_INDEX_TYPE(self) -> str:
        return self._get_nested("milvus", "index_type", "")

    @property
    def MILVUS_METRIC_TYPE(self) -> str:
        return self._get_nested("milvus", "metric_type", "")

    @property
    def MILVUS_ENABLE_DYNAMIC_FIELD(self) -> bool:
        return self._get_nested("milvus", "enable_dynamic_field", True)

    @property
    def MILVUS_LIMIT(self) -> float:
        return self._get_nested("milvus", "limit", 0)

    @property
    def MILVUS_BM25_K1(self) -> float:
        return self._get_nested("milvus", "bm25_k1", 0)

    @property
    def MILVUS_BM25_B(self) -> float:
        return self._get_nested("milvus", "bm25_b", 0)

    @property
    def MILVUS_TIMEOUT(self) -> float:
        return self._get_nested("milvus", "timeout", 0)

    @property
    def REDIS_URL(self) -> str:
        env_url = os.getenv("REDIS_URL")
        if env_url:
            return env_url
        return self._get_nested("redis", "url", "redis://localhost:6379/0")

    @property
    def MYSQL_USER(self) -> str:
        env_username = os.getenv("MYSQL_USER")
        if env_username:
            return env_username
        return self._get_nested("mysql", "username", "")

    @property
    def MYSQL_PASSWORD(self) -> str:
        env_password = os.getenv("MYSQL_PASSWORD")
        if env_password:
            return env_password
        return self._get_nested("mysql", "password", "")

    @property
    def MYSQL_SERVER(self) -> str:
        env_server = os.getenv("MYSQL_SERVER")
        if env_server:
            return env_server
        return self._get_nested("mysql", "server", "")

    @property
    def MYSQL_PORT(self) -> str:
        env_port = os.getenv("MYSQL_PORT")
        if env_port:
            return env_port
        return self._get_nested("mysql", "port", "")

    @property
    def MYSQL_DB(self) -> str:
        env_db = os.getenv("MYSQL_DB")
        if env_db:
            return env_db
        return self._get_nested("mysql", "db", "")

    @property
    def MYSQL_POLLSIZE(self) -> str:
        env_pool_size = os.getenv("MYSQL_POLLSIZE")
        if env_pool_size:
            return env_pool_size
        return self._get_nested("mysql", "pool_size", "")

    @property
    def UPLOAD_DIR(self) -> Path:
        upload_path = self._get_nested("file", "upload_dir", "./uploads")
        return Path(upload_path).resolve()

    @property
    def MAX_FILE_SIZE(self) -> int:
        return self._get_nested("file", "max_file_size", 100 * 1024 * 1024)

    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        extensions = self._get_nested("file", "allowed_extensions", "pdf,csv,txt,jpg,png,jpeg")
        return [ext.strip().lower() for ext in extensions.split(",")]

    @property
    def CHUNK_SIZE(self) -> int:
        return self._get_nested("text", "chunk_size", 512)

    @property
    def CHUNK_OVERLAP(self) -> int:
        return self._get_nested("text", "chunk_overlap", 256)

    @property
    def EMBEDDING_MODEL(self) -> str:
        return self._get_nested("embedding", "model", "qwen3-embedding:0.6b")

    @property
    def EMBEDDING_BASE_URL(self) -> str:
        return self._get_nested("embedding", "base_url", "http://localhost:11434")

    @property
    def EMBEDDING_DIMENSION(self) -> int:
        """根据模型返回向量维度"""
        model = self.EMBEDDING_MODEL
        if "qwen3-embedding" in model:
            return 1536
        elif "text-embedding-3" in model:
            return 1536
        elif "bge" in model:
            return 768
        else:
            return self._get_nested("embedding", "dimension", 768)

    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv("OPENAI_API_KEY", self._get_nested("openai", "api_key", ""))

    @property
    def OLLAMA_URI(self) -> str:
        return os.getenv("OLLAMA_URI", self._get_nested("ollama", "uri", ""))

    @property
    def OPENAI_MODEL(self) -> str:
        return self._get_nested("openai", "model", "text-embedding-3-small")

    @property
    def SEARCH_TOP_K(self) -> int:
        return self._get_nested("search", "top_k", 10)

    @property
    def SEARCH_THRESHOLD(self) -> float:
        return self._get_nested("search", "threshold", 0.5)

    @property
    def LOG_LEVEL(self) -> str:
        return self._get_nested("logging", "level", "INFO" if not self.DEBUG else "DEBUG")

    @property
    def LOG_FILE(self) -> Path:
        log_file = self._get_nested("logging", "file", "./logs/app.log")
        return Path(log_file).resolve()

    @property
    def JWT_SECRET_KEY(self) -> str:
        key = self._get_nested("jwt", "secret_key", "")
        if not key and self.ENVIRONMENT == "production":
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        return key or "your_secret_key_here_change_in_production"

    @property
    def JWT_ALGORITHM(self) -> str:
        return self._get_nested("jwt", "algorithm", "HS256")

    @property
    def JWT_EXPIRATION_HOURS(self) -> int:
        return self._get_nested("jwt", "expiration_hours", 24)

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return self._get_nested("cors", "allowed_hosts", ["*"])

    @property
    def CORS_ALLOW_ORIGINS(self) -> List[str]:
        origins = self._get_nested("cors", "allowed_origins", ["*"])
        if origins:
            return origins

        if self.ENVIRONMENT == "development":
            return ["http://localhost:3000", "http://localhost:8080"]
        elif self.ENVIRONMENT == "production":
            return []
        return []

    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool:
        return self._get_nested("cors", "allowed_credentials", True)

    @property
    def CORS_ALLOW_METHODS(self) -> List[str]:
        methods = self._get_nested("cors", "allowed_methods", ["*"])
        if isinstance(methods, str):
            return methods
        return methods

    @property
    def CORS_ALLOW_HEADERS(self) -> List[str]:
        return self._get_nested("cors", "allow_headers", ["*"])

    @property
    def CELERY_BROKER_URL(self) -> str:
        env_url = os.getenv("CELERY_BROKER_URL")
        if env_url:
            return env_url
        return self._get_nested("celery", "broker_url", "redis://localhost:6379/1")

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        env_url = os.getenv("CELERY_RESULT_BACKEND")
        if env_url:
            return env_url
        return self._get_nested("celery", "result_backend", "redis://localhost:6379/2")

    @property
    def SMTP_SERVER(self) -> str:
        return self._get_nested("smtp", "server", "")

    @property
    def SMTP_PORT(self) -> int:
        return self._get_nested("smtp", "port", 587)

    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        return os.getenv("AWS_ACCESS_KEY_ID", self._get_nested("aws", "access_key_id", ""))

    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        return os.getenv("AWS_SECRET_ACCESS_KEY", self._get_nested("aws", "secret_access_key", ""))

    # ==================== 辅助方法 ====================
    def _get_nested(self, *keys, default=None):
        """递归获取嵌套配置值"""
        # 从实例字典中获取值
        value = getattr(self, keys[0], None)

        if value is None:
            return default

        if isinstance(value, dict):
            default = value.get(keys[1])
            if default is not None:
                return default
        else:
            return default

        return value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split(".")
        value = self.__dict__.get(keys[0])

        if value is None:
            return default

        for k in keys[1:]:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（排除私有属性）"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def is_allowed_file(self, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        if not filename:
            return False
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def get_embedding_config(self) -> Dict[str, Any]:
        """获取嵌入模型配置"""
        return {
            "model": self.EMBEDDING_MODEL,
            "base_url": self.EMBEDDING_BASE_URL,
            "device": self._get_nested("embedding", "device", "cpu"),
            "batch_size": self._get_nested("embedding", "batch_size", 32),
            "dimension": self.EMBEDDING_DIMENSION,
        }


# ==================== 单例模式 ====================

class SettingsSingleton:
    """动态配置单例管理器"""

    _instance: Optional[DynamicSettings] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_instance(cls, config_file: Optional[str] = None) -> DynamicSettings:
        """获取配置单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = DynamicSettings(config_file=config_file)

        return cls._instance

    @classmethod
    def reload(cls, config_file: Optional[str] = None) -> None:
        """重新加载配置"""
        with cls._lock:
            if cls._instance:
                cls._instance.reload(config_file)
            else:
                cls._instance = DynamicSettings(config_file=config_file)

    @classmethod
    def reset(cls) -> None:
        """重置单例（仅用于测试）"""
        with cls._lock:
            cls._instance = None


def get_settings(config_file: Optional[str] = None) -> DynamicSettings:
    """获取应用配置实例"""
    return SettingsSingleton.get_instance(config_file=config_file)


# 导出全局配置实例
settings = get_settings()

# 使用示例
# if __name__ == "__main__":
#     print(settings)