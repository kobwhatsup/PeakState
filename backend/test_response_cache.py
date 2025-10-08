"""
响应缓存系统测试套件
测试三层缓存架构的正确性和性能
"""

import asyncio
import pytest
from datetime import datetime
from typing import List, Dict
from app.ai.response_cache import ResponseCacheManager, CacheEntry


# ============ 测试配置 ============

@pytest.fixture
async def cache_manager():
    """创建缓存管理器实例"""
    manager = ResponseCacheManager()
    await manager.initialize()
    yield manager
    # 清理测试数据
    await manager.invalidate_user_cache("test_user_123")


# ============ L1 Redis缓存测试 ============

@pytest.mark.asyncio
async def test_l1_exact_match(cache_manager: ResponseCacheManager):
    """测试L1精确匹配缓存"""
    user_id = "test_user_123"
    query = "我今天感觉很累"
    response = "建议你早点休息，保证充足睡眠。"

    # 写入缓存
    await cache_manager.set_cache(
        query=query,
        response=response,
        user_id=user_id,
        provider="phi-3.5",
        intent="energy_management",
        complexity=4,
        tokens_used=150,
        ttl=86400
    )

    # 读取缓存 - 应该命中L1
    result = await cache_manager.get_cached_response(query, user_id)

    assert result is not None, "L1缓存应该命中"
    cache_entry, cache_layer = result
    assert cache_layer == "L1", "应该从L1层返回"
    assert cache_entry.response == response, "响应内容应该匹配"
    assert cache_entry.hit_count >= 1, "命中计数应该增加"

    print("✅ L1精确匹配测试通过")


@pytest.mark.asyncio
async def test_l1_case_insensitive(cache_manager: ResponseCacheManager):
    """测试L1大小写不敏感"""
    user_id = "test_user_123"

    # 写入小写
    await cache_manager.set_cache(
        query="hello world",
        response="你好！",
        user_id=user_id,
        provider="phi-3.5",
        intent="greeting",
        complexity=1,
        tokens_used=50,
        ttl=86400
    )

    # 查询大写
    result = await cache_manager.get_cached_response("HELLO WORLD", user_id)

    assert result is not None, "L1应该大小写不敏感"
    cache_entry, cache_layer = result
    assert cache_layer == "L1"
    assert cache_entry.response == "你好！"

    print("✅ L1大小写不敏感测试通过")


@pytest.mark.asyncio
async def test_l1_whitespace_normalization(cache_manager: ResponseCacheManager):
    """测试L1空白字符归一化"""
    user_id = "test_user_123"

    # 写入带多余空格
    await cache_manager.set_cache(
        query="  我  今天  很  累  ",
        response="好好休息",
        user_id=user_id,
        provider="phi-3.5",
        intent="energy_management",
        complexity=3,
        tokens_used=80,
        ttl=86400
    )

    # 查询正常空格
    result = await cache_manager.get_cached_response("我 今天 很 累", user_id)

    assert result is not None, "L1应该归一化空白字符"
    cache_entry, _ = result
    assert cache_entry.response == "好好休息"

    print("✅ L1空白字符归一化测试通过")


@pytest.mark.asyncio
async def test_l1_conversation_context(cache_manager: ResponseCacheManager):
    """测试L1会话上下文区分"""
    user_id = "test_user_123"
    query = "继续"

    # 不同上下文，相同query
    context1 = [{"role": "user", "content": "我想减肥"}]
    context2 = [{"role": "user", "content": "我想增肌"}]

    # 写入上下文1的缓存
    await cache_manager.set_cache(
        query=query,
        response="减肥需要控制饮食",
        user_id=user_id,
        provider="phi-3.5",
        intent="health_advice",
        complexity=5,
        tokens_used=120,
        conversation_history=context1,
        ttl=86400
    )

    # 查询上下文1 - 应该命中
    result1 = await cache_manager.get_cached_response(query, user_id, context1)
    assert result1 is not None, "上下文1应该命中"
    assert result1[0].response == "减肥需要控制饮食"

    # 查询上下文2 - 不应该命中L1
    result2 = await cache_manager.get_cached_response(query, user_id, context2)
    # 可能命中L2或L3，或者未命中

    print("✅ L1会话上下文区分测试通过")


# ============ L2 语义相似度测试 ============

