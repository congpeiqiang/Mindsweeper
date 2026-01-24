#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 14:51
# @Author  : CongPeiQiang
# @File    : test_mongdb.py
# @Software: PyCharm
# example.py
from datetime import datetime

from mongodb_factory import MongoDBManagerFactory, MongoDBConfig


def example_usage():
    """使用示例"""

    # 1. 获取单例工厂实例
    factory = MongoDBManagerFactory()

    # 2. 创建配置
    config = MongoDBConfig(
        host="localhost",
        port=27017,
        username="admin",
        password="password",
        database="test_db",
        max_pool_size=50
    )

    # 3. 创建管理器
    manager = factory.create_manager(config, "test_manager")

    # 4. 创建索引
    manager.create_index("users", [("email", 1)], unique=True)
    manager.create_index("users", [("name", 1)])

    # 5. 插入数据
    user_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25,
        "created_at": datetime.now()
    }

    user_id = manager.insert_one("users", user_data)
    print(f"插入用户ID: {user_id}")

    # 6. 批量插入
    users = [
        {"name": "李四", "email": "lisi@example.com", "age": 30},
        {"name": "王五", "email": "wangwu@example.com", "age": 28}
    ]
    user_ids = manager.insert_many("users", users)
    print(f"批量插入用户IDs: {user_ids}")

    # 7. 查询单个
    user = manager.find_one("users", {"email": "zhangsan@example.com"})
    print(f"查询单个用户: {user}")

    # 8. 查询多个
    users = manager.find_many("users", {"age": {"$gte": 25}}, sort=[("age", -1)])
    print(f"查询多个用户: {users}")

    # 9. 更新文档
    update_result = manager.update_one(
        "users",
        {"email": "zhangsan@example.com"},
        {"$set": {"age": 26, "updated_at": datetime.now()}}
    )
    print(f"更新结果: {update_result}")

    # 10. 统计文档
    count = manager.count_documents("users", {"age": {"$gte": 25}})
    print(f"年龄>=25的用户数量: {count}")

    # 11. 聚合查询
    pipeline = [
        {"$group": {"_id": None, "average_age": {"$avg": "$age"}}}
    ]
    result = manager.aggregate("users", pipeline)
    print(f"平均年龄: {result}")

    # 12. 删除文档
    deleted_count = manager.delete_one("users", {"email": "zhangsan@example.com"})
    print(f"删除文档数量: {deleted_count}")

    # 13. 获取管理器
    manager_copy = factory.get_manager("test_manager")
    print(f"获取的管理器是否相同: {manager is manager_copy}")

    # 14. 清理资源
    factory.shutdown_all()


def multiple_databases_example():
    """多数据库示例"""

    factory = MongoDBManagerFactory()

    # 创建主数据库管理器
    main_config = MongoDBConfig(
        host="localhost",
        port=27017,
        database="main_db"
    )
    main_manager = factory.create_manager(main_config, "main")

    # 创建日志数据库管理器
    log_config = MongoDBConfig(
        host="localhost",
        port=27017,
        database="log_db"
    )
    log_manager = factory.create_manager(log_config, "log")

    # 在不同数据库中操作
    main_manager.insert_one("products", {"name": "产品1", "price": 100})
    log_manager.insert_one("operations", {"action": "insert", "collection": "products"})

    # 获取所有管理器
    all_managers = factory.get_all_managers()
    print(f"所有管理器: {list(all_managers.keys())}")


if __name__ == "__main__":
    example_usage()
    multiple_databases_example()