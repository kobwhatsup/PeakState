"""
复杂度分析器测试套件
验证ComplexityAnalyzer的准确性和性能
"""

import asyncio
import time
from typing import List, Dict
from app.ai.complexity_analyzer import get_complexity_analyzer
from app.ai.orchestrator import IntentType, IntentClassification


# 测试用例集
TEST_CASES: List[Dict] = [
    # ===== 简单请求 (预期复杂度: 1-3) =====
    {
        "message": "你好",
        "intent": IntentType.GREETING,
        "conversation_history": [],
        "user_profile": {"days_active": 1},
        "expected_range": (1, 3),
        "description": "简单问候，新用户"
    },
    {
        "message": "好的，明白了",
        "intent": IntentType.CONFIRMATION,
        "conversation_history": [
            {"role": "user", "content": "帮我看看我的睡眠数据"},
            {"role": "assistant", "content": "好的，我来帮你查看"}
        ],
        "user_profile": {"days_active": 5},
        "expected_range": (1, 3),
        "description": "简单确认，短对话"
    },

    # ===== 中等复杂度 (预期复杂度: 4-6) =====
    {
        "message": "我想查看最近7天的睡眠数据",
        "intent": IntentType.DATA_QUERY,
        "conversation_history": [],
        "user_profile": {"days_active": 10},
        "expected_range": (3, 5),
        "description": "数据查询，新对话"
    },
    {
        "message": "给我一些改善睡眠的建议，我最近总是半夜醒来",
        "intent": IntentType.ADVICE_REQUEST,
        "conversation_history": [],
        "user_profile": {"days_active": 15, "occupation": "工程师"},
        "expected_range": (5, 7),
        "description": "建议请求，包含具体症状描述"
    },
    {
        "message": "我感到很焦虑，压力很大",
        "intent": IntentType.EMOTIONAL_SUPPORT,
        "conversation_history": [],
        "user_profile": {"days_active": 3},
        "expected_range": (5, 7),
        "description": "情感支持，新用户情绪问题"
    },

    # ===== 高复杂度 (预期复杂度: 7-10) =====
    {
        "message": "帮我分析一下我的整体健康状况，我的心率变异性最近一直很低，睡眠质量也不好",
        "intent": IntentType.COMPLEX_ANALYSIS,
        "conversation_history": [],
        "user_profile": {"days_active": 45, "occupation": "医生"},
        "expected_range": (7, 10),
        "description": "复杂分析，包含专业术语（HRV），资深用户"
    },
    {
        "message": "我的症状包括持续疲劳、注意力不集中、睡眠障碍，这可能是什么原因造成的？",
        "intent": IntentType.HEALTH_DIAGNOSIS,
        "conversation_history": [],
        "user_profile": {"days_active": 30},
        "expected_range": (8, 10),
        "description": "健康诊断，多症状描述"
    },

    # ===== 上下文复杂度测试 =====
    {
        "message": "那具体应该怎么做呢？",
        "intent": IntentType.ADVICE_REQUEST,
        "conversation_history": [
            {"role": "user", "content": "我最近睡眠很差"},
            {"role": "assistant", "content": "建议你调整作息"},
            {"role": "user", "content": "我试过了，但是效果不好"},
            {"role": "assistant", "content": "可能需要更深入的调整"},
            {"role": "user", "content": "比如呢？"},
            {"role": "assistant", "content": "包括睡前习惯和环境优化"}
        ],
        "user_profile": {"days_active": 20},
        "expected_range": (6, 8),
        "description": "长对话历史（6轮），上下文引用"
    },
    {
        "message": "我想了解一下褪黑素和皮质醇的关系，以及如何通过调节昼夜节律来改善我的深度睡眠和REM睡眠比例",
        "intent": IntentType.COMPLEX_ANALYSIS,
        "conversation_history": [],
        "user_profile": {"days_active": 90, "occupation": "健康管理师"},
        "expected_range": (9, 10),
        "description": "高专业术语密度，资深用户，复杂问题"
    },

    # ===== 主题切换测试 =====
    {
        "message": "对了，我想问问营养方面的问题",
        "intent": IntentType.ADVICE_REQUEST,
        "conversation_history": [
            {"role": "user", "content": "我的睡眠数据怎么样"},
            {"role": "assistant", "content": "你的睡眠质量还不错"},
            {"role": "user", "content": "那心率呢"},
            {"role": "assistant", "content": "心率也在正常范围"}
        ],
        "user_profile": {"days_active": 15},
        "expected_range": (5, 7),
        "description": "主题切换（睡眠/心率 → 营养）"
    },

    # ===== 数据引用测试 =====
    {
        "message": "我的心率是75 bpm，睡眠时长6.5小时，深度睡眠只有1.2小时，这正常吗？",
        "intent": IntentType.DATA_QUERY,
        "conversation_history": [],
        "user_profile": {"days_active": 25},
        "expected_range": (5, 7),
        "description": "多个具体数据引用"
    }
]