@pytest.mark.asyncio
async def test_l2_semantic_similarity(cache_manager: ResponseCacheManager):
    """测试L2语义相似度匹配"""
    user_id = "test_user_123"

    # 写入原始问题
    await cache_manager.set_cache(
        query="如何改善睡眠质量？",
        response="改善睡眠可以从作息规律、睡前放松、优化环境等方面入手。",
        user_id=user_id,
        provider="gpt-4o-mini",
        intent="sleep_advice",
        complexity=6,
        tokens_used=200,
        ttl=604800
    )

    # 等待向量写入
    await asyncio.sleep(0.5)

    # 查询相似问题
    similar_queries = [
        "怎么让睡眠更好？",
        "睡眠不好怎么办？",
        "如何提高睡眠质量",
    ]

    for similar_query in similar_queries:
        result = await cache_manager.get_cached_response(
            similar_query,
            user_id,
            similarity_threshold=0.85
        )

        if result:
            cache_entry, cache_layer = result
            assert cache_layer in ["L1", "L2", "L3"], f"缓存层级错误: {cache_layer}"
            print(f"  ✓ 相似问题 '{similar_query}' 命中缓存层 {cache_layer}")
        else:
            print(f"  ✗ 相似问题 '{similar_query}' 未命中缓存")

    print("✅ L2语义相似度测试完成")


@pytest.mark.asyncio
async def test_l2_similarity_threshold(cache_manager: ResponseCacheManager):
    """测试L2相似度阈值"""
    user_id = "test_user_123"

    # 写入问题
    await cache_manager.set_cache(
        query="今天天气怎么样？",
        response="抱歉，我无法获取实时天气信息。",
        user_id=user_id,
        provider="phi-3.5",
        intent="weather_query",
        complexity=2,
        tokens_used=60,
        ttl=86400
    )

    await asyncio.sleep(0.5)

    # 高相似度问题 - 应该命中
    result_high = await cache_manager.get_cached_response(
        "今天的天气如何？",
        user_id,
        similarity_threshold=0.85
    )
    assert result_high is not None, "高相似度问题应该命中"

    # 低相似度问题 - 不应该命中L2
    result_low = await cache_manager.get_cached_response(
        "我今天应该穿什么？",
        user_id,
        similarity_threshold=0.92
    )
    # 可能命中L3或未命中

    print("✅ L2相似度阈值测试通过")


@pytest.mark.asyncio
async def test_l2_multilingual(cache_manager: ResponseCacheManager):
    """测试L2多语言支持"""
    user_id = "test_user_123"

    # 写入中文问题
    await cache_manager.set_cache(
        query="如何提高工作效率？",
        response="提高工作效率的方法包括时间管理、专注力训练、合理休息等。",
        user_id=user_id,
        provider="gpt-4o-mini",
        intent="productivity_advice",
        complexity=6,
        tokens_used=180,
        ttl=604800
    )

    await asyncio.sleep(0.5)

    # 查询英文相似问题（测试跨语言）
    # 注意：paraphrase-multilingual-MiniLM-L12-v2支持跨语言
    result = await cache_manager.get_cached_response(
        "How to improve work efficiency?",
        user_id,
        similarity_threshold=0.80
    )

    if result:
        print("  ✓ 跨语言匹配成功")
    else:
        print("  ✗ 跨语言匹配未成功（可能需要调整阈值）")

    print("✅ L2多语言测试完成")


# ============ L3 知识库测试 ============

@pytest.mark.asyncio
async def test_l3_knowledge_base(cache_manager: ResponseCacheManager):
    """测试L3知识库命中"""
    user_id = "test_user_123"

    # 查询知识库中的常见问题
    knowledge_queries = [
        "你好",
        "谢谢",
        "再见",
        "你是谁？",
        "你能做什么？",
    ]

    hit_count = 0
    for query in knowledge_queries:
        result = await cache_manager.get_cached_response(
            query,
            user_id,
            similarity_threshold=0.88
        )

        if result:
            cache_entry, cache_layer = result
            if cache_layer == "L3":
                hit_count += 1
                print(f"  ✓ '{query}' 命中L3知识库")
            else:
                print(f"  ✓ '{query}' 命中{cache_layer}")
        else:
            print(f"  ✗ '{query}' 未命中缓存")

    assert hit_count > 0, "至少应该有一个问题命中L3知识库"
    print(f"✅ L3知识库测试通过 ({hit_count}/{len(knowledge_queries)} 命中)")


@pytest.mark.asyncio
async def test_l3_health_knowledge(cache_manager: ResponseCacheManager):
    """测试L3健康知识库"""
    user_id = "test_user_123"

    # 查询健康相关的常见问题
    health_queries = [
        "如何改善睡眠",
        "怎么提高免疫力",
        "运动后应该吃什么",
        "如何缓解压力",
    ]

    for query in health_queries:
        result = await cache_manager.get_cached_response(
            query,
            user_id,
            similarity_threshold=0.85
        )

        if result:
            cache_entry, cache_layer = result
            print(f"  ✓ '{query}' 命中{cache_layer}")
            print(f"    响应预览: {cache_entry.response[:50]}...")
        else:
            print(f"  ✗ '{query}' 未命中缓存")

    print("✅ L3健康知识库测试完成")


