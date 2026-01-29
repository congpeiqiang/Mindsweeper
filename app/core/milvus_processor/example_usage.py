#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 11:02
# @Author  : CongPeiQiang
# @File    : example_usage.py
# @Software: PyCharm
"""
Milvus管理器使用示例
"""
from app.config.settings import settings
from app.core.milvus_processor import MilvusConfig
from milvus_manager import MilvusManager

def basic_example():
    """基本使用示例"""
    print("=== Milvus管理器基本使用示例 ===")

    # 1. 创建配置（可以从环境变量或JSON文件加载）
    # config = MilvusConfig(settings.milvus_uri, settings.ollama_uri, settings.timeout, settings.default_db, settings.default_collection, settings.enable_dynamic_field,
    #              settings.chunk_size, settings.chunk_overlap, settings.batch_size, settings.embedding_model, settings.embedding_dim, settings.default_search_limit, settings.bm25_k1, settings.bm25_b)

    # 2. 创建管理器
    manager = MilvusManager(settings.MILVUS_URI, settings.OLLAMA_URI, settings.MILVUS_DATABASE, settings.MILVUS_COLLECTION_NAME, settings.MILVUS_TIMEOUT)

    # 3. 初始化管理器
    if not manager.initialize():
        print("初始化失败")
        return

    # 4. 创建集合
    collection_name = "my_documents"
    if manager.create_collection(collection_name, drop_existing=True):
        print(f"集合 '{collection_name}' 创建成功")

    # 5. 插入文档
    documents = [
        {
            "doc_id": "doc_001",
            "title": "人工智能的发展历程",
            "content": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的机器...",
            "author": "张三",
            "source": "科技期刊",
            "category": "科技",
            "url": "http://example.com/doc1"
        },
        {
            "doc_id": "doc_002",
            "title": "机器学习的应用领域",
            "content": "机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习并做出预测或决策...",
            "author": "李四",
            "source": "学术论文",
            "category": "教育",
            "url": "http://example.com/doc2"
        }
    ]

    insert_result = manager.insert_documents(collection_name, documents)
    print(f"插入结果: {insert_result['message']}")

    # 6. 搜索文档
    print("\n=== 搜索示例 ===")

    # 语义搜索
    semantic_results = manager.semantic_search(
        collection_name=collection_name,
        query="人工智能技术"
    )
    print(f"语义搜索找到 {len(semantic_results or [])} 个结果")

    # 关键词搜索
    keyword_results = manager.keyword_search(
        collection_name=collection_name,
        query="机器学习"
    )
    print(f"关键词搜索找到 {len(keyword_results or [])} 个结果")

    # 混合搜索
    hybrid_results = manager.hybrid_search(
        collection_name=collection_name,
        query="AI和机器学习的关系",
        weights=[0.6, 0.4]
    )
    print(f"混合搜索找到 {len(hybrid_results or [])} 个结果")

    # 7. 查看状态
    status = manager.get_status()
    print(f"\n当前数据库: {status.get('current_database')}")
    print(f"当前集合: {status.get('collections', [])}")

    # 8. 清理
    manager.close()


def advanced_example():
    """高级使用示例"""
    print("\n=== Milvus管理器高级使用示例 ===")

    # 从JSON文件加载配置
    config = ConfigManager.load_from_json("config.json")

    # 自定义配置
    config.chunk_size = 1000
    config.batch_size = 100
    config.default_search_limit = 20

    manager = MilvusManager(config)

    if manager.initialize():
        # 批量插入JSON文件
        insert_result = manager.insert_from_json_file(
            collection_name="news_articles",
            file_path="data/documents.json",
            show_progress=True
        )

        print(f"批量插入结果: {insert_result}")

        # 复杂搜索
        results = manager.search(
            collection_name="news_articles",
            query="人工智能政策",
            search_type="hybrid",
            weights=[0.7, 0.3],
            filter_condition='category == "科技" and author != ""',
            limit=10
        )

        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"结果 {i}: {result.get('title')} (相似度: {result.get('score', 0):.4f})")

        manager.close()


if __name__ == "__main__":
    basic_example()
    # advanced_example()