"""
复杂度分析器
动态计算对话请求复杂度，优化AI路由决策
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict

from loguru import logger

from app.ai.orchestrator import IntentType, IntentClassification


@dataclass
class ComplexityFactors:
    """复杂度影响因素"""
    base_score: int  # 基础分数(基于意图)
    context_adjustment: int  # 上下文调整
    user_pattern_adjustment: int  # 用户模式调整
    conversation_depth_adjustment: int  # 对话深度调整
    technical_level_adjustment: int  # 专业程度调整

    @property
    def total_score(self) -> int:
        """计算总分"""
        return max(1, min(10,
            self.base_score +
            self.context_adjustment +
            self.user_pattern_adjustment +
            self.conversation_depth_adjustment +
            self.technical_level_adjustment
        ))


@dataclass
class UserBehaviorProfile:
    """用户行为画像"""
    days_active: int
    total_conversations: int
    avg_complexity_history: float
    is_power_user: bool
    expertise_level: str  # "beginner" | "intermediate" | "advanced"
    preferred_interaction_style: str  # "brief" | "detailed"


class ComplexityAnalyzer:
    """
    智能复杂度分析器

    功能:
    1. 对话上下文分析 (多轮、主题切换、历史引用)
    2. 用户行为模式分析 (经验等级、专业程度)
    3. 实时性能监控 (响应时长、成本效益)
    4. 动态阈值调整 (基于历史数据学习)
    """

    # 意图基础分数映射
    INTENT_BASE_SCORES = {
        IntentType.GREETING: 1,
        IntentType.CONFIRMATION: 1,
        IntentType.DATA_QUERY: 3,
        IntentType.ADVICE_REQUEST: 5,
        IntentType.EMOTIONAL_SUPPORT: 6,
        IntentType.COMPLEX_ANALYSIS: 8,
        IntentType.HEALTH_DIAGNOSIS: 9,
    }

    # 专业术语关键词 (表示用户专业程度高)
    TECHNICAL_KEYWORDS = {
        "心率变异性", "hrv", "rhr", "resting heart rate",
        "深度睡眠", "rem", "快速眼动",
        "基础代谢", "bmr", "tdee",
        "皮质醇", "褪黑素", "血清素",
        "有氧运动", "无氧运动", "hiit",
        "昼夜节律", "生物钟",
        "焦虑障碍", "抑郁症", "认知行为疗法"
    }

    def __init__(self):
        """初始化复杂度分析器"""
        # 历史决策记录 (用于动态学习)
        self.decision_history: List[Dict] = []

        # 用户行为缓存
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}

        # 性能统计
        self.analysis_count = 0
        self.avg_analysis_time_ms = 0.0

        logger.info("✅ ComplexityAnalyzer initialized")

    async def analyze_complexity(
        self,
        intent: IntentClassification,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> ComplexityFactors:
        """
        分析请求复杂度

        Args:
            intent: 意图分类结果
            user_message: 用户消息
            conversation_history: 对话历史
            user_profile: 用户画像
            user_id: 用户ID

        Returns:
            ComplexityFactors: 复杂度因素详情
        """
        start_time = datetime.now()

        # 1. 基础分数 (基于意图)
        base_score = self.INTENT_BASE_SCORES.get(intent.intent, 5)

        # 2. 上下文复杂度分析
        context_adjustment = self._analyze_context_complexity(
            user_message,
            conversation_history
        )

        # 3. 用户行为模式分析
        user_pattern_adjustment = await self._analyze_user_pattern(
            user_id,
            user_profile
        )

        # 4. 对话深度分析
        conversation_depth_adjustment = self._analyze_conversation_depth(
            conversation_history
        )

        # 5. 专业程度分析
        technical_level_adjustment = self._analyze_technical_level(
            user_message
        )

        # 构建复杂度因素
        factors = ComplexityFactors(
            base_score=base_score,
            context_adjustment=context_adjustment,
            user_pattern_adjustment=user_pattern_adjustment,
            conversation_depth_adjustment=conversation_depth_adjustment,
            technical_level_adjustment=technical_level_adjustment
        )

        # 记录分析时长
        analysis_time = (datetime.now() - start_time).total_seconds() * 1000
        self.analysis_count += 1
        self.avg_analysis_time_ms = (
            (self.avg_analysis_time_ms * (self.analysis_count - 1) + analysis_time)
            / self.analysis_count
        )

        logger.debug(
            f"🔍 Complexity: {factors.total_score} | "
            f"Base: {base_score} | "
            f"Context: +{context_adjustment} | "
            f"User: +{user_pattern_adjustment} | "
            f"Depth: +{conversation_depth_adjustment} | "
            f"Tech: +{technical_level_adjustment}"
        )

        return factors

    def _analyze_context_complexity(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]]
    ) -> int:
        """
        分析上下文复杂度

        考虑因素:
        - 消息长度
        - 问题数量
        - 条件句数量
        - 上下文长度
        """
        adjustment = 0

        # 消息长度
        message_length = len(user_message)
        if message_length > 200:
            adjustment += 2
        elif message_length > 100:
            adjustment += 1

        # 问题数量 (多个问题 → 更复杂)
        question_count = user_message.count('?') + user_message.count('？')
        if question_count >= 3:
            adjustment += 2
        elif question_count >= 2:
            adjustment += 1

        # 条件句 (如果...那么... → 逻辑复杂)
        conditional_keywords = ['如果', '假如', '要是', 'if', '但是', '不过', '然而']
        conditional_count = sum(1 for kw in conditional_keywords if kw in user_message.lower())
        if conditional_count >= 2:
            adjustment += 1

        # 上下文长度
        if conversation_history:
            history_length = len(conversation_history)
            total_chars = sum(len(msg.get("content", "")) for msg in conversation_history)

            if history_length > 10:
                adjustment += 2
            elif history_length > 5:
                adjustment += 1

            if total_chars > 2000:
                adjustment += 1

        return adjustment

    async def _analyze_user_pattern(
        self,
        user_id: Optional[str],
        user_profile: Optional[Dict]
    ) -> int:
        """
        分析用户行为模式

        考虑因素:
        - 用户活跃天数
        - 历史查询复杂度
        - 是否为高级用户
        """
        adjustment = 0

        if not user_id or not user_profile:
            return 0

        # 获取或创建用户画像
        if user_id not in self.user_profiles:
            behavior_profile = self._build_user_behavior_profile(user_profile)
            self.user_profiles[user_id] = behavior_profile
        else:
            behavior_profile = self.user_profiles[user_id]

        # 新用户 → 可能需要更详细的回答
        if behavior_profile.days_active < 7:
            adjustment += 1

        # 高级用户 → 可能提出更复杂问题
        if behavior_profile.expertise_level == "advanced":
            adjustment += 1
        elif behavior_profile.expertise_level == "beginner":
            adjustment -= 1

        # 重度用户 → 可能有特殊需求
        if behavior_profile.is_power_user:
            adjustment += 1

        return adjustment

    def _build_user_behavior_profile(
        self,
        user_profile: Dict
    ) -> UserBehaviorProfile:
        """
        构建用户行为画像

        基于用户基本信息推断行为特征
        """
        days_active = user_profile.get("days_active", 0)

        # 简单启发式判断专业程度
        occupation = user_profile.get("occupation", "").lower()
        expertise_level = "beginner"

        if any(kw in occupation for kw in ["医生", "护士", "健康", "医疗", "doctor", "nurse"]):
            expertise_level = "advanced"
        elif any(kw in occupation for kw in ["教练", "运动", "fitness", "trainer"]):
            expertise_level = "intermediate"

        # 判断是否为重度用户
        is_power_user = days_active > 30

        return UserBehaviorProfile(
            days_active=days_active,
            total_conversations=0,  # 需要从数据库查询
            avg_complexity_history=5.0,
            is_power_user=is_power_user,
            expertise_level=expertise_level,
            preferred_interaction_style="detailed" if days_active < 7 else "brief"
        )

    def _analyze_conversation_depth(
        self,
        conversation_history: Optional[List[Dict]]
    ) -> int:
        """
        分析对话深度

        考虑因素:
        - 多轮对话
        - 主题连续性
        - 深入探讨程度
        """
        adjustment = 0

        if not conversation_history or len(conversation_history) == 0:
            return 0

        history_length = len(conversation_history)

        # 多轮对话 (>3轮对话表示深入讨论)
        if history_length > 6:
            adjustment += 2
        elif history_length > 3:
            adjustment += 1

        # 检测主题切换
        # 如果最近3条消息的主题差异较大 → 复杂度提高
        if history_length >= 3:
            recent_messages = conversation_history[-3:]
            topic_switch_detected = self._detect_topic_switch(recent_messages)

            if topic_switch_detected:
                adjustment += 1

        # 检测历史引用 ("之前你说", "刚才提到")
        last_message = conversation_history[-1].get("content", "") if conversation_history else ""
        reference_keywords = ["之前", "刚才", "前面", "earlier", "previously", "上次"]

        if any(kw in last_message for kw in reference_keywords):
            adjustment += 1

        return adjustment

    def _detect_topic_switch(self, recent_messages: List[Dict]) -> bool:
        """
        检测主题切换

        简单实现: 检查关键词重叠度
        """
        if len(recent_messages) < 2:
            return False

        # 提取关键词
        def extract_keywords(text: str) -> set:
            # 简单分词 (移除常见停用词)
            stopwords = {"的", "了", "是", "我", "你", "在", "有", "和", "吗", "呢", "a", "the", "is", "are"}
            words = set(re.findall(r'[\w]+', text.lower()))
            return words - stopwords

        keywords_1 = extract_keywords(recent_messages[-1].get("content", ""))
        keywords_2 = extract_keywords(recent_messages[-2].get("content", ""))

        # 计算重叠度
        if len(keywords_1) == 0 or len(keywords_2) == 0:
            return False

        overlap = len(keywords_1 & keywords_2)
        overlap_ratio = overlap / max(len(keywords_1), len(keywords_2))

        # 重叠度<30% 认为主题切换
        return overlap_ratio < 0.3

    def _analyze_technical_level(self, user_message: str) -> int:
        """
        分析专业程度

        考虑因素:
        - 专业术语使用
        - 数据引用
        - 具体指标提及
        """
        adjustment = 0

        message_lower = user_message.lower()

        # 检测专业术语
        technical_count = sum(
            1 for keyword in self.TECHNICAL_KEYWORDS
            if keyword in message_lower
        )

        if technical_count >= 3:
            adjustment += 2
        elif technical_count >= 1:
            adjustment += 1

        # 检测数值/数据引用
        # 如: "我的心率是75", "睡眠时长6.5小时"
        number_pattern = r'\d+\.?\d*\s*(小时|分钟|次|bpm|kg|cm|%|hours?|mins?)'
        number_matches = re.findall(number_pattern, user_message)

        if len(number_matches) >= 2:
            adjustment += 1

        return adjustment

    def record_decision(
        self,
        complexity: int,
        provider_used: str,
        actual_latency_ms: float,
        actual_cost: float,
        user_satisfaction: Optional[int] = None
    ):
        """
        记录路由决策 (用于学习优化)

        Args:
            complexity: 计算出的复杂度
            provider_used: 实际使用的提供商
            actual_latency_ms: 实际响应时长
            actual_cost: 实际成本
            user_satisfaction: 用户满意度(1-5)
        """
        self.decision_history.append({
            "timestamp": datetime.now(),
            "complexity": complexity,
            "provider": provider_used,
            "latency_ms": actual_latency_ms,
            "cost": actual_cost,
            "satisfaction": user_satisfaction
        })

        # 保留最近1000条记录
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

    def get_stats(self) -> Dict:
        """获取分析器统计信息"""
        return {
            "analysis_count": self.analysis_count,
            "avg_analysis_time_ms": round(self.avg_analysis_time_ms, 2),
            "user_profiles_cached": len(self.user_profiles),
            "decision_history_size": len(self.decision_history)
        }


# 全局单例
_global_analyzer: Optional[ComplexityAnalyzer] = None


def get_complexity_analyzer() -> ComplexityAnalyzer:
    """获取全局ComplexityAnalyzer单例"""
    global _global_analyzer

    if _global_analyzer is None:
        _global_analyzer = ComplexityAnalyzer()

    return _global_analyzer
