#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""详细测试 .env 文件配置加载"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import get_settings

# 获取配置实例
settings = get_settings()

print("=" * 70)
print("详细的 .env 文件配置加载测试")
print("=" * 70)
print()

# 应用配置
print("[应用配置]")
print(f"  APP_NAME: {settings.APP_NAME}")
assert settings.APP_NAME == "知识库管理系统", "APP_NAME 未从 .env 加载"
print(f"  DEBUG: {settings.DEBUG}")
assert settings.DEBUG == True, "DEBUG 未从 .env 加载"
print(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
print()

# 服务器配置
print("[服务器配置]")
print(f"  HOST: {settings.HOST}")
print(f"  PORT: {settings.PORT}")
print(f"  WORKERS: {settings.WORKERS}")
print()

# Milvus 配置
print("[Milvus 配置]")
print(f"  MILVUS_HOST: {settings.MILVUS_HOST}")
assert settings.MILVUS_HOST == "8.155.174.96", "MILVUS_HOST 未从 .env 加载"
print(f"  MILVUS_PORT: {settings.MILVUS_PORT}")
print(f"  MILVUS_COLLECTION_NAME: {settings.MILVUS_COLLECTION_NAME}")
assert settings.MILVUS_COLLECTION_NAME == "my_collection_demo_chunked", "MILVUS_COLLECTION_NAME 未从 .env 加载"
print()

# 文件处理配置
print("[文件处理配置]")
print(f"  UPLOAD_DIR: {settings.UPLOAD_DIR}")
print(f"  MAX_FILE_SIZE: {settings.MAX_FILE_SIZE}")
print(f"  ALLOWED_EXTENSIONS: {settings.ALLOWED_EXTENSIONS}")
print()

# 嵌入模型配置
print("[嵌入模型配置]")
print(f"  EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
print(f"  EMBEDDING_BASE_URL: {settings.EMBEDDING_BASE_URL}")
assert settings.EMBEDDING_BASE_URL == "http://8.155.174.96:11434", "EMBEDDING_BASE_URL 未从 .env 加载"
print(f"  EMBEDDING_DEVICE: {settings.EMBEDDING_DEVICE}")
print()

# CORS 配置
print("[CORS 配置]")
print(f"  ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
print(f"  CORS_ORIGINS_LIST: {settings.CORS_ORIGINS_LIST}")
assert settings.CORS_ORIGINS_LIST == ['http://localhost:3000', 'http://localhost:8080'], "CORS_ORIGINS_LIST 未正确加载"
print()

# JWT 配置
print("[JWT 配置]")
print(f"  JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
print(f"  JWT_EXPIRATION_HOURS: {settings.JWT_EXPIRATION_HOURS}")
print()

print("=" * 70)
print("[OK] 所有配置已成功从 .env 文件加载!")
print("=" * 70)

