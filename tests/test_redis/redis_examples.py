#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/27 16:52
# @Author  : CongPeiQiang
# @File    : redis_examples.py
# @Software: PyCharm
import asyncio

from tests.test_redis.redis_curd import AsyncRedisClient


async def basic_crud_example():
    """基本增删查改示例"""

    # 创建Redis客户端
    redis_client = AsyncRedisClient(host='47.120.44.223', port=6379, db=1)

    try:
        # 测试连接
        if await redis_client.connect():
            print("✅ Redis连接成功")

        print("\n" + "=" * 50)
        print("1. 字符串操作示例")
        print("=" * 50)

        # 增：设置字符串
        await redis_client.set("user:1:name", "张三")
        await redis_client.set("user:1:age", 25)
        await redis_client.set("user:1:profile",
                               {"city": "北京", "job": "工程师"},
                               expire=3600)

        # 查：获取字符串
        name = await redis_client.get("user:1:name")
        age = await redis_client.get("user:1:age")
        profile = await redis_client.get("user:1:profile")
        print(f"用户名: {name}")
        print(f"年龄: {age}")
        print(f"个人资料: {profile}")

        # 改：更新字符串
        await redis_client.set("user:1:age", 26)
        new_age = await redis_client.get("user:1:age")
        print(f"更新后年龄: {new_age}")

        # 删：删除字符串
        await redis_client.delete("user:1:name")
        exists = await redis_client.exists("user:1:name")
        print(f"删除后键是否存在: {exists}")

        print("\n" + "=" * 50)
        print("2. 哈希操作示例")
        print("=" * 50)

        # 增：设置哈希
        await redis_client.hset("session:abc123", "user_id", 1001)
        await redis_client.hset("session:abc123", "username", "张三")

        # 批量设置
        await redis_client.hmset("session:def456", {
            "user_id": 1002,
            "username": "李四",
            "last_login": "2024-01-15",
            "permissions": ["read", "write"]
        })

        # 查：获取哈希
        user_id = await redis_client.hget("session:abc123", "user_id")
        username = await redis_client.hget("session:abc123", "username")
        print(f"会话用户ID: {user_id}")
        print(f"会话用户名: {username}")

        # 获取所有字段
        session_data = await redis_client.hgetall("session:def456")
        print(f"完整会话数据: {session_data}")

        # 改：更新哈希字段
        await redis_client.hset("session:abc123", "username", "张三丰")
        new_username = await redis_client.hget("session:abc123", "username")
        print(f"更新后用户名: {new_username}")

        # 删：删除哈希字段
        await redis_client.hdel("session:def456", "permissions")
        has_perm = await redis_client.hexists("session:def456", "permissions")
        print(f"删除后权限字段是否存在: {has_perm}")

        print("\n" + "=" * 50)
        print("3. 列表操作示例")
        print("=" * 50)

        # 增：推入列表
        await redis_client.lpush("task_queue", "任务1")
        await redis_client.rpush("task_queue", "任务2")
        await redis_client.rpush("task_queue", {"task": "任务3", "priority": "high"})

        # 查：获取列表
        tasks = await redis_client.lrange("task_queue", 0, -1)
        print(f"所有任务: {tasks}")

        # 改：无法直接修改列表中的元素，需要重新构建
        # 通常做法是弹出->修改->推回

        # 删：弹出元素
        first_task = await redis_client.lpop("task_queue")
        print(f"弹出的第一个任务: {first_task}")
        remaining_tasks = await redis_client.lrange("task_queue", 0, -1)
        print(f"剩余任务: {remaining_tasks}")

        print("\n" + "=" * 50)
        print("4. 集合操作示例")
        print("=" * 50)

        # 增：添加集合成员
        await redis_client.sadd("article:1001:tags", "Python", "Redis", "异步编程")
        await redis_client.sadd("user:1001:favorites", "文章1", "文章2", "文章3")

        # 查：获取集合成员
        tags = await redis_client.smembers("article:1001:tags")
        favorites = await redis_client.smembers("user:1001:favorites")
        print(f"文章标签: {tags}")
        print(f"用户收藏: {favorites}")

        # 改：添加新成员（集合会自动去重）
        await redis_client.sadd("article:1001:tags", "数据库", "Python")  # Python已存在
        new_tags = await redis_client.smembers("article:1001:tags")
        print(f"添加新标签后: {new_tags}")

        # 删：删除集合
        await redis_client.delete("user:1001:favorites")
        favorites_exists = await redis_client.exists("user:1001:favorites")
        print(f"删除后集合是否存在: {favorites_exists}")

        print("\n" + "=" * 50)
        print("5. 键操作示例")
        print("=" * 50)

        # 查询所有键
        all_keys = await redis_client.keys("*")
        print(f"所有键: {all_keys}")

        # 查询匹配模式的键
        user_keys = await redis_client.keys("user:*")
        print(f"用户相关键: {user_keys}")

        # 设置过期时间
        await redis_client.expire("session:abc123", 60)
        ttl = await redis_client.ttl("session:abc123")
        print(f"会话剩余生存时间: {ttl}秒")

        print("\n" + "=" * 50)
        print("6. 管道批量操作示例")
        print("=" * 50)

        # 使用管道进行批量操作
        async with redis_client.pipeline() as pipe:
            # 添加多个操作到管道
            pipe.set("batch:key1", "value1")
            pipe.set("batch:key2", "value2")
            pipe.hset("batch:hash", "field1", "value3")
            pipe.sadd("batch:set", "member1", "member2")

            # 执行所有操作（一次性发送到Redis）
            results = await pipe.execute()
            print(f"管道批量操作结果: {results}")

        print("\n✅ 所有操作完成！")

    finally:
        # 清理测试数据
        await redis_client.delete(
            "user:1:age", "user:1:profile",
            "session:abc123", "session:def456",
            "task_queue", "article:1001:tags",
            "batch:key1", "batch:key2",
            "batch:hash", "batch:set"
        )

        # 关闭连接
        await redis_client.close()
        print("🔌 Redis连接已关闭")


