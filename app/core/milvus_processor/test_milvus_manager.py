#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/29 12:12
# @Author  : CongPeiQiang
# @File    : test_milvus_manager.py
# @Software: PyCharm
"""
Milvus管理器系统测试脚本
测试重构后的所有模块功能
"""
from app.core.milvus_processor.milvus_manager import get_milvus_manager


def demo_basic_usage():
    """基本使用演示"""
    print("=== Milvus管理器基本使用演示 ===")

    # 1. 创建管理器
    manager = get_milvus_manager()

    # 2. 创建集合
    collection_name = "demo_collection"
    if manager.create_collection(collection_name, drop_existing=True):
        print(f"✅ 创建集合 '{collection_name}' 成功")

    # 3. 插入文档
    documents = [
        {
            "doc_id": "demo_001",
            "title": "人工智能简介",
            "content": "人工智能是计算机科学的一个分支，致力于创建智能机器。",
            "author": "AI专家",
            "category": "科技"
        }
    ]

    result = manager.insert_documents(collection_name, documents)
    print(f"✅ 插入文档: {result['message']}")

    # 4. 搜索文档
    search_results = manager.search(
        collection_name=collection_name,
        query="人工智能",
        search_type="semantic"
    )

    if search_results:
        print(f"✅ 搜索成功，找到 {len(search_results)} 个结果")
        for i, r in enumerate(search_results[:2], 1):
            print(f"   {i}. {r.get('title')} (得分: {r.get('score', 0):.3f})")

    # 5. 查看状态
    status = manager.get_status()
    print(f"\n📊 系统状态:")
    print(f"   数据库: {status.get('current_database')}")
    print(f"   集合: {status.get('collections', [])}")

    # 6. 清理
    manager.delete_collection(collection_name)
    manager.close()
    print("\n🎉 演示完成！")


if __name__ == "__main__":
    # 直接运行此文件时执行演示

    demo_basic_usage()