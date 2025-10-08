"""
意图分类器测试套件
测试混合意图分类系统的准确性和性能
"""

import asyncio
import time
from typing import List, Dict
from app.ai.intent_classifier import get_intent_classifier
from app.ai.orchestrator import IntentType


# 测试用例集
TEST_CASES: List[Dict] = [
    # ===== 问候 (GREETING) =====
    {
        "message": "你好",
        "expected": IntentType.GREETING,
        "description": "简单问候"
    },
    {
        "message": "早上好！今天天气不错",
        "expected": IntentType.GREETING,
        "description": "早上问候"
    },
    {
        "message": "嗨，在吗？",
        "expected": IntentType.GREETING,
        "description": "打招呼"
    },

    # ===== 确认 (CONFIRMATION) =====
    {
        "message": "好的",
        "expected": IntentType.CONFIRMATION,
        "description": "简单确认"
    },
    {
        "message": "嗯，可以",
        "expected": IntentType.CONFIRMATION,
        "description": "同意确认"
    },
    {
        "message": "没问题",
        "expected": IntentType.CONFIRMATION,
        "description": "肯定回答"
    },

    # ===== 数据查询 (DATA_QUERY) =====
    {
        "message": "查询我的睡眠数据",
        "expected": IntentType.DATA_QUERY,
        "description": "查询睡眠数据"
    },
    {
        "message": "我想看看最近的心率记录",
        "expected": IntentType.DATA_QUERY,
        "description": "查看心率"
    },
    {
        "message": "显示我的运动统计",
        "expected": IntentType.DATA_QUERY,
        "description": "查看运动数据"
    },
    {
        "message": "我最近睡得怎么样",
        "expected": IntentType.DATA_QUERY,
        "description": "询问睡眠情况"
    },
    {
        "message": "我的步数是多少",
        "expected": IntentType.DATA_QUERY,
        "description": "询问步数"
    },

    # ===== 建议请求 (ADVICE_REQUEST) =====
    {
        "message": "给我一些健康建议",
        "expected": IntentType.ADVICE_REQUEST,
        "description": "请求健康建议"
    },
    {
        "message": "我应该如何改善睡眠",
        "expected": IntentType.ADVICE_REQUEST,
        "description": "请求睡眠改善建议"
    },
    {
        "message": "帮我制定运动计划",
        "expected": IntentType.ADVICE_REQUEST,
        "description": "请求运动计划"
    },
    {
        "message": "怎样才能提高能量水平",
        "expected": IntentType.ADVICE_REQUEST,
        "description": "询问提高能量方法"
    },
    {
        "message": "如何降低压力",
        "expected": IntentType.ADVICE_REQUEST,
        "description": "请求减压建议"
    },

    # ===== 情感支持 (EMOTIONAL_SUPPORT) =====
    {
        "message": "我感到很焦虑",
        "expected": IntentType.EMOTIONAL_SUPPORT,
        "description": "表达焦虑情绪"
    },
    {
        "message": "最近压力很大，撑不下去了",
        "expected": IntentType.EMOTIONAL_SUPPORT,
        "description": "表达压力"
    },
    {
        "message": "心情不好，想聊聊",
        "expected": IntentType.EMOTIONAL_SUPPORT,
        "description": "寻求倾诉"
    },
    {
        "message": "我很疲惫，需要帮助",
        "expected": IntentType.EMOTIONAL_SUPPORT,
        "description": "表达疲惫求助"
    },
    {
        "message": "我很难受，感觉很沮丧",
        "expected": IntentType.EMOTIONAL_SUPPORT,
        "description": "表达沮丧情绪"
    },

    # ===== 复杂分析 (COMPLEX_ANALYSIS) =====
    {
        "message": "分析我的整体健康状况",
        "expected": IntentType.COMPLEX_ANALYSIS,
        "description": "请求全面分析"
    },
    {
        "message": "评估我的能量管理效果",
        "expected": IntentType.COMPLEX_ANALYSIS,
        "description": "请求效果评估"
    },
    {
        "message": "帮我诊断睡眠问题",
        "expected": IntentType.COMPLEX_ANALYSIS,
        "description": "请求诊断"
    },
    {
        "message": "制定个性化健康方案",
        "expected": IntentType.COMPLEX_ANALYSIS,
        "description": "请求个性化方案"
    },

    # ===== 健康诊断 (HEALTH_DIAGNOSIS) =====
    {
        "message": "我的症状是什么原因",
        "expected": IntentType.HEALTH_DIAGNOSIS,
        "description": "询问症状原因"
    },
    {
        "message": "帮我诊断这个健康问题",
        "expected": IntentType.HEALTH_DIAGNOSIS,
        "description": "请求健康诊断"
    },
    {
        "message": "这些数据说明我有什么问题",
        "expected": IntentType.HEALTH_DIAGNOSIS,
        "description": "基于数据询问问题"
    },
    {
        "message": "为什么我会有这些症状",
        "expected": IntentType.HEALTH_DIAGNOSIS,
        "description": "询问症状原因"
    },

    # ===== 难例测试 (测试旧系统误分类的情况) =====
    {
        "message": "我睡眠很差，心情也很糟糕",
        "expected": IntentType.EMOTIONAL_SUPPORT,  # 旧系统会错误识别为DATA_QUERY
        "description": "混合情感+数据关键词 (难例)"
    },
    {
        "message": "虽然我的心率数据正常，但我还是感觉很累",
        "expected": IntentType.EMOTIONAL_SUPPORT,  # 主要是情感诉求
        "description": "数据+情感 (难例)"
    },
    {
        "message": "怎么查看我的压力水平",
        "expected": IntentType.DATA_QUERY,  # 是查询，不是减压建议
        "description": "查询+压力关键词 (难例)"
    }
]