async def user_session_example():
    """用户会话管理示例"""

    redis_client = AsyncRedisClient()

    try:
        # 模拟用户会话管理
        user_id = "user_001"

        # 创建会话
        session_data = {
            "session_id": "sess_001",
            "user_id": user_id,
            "created_at": "2024-01-15 10:00:00",
            "last_active": "2024-01-15 10:30:00",
            "ip_address": "192.168.1.100",
            "user_agent": "Chrome/120.0"
        }

        # 存储会话（哈希结构）
        await redis_client.hmset(f"session:{session_data['session_id']}", session_data)
        await redis_client.expire(f"session:{session_data['session_id']}", 1800)  # 30分钟过期

        # 存储用户的所有会话ID（集合）
        await redis_client.sadd(f"user:{user_id}:sessions", session_data['session_id'])

        # 查询会话
        session = await redis_client.hgetall(f"session:{session_data['session_id']}")
        print(f"用户会话: {session}")

        # 查询用户的所有会话
        session_ids = await redis_client.smembers(f"user:{user_id}:sessions")
        print(f"用户所有会话ID: {session_ids}")

        # 更新会话活跃时间
        await redis_client.hset(f"session:{session_data['session_id']}",
                                "last_active", "2024-01-15 11:00:00")

        # 删除会话
        await redis_client.delete(f"session:{session_data['session_id']}")
        await redis_client.srem(f"user:{user_id}:sessions", session_data['session_id'])

        print("✅ 用户会话管理完成")

    finally:
        await redis_client.close()


async def cache_example():
    """缓存使用示例"""

    redis_client = AsyncRedisClient()

    try:
        # 模拟缓存数据
        cache_key = "api:products:popular"

        # 检查缓存
        cached_data = await redis_client.get(cache_key)

        if cached_data:
            print("📦 从缓存获取数据")
            products = cached_data
        else:
            print("🔄 缓存未命中，从数据库获取")
            # 模拟从数据库获取数据
            products = [
                {"id": 1, "name": "商品A", "price": 100},
                {"id": 2, "name": "商品B", "price": 200},
                {"id": 3, "name": "商品C", "price": 300}
            ]

            # 存入缓存（5分钟过期）
            await redis_client.set(cache_key, products, expire=300)
            print("💾 数据已缓存")

        print(f"商品数据: {products}")

        # 更新缓存
        products.append({"id": 4, "name": "商品D", "price": 400})
        await redis_client.set(cache_key, products, expire=300)
        print("🔄 缓存已更新")

    finally:
        await redis_client.delete("api:products:popular")
        await redis_client.close()


async def main():
    """主函数"""
    print("🚀 Redis异步操作示例")

    # 运行基本CRUD示例
    await basic_crud_example()

    print("\n" + "=" * 60)
    print("用户会话管理示例")
    print("=" * 60)
    await user_session_example()

    print("\n" + "=" * 60)
    print("缓存使用示例")
    print("=" * 60)
    await cache_example()

    print("\n🎉 所有示例执行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())