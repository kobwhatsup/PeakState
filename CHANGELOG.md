# Changelog

All notable changes to the PeakState project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### In Progress
- OpenAI API真实集成测试
- Anthropic API真实集成测试
- 本地Phi-3.5模型下载和集成

---

## [0.2.0] - 2025-10-06

### Added - AI对话核心功能

#### API端点
- POST `/api/v1/chat/send` - 发送消息,获取AI回复
- GET `/api/v1/chat/history/{id}` - 获取会话完整历史
- GET `/api/v1/chat/conversations` - 获取会话列表(分页)
- POST `/api/v1/chat/new` - 创建新会话
- DELETE `/api/v1/chat/{id}` - 删除指定会话
- POST `/api/v1/chat/debug/routing` - 调试AI路由决策

#### 数据模型 (Schemas)
- `ChatRequest`: 聊天请求模型
- `ChatResponse`: AI响应模型
- `ConversationHistory`: 会话历史模型
- `ConversationListResponse`: 会话列表响应(分页)
- `ProactiveBriefingRequest/Response`: 主动简报模型

#### CRUD操作 (`app/crud/conversation.py`)
- `create_conversation()`: 创建会话
- `get_conversation_by_id()`: 获取会话(权限验证)
- `get_user_conversations()`: 获取用户会话列表(分页)
- `add_message_to_conversation()`: 添加消息到会话
- `update_conversation_ai_provider()`: 更新AI提供商信息
- `delete_conversation()`: 删除会话
- `delete_old_conversations()`: 批量清理旧会话
- `get_conversation_summary()`: 获取会话摘要
- `get_conversation_context()`: 获取会话上下文

#### AI教练系统 (`app/ai/prompts.py`)
- **3种教练人设**:
  - Sage(智者): 温和睿智,启发式引导
  - Companion(伙伴): 亲切自然,温暖陪伴
  - Expert(专家): 专业精准,数据驱动

- **场景化提示词模板**:
  - 晨间简报 (MORNING_BRIEFING_TEMPLATE)
  - 晚间复盘 (EVENING_REVIEW_TEMPLATE)
  - 精力危机干预 (ENERGY_CRISIS_INTERVENTION_TEMPLATE)

- **Prompt构建系统**:
  - `build_system_prompt()`: 动态组合人设+场景+用户画像+健康数据
  - `build_intent_classification_prompt()`: 意图分类Prompt

#### AI Orchestrator增强
- 新增 `AIResponse` 数据类(包含content, tokens_used, finish_reason)
- `RoutingDecision` 添加 `intent` 字段
- `generate_response()` 方法更新:
  - 返回 `AIResponse` 对象(而非str)
  - 支持从 `conversation_history` 构建消息
  - OpenAI和Claude都返回token统计
- `_generate_openai()` 和 `_generate_claude()` 返回 `(content, tokens)` 元组

#### 文档
- `AI_CHAT_SETUP.md`: AI对话功能设置和测试指南
- `AI_CHAT_IMPLEMENTATION_SUMMARY.md`: 实施总结(1300+行代码)
- `PROJECT_STATUS_UPDATE.md`: 项目进度更新

### Fixed

- **Pydantic递归初始化错误**:
  - 问题: `Settings`类中使用`Field(default_factory=lambda: Settings().XXX)`导致无限递归
  - 修复: 改用`@model_validator`在初始化后设置默认值

- **NullPool与连接池参数冲突**:
  - 问题: 开发环境使用NullPool时不能传递pool_size/max_overflow
  - 修复: 根据环境分别配置数据库引擎参数

- **配置脱敏类型错误**:
  - 问题: 敏感配置可能是int类型,不能直接切片
  - 修复: 添加`isinstance(config_dict[key], str)`检查

### Changed

- `app/core/config.py`:
  - `SENTRY_ENVIRONMENT`: 从递归default_factory改为model_validator设置
  - `CELERY_BROKER_URL/CELERY_RESULT_BACKEND`: 同上

