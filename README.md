# PeakState - AI精力管理教练

<div align="center">

![PeakState Logo](docs/assets/logo.png)

**将全球顶尖精力管理专家的智慧,通过超个性化的AI,赋能给每一位渴望自我超越的用户**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688.svg)](backend/)
[![Frontend](https://img.shields.io/badge/frontend-React%20Native-61DAFB.svg)](frontend/)
[![AI](https://img.shields.io/badge/AI-GPT--4%20%7C%20Claude-FF6B6B.svg)](docs/AI_ARCHITECTURE.md)

</div>

---

## ⚠️ **重要安全提醒**

**🔒 NEVER commit API keys or secrets to Git!**

- 本项目包含 pre-commit hook 防止密钥泄露
- 始终使用 `.env` 存储敏感配置(已在 `.gitignore` 中)
- 详细安全指南: [SECURITY.md](SECURITY.md)

---

## 📖 项目概述

PeakState是一款基于AI的个性化精力管理应用,提供7×24小时在线的私人AI教练服务。通过整合生理数据、行为数据和主观感受,运用先进的AI技术进行深度分析,帮助用户优化精力分配,保持巅峰状态。

### 🎯 核心特性

- **🤖 混合AI架构**: 本地模型(Phi-3.5) + 云端API(GPT-4o/Claude 3.5),智能路由
- **🔌 MCP标准化集成**: 基于Model Context Protocol的工具调用架构
- **📊 多源数据感知**: 支持HealthKit/Google Fit,无硬件用户同样可用
- **💬 主动对话触发**: 晨间简报、晚间复盘,AI主动关怀
- **🎨 3种AI人格**: 智者/伙伴/专家,满足不同用户偏好
- **🔒 隐私优先**: 端到端加密 + 本地推理选项

## 🏗️ 技术架构

### 核心技术栈

| 层面 | 技术选型 | 版本 |
|------|----------|------|
| **前端** | React Native + TypeScript | 0.73+ |
| **后端** | Python + FastAPI | 3.11+ |
| **数据库** | PostgreSQL + Redis | 15+ / 7+ |
| **向量DB** | Qdrant | 1.7+ |
| **AI核心** | OpenAI + Anthropic + Local Models | - |
| **消息队列** | Celery + Redis | - |
| **部署** | Docker + Aliyun ECS | - |

### AI架构亮点

```
┌─────────────────────────────────────────┐
│        AI Orchestrator (智能路由)        │
│     • 意图分类                           │
│     • 复杂度评分                         │
│     • 成本优化                           │
└─────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌───────────────┐       ┌──────────────────┐
│  本地模型      │       │  云端API         │
│  (70%请求)    │       │  (30%请求)       │
│               │       │                  │
│ • Phi-3.5     │       │ • GPT-4o-mini    │
│ • 零成本      │       │ • Claude 3.5     │
│ • <100ms      │       │ • GPT-4o         │
└───────────────┘       └──────────────────┘
```

**成本优化**: AI调用成本降低98% (从$900/月 → $15/月)

### MCP架构

使用Anthropic的Model Context Protocol实现标准化工具调用:

- **Health MCP Server**: 健康数据读取、分析
- **Calendar MCP Server**: 日程管理、负载预测
- **可扩展性**: 易于添加新工具(天气、运动等)

## 📁 项目结构

```
PeakState/
├── backend/                  # FastAPI后端
│   ├── app/
│   │   ├── ai/              # AI核心模块
│   │   │   ├── orchestrator.py    # 智能路由
│   │   │   ├── local_models.py    # 本地模型
│   │   │   └── mcp_client.py      # MCP客户端
│   │   ├── mcp/             # MCP服务器
│   │   │   ├── health_server.py
│   │   │   └── calendar_server.py
│   │   ├── api/             # API端点
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   └── rag/             # RAG知识库
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/                 # React Native前端
│   ├── src/
│   │   ├── screens/         # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── services/        # API服务
│   │   ├── store/           # 状态管理(Zustand)
│   │   └── utils/           # 工具函数
│   ├── ios/
│   ├── android/
│   └── package.json
│
├── infrastructure/           # 基础设施配置
│   ├── docker/
│   ├── k8s/
│   └── terraform/
│
└── docs/                     # 文档
    ├── AI_ARCHITECTURE.md
    ├── MCP_INTEGRATION.md
    └── API_REFERENCE.md
```

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/peakstate.git
cd peakstate
```

#### 2. 后端设置

```bash
cd backend

# 安装依赖(使用Poetry)
poetry install

# 配置环境变量
cp .env.example .env
# 编辑.env,填入API密钥等配置

# 启动数据库(Docker)
docker-compose up -d postgres redis qdrant

# 运行数据库迁移
poetry run alembic upgrade head

# 启动开发服务器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# iOS开发
npx pod-install
npm run ios

# Android开发
npm run android
```

#### 4. 启动MCP服务器

```bash
cd backend

# 启动Health MCP Server
poetry run python -m app.mcp.health_server

# 启动Calendar MCP Server
poetry run python -m app.mcp.calendar_server
```

### Docker一键启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 📊 开发进度

- [x] 技术架构设计
- [x] 项目初始化
- [ ] AI Orchestrator实现
- [ ] MCP服务器开发
- [ ] 用户认证系统
- [ ] AI对话引擎
- [ ] RAG知识库
- [ ] 前端入职流程
- [ ] 健康数据集成
- [ ] 测试与优化
- [ ] 生产部署

## 🤝 贡献指南

欢迎贡献代码!请查看[CONTRIBUTING.md](CONTRIBUTING.md)了解详情。

### 开发规范

- 代码风格: Black(Python) + ESLint+Prettier(TypeScript)
- 提交规范: Conventional Commits
- 分支策略: Git Flow
- 测试覆盖率: ≥80%

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 📞 联系方式

- 项目负责人: Manus
- 邮箱: contact@peakstate.com
- 文档: https://docs.peakstate.com

## 🙏 致谢

- [Anthropic](https://www.anthropic.com/) - Claude AI & MCP协议
- [OpenAI](https://openai.com/) - GPT模型
- [Microsoft](https://www.microsoft.com/) - Phi-3.5模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python框架
- [React Native](https://reactnative.dev/) - 跨平台框架

---

<div align="center">

**Built with ❤️ by PeakState Team**

[官网](https://peakstate.com) · [文档](https://docs.peakstate.com) · [博客](https://blog.peakstate.com)

</div>
