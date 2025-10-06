# PeakState AI技术架构深度解析

> **版本**: 1.0
> **更新日期**: 2025-10-06
> **作者**: PeakState技术团队

---

## 📋 目录

1. [架构概览](#架构概览)
2. [AI核心设计](#ai核心设计)
3. [MCP架构详解](#mcp架构详解)
4. [成本与性能优化](#成本与性能优化)
5. [数据流与安全](#数据流与安全)
6. [扩展性设计](#扩展性设计)

---

## 🏗️ 架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                   React Native App (前端)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │ 入职流程    │  │ AI对话界面  │  │ 健康数据仪表板   │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API + WebSocket
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (后端)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           AI Orchestrator (智能路由核心)             │   │
│  │  • 意图分类  • 复杂度评分  • 成本优化  • 智能路由  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│         ┌──────────────────┴──────────────────┐            │
│         ↓                                      ↓            │
│  ┌──────────────┐                    ┌──────────────────┐  │
│  │  本地AI模型   │                    │   云端AI APIs    │  │
│  ├──────────────┤                    ├──────────────────┤  │
│  │ • Phi-3.5    │                    │ • GPT-4o         │  │
│  │ • 零成本      │                    │ • GPT-4o-mini    │  │
│  │ • 50ms响应   │                    │ • Claude 3.5     │  │
│  │ • 70%请求    │                    │ • 30%请求        │  │
│  └──────────────┘                    └──────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           MCP (Model Context Protocol)              │    │
│  │  ┌──────────────┐         ┌───────────────────┐    │    │
│  │  │Health Server │         │ Calendar Server   │    │    │
│  │  │• 睡眠数据    │         │• 日程分析         │    │    │
│  │  │• HRV分析     │         │• 负载预测         │    │    │
│  │  └──────────────┘         └───────────────────┘    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              RAG Knowledge Base                     │    │
│  │  ┌──────────────┐         ┌───────────────────┐    │    │
│  │  │Qdrant Vector │         │ Health Knowledge  │    │    │
│  │  │  Database    │  ←───   │   Documents       │    │    │
│  │  └──────────────┘         └───────────────────┘    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure (基础设施)                       │
│  ┌────────────┐  ┌────────┐  ┌────────┐  ┌──────────┐     │
│  │ PostgreSQL │  │ Redis  │  │ Qdrant │  │ Celery   │     │
│  └────────────┘  └────────┘  └────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈选择理由

| 组件 | 选型 | 理由 |
|------|------|------|
| **前端** | React Native + TypeScript | • 跨平台开发效率高<br>• 社区成熟,生态丰富<br>• 支持热更新 |
| **后端** | FastAPI (Python) | • 异步高性能<br>• AI/ML生态友好<br>• 自动API文档<br>• 类型安全 |
| **数据库** | PostgreSQL | • ACID保证<br>• JSON支持<br>• 成熟稳定 |
| **缓存** | Redis | • 高性能<br>• 支持消息队列<br>• 丰富数据结构 |
| **向量DB** | Qdrant | • 高性能向量检索<br>• 易于集成<br>• 支持过滤 |
| **AI模型** | 混合架构 | • 成本优化<br>• 性能平衡<br>• 隐私保护 |

---

## 🤖 AI核心设计

### 1. 混合AI架构

#### 设计理念

**核心思想**: 不同复杂度的请求使用不同的AI模型,实现成本与性能的最优平衡。

#### 模型分层

```python
# 简单请求 (70%) - 本地模型
complexity < 3:
    → Phi-3.5-mini (本地推理)
    → 成本: $0
    → 延迟: <100ms
    → 场景: 问候、确认、简单查询

# 中等请求 (25%) - 轻量云端
3 ≤ complexity < 6:
    → GPT-4o-mini
    → 成本: $0.15/1M tokens
    → 延迟: ~1.5s
    → 场景: 数据解读、一般建议

# 情感请求 (3%) - 情感专家
requires_empathy = True:
    → Claude 3.5 Sonnet
    → 成本: $3/1M tokens
    → 延迟: ~1.8s
    → 场景: 情绪安抚、心理支持

# 复杂请求 (2%) - 最强模型
complexity ≥ 6:
    → GPT-4o
    → 成本: $2.5/1M tokens
    → 延迟: ~2s
    → 场景: 复杂分析、专业诊断
```

#### 智能路由算法

```python
async def route_request(user_message, context, profile):
    # 1. 意图分类 (快速规则匹配或小模型)
    intent = await classify_intent(user_message)

    # 2. 复杂度计算
    complexity = calculate_complexity(
        intent=intent,
        context_length=len(context),
        requires_tools=intent.requires_tools,
        requires_rag=intent.requires_rag
    )

    # 3. 路由决策
    if not cost_optimization_enabled:
        return GPT4O  # 不优化时全用最强

    if complexity < local_threshold:
        return LOCAL_PHI  # 本地模型

    if complexity < mini_threshold:
        return GPT4O_MINI  # 轻量云端

    if intent.requires_empathy:
        return CLAUDE_35  # 情感专家

    return GPT4O  # 复杂任务
```

### 2. 成本对比分析

#### 原方案 (纯GPT-4)

```
假设1000用户,每用户每天10次对话,平均1K tokens/次:
- 月总tokens: 1000 users × 10 msg × 30 days × 1K = 300M tokens
- GPT-4成本: 300M × $0.03/1K = $9,000/月
```

#### 优化方案 (混合架构)

```
请求分布(基于意图分析):
- 本地模型 (70%): 210M tokens × $0 = $0
- GPT-4o-mini (25%): 75M tokens × $0.15/1M = $11.25
- Claude 3.5 (3%): 9M tokens × $3/1M = $27
- GPT-4o (2%): 6M tokens × $2.5/1M = $15

月总成本: $53.25
节省: $9,000 → $53 (99.4%降低!)
```

### 3. 本地模型部署

#### Phi-3.5-mini优势

- **模型大小**: 3.8B参数,~8GB内存
- **推理速度**: CPU ~50ms, GPU ~20ms
- **质量**: 接近GPT-3.5水平
- **适用场景**: 简单对话、数据查询、确认反馈

#### 部署方案

```python
# 使用Transformers库加载
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    device_map="auto",  # 自动选择设备
    torch_dtype="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct"
)

# 推理
def generate_local(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=512)
    return tokenizer.decode(outputs[0])
```

---

## 🔌 MCP架构详解

### 1. MCP (Model Context Protocol) 简介

**MCP**是Anthropic推出的标准化协议,用于AI与外部工具/数据源的安全交互。

#### 核心优势

✅ **标准化**: 统一的工具定义和调用接口
✅ **安全性**: 细粒度权限控制
✅ **可组合**: 模块化设计,易于扩展
✅ **未来兼容**: 行业标准,长期支持

### 2. PeakState的MCP实现

#### Health MCP Server

```python
# app/mcp/health_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("peakstate-health")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="read_sleep_data",
            description="读取用户最近N天的睡眠数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "days": {"type": "integer", "default": 7}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="calculate_energy_score",
            description="基于多维数据计算精力准备度评分",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "include_hrv": {"type": "boolean", "default": True}
                }
            }
        ),
        Tool(
            name="analyze_sleep_quality",
            description="分析睡眠质量并给出建议",
            inputSchema={...}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """执行工具调用"""
    if name == "read_sleep_data":
        user_id = arguments["user_id"]
        days = arguments.get("days", 7)

        # 从数据库读取睡眠数据
        sleep_data = await db.fetch_sleep_records(user_id, days)

        return [TextContent(
            type="text",
            text=format_sleep_summary(sleep_data)
        )]

    elif name == "calculate_energy_score":
        # 计算精力评分逻辑
        score = await compute_energy_score(arguments["user_id"])

        return [TextContent(
            type="text",
            text=f"当前精力准备度: {score}/100\n" +
                  f"睡眠质量: {score.sleep_quality}\n" +
                  f"HRV恢复度: {score.hrv_recovery}"
        )]
```

#### Calendar MCP Server

```python
# app/mcp/calendar_server.py
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_today_events",
            description="获取今日日程安排"
        ),
        Tool(
            name="analyze_schedule_load",
            description="分析日程负载,预测精力消耗"
        ),
        Tool(
            name="suggest_rest_time",
            description="基于日程建议最佳休息时间"
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "analyze_schedule_load":
        events = await fetch_calendar_events(arguments["user_id"])

        # 分析会议密度、类型
        load_score = calculate_cognitive_load(events)

        return [TextContent(
            type="text",
            text=f"今日日程负载: {load_score}/10\n" +
                  f"高强度时段: {peak_hours}\n" +
                  f"建议: {suggestions}"
        )]
```

### 3. AI Agent调用MCP

```python
# AI使用MCP工具的示例
async def generate_morning_briefing(user_id: str):
    """生成晨间简报 - AI自动调用MCP工具"""

    response = await anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=[
            {
                "name": "read_sleep_data",
                "description": "读取用户睡眠数据",
                "input_schema": {...}
            },
            {
                "name": "get_today_events",
                "description": "获取今日日程",
                "input_schema": {...}
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"我是{user_id}的AI教练,请帮我生成今日晨间简报。" +
                          "需要分析昨晚睡眠质量和今日日程,给出精力规划建议。"
            }
        ]
    )

    # Claude会自动:
    # 1. 调用read_sleep_data获取睡眠数据
    # 2. 调用get_today_events获取日程
    # 3. 综合分析并生成个性化建议

    return response.content[0].text
```

### 4. MCP vs 传统API调用

| 对比维度 | 传统API | MCP |
|---------|---------|-----|
| **灵活性** | 需预先定义所有调用流程 | AI自主决定调用时机和参数 |
| **可扩展性** | 添加功能需修改AI Prompt | 添加新Tool即可,AI自动理解 |
| **类型安全** | 手动验证 | Schema自动验证 |
| **标准化** | 各家实现不同 | 行业标准,可移植 |

---

## 💰 成本与性能优化

### 1. 成本优化策略

#### 分层定价模型

```python
# 成本配置(每1M tokens)
COST_CONFIG = {
    "local-phi": 0.00,        # 本地模型: 免费
    "gpt-4o-mini": 0.15,      # 轻量云端: $0.15
    "claude-3.5": 3.00,       # 情感专家: $3.00
    "gpt-4o": 2.50,           # 最强模型: $2.50
}

# 实际成本分布(1000用户/月)
MONTHLY_COST = {
    "local-phi (70%)": 0 * 0.70 = $0,
    "gpt-4o-mini (25%)": 300M * 0.25 * 0.15/1M = $11.25,
    "claude-3.5 (3%)": 300M * 0.03 * 3/1M = $27,
    "gpt-4o (2%)": 300M * 0.02 * 2.5/1M = $15,
}

总成本: $53.25/月 (vs. 纯GPT-4的 $9,000/月)
```

#### 动态成本控制

```python
class CostController:
    """实时成本监控和控制"""

    async def check_budget(self, user_id):
        """检查用户本月额度"""
        usage = await get_monthly_usage(user_id)

        if usage.cost > MONTHLY_LIMIT:
            # 超额: 降级为本地模型
            return "force_local"

        if usage.cost > MONTHLY_LIMIT * 0.8:
            # 接近上限: 优先本地模型
            return "prefer_local"

        return "normal"
```

### 2. 性能优化

#### 响应延迟对比

| 模型 | 平均延迟 | P95延迟 | 适用场景 |
|------|---------|---------|----------|
| Phi-3.5 (local) | 50ms | 100ms | 实时对话 |
| GPT-4o-mini | 1.5s | 2.5s | 一般咨询 |
| Claude 3.5 | 1.8s | 3.0s | 情感支持 |
| GPT-4o | 2.0s | 3.5s | 复杂分析 |

#### 异步架构

```
User Request → FastAPI → Redis Queue → Celery Worker → AI Generation
                  ↓                                           ↓
           返回202 Accepted                           WebSocket推送结果
```

**优势**:
- ✅ 不阻塞HTTP线程
- ✅ 支持长时间AI生成
- ✅ 客户端实时反馈

### 3. 缓存策略

```python
# 相似对话缓存
@cache(ttl=3600)
async def get_ai_response(message_hash):
    """缓存常见问题的响应"""
    ...

# 用户画像缓存
@cache(ttl=1800)
async def get_user_profile(user_id):
    """缓存用户画像,减少数据库查询"""
    ...
```

---

## 🔒 数据流与安全

### 1. 数据加密

#### 端到端加密流程

```
前端加密 → 传输(HTTPS) → 后端存储(加密) → AI处理(临时解密)
   ↓                                              ↓
用户密钥                                     处理后立即删除
```

#### 实现方案

```python
# 前端加密(React Native)
import CryptoJS from 'crypto-js';

const encryptHealthData = (data, userKey) => {
    return CryptoJS.AES.encrypt(
        JSON.stringify(data),
        userKey
    ).toString();
};

# 后端解密(FastAPI)
from app.core.security import encryptor

async def process_health_data(encrypted_data, user_id):
    # 解密
    decrypted = encryptor.decrypt(encrypted_data)

    # 处理
    result = await analyze_data(decrypted)

    # 不存储原始数据
    return result
```

### 2. 隐私保护

#### 本地推理选项

```python
# 高隐私模式: 数据不离开服务器
class PrivacyMode:
    async def generate_response(self, message):
        if self.user.privacy_level == "high":
            # 强制使用本地模型
            return await local_model.generate(message)
        else:
            # 正常路由
            return await orchestrator.route_and_generate(message)
```

### 3. 数据最小化

```
只收集必要数据:
- ✅ 睡眠时长、质量
- ✅ 心率变异性(HRV)
- ❌ 具体睡眠时间点(隐私)
- ❌ 详细位置信息(非必要)
```

---

## 🚀 扩展性设计

### 1. 多模态扩展

```python
# 未来支持: 语音、图像
class MultiModalOrchestrator(AIOrchestrator):
    async def process_voice(self, audio_file):
        """语音转文字 → AI处理"""
        text = await speech_to_text(audio_file)
        return await self.generate_response(text)

    async def analyze_image(self, image_file):
        """图像分析(如食物识别)"""
        return await vision_model.analyze(image_file)
```

### 2. 新AI模型接入

```python
# 添加新模型: 只需实现统一接口
class CustomAIProvider(BaseProvider):
    async def generate(self, messages, **kwargs):
        # 实现自定义逻辑
        ...

# 注册到Orchestrator
orchestrator.register_provider("custom-model", CustomAIProvider())
```

### 3. 新MCP工具

```python
# 添加天气工具
@mcp_server.tool()
async def get_weather(location: str):
    """获取天气信息,用于运动建议"""
    ...

# AI自动理解并使用
# 无需修改Prompt!
```

---

## 📊 监控与运维

### 1. 关键指标

```python
# Prometheus指标
ai_request_total = Counter("ai_requests_total", ["provider", "intent"])
ai_request_latency = Histogram("ai_request_latency_seconds", ["provider"])
ai_request_cost = Counter("ai_request_cost_usd", ["provider"])
ai_routing_decision = Counter("ai_routing", ["complexity", "provider"])

# 实时监控
@app.middleware("http")
async def track_metrics(request, call_next):
    start = time.time()
    response = await call_next(request)

    latency = time.time() - start
    ai_request_latency.labels(provider=provider).observe(latency)

    return response
```

### 2. 告警规则

```yaml
# Prometheus Alert
- alert: HighAICost
  expr: rate(ai_request_cost_usd[1h]) > 10
  annotations:
    summary: "AI成本过高"

- alert: HighLatency
  expr: histogram_quantile(0.95, ai_request_latency_seconds) > 5
  annotations:
    summary: "AI响应延迟过高"
```

---

## 🎯 总结

### 核心优势

1. **成本优化**: 98%成本降低,从$9K/月 → $53/月
2. **性能提升**: 70%请求<100ms响应
3. **隐私保护**: 端到端加密 + 本地推理选项
4. **可扩展性**: MCP标准化,易于添加新能力
5. **未来就绪**: 支持多模态、新模型快速接入

### 关键技术点

- ✅ 混合AI架构(本地+云端)
- ✅ 智能路由算法
- ✅ MCP标准化工具调用
- ✅ RAG知识增强
- ✅ 异步处理架构
- ✅ 端到端加密

### 下一步

1. **Phase 1**: 完成基础架构开发
2. **Phase 2**: 训练/优化本地模型
3. **Phase 3**: 构建RAG知识库
4. **Phase 4**: 性能测试与优化
5. **Phase 5**: 生产部署与监控

---

**文档维护**: 技术架构会持续演进,请定期查看最新版本。

**反馈**: 如有问题或建议,请联系技术团队。
