import redis.asyncio as redis
import json
import asyncio
from typing import Any, Optional, Dict, List, Set, AsyncIterator
from contextlib import asynccontextmanager
import time


class AsyncRedisClient:
    """Redis异步客户端 - 增强版"""

    def __init__(self, host='47.120.44.223', port=6379, db=0):
        """
        初始化Redis客户端

        Args:
            host: Redis主机地址
            port: Redis端口
            db: Redis数据库编号
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,  # 自动解码为字符串
            socket_connect_timeout=5,
            socket_timeout=5
        )

    async def connect(self) -> bool:
        """测试连接"""
        try:
            return await self.client.ping()
        except Exception as e:
            print(f"Redis连接失败: {e}")
            return False

    async def close(self):
        """关闭连接"""
        await self.client.close()

    # ========== 字符串操作 ==========

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对

        Args:
            key: 键名
            value: 值
            expire: 过期时间(秒)

        Returns:
            bool: 是否成功
        """
        # 序列化值
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif not isinstance(value, str):
            value = str(value)

        if expire:
            return await self.client.setex(key, expire, value)
        return await self.client.set(key, value)

    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取值

        Args:
            key: 键名
            default: 默认值

        Returns:
            Any: 值
        """
        value = await self.client.get(key)
        if value is None:
            return default

        # 尝试反序列化JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    # ========== 哈希操作 ==========

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """
        设置哈希字段

        Args:
            key: 哈希键名
            field: 字段名
            value: 值

        Returns:
            bool: 是否成功
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif not isinstance(value, str):
            value = str(value)

        result = await self.client.hset(key, field, value)
        return bool(result)

    async def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """
        批量设置哈希字段

        Args:
            key: 哈希键名
            mapping: 字段字典

        Returns:
            bool: 是否成功
        """
        # 序列化所有值
        serialized = {}
        for k, v in mapping.items():
            if isinstance(v, (dict, list)):
                serialized[k] = json.dumps(v, ensure_ascii=False)
            else:
                serialized[k] = str(v)

        result = await self.client.hset(key, mapping=serialized)
        return bool(result)

    async def hget(self, key: str, field: str, default: Any = None) -> Any:
        """
        获取哈希字段值

        Args:
            key: 哈希键名
            field: 字段名
            default: 默认值

        Returns:
            Any: 字段值
        """
        value = await self.client.hget(key, field)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """
        获取所有哈希字段

        Args:
            key: 哈希键名

        Returns:
            Dict[str, Any]: 所有字段
        """
        result = await self.client.hgetall(key)
        parsed = {}
        for k, v in result.items():
            try:
                parsed[k] = json.loads(v)
            except json.JSONDecodeError:
                parsed[k] = v
        return parsed

    # ========== 列表操作 ==========

    async def lpush(self, key: str, *values: Any) -> int:
        """
        从左侧推入列表

        Args:
            key: 列表键名
            *values: 要推入的值

        Returns:
            int: 列表长度
        """
        serialized = []
        for v in values:
            if isinstance(v, (dict, list)):
                serialized.append(json.dumps(v, ensure_ascii=False))
            else:
                serialized.append(str(v))

        return await self.client.lpush(key, *serialized)

    async def rpush(self, key: str, *values: Any) -> int:
        """
        从右侧推入列表
        """
        serialized = []
        for v in values:
            if isinstance(v, (dict, list)):
                serialized.append(json.dumps(v, ensure_ascii=False))
            else:
                serialized.append(str(v))

        return await self.client.rpush(key, *serialized)

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表范围

        Args:
            key: 列表键名
            start: 起始索引
            end: 结束索引

        Returns:
            List[Any]: 元素列表
        """
        values = await self.client.lrange(key, start, end)
        parsed = []
        for v in values:
            try:
                parsed.append(json.loads(v))
            except json.JSONDecodeError:
                parsed.append(v)
        return parsed

    async def lpop(self, key: str) -> Any:
        """
        从左侧弹出元素

        Args:
            key: 列表键名

        Returns:
            Any: 弹出的元素
        """
        value = await self.client.lpop(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    # ========== 集合操作 ==========

    async def sadd(self, key: str, *members: Any) -> int:
        """
        添加集合成员

        Args:
            key: 集合键名
            *members: 成员列表

        Returns:
            int: 添加成功的成员数
        """
        serialized = []
        for m in members:
            if isinstance(m, (dict, list)):
                serialized.append(json.dumps(m, ensure_ascii=False))
            else:
                serialized.append(str(m))

        return await self.client.sadd(key, *serialized)

    async def smembers(self, key: str) -> List[Any]:
        """
        获取所有集合成员

        Args:
            key: 集合键名

        Returns:
            List[Any]: 成员列表
        """
        members = await self.client.smembers(key)
        parsed = []
        for m in members:
            try:
                parsed.append(json.loads(m))
            except json.JSONDecodeError:
                parsed.append(m)
        return parsed

    async def scard(self, key: str) -> int:
        """
        获取集合的成员数量

        Args:
            key: 集合键名

        Returns:
            int: 集合成员数量
        """
        return await self.client.scard(key)

    async def sismember(self, key: str, member: Any) -> bool:
        """
        检查成员是否在集合中

        Args:
            key: 集合键名
            member: 要检查的成员

        Returns:
            bool: 是否存在
        """
        if isinstance(member, (dict, list)):
            member = json.dumps(member, ensure_ascii=False)
        else:
            member = str(member)

        return await self.client.sismember(key, member)

    # ========== 删除操作 ==========

    async def delete(self, *keys: str) -> int:
        """
        删除键

        Args:
            *keys: 要删除的键名

        Returns:
            int: 删除的键数量
        """
        return await self.client.delete(*keys)

    async def hdel(self, key: str, *fields: str) -> int:
        """
        删除哈希字段

        Args:
            key: 哈希键名
            *fields: 要删除的字段名

        Returns:
            int: 删除的字段数量
        """
        return await self.client.hdel(key, *fields)

    # ========== 查询操作 ==========

    async def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 键名

        Returns:
            bool: 是否存在
        """
        return bool(await self.client.exists(key))

    async def hexists(self, key: str, field: str) -> bool:
        """
        检查哈希字段是否存在

        Args:
            key: 哈希键名
            field: 字段名

        Returns:
            bool: 是否存在
        """
        return await self.client.hexists(key, field)

    async def keys(self, pattern: str = "*") -> List[str]:
        """
        查找匹配的键

        Args:
            pattern: 匹配模式

        Returns:
            List[str]: 匹配的键列表
        """
        return await self.client.keys(pattern)

    # ========== 扫描操作 ==========

    def scan_iter(self, match: str = "*", count: int = 100,
                  _type: Optional[str] = None) -> AsyncIterator[str]:
        """
        迭代扫描匹配的键（安全遍历，适合大数据集）

        Args:
            match: 匹配模式
            count: 每次迭代返回的数量
            _type: 键类型过滤（string, hash, list, set, zset）

        Yields:
            str: 匹配的键名
        """
        return self.client.scan_iter(match=match, count=count, _type=_type)

    async def scan_all(self, match: str = "*", count: int = 100,
                       _type: Optional[str] = None) -> List[str]:
        """
        扫描所有匹配的键并返回列表

        Args:
            match: 匹配模式
            count: 每次迭代返回的数量
            _type: 键类型过滤

        Returns:
            List[str]: 所有匹配的键
        """
        keys = []
        async for key in self.scan_iter(match=match, count=count, _type=_type):
            keys.append(key)
        return keys

    async def scan_count(self, match: str = "*") -> int:
        """
        统计匹配模式的键数量

        Args:
            match: 匹配模式

        Returns:
            int: 键数量
        """
        count = 0
        async for _ in self.scan_iter(match=match):
            count += 1
        return count

    # ========== 其他实用方法 ==========

    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 键名
            seconds: 过期秒数

        Returns:
            bool: 是否成功
        """
        return await self.client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        Args:
            key: 键名

        Returns:
            int: 剩余秒数
        """
        return await self.client.ttl(key)

    async def type(self, key: str) -> str:
        """
        获取键的类型

        Args:
            key: 键名

        Returns:
            str: 键类型（string, hash, list, set, zset）
        """
        return await self.client.type(key)

    async def dbsize(self) -> int:
        """
        获取当前数据库的键总数

        Returns:
            int: 键总数
        """
        return await self.client.dbsize()

    @asynccontextmanager
    async def pipeline(self, transaction: bool = False):
        """
        获取管道对象，用于批量操作

        Args:
            transaction: 是否使用事务

        Yields:
            Pipeline: Redis管道对象
        """
        async with self.client.pipeline(transaction=transaction) as pipe:
            yield pipe

    async def execute_pipeline(self, operations: list):
        """
        执行管道批量操作

        Args:
            operations: 操作列表，每个元素为 (命令, 参数列表)
            示例: [('set', ['key1', 'value1']), ('set', ['key2', 'value2'])]

        Returns:
            list: 执行结果
        """
        async with self.pipeline() as pipe:
            for cmd, args in operations:
                method = getattr(pipe, cmd)
                method(*args)
            return await pipe.execute()


