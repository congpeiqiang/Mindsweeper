#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 settings.py 是否正确加载 .env 文件"""

import sys
import os

print("=" * 70)
print("测试 Settings 配置加载")
print("=" * 70)
print()

# 打印当前工作目录
print(f"当前工作目录: {os.getcwd()}")
print(f".env 文件存在: {os.path.exists('.env')}")
print()

try:
    print("正在导入 settings...")
    from app.config.settings import get_settings
    print("[OK] 导入成功")
    print()

    print("正在获取配置实例...")
    settings = get_settings()
    print("[OK] 配置获取成功")
    print()

    print("=" * 70)
    print("从 .env 文件加载的配置值")
    print("=" * 70)
    print()
    
    # 应用配置
    print("【应用配置】")
    print(f"  APP_NAME: {settings.APP_NAME}")
    print(f"  APP_VERSION: {settings.APP_VERSION}")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
    print()
    
    # 服务器配置
    print("【服务器配置】")
    print(f"  HOST: {settings.HOST}")
    print(f"  PORT: {settings.PORT}")
    print(f"  WORKERS: {settings.WORKERS}")
    print()
    
    # 数据库配置
    print("【数据库配置】")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"  DATABASE_POOL_SIZE: {settings.DATABASE_POOL_SIZE}")
    print()
    
    # Milvus 配置
    print("【Milvus 配置】")
    print(f"  MILVUS_HOST: {settings.MILVUS_HOST}")
    print(f"  MILVUS_PORT: {settings.MILVUS_PORT}")
    print(f"  MILVUS_COLLECTION_NAME: {settings.MILVUS_COLLECTION_NAME}")
    print(f"  MILVUS_VECTOR_DIM: {settings.MILVUS_VECTOR_DIM}")
    print()
    
    # 文件处理配置
    print("【文件处理配置】")
    print(f"  UPLOAD_DIR: {settings.UPLOAD_DIR}")
    print(f"  MAX_FILE_SIZE: {settings.MAX_FILE_SIZE}")
    print(f"  ALLOWED_EXTENSIONS: {settings.ALLOWED_EXTENSIONS}")
    print()
    
    # 嵌入模型配置
    print("【嵌入模型配置】")
    print(f"  EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
    print(f"  EMBEDDING_BASE_URL: {settings.EMBEDDING_BASE_URL}")
    print(f"  EMBEDDING_DEVICE: {settings.EMBEDDING_DEVICE}")
    print()
    
    # CORS 配置
    print("【CORS 配置】")
    print(f"  ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
    print(f"  CORS_ORIGINS_LIST: {settings.CORS_ORIGINS_LIST}")
    print()
    
    # JWT 配置
    print("【JWT 配置】")
    print(f"  JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"  JWT_EXPIRATION_HOURS: {settings.JWT_EXPIRATION_HOURS}")
    print()
    
    print("=" * 70)
    print("[OK] 所有配置已成功从 .env 文件加载")
    print("=" * 70)

except Exception as e:
    print(f"[ERROR] 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

