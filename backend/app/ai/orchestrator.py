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
        意图分类 (升级版)
        使用混合策略: 规则匹配 + Sentence-Transformers语义相似度

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            IntentClassification: 意图分类结果
        """
        from app.ai.intent_classifier import get_intent_classifier

        classifier = get_intent_classifier()

        # 调用新的分类器
        result = await classifier.classify(
            message=user_message,
            conversation_history=conversation_history
        )

        # 记录分类结果 (用于监控)
        logger.info(
            f"🎯 Intent: {result.intent.value} | "
            f"Confidence: {result.confidence:.2f}"
        )

        return result

    async def _calculate_complexity(
        self,
        intent: IntentClassification,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> int:
        """
        计算请求复杂度(1-10) - 升级版
        使用ComplexityAnalyzer进行智能分析

        Args:
            intent: 意图分类
            user_message: 用户消息
            conversation_history: 对话历史
            user_profile: 用户画像
            user_id: 用户ID

        Returns:
            int: 复杂度分数(1-10)
        """
        from app.ai.complexity_analyzer import get_complexity_analyzer

        analyzer = get_complexity_analyzer()

        # 使用ComplexityAnalyzer进行智能分析
        factors = await analyzer.analyze_complexity(
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            user_profile=user_profile,
            user_id=user_id
        )

        return factors.total_score

    async def route_request(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None,
        force_provider: Optional[AIProvider] = None,
        user_id: Optional[str] = None
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

        # 2. 计算复杂度 (使用升级版ComplexityAnalyzer)
        complexity = await self._calculate_complexity(
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            user_profile=user_profile,
            user_id=user_id
        )

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
        tools: Optional[List[Dict]] = None,
        user_id: Optional["UUID"] = None,
        db: Optional["AsyncSession"] = None
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
            content, tokens = await self._generate_claude(
                messages, system_prompt, max_tokens, temperature, tools, user_id, db
            )
            return AIResponse(content=content, tokens_used=tokens)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _generate_local(
        self,
        messages: List[Dict],
        system_prompt: Optional[str],
        max_tokens: int
    ) -> str:
        """使用本地Phi-3.5模型生成"""
        from app.ai.local_models import get_local_model_manager

        local_manager = get_local_model_manager()

        # 构建完整提示词
        prompt_parts = []

        # 添加系统提示
        if system_prompt:
            prompt_parts.append(f"系统指令: {system_prompt}\n")

        # 添加对话历史
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                prompt_parts.append(f"用户: {content}")
            elif role == "assistant":
                prompt_parts.append(f"助手: {content}")

        full_prompt = "\n\n".join(prompt_parts)

        # 使用本地模型生成
        response = await local_manager.generate(
            prompt=full_prompt,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9
        )

        return response

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
        tools: Optional[List[Dict]],
        user_id: Optional["UUID"] = None,
        db: Optional["AsyncSession"] = None
    ) -> Tuple[str, int]:
        """
        使用Claude生成,支持MCP工具调用

        处理流程：
        1. 调用Claude API (传入tools)
        2. 如果响应包含tool_use，执行工具并返回结果给Claude
        3. Claude基于工具结果继续生成最终响应
        4. 递归处理直到获得最终文本响应
        """
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        try:
            # 调用Claude API
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
                logger.info("🔧 Tool use detected, processing...")

                # 导入MCP工具执行器
                from app.mcp import execute_tool
                import json

                # 收集所有工具调用结果
                tool_results = []

                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id

                        logger.info(f"   Executing tool: {tool_name}")
                        logger.debug(f"   Input: {tool_input}")

                        try:
                            # 执行工具
                            result = await execute_tool(
                                tool_name=tool_name,
                                tool_input=tool_input,
                                user_id=user_id,
                                db=db
                            )

                            logger.info(f"   ✅ Tool executed: {tool_name}")

                            # 添加工具结果
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(result, ensure_ascii=False)
                            })

                        except Exception as e:
                            logger.error(f"   ❌ Tool execution failed: {tool_name} - {e}")

                            # 返回错误信息给Claude
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps({
                                    "error": str(e),
                                    "tool": tool_name
                                }, ensure_ascii=False),
                                "is_error": True
                            })

                # 将工具调用和结果添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # 递归调用，让Claude基于工具结果继续生成
                logger.info("🔄 Calling Claude with tool results...")
                return await self._generate_claude(
                    messages=messages,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    tools=tools,
                    user_id=user_id,
                    db=db
                )

            # 提取文本内容
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else None

            return content, tokens_used

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


# 全局单例
orchestrator = AIOrchestrator()