async def basic_crud_example():
    """基本增删查改示例 - 增强版"""

    # 创建Redis客户端
    redis_client = AsyncRedisClient(host='47.120.44.223', port=6379, db=2)

    try:
        # 测试连接
        if await redis_client.connect():
            print("✅ Redis连接成功")
        else:
            print("❌ Redis连接失败")
            return

        print("\n" + "=" * 50)
        print("1. .exists() 方法示例")
        print("=" * 50)

        # 检查键是否存在
        key_exists = await redis_client.exists("test_key")
        print(f"检查 test_key 是否存在: {key_exists}")

        # 设置一个键
        await redis_client.set("test_key", "test_value")
        key_exists = await redis_client.exists("test_key")
        print(f"设置后检查 test_key 是否存在: {key_exists}")

        # 删除键后再次检查
        await redis_client.delete("test_key")
        key_exists = await redis_client.exists("test_key")
        print(f"删除后检查 test_key 是否存在: {key_exists}")

        print("\n" + "=" * 50)
        print("2. .scard() 方法示例 - 集合成员数量")
        print("=" * 50)

        # 创建测试数据 - 用户标签系统
        user_id = "user_1001"
        tags_key = f"user:{user_id}:tags"

        # 添加用户标签
        tags = ["Python", "Redis", "数据库", "缓存", "异步编程"]
        added_count = await redis_client.sadd(tags_key, *tags)
        print(f"为用户 {user_id} 添加标签，成功添加 {added_count} 个标签")

        # 使用 scard 获取集合成员数量
        tag_count = await redis_client.scard(tags_key)
        print(f"用户 {user_id} 的标签数量: {tag_count}")

        # 检查具体标签是否存在
        is_python_tag = await redis_client.sismember(tags_key, "Python")
        is_java_tag = await redis_client.sismember(tags_key, "Java")
        print(f"标签 'Python' 是否存在: {is_python_tag}")
        print(f"标签 'Java' 是否存在: {is_java_tag}")

        # 模拟用户添加更多标签
        new_tags = ["Docker", "Kubernetes", "Python"]  # Python已存在
        added_count = await redis_client.sadd(tags_key, *new_tags)
        tag_count = await redis_client.scard(tags_key)
        print(f"添加新标签后，实际添加 {added_count} 个（去重后）")
        print(f"当前标签数量: {tag_count}")

        # 获取所有标签
        all_tags = await redis_client.smembers(tags_key)
        print(f"所有标签: {all_tags}")

        print("\n" + "=" * 50)
        print("3. .scan_iter() 方法示例 - 安全遍历键")
        print("=" * 50)

        # 创建一些测试数据
        test_data = {
            "user:1001:name": "张三",
            "user:1001:age": 25,
            "user:1001:city": "北京",
            "user:1002:name": "李四",
            "user:1002:age": 30,
            "user:1002:city": "上海",
            "product:001:name": "iPhone",
            "product:001:price": 6999,
            "product:002:name": "MacBook",
            "product:002:price": 12999,
            "session:abc123": "active",
            "session:def456": "inactive",
            "cache:config": "some_config",
            "temp:data": "temporary_data"
        }

        # 批量设置测试数据
        print("创建测试数据...")
        for key, value in test_data.items():
            await redis_client.set(key, value)

        # 示例1: 扫描所有键
        print("\n扫描所有键:")
        all_keys_count = 0
        async for key in redis_client.scan_iter():
            all_keys_count += 1
            if all_keys_count <= 5:  # 只显示前5个
                key_type = await redis_client.type(key)
                print(f"  {key} [{key_type}]")

        total_keys = await redis_client.dbsize()
        print(f"总键数: {all_keys_count} (dbsize: {total_keys})")

        # 示例2: 使用模式匹配扫描
        print("\n扫描所有用户键 (user:*):")
        user_keys = []
        async for key in redis_client.scan_iter("user:*"):
            user_keys.append(key)
            value = await redis_client.get(key)
            print(f"  {key} = {value}")
        print(f"找到 {len(user_keys)} 个用户键")

        # 示例3: 扫描产品键
        print("\n扫描所有产品键 (product:*):")
        product_keys = []
        async for key in redis_client.scan_iter("product:*"):
            product_keys.append(key)
            print(f"  {key}")
        print(f"找到 {len(product_keys)} 个产品键")

        # 示例4: 按类型扫描（只扫描字符串类型的会话键）
        print("\n扫描会话键（字符串类型）:")
        session_keys = []
        async for key in redis_client.scan_iter("session:*", _type="string"):
            session_keys.append(key)
            ttl = await redis_client.ttl(key)
            print(f"  {key}, TTL: {ttl}秒")
        print(f"找到 {len(session_keys)} 个会话键")

        # 示例5: 使用 scan_all 获取所有匹配的键
        print("\n使用 scan_all 获取所有缓存键:")
        cache_keys = await redis_client.scan_all("cache:*")
        print(f"缓存键: {cache_keys}")

        # 示例6: 统计特定模式的键数量
        print("\n统计各种模式的键数量:")
        patterns = ["user:*", "product:*", "session:*", "cache:*", "temp:*"]
        for pattern in patterns:
            count = await redis_client.scan_count(pattern)
            print(f"  {pattern}: {count} 个")

        print("\n" + "=" * 50)
        print("4. 高级应用示例 - 清理过期数据")
        print("=" * 50)

        # 模拟设置一些会过期的键
        await redis_client.set("temp:session:1", "data1", expire=5)  # 5秒后过期
        await redis_client.set("temp:session:2", "data2", expire=10)  # 10秒后过期
        await redis_client.set("temp:cache:1", "cache_data", expire=3)  # 3秒后过期

        # 立即扫描临时键
        print("扫描临时键（设置过期时间前）:")
        temp_keys_before = await redis_client.scan_all("temp:*")
        print(f"临时键数量: {len(temp_keys_before)}")
        for key in temp_keys_before:
            ttl = await redis_client.ttl(key)
            print(f"  {key} - 剩余时间: {ttl}秒")

        # 等待一些键过期
        print("\n等待6秒让部分键过期...")
        await asyncio.sleep(6)

        # 再次扫描，演示如何清理过期键
        print("\n扫描并清理已过期的临时键:")
        expired_keys = []
        async for key in redis_client.scan_iter("temp:*"):
            ttl = await redis_client.ttl(key)
            if ttl <= 0:  # 已过期
                expired_keys.append(key)
                print(f"  🔴 {key} 已过期，删除中...")
                await redis_client.delete(key)

        if not expired_keys:
            print("  没有发现过期键")

        # 检查剩余临时键
        remaining_keys = await redis_client.scan_all("temp:*")
        print(f"\n清理后剩余临时键: {len(remaining_keys)} 个")
        for key in remaining_keys:
            ttl = await redis_client.ttl(key)
            print(f"  {key} - 剩余时间: {ttl}秒")

        print("\n" + "=" * 50)
        print("5. 使用管道优化扫描和批量操作")
        print("=" * 50)

        # 创建一些测试键用于批量操作
        for i in range(1, 11):
            await redis_client.set(f"batch:item:{i}", f"value_{i}")

        # 使用管道批量获取键的值
        print("使用管道批量获取值:")
        batch_keys = []
        async for key in redis_client.scan_iter("batch:item:*"):
            batch_keys.append(key)

        if batch_keys:
            # 使用管道批量获取
            async with redis_client.pipeline() as pipe:
                for key in batch_keys:
                    pipe.get(key)
                results = await pipe.execute()

                for key, value in zip(batch_keys, results):
                    print(f"  {key} = {value}")

        # 使用管道批量删除
        print(f"\n批量删除 {len(batch_keys)} 个测试键...")
        async with redis_client.pipeline() as pipe:
            for key in batch_keys:
                pipe.delete(key)
            delete_results = await pipe.execute()
            deleted_count = sum(delete_results)
            print(f"成功删除 {deleted_count} 个键")

        print("\n" + "=" * 50)
        print("6. 综合应用 - 用户系统统计")
        print("=" * 50)

        # 创建模拟用户数据
        users = [
            {"id": "1001", "name": "张三", "tags": ["程序员", "Python", "Redis"]},
            {"id": "1002", "name": "李四", "tags": ["设计师", "UI", "UX"]},
            {"id": "1003", "name": "王五", "tags": ["产品经理", "需求分析"]},
            {"id": "1004", "name": "赵六", "tags": ["程序员", "Java", "Spring"]},
            {"id": "1005", "name": "钱七", "tags": ["程序员", "Python", "AI"]},
        ]

        for user in users:
            # 存储用户基本信息
            await redis_client.set(f"user:{user['id']}:name", user["name"])

            # 存储用户标签
            tags_key = f"user:{user['id']}:tags"
            await redis_client.sadd(tags_key, *user["tags"])

            # 为用户标签建立反向索引
            for tag in user["tags"]:
                await redis_client.sadd(f"tag:{tag}:users", user["id"])

        # 统计信息
        print("用户系统统计:")

        # 总用户数
        user_count = await redis_client.scan_count("user:*:name")
        print(f"总用户数: {user_count}")

        # 程序员用户数
        programmer_users = await redis_client.scard("tag:程序员:users")
        print(f"程序员用户数: {programmer_users}")

        # Python用户数
        python_users = await redis_client.scard("tag:Python:users")
        print(f"Python用户数: {python_users}")

        # 检查具体用户
        user_id_to_check = "1001"
        user_exists = await redis_client.exists(f"user:{user_id_to_check}:name")
        print(f"\n检查用户 {user_id_to_check} 是否存在: {user_exists}")

        if user_exists:
            user_name = await redis_client.get(f"user:{user_id_to_check}:name")
            user_tags = await redis_client.smembers(f"user:{user_id_to_check}:tags")
            tag_count = await redis_client.scard(f"user:{user_id_to_check}:tags")
            print(f"用户名: {user_name}")
            print(f"标签数量: {tag_count}")
            print(f"用户标签: {user_tags}")

            # 检查用户是否有特定标签
            has_python_tag = await redis_client.sismember(
                f"user:{user_id_to_check}:tags", "Python"
            )
            print(f"是否有Python标签: {has_python_tag}")

        print("\n✅ 所有操作完成！")

    except Exception as e:
        print(f"❌ 执行过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理所有测试数据
        print("\n正在清理测试数据...")

        # 收集所有测试键
        test_patterns = [
            "test_*", "user:*", "product:*", "session:*",
            "cache:*", "temp:*", "batch:*", "tag:*"
        ]

        for pattern in test_patterns:
            keys_to_delete = []
            async for key in redis_client.scan_iter(pattern):
                keys_to_delete.append(key)

            if keys_to_delete:
                deleted = await redis_client.delete(*keys_to_delete)
                print(f"清理 {pattern}: 删除 {deleted} 个键")

        # 关闭连接
        await redis_client.close()
        print("🔌 Redis连接已关闭")


async def scan_iter_advanced_examples():
    """scan_iter 高级用法示例"""

    redis_client = AsyncRedisClient()

    try:
        if not await redis_client.connect():
            return

        print("\n" + "=" * 50)
        print("scan_iter 高级用法示例")
        print("=" * 50)

        # 创建更多测试数据
        for i in range(1, 101):
            await redis_client.set(f"data:item:{i:03d}", f"value_{i}")
            if i % 10 == 0:
                await redis_client.sadd("data:sets:group1", f"member_{i}")
                await redis_client.hset("data:hashes:group1", f"field_{i}", f"value_{i}")

        print("1. 分批处理大量数据")
        batch_size = 20
        processed = 0

        async for key in redis_client.scan_iter("data:item:*", count=batch_size):
            # 模拟处理每个键
            value = await redis_client.get(key)
            processed += 1
            if processed % 20 == 0:
                print(f"已处理 {processed} 个数据项...")

        print(f"总共处理 {processed} 个数据项")

        print("\n2. 按类型扫描不同数据结构")
        print("字符串类型:")
        str_count = 0
        async for key in redis_client.scan_iter("data:*", _type="string"):
            str_count += 1
        print(f"  找到 {str_count} 个字符串键")

        print("集合类型:")
        set_count = 0
        async for key in redis_client.scan_iter("data:*", _type="set"):
            set_count += 1
            members_count = await redis_client.scard(key)
            print(f"  {key}: {members_count} 个成员")
        print(f"  找到 {set_count} 个集合键")

        print("哈希类型:")
        hash_count = 0
        async for key in redis_client.scan_iter("data:*", _type="hash"):
            hash_count += 1
            fields_count = len(await redis_client.hgetall(key))
            print(f"  {key}: {fields_count} 个字段")
        print(f"  找到 {hash_count} 个哈希键")

        print("\n3. 实时监控键变化")
        monitor_key = "monitor:counter"
        await redis_client.set(monitor_key, 0)

        # 模拟键变化
        async def increment_counter():
            for i in range(5):
                await asyncio.sleep(1)
                current = int(await redis_client.get(monitor_key))
                await redis_client.set(monitor_key, current + 1)
                print(f"计数器更新: {current} -> {current + 1}")

        print("开始监控键变化...")
        monitor_task = asyncio.create_task(increment_counter())

        # 模拟监控循环
        last_value = -1
        for _ in range(10):
            await asyncio.sleep(0.5)
            if await redis_client.exists(monitor_key):
                current_value = await redis_client.get(monitor_key)
                if current_value != last_value:
                    print(f"监控到变化: {monitor_key} = {current_value}")
                    last_value = current_value

        await monitor_task

    finally:
        # 清理
        keys_to_delete = []
        async for key in redis_client.scan_iter("data:*"):
            keys_to_delete.append(key)
        async for key in redis_client.scan_iter("monitor:*"):
            keys_to_delete.append(key)

        if keys_to_delete:
            await redis_client.delete(*keys_to_delete)

        await redis_client.close()


async def main():
    """主函数"""
    print("🚀 Redis异步操作示例 - 增强版")

    # 运行基本CRUD示例
    await basic_crud_example()

    print("\n" + "=" * 60)
    print("scan_iter 高级用法示例")
    print("=" * 60)
    await scan_iter_advanced_examples()

    print("\n🎉 所有示例执行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())