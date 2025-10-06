"""
AI Orchestrator - 智能路由核心
根据请求复杂度和意图,自动选择最优的AI模型
实现成本优化和性能优化的平衡
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import asyncio
from loguru import logger

from app.core.config import settings


class AIProvider(str, Enum):
    """AI提供商枚举"""
    LOCAL_PHI = "phi-3.5"
    OPENAI_GPT5 = "gpt-5"  # GPT-5 旗舰模型
    OPENAI_GPT5_NANO = "gpt-5-nano-2025-08-07"  # GPT-5 Nano 最新版本
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"  # Claude Sonnet 4 最新版本


class IntentType(str, Enum):
    """意图类型"""
    GREETING = "greeting"  # 问候
    CONFIRMATION = "confirmation"  # 确认
    DATA_QUERY = "data_query"  # 数据查询
    ADVICE_REQUEST = "advice_request"  # 建议请求
    EMOTIONAL_SUPPORT = "emotional_support"  # 情感支持
    COMPLEX_ANALYSIS = "complex_analysis"  # 复杂分析
    HEALTH_DIAGNOSIS = "health_diagnosis"  # 健康诊断


@dataclass
class IntentClassification:
    """意图分类结果"""
    intent: IntentType
    confidence: float
    requires_empathy: bool = False  # 是否需要情感理解
    requires_tools: bool = False  # 是否需要工具调用
    requires_rag: bool = False  # 是否需要RAG增强


@dataclass
class RoutingDecision:
    """路由决策结果"""
    provider: AIProvider
    complexity: int  # 1-10
    estimated_cost: float  # 预估成本(美元)
    estimated_latency: float  # 预估延迟(秒)
    reason: str  # 路由原因
    intent: IntentClassification  # 意图分类结果


@dataclass
class AIResponse:
    """AI响应结果"""
    content: str  # 响应内容
    tokens_used: Optional[int] = None  # 使用的token数
    finish_reason: Optional[str] = None  # 完成原因


class AIOrchestrator:
    """
    AI编排器
    负责智能路由、请求分发、响应聚合
    """

    def __init__(self):
        """初始化编排器"""
        self.local_model = None  # 延迟加载
        self.openai_client = None
        self.anthropic_client = None

        # 成本配置(每1K tokens) - 基于2025年最新定价
        self.cost_config = {
            AIProvider.LOCAL_PHI: 0.0,
            AIProvider.OPENAI_GPT5_NANO: 0.0002,  # $0.2/1M tokens (超经济)
            AIProvider.OPENAI_GPT5: 0.005,  # $5/1M tokens (旗舰级)
            AIProvider.CLAUDE_SONNET_4: 0.003,  # $3/1M tokens
        }

        # 延迟配置(秒)
        self.latency_config = {
            AIProvider.LOCAL_PHI: 0.05,  # 50ms
            AIProvider.OPENAI_GPT5_NANO: 0.8,  # 超快速响应
            AIProvider.OPENAI_GPT5: 2.0,
            AIProvider.CLAUDE_SONNET_4: 1.5,
        }

        logger.info("🤖 AI Orchestrator initialized")

    async def _lazy_load_clients(self):
        """延迟加载AI客户端"""
        if not self.openai_client and settings.OPENAI_API_KEY:
            import openai
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("✅ OpenAI client loaded")

        if not self.anthropic_client and settings.ANTHROPIC_API_KEY:
            import anthropic
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
            logger.info("✅ Anthropic client loaded")

        if not self.local_model and settings.USE_LOCAL_MODEL:
            # 本地模型加载将在单独的模块中实现
            logger.info("⏳ Local model loading deferred")

    async def classify_intent(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentClassification:
        """
        意图分类
        使用简单规则或轻量模型进行快速意图识别

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            IntentClassification: 意图分类结果
        """
        message_lower = user_message.lower()

        # 简单规则分类(生产环境可用小模型)
        if any(word in message_lower for word in ["你好", "hi", "hello", "早", "晚上好"]):
            return IntentClassification(
                intent=IntentType.GREETING,
                confidence=0.95
            )

        if any(word in message_lower for word in ["好的", "嗯", "是的", "对", "ok"]):
            return IntentClassification(
                intent=IntentType.CONFIRMATION,
                confidence=0.9
            )

        if any(word in message_lower for word in ["睡眠", "心率", "数据", "查看"]):
            return IntentClassification(
                intent=IntentType.DATA_QUERY,
                confidence=0.85,
                requires_tools=True
            )

        if any(word in message_lower for word in ["建议", "怎么", "如何", "帮我"]):
            return IntentClassification(
                intent=IntentType.ADVICE_REQUEST,
                confidence=0.8,
                requires_rag=True
            )

        if any(word in message_lower for word in ["焦虑", "压力", "累", "疲惫", "难受"]):
            return IntentClassification(
                intent=IntentType.EMOTIONAL_SUPPORT,
                confidence=0.85,
                requires_empathy=True
            )

        if any(word in message_lower for word in ["分析", "评估", "诊断", "方案"]):
            return IntentClassification(
                intent=IntentType.COMPLEX_ANALYSIS,
                confidence=0.75,
                requires_tools=True,
                requires_rag=True
            )

        # 默认: 简单咨询
        return IntentClassification(
            intent=IntentType.ADVICE_REQUEST,
            confidence=0.6
        )

    def _calculate_complexity(
        self,
        intent: IntentClassification,
        context_length: int,
        user_profile: Optional[Dict] = None
    ) -> int:
        """
        计算请求复杂度(1-10)

        Args:
            intent: 意图分类
            context_length: 上下文长度(字符数)
            user_profile: 用户画像

        Returns:
            int: 复杂度分数(1-10)
        """
        complexity = 0

        # 基于意图的基础分数
        intent_base_score = {
            IntentType.GREETING: 1,
            IntentType.CONFIRMATION: 1,
            IntentType.DATA_QUERY: 3,
            IntentType.ADVICE_REQUEST: 5,
            IntentType.EMOTIONAL_SUPPORT: 6,
            IntentType.COMPLEX_ANALYSIS: 8,
            IntentType.HEALTH_DIAGNOSIS: 9,
        }
        complexity += intent_base_score.get(intent.intent, 5)

        # 上下文长度加分
        if context_length > 1000:
            complexity += 2
        elif context_length > 500:
            complexity += 1

        # 需要工具调用加分
        if intent.requires_tools:
            complexity += 1

        # 需要RAG加分
        if intent.requires_rag:
            complexity += 1

        return min(complexity, 10)  # 上限10

    async def route_request(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None,
        force_provider: Optional[AIProvider] = None
    ) -> RoutingDecision:
        """
        智能路由决策

        Args:
            user_message: 用户消息
            conversation_history: 对话历史
            user_profile: 用户画像
            force_provider: 强制使用指定提供商(用于测试)

        Returns:
            RoutingDecision: 路由决策
        """
        # 如果强制指定提供商,直接返回
        if force_provider:
            return RoutingDecision(
                provider=force_provider,
                complexity=5,
                estimated_cost=self.cost_config[force_provider] * 2,  # 假设2K tokens
                estimated_latency=self.latency_config[force_provider],
                reason="强制指定"
            )

        # 1. 意图分类
        intent = await self.classify_intent(user_message, conversation_history)

        # 2. 计算复杂度
        context_length = len(user_message)
        if conversation_history:
            context_length += sum(len(msg.get("content", "")) for msg in conversation_history)

        complexity = self._calculate_complexity(intent, context_length, user_profile)

        # 3. 路由决策
        provider: AIProvider
        reason: str

        if not settings.AI_COST_OPTIMIZATION:
            # 不启用成本优化: 全部使用GPT-5旗舰
            provider = AIProvider.OPENAI_GPT5
            reason = "成本优化未启用,使用最强模型"

        elif complexity < settings.AI_ROUTE_LOCAL_THRESHOLD:
            # 低复杂度: 使用本地模型
            provider = AIProvider.LOCAL_PHI
            reason = f"低复杂度({complexity}),使用本地模型"

        elif complexity < settings.AI_ROUTE_MINI_THRESHOLD:
            # 中等复杂度: 使用GPT-5 Nano(超快速、超经济)
            provider = AIProvider.OPENAI_GPT5_NANO
            reason = f"中等复杂度({complexity}),使用GPT-5 Nano"

        elif intent.requires_empathy:
            # 需要情感理解: 使用Claude Sonnet 4(情感能力最强)
            provider = AIProvider.CLAUDE_SONNET_4
            reason = f"需要情感理解,使用Claude Sonnet 4"

        else:
            # 高复杂度: 使用GPT-5旗舰
            provider = AIProvider.OPENAI_GPT5
            reason = f"高复杂度({complexity}),使用GPT-5"

        # 计算预估成本和延迟
        estimated_tokens = max(len(user_message) / 4, 100)  # 粗略估算
        estimated_cost = self.cost_config[provider] * (estimated_tokens / 1000)
        estimated_latency = self.latency_config[provider]

        decision = RoutingDecision(
            provider=provider,
            complexity=complexity,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            reason=reason,
            intent=intent
        )

        logger.info(
            f"🎯 Routing: {provider.value} | "
            f"Intent: {intent.intent.value} | "
            f"Complexity: {complexity} | "
            f"Cost: ${estimated_cost:.6f}"
        )

        return decision

    async def generate_response(
        self,
        provider: AIProvider,
        messages: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None,
        user_message: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> AIResponse:
        """
        生成AI响应
        统一的响应生成接口,支持多个AI提供商

        Args:
            provider: AI提供商
            messages: 对话消息列表(如果提供,优先使用)
            system_prompt: 系统提示
            user_message: 用户消息(如果messages为None,从此构建)
            conversation_history: 会话历史
            max_tokens: 最大token数
            temperature: 温度参数
            tools: 工具列表(用于MCP)

        Returns:
            AIResponse: AI生成的响应对象
        """
        await self._lazy_load_clients()

        # 构建消息列表
        if messages is None:
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            if user_message:
                messages.append({"role": "user", "content": user_message})

        if provider == AIProvider.LOCAL_PHI:
            content = await self._generate_local(messages, system_prompt, max_tokens)
            return AIResponse(content=content, tokens_used=None)

        elif provider in [AIProvider.OPENAI_GPT5, AIProvider.OPENAI_GPT5_NANO]:
            content, tokens = await self._generate_openai(provider, messages, system_prompt, max_tokens, temperature)
            return AIResponse(content=content, tokens_used=tokens)

        elif provider == AIProvider.CLAUDE_SONNET_4:
            content, tokens = await self._generate_claude(messages, system_prompt, max_tokens, temperature, tools)
            return AIResponse(content=content, tokens_used=tokens)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _generate_local(
        self,
        messages: List[Dict],
        system_prompt: Optional[str],
        max_tokens: int
    ) -> str:
        """使用本地模型生成"""
        # TODO: 实现本地模型推理
        logger.warning("⚠️  Local model not implemented yet, using mock response")
        return "这是本地模型的模拟响应。实际实现中会加载Phi-3.5模型进行推理。"

    async def _generate_openai(
        self,
        provider: AIProvider,
        messages: List[Dict],
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Tuple[str, int]:
        """使用OpenAI生成,返回(content, tokens)"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        model = settings.OPENAI_MODEL_MAIN if provider == AIProvider.OPENAI_GPT5 else settings.OPENAI_MODEL_MINI

        # 添加系统提示
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            # GPT-5系列使用max_completion_tokens，其他模型使用max_tokens
            token_param = "max_completion_tokens" if model.startswith("gpt-5") else "max_tokens"

            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=full_messages,
                **{token_param: max_tokens},
                temperature=temperature
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            return content, tokens_used

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_claude(
        self,
        messages: List[Dict],
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        tools: Optional[List[Dict]]
    ) -> Tuple[str, int]:
        """使用Claude生成,返回(content, tokens)"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        try:
            response = await self.anthropic_client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=messages,
                tools=tools or []
            )

            # 处理工具调用
            if response.stop_reason == "tool_use":
                # TODO: 处理MCP工具调用
                logger.info("🔧 Tool use detected")

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else None

            return content, tokens_used

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


# 全局单例
orchestrator = AIOrchestrator()
