"""
AI响应缓存管理器
三层缓存架构：L1(Redis精确匹配) + L2(Qdrant语义相似) + L3(知识库预答案)

目标：
- 降低AI调用成本 20-30%
- 提升响应速度 50-200倍（缓存命中时）
- 改善用户体验
"""

import hashlib
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from loguru import logger

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import settings


@dataclass
class CacheEntry:
    """缓存条目"""
    query: str  # 用户问题
    response: str  # AI回答
    provider: str  # 使用的AI提供商
    intent: str  # 意图类型
    complexity: int  # 复杂度(1-10)
    tokens_used: int  # token使用量
    cached_at: str  # 缓存时间 (ISO格式)
    hit_count: int = 0  # 命中次数
    user_id: Optional[str] = None  # 用户ID

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        """从字典创建"""
        return cls(**data)


@dataclass
class CacheStats:
    """缓存统计"""
    total_requests: int = 0
    l1_hits: int = 0  # Redis精确匹配命中
    l2_hits: int = 0  # Qdrant语义相似命中
    l3_hits: int = 0  # 知识库预答案命中
    cache_misses: int = 0  # 未命中
    total_cost_saved_usd: float = 0.0  # 节省成本
    total_latency_saved_ms: float = 0.0  # 节省延迟
    avg_response_time_cached_ms: float = 0.0  # 缓存命中平均响应时间
    avg_response_time_uncached_ms: float = 0.0  # 未缓存平均响应时间