async def run_tests():
    """运行测试套件"""
    print("=" * 80)
    print("🧪 意图分类器测试套件")
    print("=" * 80)
    print()

    classifier = get_intent_classifier()

    correct = 0
    total = len(TEST_CASES)
    errors = []
    inference_times = []

    for i, test in enumerate(TEST_CASES, 1):
        message = test["message"]
        expected = test["expected"]
        description = test["description"]

        # 计时
        start_time = time.time()
        result = await classifier.classify(message)
        inference_time = (time.time() - start_time) * 1000  # ms

        inference_times.append(inference_time)

        # 判断正确性
        is_correct = result.intent == expected
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
            errors.append({
                "message": message,
                "expected": expected.value,
                "got": result.intent.value,
                "confidence": result.confidence,
                "description": description
            })

        # 打印结果
        print(f"{status} [{i}/{total}] {description}")
        print(f"   消息: \"{message}\"")
        print(f"   预期: {expected.value}")
        print(f"   实际: {result.intent.value} (置信度: {result.confidence:.2f})")
        print(f"   耗时: {inference_time:.1f}ms")
        print()

    # 统计结果
    accuracy = (correct / total) * 100
    avg_time = sum(inference_times) / len(inference_times)
    max_time = max(inference_times)
    min_time = min(inference_times)

    print("=" * 80)
    print("📊 测试结果统计")
    print("=" * 80)
    print(f"总测试用例: {total}")
    print(f"正确: {correct}")
    print(f"错误: {total - correct}")
    print(f"准确率: {accuracy:.1f}%")
    print()
    print(f"平均推理时间: {avg_time:.1f}ms")
    print(f"最快: {min_time:.1f}ms")
    print(f"最慢: {max_time:.1f}ms")
    print()

    # 性能统计
    stats = classifier.get_stats()
    if stats["status"] == "active":
        print("📈 分类器性能统计")
        print("=" * 80)
        print(f"模型已加载: {stats['model_loaded']}")
        print(f"总分类次数: {stats['classification_count']}")
        print(f"规则匹配: {stats['rule_match_count']} ({stats['rule_percentage']}%)")
        print(f"语义匹配: {stats['semantic_match_count']} ({stats['semantic_percentage']}%)")
        print(f"平均推理时间: {stats['avg_inference_time_ms']:.1f}ms")
        print()

    # 错误详情
    if errors:
        print("❌ 错误详情")
        print("=" * 80)
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error['description']}")
            print(f"   消息: \"{error['message']}\"")
            print(f"   预期: {error['expected']}")
            print(f"   实际: {error['got']} (置信度: {error['confidence']:.2f})")
            print()

    # 评估
    print("=" * 80)
    print("🎯 评估结论")
    print("=" * 80)
    if accuracy >= 90:
        print("✅ 优秀! 意图分类准确率达到90%以上")
    elif accuracy >= 80:
        print("✅ 良好! 意图分类准确率达到80%以上")
    elif accuracy >= 70:
        print("⚠️  合格，但需要进一步优化模板")
    else:
        print("❌ 不合格，需要检查模板配置和模型")

    if avg_time < 100:
        print("✅ 推理速度优秀 (平均 <100ms)")
    elif avg_time < 200:
        print("✅ 推理速度良好 (平均 <200ms)")
    else:
        print("⚠️  推理速度较慢，考虑优化")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_tests())
