"""
意图分类器 - 升级版
使用混合策略: 规则匹配 + Sentence-Transformers语义相似度

策略：
- 简单意图 (GREETING, CONFIRMATION) → 规则匹配 (<5ms)
- 复杂意图 → Sentence-Transformers语义匹配 (~50ms)
"""

import re
import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, field

from sentence_transformers import SentenceTransformer, util
import torch

# Import IntentType and IntentClassification from orchestrator
from app.ai.orchestrator import IntentType, IntentClassification

logger = logging.getLogger(__name__)


@dataclass
class IntentTemplate:
    """意图模板配置"""
    intent_type: IntentType
    examples: List[str]
    keywords: List[str] = field(default_factory=list)


class IntentClassifier:
    """
    混合意图分类器

    功能：
    1. 快速规则匹配 (简单意图)
    2. 语义相似度匹配 (复杂意图)
    3. 置信度校准
    4. 性能监控
    """

    def __init__(self):
        """初始化分类器"""
        self.model = None  # 懒加载
        self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.is_loaded = False
        self.load_lock = asyncio.Lock()

        # 性能指标
        self.classification_count = 0
        self.total_inference_time = 0.0
        self.rule_match_count = 0
        self.semantic_match_count = 0

        # 预定义意图模板
        self.intent_templates = self._initialize_templates()

        # 预计算的模板嵌入 (懒加载后填充)
        self.template_embeddings: Dict[IntentType, torch.Tensor] = {}

        logger.info("🎯 IntentClassifier initialized")

    def _initialize_templates(self) -> Dict[IntentType, IntentTemplate]:
        """
        初始化意图模板
        每个意图包含：
        - 示例句子 (用于语义匹配)
        - 关键词 (用于辅助判断)
        """
        return {
            IntentType.DATA_QUERY: IntentTemplate(
                intent_type=IntentType.DATA_QUERY,
                examples=[
                    "查询我的睡眠数据",
                    "查看我的心率记录",
                    "显示我的健康数据",
                    "我想看看我的运动统计",
                    "我最近睡得怎么样",
                    "我的步数是多少",
                    "查看我的HRV数据",
                    "我的健康指标如何"
                ],
                keywords=["查询", "查看", "显示", "数据", "记录", "统计", "多少"]
            ),

            IntentType.ADVICE_REQUEST: IntentTemplate(
                intent_type=IntentType.ADVICE_REQUEST,
                examples=[
                    "给我一些健康建议",
                    "我应该如何改善睡眠",
                    "帮我制定运动计划",
                    "怎样才能提高能量水平",
                    "如何降低压力",
                    "怎么能睡得更好",
                    "有什么方法可以提升精力",
                    "给我一些减压的建议"
                ],
                keywords=["建议", "怎么", "如何", "怎样", "帮我", "方法", "计划"]
            ),

            IntentType.EMOTIONAL_SUPPORT: IntentTemplate(
                intent_type=IntentType.EMOTIONAL_SUPPORT,
                examples=[
                    "我感到很焦虑",
                    "最近压力很大",
                    "我很疲惫，需要帮助",
                    "心情不好，想聊聊",
                    "我很难受",
                    "感觉很累，撑不下去了",
                    "最近很沮丧",
                    "我需要有人理解我"
                ],
                keywords=["焦虑", "压力", "累", "疲惫", "难受", "沮丧", "痛苦", "抑郁"]
            ),

            IntentType.COMPLEX_ANALYSIS: IntentTemplate(
                intent_type=IntentType.COMPLEX_ANALYSIS,
                examples=[
                    "分析我的整体健康状况",
                    "评估我的能量管理效果",
                    "帮我诊断睡眠问题",
                    "制定个性化健康方案",
                    "综合分析我的健康数据",
                    "评估我最近的健康趋势",
                    "帮我找出健康问题的原因",
                    "全面评估我的身体状态"
                ],
                keywords=["分析", "评估", "诊断", "方案", "综合", "全面", "整体"]
            ),

            IntentType.HEALTH_DIAGNOSIS: IntentTemplate(
                intent_type=IntentType.HEALTH_DIAGNOSIS,
                examples=[
                    "我的症状是什么原因",
                    "帮我诊断这个健康问题",
                    "这些数据说明我有什么问题",
                    "评估我的健康风险",
                    "我这是什么病",
                    "为什么我会有这些症状",
                    "我的身体有什么问题",
                    "这种情况严重吗"
                ],
                keywords=["症状", "诊断", "问题", "风险", "病", "严重", "原因"]
            )
        }

    async def _load_model(self):
        """懒加载Sentence-Transformers模型"""
        async with self.load_lock:
            if self.is_loaded:
                return

            logger.info(f"📦 Loading Sentence-Transformers model: {self.model_name}")
            start_time = datetime.now()

            try:
                # 在线程池中加载模型（避免阻塞事件循环）
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None,
                    self._load_model_sync
                )

                # 预计算所有模板的嵌入
                await self._precompute_template_embeddings()

                load_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Model loaded in {load_time:.2f}s")

                self.is_loaded = True

            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}", exc_info=True)
                raise RuntimeError(f"Intent classifier model loading failed: {e}")

    def _load_model_sync(self) -> SentenceTransformer:
        """同步加载模型（在线程池中执行）"""
        return SentenceTransformer(self.model_name)

    async def _precompute_template_embeddings(self):
        """预计算所有意图模板的嵌入向量"""
        logger.info("🔄 Precomputing template embeddings...")

        loop = asyncio.get_event_loop()

        for intent_type, template in self.intent_templates.items():
            # 在线程池中编码
            embeddings = await loop.run_in_executor(
                None,
                lambda examples=template.examples: self.model.encode(
                    examples,
                    convert_to_tensor=True
                )
            )

            self.template_embeddings[intent_type] = embeddings
            logger.debug(f"   ✓ {intent_type.value}: {len(template.examples)} templates")

        logger.info(f"✅ Precomputed {len(self.template_embeddings)} intent embeddings")

    def _classify_simple_intents(self, message: str) -> Optional[IntentClassification]:
        """
        快速规则匹配 (适用于简单意图)

        返回 None 表示需要使用语义模型

        Args:
            message: 用户消息

        Returns:
            IntentClassification 或 None
        """
        msg_lower = message.lower().strip()

        # 问候 (高置信度关键词)
        greeting_patterns = [
            r'^(你好|您好|hi|hello|早上好|下午好|晚上好|嗨|hey)',
            r'^(在吗|在不在|有人吗)'
        ]

        for pattern in greeting_patterns:
            if re.search(pattern, msg_lower):
                return IntentClassification(
                    intent=IntentType.GREETING,
                    confidence=0.95,
                    requires_empathy=False,
                    requires_tools=False,
                    requires_rag=False
                )

        # 确认 (简短回复)
        if len(message) <= 6:
            confirmation_words = [
                "好的", "好", "嗯", "是的", "对", "ok",
                "行", "可以", "没问题", "同意", "确定"
            ]
            if any(word in msg_lower for word in confirmation_words):
                return IntentClassification(
                    intent=IntentType.CONFIRMATION,
                    confidence=0.90,
                    requires_empathy=False,
                    requires_tools=False,
                    requires_rag=False
                )

        return None  # 需要使用语义模型

    async def _classify_with_semantic_model(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentClassification:
        """
        使用Sentence-Transformers进行语义相似度匹配

        Args:
            message: 用户消息
            conversation_history: 对话历史（可选）

        Returns:
            IntentClassification
        """
        # 确保模型已加载
        if not self.is_loaded:
            await self._load_model()

        # 编码用户消息
        loop = asyncio.get_event_loop()
        message_embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(message, convert_to_tensor=True)
        )

        # 计算与每个意图模板的相似度
        best_intent = None
        best_score = 0.0
        intent_scores = {}

        for intent_type, template_embeddings in self.template_embeddings.items():
            # 计算余弦相似度
            similarities = util.cos_sim(message_embedding, template_embeddings)[0]

            # 取最大相似度
            max_similarity = similarities.max().item()
            intent_scores[intent_type] = max_similarity

            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent_type

        # 如果没有找到合适的意图，默认为ADVICE_REQUEST
        if best_intent is None:
            best_intent = IntentType.ADVICE_REQUEST
            best_score = 0.5

        # 判断标志位
        requires_empathy = best_intent == IntentType.EMOTIONAL_SUPPORT
        requires_tools = best_intent in [
            IntentType.DATA_QUERY,
            IntentType.COMPLEX_ANALYSIS,
            IntentType.HEALTH_DIAGNOSIS
        ]
        requires_rag = best_intent in [
            IntentType.ADVICE_REQUEST,
            IntentType.COMPLEX_ANALYSIS,
            IntentType.HEALTH_DIAGNOSIS
        ]

        # 置信度校准
        confidence = self._calibrate_confidence(best_score, intent_scores)

        return IntentClassification(
            intent=best_intent,
            confidence=confidence,
            requires_empathy=requires_empathy,
            requires_tools=requires_tools,
            requires_rag=requires_rag
        )

    def _calibrate_confidence(
        self,
        best_score: float,
        all_scores: Dict[IntentType, float]
    ) -> float:
        """
        根据分数分布校准置信度

        考虑因素：
        - 最高分的绝对值
        - 最高分与第二高分的差距 (margin)

        Args:
            best_score: 最高相似度分数
            all_scores: 所有意图的分数

        Returns:
            校准后的置信度 (0-1)
        """
        sorted_scores = sorted(all_scores.values(), reverse=True)
        top_score = sorted_scores[0]
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0

        # 计算margin (差距)
        margin = top_score - second_score

        # 置信度公式
        # - top_score越高，置信度越高
        # - margin越大，置信度越高 (说明判断越明确)
        confidence = top_score * (1 + margin * 0.5)

        # 限制范围
        confidence = max(0.5, min(confidence, 0.99))

        return confidence

    async def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentClassification:
        """
        分类用户消息意图

        策略：
        1. 尝试规则匹配 (简单意图)
        2. 如果规则匹配失败，使用语义模型

        Args:
            message: 用户消息
            conversation_history: 对话历史（可选，暂未使用）

        Returns:
            IntentClassification
        """
        start_time = datetime.now()

        # 1. 尝试规则匹配
        rule_result = self._classify_simple_intents(message)

        if rule_result:
            # 规则匹配成功
            inference_time = (datetime.now() - start_time).total_seconds() * 1000

            self.classification_count += 1
            self.rule_match_count += 1
            self.total_inference_time += inference_time

            logger.debug(
                f"🎯 Intent (rule): {rule_result.intent.value} | "
                f"Confidence: {rule_result.confidence:.2f} | "
                f"Time: {inference_time:.1f}ms"
            )

            return rule_result

        # 2. 使用语义模型
        semantic_result = await self._classify_with_semantic_model(
            message,
            conversation_history
        )

        inference_time = (datetime.now() - start_time).total_seconds() * 1000

        self.classification_count += 1
        self.semantic_match_count += 1
        self.total_inference_time += inference_time

        logger.debug(
            f"🎯 Intent (semantic): {semantic_result.intent.value} | "
            f"Confidence: {semantic_result.confidence:.2f} | "
            f"Time: {inference_time:.1f}ms"
        )

        return semantic_result

    def get_stats(self) -> Dict[str, any]:
        """获取性能统计"""
        if self.classification_count == 0:
            return {
                "status": "not_used",
                "classification_count": 0
            }

        avg_time = self.total_inference_time / self.classification_count
        rule_percentage = (self.rule_match_count / self.classification_count) * 100
        semantic_percentage = (self.semantic_match_count / self.classification_count) * 100

        return {
            "status": "active",
            "model_loaded": self.is_loaded,
            "classification_count": self.classification_count,
            "rule_match_count": self.rule_match_count,
            "semantic_match_count": self.semantic_match_count,
            "rule_percentage": round(rule_percentage, 1),
            "semantic_percentage": round(semantic_percentage, 1),
            "avg_inference_time_ms": round(avg_time, 1),
            "total_time_seconds": round(self.total_inference_time / 1000, 2)
        }


# 全局单例
_global_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """获取全局IntentClassifier单例"""
    global _global_classifier

    if _global_classifier is None:
        _global_classifier = IntentClassifier()

    return _global_classifier