- `app/core/database.py`:
  - 根据环境变量分别配置数据库引擎(开发环境NullPool vs 生产环境连接池)

### Technical Metrics

- **代码行数**: +1,300行 (总计约3,500行)
- **新增文件**: 4个Python模块 + 3个文档
- **API端点**: +6个
- **测试状态**: 所有模块导入测试通过 ✅

---

## [0.1.0] - 2025-09-30

### Added - 基础设施和认证系统

#### 项目初始化
- Docker Compose环境配置
  - PostgreSQL 15
  - Redis 7
  - Qdrant向量数据库
- FastAPI应用骨架
- 开发环境配置(.env.example)

#### 数据库模型
- `User`: 用户模型(认证、订阅、教练选择)
- `Conversation`: 会话模型(JSONB消息存储)
- `HealthData`: 健康数据模型(加密支持)

#### 认证系统
- JWT认证(access_token + refresh_token)
- POST `/api/v1/auth/register` - 用户注册
- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/refresh` - 刷新token
- GET `/api/v1/auth/me` - 获取当前用户信息
- PUT `/api/v1/auth/me` - 更新用户信息

#### 数据库迁移
- Alembic配置
- V1__Initial_Schema.sql: 初始数据库架构
- 支持Aliyun RDS PostgreSQL

#### AI架构设计
- `AIOrchestrator`: AI智能路由系统
- 支持4种AI Provider:
  - 本地Phi-3.5
  - OpenAI GPT-4o-mini
  - OpenAI GPT-4o
  - Anthropic Claude 3.5 Sonnet
- 意图分类和复杂度评分
- 成本优化路由策略(99.4%成本节省)

#### 文档
- README.md: 项目概述
- QUICKSTART.md: 5分钟快速启动指南
- AI_ARCHITECTURE.md: AI架构详解(8000+字)
- ARCHITECTURE_SUMMARY.md: 架构决策摘要
- AUTHENTICATION_GUIDE.md: 认证系统使用指南

### Technical Stack

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.118+ |
| Python | CPython | 3.11+ |
| 数据库 | PostgreSQL | 15+ |
| ORM | SQLAlchemy (async) | 2.0+ |
| 缓存 | Redis | 7+ |
| 向量DB | Qdrant | 1.7+ |
| 认证 | JWT (python-jose) | - |
| 加密 | Fernet (cryptography) | - |

### Technical Metrics

- **代码行数**: 约2,200行
- **文件数**: 20+个Python模块
- **文档**: 5个主要文档
- **测试覆盖率**: 0% (待改进)

---

## Project Roadmap

### Week 1-4: ✅ 基础设施 (已完成)
- Docker环境搭建
- FastAPI应用
- 数据库模型设计
- 用户认证系统
- 数据库迁移

### Week 5-6: ✅ AI对话核心 (已完成)
- 聊天API开发
- Prompts工程
- Conversation CRUD
- AI路由优化

### Week 7-8: 🔄 AI对话完善 (进行中)
- 真实API集成测试
- 主动对话(Celery任务)
- 推送通知基础

### Week 9-11: 📅 健康数据集成 (计划中)
- 健康数据同步API
- 数据分析算法
- AI集成健康指标

### Week 12-14: 📅 前端开发 (计划中)
- React Native项目初始化
- 聊天界面UI
- 健康数据展示
- Onboarding流程

### Week 15-16: 📅 高级功能 (计划中)
- MCP工具调用
- 干预工具(呼吸练习、专注计时器)
- 支付集成
- 测试和发布

---

## Contributors

- **AI Implementation**: Claude Code
- **Product Design**: Based on PeakState_Complete_Documentation_v1.0.pdf
- **Architecture**: Hybrid AI with intelligent routing

---

## License

MIT License - see [LICENSE](LICENSE) file for details