class ResponseCacheManager:
    """
    AI响应缓存管理器

    三层缓存策略:
    - L1 (Redis): 精确匹配，最快 (<5ms)，命中率15-20%
    - L2 (Qdrant): 语义相似，快 (~30ms)，命中率8-12%
    - L3 (Qdrant): 知识库预答案，快 (~30ms)，命中率2-5%

    总体预期命中率: 25-35%
    """

    # 成本估算（每1K tokens美元）
    COST_PER_1K_TOKENS = {
        "gpt-5": 0.03,
        "gpt-5-nano-2025-08-07": 0.01,
        "claude-sonnet-4-20250514": 0.015,
        "phi-3.5": 0.0,  # 本地模型无成本
    }

    # 延迟估算（毫秒）
    LATENCY_ESTIMATE_MS = {
        "gpt-5": 3000,
        "gpt-5-nano-2025-08-07": 1500,
        "claude-sonnet-4-20250514": 2500,
        "phi-3.5": 500,
    }

    def __init__(self):
        """初始化缓存管理器"""
        self.redis_manager = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.sentence_transformer = None

        # 统计数据
        self.stats = CacheStats()

        # 初始化标志
        self._initialized = False
        self._init_lock = asyncio.Lock()

        logger.info("📦 ResponseCacheManager created")

    async def initialize(self):
        """
        初始化所有依赖

        懒加载模式，仅在首次使用时初始化
        """
        if self._initialized:
            return

        async with self._init_lock:
            if self._initialized:
                return

            try:
                # 1. Redis客户端
                from app.core.redis_client import get_redis_manager
                self.redis_manager = await get_redis_manager()

                # 2. Qdrant客户端
                self.qdrant_client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=10
                )

                # 3. 复用意图分类器的Sentence-Transformer
                from app.ai.intent_classifier import get_intent_classifier
                classifier = get_intent_classifier()

                # 确保模型已加载
                if not classifier.is_loaded:
                    async with classifier.load_lock:
                        if not classifier.is_loaded:
                            await classifier._load_model()

                self.sentence_transformer = classifier.model

                # 4. 确保知识库collection存在
                await self._ensure_knowledge_base_collection()

                self._initialized = True
                logger.info("✅ ResponseCacheManager initialized")

            except Exception as e:
                logger.error(f"❌ ResponseCacheManager initialization failed: {e}")
                raise

    async def _ensure_knowledge_base_collection(self):
        """确保知识库collection存在"""
        collection_name = "knowledge_base_qa"

        try:
            # 检查collection是否存在
            self.qdrant_client.get_collection(collection_name)
            logger.debug(f"✓ Qdrant collection '{collection_name}' exists")
        except:
            # 不存在则创建
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,  # MiniLM维度
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created Qdrant collection '{collection_name}'")

    def _generate_cache_key(
        self,
        query: str,
        user_id: str,
        context_hash: Optional[str] = None
    ) -> str:
        """
        生成Redis缓存键

        格式: response:{user_id}:{query_hash}[:context_hash]

        Args:
            query: 用户问题
            user_id: 用户ID
            context_hash: 上下文哈希（可选）

        Returns:
            缓存键
        """
        # 归一化查询（小写+去除首尾空格）
        query_normalized = query.lower().strip()

        # 生成查询哈希（MD5前16位）
        query_hash = hashlib.md5(query_normalized.encode()).hexdigest()[:16]

        if context_hash:
            return f"response:{user_id}:{query_hash}:{context_hash}"

        return f"response:{user_id}:{query_hash}"

    def _calculate_context_hash(
        self,
        conversation_history: Optional[List[Dict]]
    ) -> Optional[str]:
        """
        计算对话上下文哈希

        仅使用最近3轮对话计算hash

        Args:
            conversation_history: 对话历史

        Returns:
            上下文哈希，无历史返回None
        """
        if not conversation_history or len(conversation_history) == 0:
            return None

        # 取最近3轮对话
        recent_history = conversation_history[-3:]

        # 拼接内容
        context_str = ""
        for msg in recent_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            context_str += f"{role}:{content}|"

        # 生成哈希
        return hashlib.md5(context_str.encode()).hexdigest()[:8]

    async def get_cached_response(
        self,
        query: str,
        user_id: str,
        conversation_history: Optional[List[Dict]] = None,
        similarity_threshold: float = 0.92
    ) -> Optional[Tuple[CacheEntry, str]]:
        """
        获取缓存响应

        按L1 → L2 → L3顺序检查

        Args:
            query: 用户问题
            user_id: 用户ID
            conversation_history: 对话历史
            similarity_threshold: 语义相似度阈值(0-1)

        Returns:
            (CacheEntry, cache_layer) 或 None
            cache_layer: "L1" | "L2" | "L3"
        """
        # 确保已初始化
        if not self._initialized:
            await self.initialize()

        self.stats.total_requests += 1
        start_time = datetime.now()

        # L1: Redis精确匹配
        l1_result = await self._check_l1_cache(query, user_id, conversation_history)
        if l1_result:
            self.stats.l1_hits += 1
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_cache_latency_stats(latency_ms, cached=True)

            logger.debug(
                f"✅ L1 HIT | "
                f"Query: {query[:30]}... | "
                f"Latency: {latency_ms:.1f}ms"
            )
            return (l1_result, "L1")

        # L2: Qdrant语义相似匹配
        l2_result = await self._check_l2_cache(
            query,
            user_id,
            similarity_threshold
        )
        if l2_result:
            self.stats.l2_hits += 1
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_cache_latency_stats(latency_ms, cached=True)

            logger.debug(
                f"✅ L2 HIT | "
                f"Query: {query[:30]}... | "
                f"Latency: {latency_ms:.1f}ms"
            )
            return (l2_result, "L2")

        # L3: 知识库预答案
        l3_result = await self._check_l3_cache(query)
        if l3_result:
            self.stats.l3_hits += 1
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_cache_latency_stats(latency_ms, cached=True)

            logger.debug(
                f"✅ L3 HIT | "
                f"Query: {query[:30]}... | "
                f"Latency: {latency_ms:.1f}ms"
            )
            return (l3_result, "L3")

        # 全部未命中
        self.stats.cache_misses += 1
        logger.debug(f"❌ CACHE MISS | Query: {query[:30]}...")

        return None

    async def _check_l1_cache(
        self,
        query: str,
        user_id: str,
        conversation_history: Optional[List[Dict]]
    ) -> Optional[CacheEntry]:
        """
        L1: Redis精确匹配检查

        最快，<5ms
        """
        try:
            # 计算上下文哈希
            context_hash = self._calculate_context_hash(conversation_history)

            # 生成缓存键
            cache_key = self._generate_cache_key(query, user_id, context_hash)

            # 从Redis读取
            cached_data = await self.redis_manager.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                cache_entry = CacheEntry.from_dict(data)

                # 更新命中次数
                cache_entry.hit_count += 1
                await self.redis_manager.set(
                    cache_key,
                    json.dumps(cache_entry.to_dict()),
                    ttl=86400  # 保持24小时TTL
                )

                return cache_entry

            return None

        except Exception as e:
            logger.error(f"L1 cache check error: {e}")
            return None

    async def _check_l2_cache(
        self,
        query: str,
        user_id: str,
        threshold: float
    ) -> Optional[CacheEntry]:
        """
        L2: Qdrant语义相似检查

        较快，~30ms
        """
        try:
            # 编码查询向量
            loop = asyncio.get_event_loop()
            query_vector = await loop.run_in_executor(
                None,
                lambda: self.sentence_transformer.encode(
                    query,
                    convert_to_tensor=False
                ).tolist()
            )

            # 用户专属collection名称
            collection_name = f"cache_user_{user_id}"

            # 检查collection是否存在
            try:
                self.qdrant_client.get_collection(collection_name)
            except:
                # collection不存在，未命中
                return None

            # Qdrant向量搜索
            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=1,
                score_threshold=threshold
            )

            if search_results and len(search_results) > 0:
                result = search_results[0]
                if result.score >= threshold:
                    cache_entry = CacheEntry.from_dict(result.payload)
                    return cache_entry

            return None

        except Exception as e:
            logger.error(f"L2 cache check error: {e}")
            return None

    async def _check_l3_cache(self, query: str) -> Optional[CacheEntry]:
        """
        L3: 知识库预答案检查

        快，~30ms
        """
        try:
            # 编码查询向量
            loop = asyncio.get_event_loop()
            query_vector = await loop.run_in_executor(
                None,
                lambda: self.sentence_transformer.encode(
                    query,
                    convert_to_tensor=False
                ).tolist()
            )

            # 从知识库搜索
            search_results = self.qdrant_client.search(
                collection_name="knowledge_base_qa",
                query_vector=query_vector,
                limit=1,
                score_threshold=0.88  # L3阈值略低
            )

            if search_results and len(search_results) > 0:
                result = search_results[0]
                if result.score >= 0.88:
                    cache_entry = CacheEntry.from_dict(result.payload)
                    return cache_entry

            return None

        except Exception as e:
            logger.error(f"L3 cache check error: {e}")
            return None

    async def set_cache(
        self,
        query: str,
        response: str,
        user_id: str,
        provider: str,
        intent: str,
        complexity: int,
        tokens_used: int,
        conversation_history: Optional[List[Dict]] = None,
        ttl: int = 86400  # 24小时
    ):
        """
        设置缓存

        同时写入L1(Redis)和L2(Qdrant)

        Args:
            query: 用户问题
            response: AI回答
            user_id: 用户ID
            provider: AI提供商
            intent: 意图类型
            complexity: 复杂度
            tokens_used: token使用量
            conversation_history: 对话历史
            ttl: Redis缓存TTL（秒）
        """
        try:
            # 确保已初始化
            if not self._initialized:
                await self.initialize()

            # 创建缓存条目
            cache_entry = CacheEntry(
                query=query,
                response=response,
                provider=provider,
                intent=intent,
                complexity=complexity,
                tokens_used=tokens_used,
                cached_at=datetime.utcnow().isoformat(),
                hit_count=0,
                user_id=user_id
            )

            # 计算节省成本
            cost_per_1k = self.COST_PER_1K_TOKENS.get(provider, 0.02)
            cost_saved = (tokens_used / 1000) * cost_per_1k
            self.stats.total_cost_saved_usd += cost_saved

            # 计算节省延迟
            latency_saved = self.LATENCY_ESTIMATE_MS.get(provider, 2000)
            self.stats.total_latency_saved_ms += latency_saved

            # 写入L1 (Redis)
            await self._write_to_redis(
                query,
                cache_entry,
                user_id,
                conversation_history,
                ttl
            )

            # 写入L2 (Qdrant) - 仅对复杂度>=3的问题
            if complexity >= 3:
                await self._write_to_qdrant(query, cache_entry, user_id)

            logger.debug(
                f"💾 Cache SET | "
                f"Query: {query[:30]}... | "
                f"Provider: {provider} | "
                f"Complexity: {complexity}"
            )

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def _write_to_redis(
        self,
        query: str,
        cache_entry: CacheEntry,
        user_id: str,
        conversation_history: Optional[List[Dict]],
        ttl: int
    ):
        """写入Redis (L1)"""
        try:
            context_hash = self._calculate_context_hash(conversation_history)
            cache_key = self._generate_cache_key(query, user_id, context_hash)

            await self.redis_manager.set(
                cache_key,
                json.dumps(cache_entry.to_dict()),
                ttl=ttl
            )
        except Exception as e:
            logger.error(f"Redis write error: {e}")

    async def _write_to_qdrant(
        self,
        query: str,
        cache_entry: CacheEntry,
        user_id: str
    ):
        """写入Qdrant (L2)"""
        try:
            # 编码查询向量
            loop = asyncio.get_event_loop()
            query_vector = await loop.run_in_executor(
                None,
                lambda: self.sentence_transformer.encode(
                    query,
                    convert_to_tensor=False
                ).tolist()
            )

            # 用户专属collection
            collection_name = f"cache_user_{user_id}"

            # 确保collection存在
            try:
                self.qdrant_client.get_collection(collection_name)
            except:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created Qdrant collection '{collection_name}'")

            # 生成点ID
            point_id = hashlib.md5(
                f"{user_id}:{query}".encode()
            ).hexdigest()

            # 插入向量
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=query_vector,
                        payload=cache_entry.to_dict()
                    )
                ]
            )

        except Exception as e:
            logger.error(f"Qdrant write error: {e}")

    async def invalidate_user_cache(self, user_id: str):
        """
        清空用户缓存

        Args:
            user_id: 用户ID
        """
        try:
            # 清空Redis
            pattern = f"response:{user_id}:*"
            deleted_count = await self.redis_manager.delete_pattern(pattern)

            # 清空Qdrant collection
            collection_name = f"cache_user_{user_id}"
            try:
                self.qdrant_client.delete_collection(collection_name)
            except:
                pass

            logger.info(
                f"🗑️  Cache invalidated for user {user_id} | "
                f"Deleted {deleted_count} Redis keys"
            )

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")

    def _update_cache_latency_stats(self, latency_ms: float, cached: bool):
        """更新延迟统计"""
        if cached:
            total_cached = (
                self.stats.l1_hits +
                self.stats.l2_hits +
                self.stats.l3_hits
            )
            if total_cached > 0:
                self.stats.avg_response_time_cached_ms = (
                    (self.stats.avg_response_time_cached_ms * (total_cached - 1) + latency_ms)
                    / total_cached
                )
        else:
            if self.stats.cache_misses > 0:
                self.stats.avg_response_time_uncached_ms = (
                    (self.stats.avg_response_time_uncached_ms * (self.stats.cache_misses - 1) + latency_ms)
                    / self.stats.cache_misses
                )

    def get_stats(self) -> dict:
        """
        获取缓存统计

        Returns:
            统计信息字典
        """
        total = self.stats.total_requests
        if total == 0:
            return {
                "message": "No requests yet",
                "total_requests": 0
            }

        total_hits = (
            self.stats.l1_hits +
            self.stats.l2_hits +
            self.stats.l3_hits
        )

        return {
            "total_requests": total,
            "total_hits": total_hits,
            "cache_hit_rate_percent": round(total_hits / total * 100, 2),
            "l1_hits": self.stats.l1_hits,
            "l1_hit_rate_percent": round(self.stats.l1_hits / total * 100, 2),
            "l2_hits": self.stats.l2_hits,
            "l2_hit_rate_percent": round(self.stats.l2_hits / total * 100, 2),
            "l3_hits": self.stats.l3_hits,
            "l3_hit_rate_percent": round(self.stats.l3_hits / total * 100, 2),
            "cache_misses": self.stats.cache_misses,
            "cache_miss_rate_percent": round(self.stats.cache_misses / total * 100, 2),
            "total_cost_saved_usd": round(self.stats.total_cost_saved_usd, 4),
            "total_latency_saved_ms": round(self.stats.total_latency_saved_ms, 2),
            "avg_cached_response_time_ms": round(self.stats.avg_response_time_cached_ms, 2),
            "avg_uncached_response_time_ms": round(self.stats.avg_response_time_uncached_ms, 2)
        }


# 全局单例
_cache_manager: Optional[ResponseCacheManager] = None


async def get_response_cache_manager() -> ResponseCacheManager:
    """
    获取全局ResponseCacheManager单例

    Returns:
        ResponseCacheManager实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = ResponseCacheManager()
        # 注意：不在这里初始化，懒加载到首次使用时

    return _cache_manager
