#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/11 18:53
# @Author  : CongPeiQiang
# @File    : redis_session_manager.py
# @Software: PyCharm
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
import aioredis

# 设置日志
logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """假设的智能体响应模型"""
    content: str
    status: str = "success"
    metadata: Dict[str, Any] = {}


class RedisSessionManager:
    """异步Redis会话管理器"""

    def __init__(
            self,
            redis_host: str = "localhost",
            redis_port: int = 6379,
            redis_db: int = 0,
            redis_password: Optional[str] = None,
            session_timeout: int = 3600
    ):
        """
        初始化异步Redis会话管理器

        Args:
            redis_host: Redis主机地址
            redis_port: Redis端口
            redis_db: 数据库编号
            redis_password: Redis密码
            session_timeout: 会话过期时间（秒）
        """
        self.redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        if redis_password:
            self.redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

        self.redis_client = None
        self.session_timeout = session_timeout
        self.pool = None

    async def initialize(self):
        """初始化Redis连接池"""
        try:
            # 使用连接池
            self.pool = await aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=10
            )
            logger.info(f"已连接到Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"连接Redis失败: {e}")
            raise

    async def close(self):
        """关闭Redis连接"""
        if self.pool:
            await self.pool.close()
            logger.info("Redis连接已关闭")

    async def _ensure_connection(self):
        """确保连接已初始化"""
        if not self.pool:
            await self.initialize()

    async def create_session(
            self,
            user_id: str,
            session_id: Optional[str] = None,
            status: str = "active",
            last_query: Optional[str] = None,
            last_response: Optional[AgentResponse] = None,
            additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID
            session_id: 会话ID（为空则自动生成）
            status: 会话状态
            last_query: 上次查询内容
            last_response: 上次响应
            additional_data: 额外数据

        Returns:
            会话ID
        """
        await self._ensure_connection()

        if session_id is None:
            session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": status,
            "last_query": last_query or "",
            "last_response": last_response.model_dump() if last_response else {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

        # 添加额外数据
        if additional_data:
            session_data.update(additional_data)

        # 使用哈希存储会话数据
        key = f"session:{user_id}"

        # 存储所有字段到哈希
        for field, value in session_data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await self.pool.hset(key, field, value)

        # 设置过期时间
        await self.pool.expire(key, self.session_timeout)

        logger.info(f"已创建会话: user_id={user_id}, session_id={session_id}")
        return session_id

    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话数据

        Args:
            user_id: 用户ID

        Returns:
            会话数据字典，不存在则返回None
        """
        await self._ensure_connection()

        key = f"session:{user_id}"

        # 获取所有字段
        session_data = await self.pool.hgetall(key)

        if not session_data:
            return None

        # 解析JSON字段
        if "last_response" in session_data and session_data["last_response"]:
            try:
                session_data["last_response"] = json.loads(session_data["last_response"])
            except json.JSONDecodeError:
                session_data["last_response"] = {}

        # 尝试转换为AgentResponse对象
        try:
            if session_data.get("last_response"):
                session_data["last_response"] = AgentResponse(**session_data["last_response"])
        except Exception as e:
            logger.warning(f"无法转换last_response为AgentResponse: {e}")
            session_data["last_response"] = None

        return session_data

    async def update_session(
            self,
            user_id: str,
            **kwargs
    ) -> bool:
        """
        更新会话数据

        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段

        Returns:
            更新是否成功
        """
        await self._ensure_connection()

        key = f"session:{user_id}"

        # 检查会话是否存在
        if not await self.pool.exists(key):
            return False

        # 更新字段
        for field, value in kwargs.items():
            if field in ["last_response", "metadata"]:
                # 特殊处理复杂对象
                if hasattr(value, 'model_dump'):
                    value = json.dumps(value.model_dump(), ensure_ascii=False)
                elif isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
            elif field == "last_updated":
                value = datetime.now().isoformat()

            await self.pool.hset(key, field, value)

        # 刷新过期时间
        await self.pool.expire(key, self.session_timeout)

        logger.debug(f"已更新会话: user_id={user_id}, fields={list(kwargs.keys())}")
        return True

    async def update_session_partial(
            self,
            user_id: str,
            status: Optional[str] = None,
            last_query: Optional[str] = None,
            last_response: Optional[AgentResponse] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新部分会话字段（兼容旧接口）
        """
        update_data = {}

        if status is not None:
            update_data["status"] = status
        if last_query is not None:
            update_data["last_query"] = last_query
        if last_response is not None:
            update_data["last_response"] = last_response
        if metadata is not None:
            update_data["metadata"] = metadata

        update_data["last_updated"] = datetime.now().isoformat()

        return await self.update_session(user_id, **update_data)

    async def delete_session(self, user_id: str) -> bool:
        """
        删除会话

        Args:
            user_id: 用户ID

        Returns:
            删除是否成功
        """
        await self._ensure_connection()

        key = f"session:{user_id}"
        deleted = await self.pool.delete(key)

        if deleted > 0:
            logger.info(f"已删除会话: user_id={user_id}")
            return True
        return False

    async def get_session_count(self) -> int:
        """
        获取所有会话数量

        Returns:
            会话数量
        """
        await self._ensure_connection()

        count = 0
        async for key in self.pool.scan_iter(match="session:*", count=100):
            count += 1

        return count

    async def get_all_user_ids(self) -> List[str]:
        """
        获取所有用户ID

        Returns:
            用户ID列表
        """
        await self._ensure_connection()

        user_ids = []
        async for key in self.pool.scan_iter(match="session:*", count=100):
            # key格式: session:user_id
            if ":" in key:
                user_id = key.split(":", 1)[1]
                user_ids.append(user_id)

        return user_ids

    async def user_id_exists(self, user_id: str) -> bool:
        """
        检查用户会话是否存在

        Args:
            user_id: 用户ID

        Returns:
            是否存在
        """
        await self._ensure_connection()

        key = f"session:{user_id}"
        exists = await self.pool.exists(key)

        return exists > 0

    async def get_session_ttl(self, user_id: str) -> int:
        """
        获取会话剩余生存时间

        Args:
            user_id: 用户ID

        Returns:
            剩余时间（秒），-1表示永不过期，-2表示键不存在
        """
        await self._ensure_connection()

        key = f"session:{user_id}"
        ttl = await self.pool.ttl(key)

        return ttl

    async def refresh_session(self, user_id: str) -> bool:
        """
        刷新会话过期时间

        Args:
            user_id: 用户ID

        Returns:
            刷新是否成功
        """
        await self._ensure_connection()

        key = f"session:{user_id}"

        if await self.pool.exists(key):
            await self.pool.expire(key, self.session_timeout)
            return True
        return False

    async def get_active_sessions(self, status: str = "active") -> List[Dict[str, Any]]:
        """
        获取指定状态的所有会话

        Args:
            status: 会话状态

        Returns:
            会话列表
        """
        await self._ensure_connection()

        sessions = []
        user_ids = await self.get_all_user_ids()

        for user_id in user_ids:
            session = await self.get_session(user_id)
            if session and session.get("status") == status:
                sessions.append(session)

        return sessions

    async def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话（实际Redis会自动清理，此方法用于统计）

        Returns:
            清理的会话数量
        """
        await self._ensure_connection()

        expired_count = 0
        user_ids = await self.get_all_user_ids()

        for user_id in user_ids:
            ttl = await self.get_session_ttl(user_id)
            if ttl <= 0:  # 已过期或不存在
                await self.delete_session(user_id)
                expired_count += 1

        return expired_count