async def run_tests():
    """运行测试套件"""
    print("=" * 80)
    print("🧪 复杂度分析器测试套件")
    print("=" * 80)
    print()

    analyzer = get_complexity_analyzer()

    correct = 0
    total = len(TEST_CASES)
    errors = []
    analysis_times = []

    for i, test in enumerate(TEST_CASES, 1):
        message = test["message"]
        intent_type = test["intent"]
        conversation_history = test["conversation_history"]
        user_profile = test["user_profile"]
        expected_range = test["expected_range"]
        description = test["description"]

        # 构建IntentClassification
        intent = IntentClassification(
            intent=intent_type,
            confidence=0.95,
            requires_empathy=(intent_type == IntentType.EMOTIONAL_SUPPORT),
            requires_tools=(intent_type in [IntentType.DATA_QUERY, IntentType.COMPLEX_ANALYSIS]),
            requires_rag=(intent_type in [IntentType.ADVICE_REQUEST, IntentType.COMPLEX_ANALYSIS])
        )

        # 计时
        start_time = time.time()
        factors = await analyzer.analyze_complexity(
            intent=intent,
            user_message=message,
            conversation_history=conversation_history,
            user_profile=user_profile,
            user_id=f"test_user_{i}"
        )
        analysis_time = (time.time() - start_time) * 1000  # ms

        analysis_times.append(analysis_time)

        # 判断是否在预期范围内
        complexity = factors.total_score
        expected_min, expected_max = expected_range
        is_correct = expected_min <= complexity <= expected_max

        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
            errors.append({
                "message": message,
                "expected_range": expected_range,
                "actual": complexity,
                "description": description,
                "factors": factors
            })

        # 打印结果
        print(f"{status} [{i}/{total}] {description}")
        print(f"   消息: \"{message[:50]}{'...' if len(message) > 50 else ''}\"")
        print(f"   意图: {intent_type.value}")
        print(f"   预期范围: {expected_min}-{expected_max}")
        print(f"   实际复杂度: {complexity}")
        print(f"   分解: Base={factors.base_score} "
              f"Context=+{factors.context_adjustment} "
              f"User=+{factors.user_pattern_adjustment} "
              f"Depth=+{factors.conversation_depth_adjustment} "
              f"Tech=+{factors.technical_level_adjustment}")
        print(f"   耗时: {analysis_time:.1f}ms")
        print()

    # 统计结果
    accuracy = (correct / total) * 100
    avg_time = sum(analysis_times) / len(analysis_times)
    max_time = max(analysis_times)
    min_time = min(analysis_times)

    print("=" * 80)
    print("📊 测试结果统计")
    print("=" * 80)
    print(f"总测试用例: {total}")
    print(f"正确: {correct}")
    print(f"错误: {total - correct}")
    print(f"准确率: {accuracy:.1f}%")
    print()
    print(f"平均分析时间: {avg_time:.1f}ms")
    print(f"最快: {min_time:.1f}ms")
    print(f"最慢: {max_time:.1f}ms")
    print()

    # 分析器统计
    stats = analyzer.get_stats()
    print("📈 分析器性能统计")
    print("=" * 80)
    print(f"总分析次数: {stats['analysis_count']}")
    print(f"平均分析时间: {stats['avg_analysis_time_ms']:.1f}ms")
    print(f"用户画像缓存: {stats['user_profiles_cached']}")
    print(f"决策历史记录: {stats['decision_history_size']}")
    print()

    # 错误详情
    if errors:
        print("❌ 错误详情")
        print("=" * 80)
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error['description']}")
            print(f"   消息: \"{error['message'][:50]}{'...' if len(error['message']) > 50 else ''}\"")
            print(f"   预期范围: {error['expected_range'][0]}-{error['expected_range'][1]}")
            print(f"   实际复杂度: {error['actual']}")
            print(f"   偏差: {error['actual'] - sum(error['expected_range'])/2:.1f}")
            print()

    # 评估
    print("=" * 80)
    print("🎯 评估结论")
    print("=" * 80)
    if accuracy >= 90:
        print("✅ 优秀! 复杂度计算准确率达到90%以上")
    elif accuracy >= 80:
        print("✅ 良好! 复杂度计算准确率达到80%以上")
    elif accuracy >= 70:
        print("⚠️  合格，但需要进一步优化权重")
    else:
        print("❌ 不合格，需要调整计算逻辑")

    if avg_time < 5:
        print("✅ 分析速度优秀 (平均 <5ms)")
    elif avg_time < 10:
        print("✅ 分析速度良好 (平均 <10ms)")
    else:
        print("⚠️  分析速度较慢，考虑优化")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_tests())