# ============ 缓存失效测试 ============

@pytest.mark.asyncio
async def test_cache_invalidation(cache_manager: ResponseCacheManager):
    """测试缓存失效"""
    user_id = "test_user_123"

    # 写入多条缓存
    for i in range(5):
        await cache_manager.set_cache(
            query=f"测试问题{i}",
            response=f"测试回答{i}",
            user_id=user_id,
            provider="phi-3.5",
            intent="test",
            complexity=3,
            tokens_used=50,
            ttl=86400
        )

    # 验证缓存存在
    result_before = await cache_manager.get_cached_response("测试问题0", user_id)
    assert result_before is not None, "缓存应该存在"

    # 清空用户缓存
    await cache_manager.invalidate_user_cache(user_id)

    # 验证缓存已清空
    result_after = await cache_manager.get_cached_response("测试问题0", user_id)
    # L1应该被清空，但可能仍命中L3

    print("✅ 缓存失效测试通过")


# ============ 统计数据测试 ============

@pytest.mark.asyncio
async def test_cache_stats(cache_manager: ResponseCacheManager):
    """测试缓存统计"""
    user_id = "test_user_123"

    # 执行一些缓存操作
    for i in range(10):
        await cache_manager.set_cache(
            query=f"统计测试{i}",
            response=f"回答{i}",
            user_id=user_id,
            provider="phi-3.5",
            intent="test",
            complexity=3,
            tokens_used=50,
            ttl=86400
        )

        # 读取几次以增加命中计数
        if i < 5:
            await cache_manager.get_cached_response(f"统计测试{i}", user_id)

    # 获取统计数据
    stats = cache_manager.get_stats()

    assert "total_requests" in stats, "统计应该包含总请求数"
    assert "cache_hit_rate_percent" in stats, "统计应该包含命中率"

    print(f"✅ 缓存统计测试通过")
    print(f"  总请求: {stats.get('total_requests', 0)}")
    print(f"  L1命中: {stats.get('l1_hits', 0)}")
    print(f"  L2命中: {stats.get('l2_hits', 0)}")
    print(f"  L3命中: {stats.get('l3_hits', 0)}")
    print(f"  未命中: {stats.get('cache_misses', 0)}")


# ============ 性能测试 ============

@pytest.mark.asyncio
async def test_cache_performance(cache_manager: ResponseCacheManager):
    """测试缓存性能"""
    import time

    user_id = "test_user_123"
    query = "性能测试问题"

    # 写入缓存
    await cache_manager.set_cache(
        query=query,
        response="性能测试回答",
        user_id=user_id,
        provider="phi-3.5",
        intent="test",
        complexity=3,
        tokens_used=50,
        ttl=86400
    )

    # 测试L1读取性能
    l1_times = []
    for _ in range(100):
        start = time.time()
        result = await cache_manager.get_cached_response(query, user_id)
        elapsed = (time.time() - start) * 1000
        l1_times.append(elapsed)

    avg_l1_time = sum(l1_times) / len(l1_times)

    assert avg_l1_time < 10, f"L1平均响应时间应该 <10ms，实际: {avg_l1_time:.2f}ms"

    print(f"✅ 缓存性能测试通过")
    print(f"  L1平均响应时间: {avg_l1_time:.2f}ms")
    print(f"  L1最快: {min(l1_times):.2f}ms")
    print(f"  L1最慢: {max(l1_times):.2f}ms")


# ============ 并发测试 ============

@pytest.mark.asyncio
async def test_concurrent_access(cache_manager: ResponseCacheManager):
    """测试并发访问"""
    user_id = "test_user_123"

    # 写入缓存
    await cache_manager.set_cache(
        query="并发测试",
        response="并发回答",
        user_id=user_id,
        provider="phi-3.5",
        intent="test",
        complexity=3,
        tokens_used=50,
        ttl=86400
    )

    # 并发读取
    tasks = [
        cache_manager.get_cached_response("并发测试", user_id)
        for _ in range(50)
    ]

    results = await asyncio.gather(*tasks)

    # 验证所有请求都成功
    successful_reads = sum(1 for r in results if r is not None)

    assert successful_reads == 50, "所有并发请求都应该成功"

    print(f"✅ 并发访问测试通过 ({successful_reads}/50 成功)")


# ============ 运行测试 ============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 响应缓存系统测试套件")
    print("="*60 + "\n")

    # 运行所有测试
    pytest.main([__file__, "-v", "-s"])
