# AI对话功能设置和测试指南

本文档介绍如何配置和测试PeakState的AI对话功能。

## 📋 前置条件

1. 已完成[QUICKSTART.md](../QUICKSTART.md)中的基础环境设置
2. PostgreSQL数据库运行中
3. 已运行数据库迁移

## 🔑 步骤1: 配置AI API密钥

### 1.1 复制环境变量文件

```bash
cd /Users/apple/Desktop/PeakState
cp .env.example .env
```

### 1.2 配置OpenAI API密钥(必需)

在`.env`文件中设置:

```bash
# OpenAI配置
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
OPENAI_MODEL_MAIN=gpt-4o
OPENAI_MODEL_MINI=gpt-4o-mini
```

**获取OpenAI API密钥**:
1. 访问 https://platform.openai.com/api-keys
2. 登录或注册账号
3. 点击"Create new secret key"
4. 复制密钥并粘贴到`.env`文件

### 1.3 配置Anthropic API密钥(可选,用于情感支持场景)

```bash
# Anthropic Claude配置
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**获取Anthropic API密钥**:
1. 访问 https://console.anthropic.com/
2. 登录或注册账号
3. 进入Settings -> API Keys
4. 创建新密钥并复制

### 1.4 本地模型配置(可选)

如果想使用本地Phi-3.5模型(成本为0,但需要下载模型):

```bash
USE_LOCAL_MODEL=true
LOCAL_MODEL_PATH=./models/phi-3.5-mini-instruct
LOCAL_MODEL_DEVICE=cpu  # 如果有GPU,设为cuda或mps(Mac)
```

**注意**: 本地模型功能尚未完全实现,当前版本会使用云端API。

## 🚀 步骤2: 启动后端服务

```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 🧪 步骤3: 测试AI对话功能

### 3.1 注册测试用户

使用curl或API文档界面:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000",
    "password": "Test123456",
    "coach_selection": "companion"
  }'
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

保存`access_token`,后续请求需要使用。

### 3.2 发送第一条消息

```bash
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "我最近总是感觉很累,精力不足,怎么办?",
    "include_history": true
  }'
```

**响应示例**:
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "我完全理解这种感觉,很多时候我们都会经历这样的疲惫期😊 让我帮你分析一下...",
  "ai_provider": "gpt-4o-mini",
  "complexity_score": 5,
  "intent": "energy_management",
  "tokens_used": 156,
  "response_time_ms": 1250,
  "timestamp": "2025-10-06T10:30:00Z"
}
```

### 3.3 继续对话(带历史上下文)

```bash
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "我的睡眠时间大概6小时左右",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "include_history": true
  }'
```

### 3.4 查看会话历史

```bash
curl -X GET "http://localhost:8000/api/v1/chat/history/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3.5 获取所有会话列表

```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🎯 步骤4: 测试AI路由决策(调试)

查看不同消息如何被路由到不同的AI模型:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/debug/routing" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "你好"
  }'
```

**响应示例**:
```json
{
  "provider": "phi-3.5",
  "complexity": 1,
  "intent": {
    "primary_intent": "greeting",
    "confidence": 0.98,
    "requires_empathy": false,
    "suggested_actions": []
  },
  "estimated_cost": 0.0,
  "estimated_latency_ms": 50,
  "reasoning": "低复杂度(1),使用本地模型"
}
```

## 📊 AI路由策略说明

系统会根据消息复杂度自动选择最优AI模型:

| 复杂度 | AI模型 | 使用场景 | 成本 | 延迟 |
|--------|--------|----------|------|------|
| 1-2 | 本地Phi-3.5 | 简单问候、确认 | $0 | ~50ms |
| 3-5 | GPT-4o-mini | 一般咨询、建议 | $0.00015/1K | ~1.5s |
| 6-8 | Claude 3.5 | 情感支持、共情 | $0.003/1K | ~1.8s |
| 9-10 | GPT-4o | 复杂分析、诊断 | $0.0025/1K | ~2s |

**成本优化**: 约70%请求使用本地模型,实现99.4%成本节省。

## 🎭 教练人设测试

系统支持3种教练人设,在注册时通过`coach_selection`指定:

### 1. Sage(智者) - 启发式引导

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138001",
    "password": "Test123456",
    "coach_selection": "sage"
  }'
```

**特点**: 温和、睿智、使用隐喻和问题引导思考

### 2. Companion(伙伴) - 温暖陪伴

```bash
{
  "coach_selection": "companion"
}
```

**特点**: 亲切、自然、充满同理心、鼓励式沟通

### 3. Expert(专家) - 数据驱动

```bash
{
  "coach_selection": "expert"
}
```

**特点**: 专业、精准、基于科学证据、系统化方案

## 🔍 故障排查

### 问题1: "OpenAI client not initialized"

**原因**: `.env`文件中未设置`OPENAI_API_KEY`

**解决**:
1. 检查`.env`文件是否存在
2. 确认`OPENAI_API_KEY`已正确设置
3. 重启后端服务

### 问题2: "Subscription expired"

**原因**: 测试用户试用期已过

**解决**:
```bash
# 注册新用户(自动获得7天试用)
# 或在数据库中手动延长trial_end_date
```

### 问题3: AI响应错误

**检查步骤**:
1. 查看后端日志: `tail -f backend/logs/app.log`
2. 验证API密钥是否有效
3. 检查API余额是否充足
4. 确认网络连接正常

### 问题4: 响应速度慢

**优化建议**:
1. 启用本地模型(需下载Phi-3.5)
2. 减少`include_history`中的历史消息数量
3. 使用`gpt-4o-mini`而非`gpt-4o`

## 📖 API端点总览

### 聊天相关

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/chat/send` | 发送消息 |
| GET | `/api/v1/chat/history/{id}` | 获取会话历史 |
| GET | `/api/v1/chat/conversations` | 获取会话列表 |
| POST | `/api/v1/chat/new` | 创建新会话 |
| DELETE | `/api/v1/chat/{id}` | 删除会话 |
| POST | `/api/v1/chat/debug/routing` | 调试路由决策 |

### 认证相关

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册用户 |
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/refresh` | 刷新token |
| GET | `/api/v1/auth/me` | 获取当前用户 |

## 🎓 下一步

1. **集成健康数据**: 实现HealthData API,让AI能访问真实健康指标
2. **主动对话**: 实现Celery定时任务,触发晨间简报和晚间复盘
3. **MCP工具调用**: 接入日历、睡眠分析等工具
4. **本地模型**: 下载并集成Phi-3.5本地模型
5. **前端开发**: 创建React Native聊天界面

## 📚 相关文档

- [AI架构详解](../docs/AI_ARCHITECTURE.md)
- [认证系统指南](./AUTHENTICATION_GUIDE.md)
- [数据库迁移指南](./DATABASE_MIGRATIONS.md)
- [快速开始](../QUICKSTART.md)

## 💡 提示

- 使用Swagger文档界面测试更方便: http://localhost:8000/docs
- 查看详细日志: `tail -f backend/logs/app.log`
- 监控token使用: 每次响应都包含`tokens_used`字段
- 测试不同复杂度消息,观察AI路由策略
