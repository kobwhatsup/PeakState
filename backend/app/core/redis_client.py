"""
Redis客户端管理器
提供缓存操作的统一接口，支持异步操作
"""

import redis.asyncio as aioredis
from typing import Optional, List
from loguru import logger

from app.core.config import settings


class RedisManager:
    """
    Redis管理器

    功能:
    1. 异步Redis操作
    2. 缓存CRUD
    3. 批量操作
    4. 统计信息
    """

    def __init__(self):
        """初始化Redis管理器"""
        self.client: Optional[aioredis.Redis] = None
        self.cache_db = settings.REDIS_CACHE_DB  # DB 1用于缓存
        self._connected = False

    async def connect(self):
        """
        建立Redis连接

        使用连接池以提高性能
        """
        if self._connected:
            return

        try:
            # 解析Redis URL
            self.client = await aioredis.from_url(
                settings.REDIS_URL,
                db=self.cache_db,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,  # 连接池大小
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # 测试连接
            await self.client.ping()
            self._connected = True

            logger.info(
                f"✅ Redis connected | "
                f"DB: {self.cache_db} | "
                f"URL: {settings.REDIS_URL.split('@')[-1]}"
            )

        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def disconnect(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("🔌 Redis disconnected")

    async def get(self, key: str) -> Optional[str]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在返回None
        """
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示永不过期

        Returns:
            是否设置成功
        """
        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """
        删除缓存键

        Args:
            *keys: 要删除的键

        Returns:
            删除的键数量
        """
        try:
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """
        批量删除匹配模式的键

        Args:
            pattern: 键的模式，如 "user:123:*"

        Returns:
            删除的键数量
        """
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 缓存键
            seconds: 过期秒数

        Returns:
            是否设置成功
        """
        try:
            return bool(await self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1表示永不过期，-2表示不存在
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            return -2

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        递增计数器

        Args:
            key: 计数器键
            amount: 递增量

        Returns:
            递增后的值
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return 0

    async def get_keys_count(self, pattern: str = "*") -> int:
        """
        获取匹配模式的键数量

        Args:
            pattern: 键模式

        Returns:
            键数量
        """
        try:
            keys = await self.client.keys(pattern)
            return len(keys)
        except Exception as e:
            logger.error(f"Redis GET_KEYS_COUNT error: {e}")
            return 0

    async def get_stats(self) -> dict:
        """
        获取Redis统计信息

        Returns:
            统计信息字典
        """
        try:
            info = await self.client.info("stats")
            keyspace = await self.client.info("keyspace")

            # 提取当前DB的键数量
            db_key = f"db{self.cache_db}"
            db_info = keyspace.get(db_key, {})
            keys_count = db_info.get("keys", 0) if isinstance(db_info, dict) else 0

            # 计算命中率
            hits = int(info.get("keyspace_hits", 0))
            misses = int(info.get("keyspace_misses", 0))
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            return {
                "connected": self._connected,
                "db": self.cache_db,
                "total_keys": keys_count,
                "total_commands": int(info.get("total_commands_processed", 0)),
                "keyspace_hits": hits,
                "keyspace_misses": misses,
                "hit_rate_percent": round(hit_rate, 2),
                "memory_used_human": info.get("used_memory_human", "N/A"),
                "evicted_keys": int(info.get("evicted_keys", 0))
            }
        except Exception as e:
            logger.error(f"Redis GET_STATS error: {e}")
            return {
                "connected": self._connected,
                "error": str(e)
            }

    async def flush_db(self):
        """
        清空当前数据库

        警告：谨慎使用！
        """
        try:
            await self.client.flushdb()
            logger.warning(f"⚠️  Redis DB {self.cache_db} flushed")
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")


# 全局单例
_redis_manager: Optional[RedisManager] = None


async def get_redis_manager() -> RedisManager:
    """
    获取全局Redis管理器单例

    Returns:
        RedisManager实例
    """
    global _redis_manager

    if _redis_manager is None:
        _redis_manager = RedisManager()
        await _redis_manager.connect()

    return _redis_manager


async def close_redis_manager():
    """关闭全局Redis管理器"""
    global _redis_manager

    if _redis_manager:
        await _redis_manager.disconnect()
        _redis_manager = None
