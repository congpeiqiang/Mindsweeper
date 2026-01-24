#!/usr/bin/env python3
"""
项目目录结构初始化脚本
用于快速生成知识库管理系统的完整目录结构
"""

import os
from pathlib import Path


def create_directory_structure(base_path: str = "."):
    """创建完整的项目目录结构"""
    
    base = Path(base_path)
    
    # 定义所有需要创建的目录
    directories = [
        # 应用主目录
        "app",
        "app/api/v1",
        "app/core/file_processor",
        "app/core/vectorization",
        "app/core/milvus_manager",
        "app/core/search_engine",
        "app/models",
        "app/services",
        "app/utils",
        "app/middleware",
        
        # 测试目录
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        
        # 文档目录
        "docs",
        
        # 配置目录
        "config",
        
        # 脚本目录
        "scripts",
        
        # 上传文件目录
        "uploads/temp",
        "uploads/processed",
        
        # 日志目录
        "logs",
    ]
    
    # 创建所有目录
    for directory in directories:
        dir_path = base / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    # 创建 __init__.py 文件
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/core/file_processor/__init__.py",
        "app/core/vectorization/__init__.py",
        "app/core/milvus_manager/__init__.py",
        "app/core/search_engine/__init__.py",
        "app/models/__init__.py",
        "app/services/__init__.py",
        "app/utils/__init__.py",
        "app/middleware/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/fixtures/__init__.py",
        "config/__init__.py",
    ]
    
    for init_file in init_files:
        file_path = base / init_file
        file_path.touch(exist_ok=True)
        print(f"✓ 创建文件: {init_file}")
    
    # 创建核心Python文件（空文件）
    core_files = {
        "app/main.py": "# FastAPI应用入口\n",
        "app/config.py": "# 配置管理\n",
        "app/dependencies.py": "# 依赖注入\n",
        
        "app/api/health.py": "# 健康检查接口\n",
        "app/api/v1/files.py": "# 文件上传相关接口\n",
        "app/api/v1/documents.py": "# 文档管理接口\n",
        "app/api/v1/search.py": "# 检索接口\n",
        "app/api/v1/knowledge_base.py": "# 知识库管理接口\n",
        
        "app/core/file_processor/base.py": "# 文件处理基类\n",
        "app/core/file_processor/pdf_processor.py": "# PDF处理器\n",
        "app/core/file_processor/csv_processor.py": "# CSV处理器\n",
        "app/core/file_processor/image_processor.py": "# 图片处理器\n",
        "app/core/file_processor/text_processor.py": "# 文本处理器\n",
        
        "app/core/vectorization/embeddings.py": "# 嵌入模型管理\n",
        "app/core/vectorization/chunking.py": "# 文本分块策略\n",
        "app/core/vectorization/vectorizer.py": "# 向量化处理\n",
        
        "app/core/milvus_manager/connection.py": "# 连接管理\n",
        "app/core/milvus_manager/collection.py": "# 集合管理\n",
        "app/core/milvus_manager/operations.py": "# 数据操作\n",
        "app/core/milvus_manager/search.py": "# 向量搜索\n",
        
        "app/core/search_engine/retriever.py": "# 检索器\n",
        "app/core/search_engine/ranker.py": "# 排序器\n",
        "app/core/search_engine/query_processor.py": "# 查询处理\n",
        
        "app/models/schemas.py": "# Pydantic数据模型\n",
        "app/models/database.py": "# 数据库模型\n",
        "app/models/enums.py": "# 枚举类型\n",
        
        "app/services/file_service.py": "# 文件服务\n",
        "app/services/document_service.py": "# 文档服务\n",
        "app/services/knowledge_base_service.py": "# 知识库服务\n",
        "app/services/search_service.py": "# 搜索服务\n",
        
        "app/utils/logger.py": "# 日志配置\n",
        "app/utils/exceptions.py": "# 自定义异常\n",
        "app/utils/validators.py": "# 数据验证\n",
        "app/utils/helpers.py": "# 辅助函数\n",
        
        "app/middleware/error_handler.py": "# 错误处理\n",
        "app/middleware/request_logger.py": "# 请求日志\n",
        
        "tests/conftest.py": "# pytest配置\n",
        "tests/unit/test_file_processor.py": "# 文件处理器测试\n",
        "tests/unit/test_vectorizer.py": "# 向量化测试\n",
        "tests/unit/test_milvus_manager.py": "# Milvus管理器测试\n",
        "tests/unit/test_search_engine.py": "# 搜索引擎测试\n",
        "tests/integration/test_file_upload.py": "# 文件上传集成测试\n",
        "tests/integration/test_search_flow.py": "# 搜索流程集成测试\n",
        "tests/integration/test_knowledge_base.py": "# 知识库集成测试\n",
        
        "config/settings.py": "# 环境配置\n",
        "config/logging.yaml": "# 日志配置\n",
        "config/milvus.yaml": "# Milvus配置\n",
        
        "scripts/init_db.py": "# 初始化数据库\n",
        "scripts/create_collection.py": "# 创建Milvus集合\n",
        "scripts/migrate.py": "# 数据迁移脚本\n",
        "scripts/seed_data.py": "# 种子数据脚本\n",
    }
    
    for file_path, content in core_files.items():
        full_path = base / file_path
        if not full_path.exists():
            full_path.write_text(content, encoding='utf-8')
            print(f"✓ 创建文件: {file_path}")
    
    print("\n✅ 项目目录结构创建完成！")
    print(f"📁 项目根目录: {base.absolute()}")


if __name__ == "__main__":
    import sys
    
    # 获取项目根目录（可选参数）
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print("🚀 开始创建项目目录结构...\n")
    create_directory_structure(project_root)
    print("\n📖 请参考 docs/项目架构设计.md 了解详细信息")

