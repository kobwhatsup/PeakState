# 🚀 PeakState快速开始指南

> 5分钟内启动PeakState开发环境

---

## 📋 前置条件检查

在开始之前,请确保您的系统已安装:

- ✅ **Node.js** 18+ (已安装: v24.3.0)
- ✅ **Python** 3.11+ (已安装: 3.11.7)
- ✅ **Docker** & Docker Compose (已安装)
- ⬜ **Poetry** (Python包管理器)
- ⬜ **Git** (版本控制)

### 安装Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# 添加到PATH
export PATH="$HOME/.local/bin:$PATH"

# 验证安装
poetry --version
```

---

## 🏃 快速启动(3步)

### Step 1: 环境配置

```bash
cd /Users/apple/Desktop/PeakState

# 复制环境变量模板
cp .env.example .env

# 编辑.env,填入必要的API密钥
# 至少需要配置:
# - OPENAI_API_KEY (用于GPT模型)
# - ANTHROPIC_API_KEY (用于Claude模型)
nano .env
```

**重要**: 获取API密钥

- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

### Step 2: 启动基础设施

```bash
# 启动数据库、Redis、Qdrant
docker-compose up -d postgres redis qdrant

# 查看服务状态
docker-compose ps

# 预期输出:
# ✅ peakstate-postgres   running   0.0.0.0:5432
# ✅ peakstate-redis      running   0.0.0.0:6379
# ✅ peakstate-qdrant     running   0.0.0.0:6333
```

### Step 3: 启动后端服务

```bash
cd backend

# 安装依赖
poetry install

# 启动开发服务器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
open http://localhost:8000/docs
```

🎉 **成功!** 后端服务已启动在 http://localhost:8000

---

## 🧪 验证安装

### 1. 检查健康状态

```bash
curl http://localhost:8000/health

# 预期输出:
{
  "status": "healthy",
  "environment": "development",
  "timestamp": 1696579200.123
}
```

### 2. 测试AI Orchestrator

```bash
# 启动Python交互式shell
cd backend
poetry run ipython

# 测试代码:
```

```python
from app.ai.orchestrator import orchestrator
import asyncio

# 测试意图分类
async def test():
    # 简单问候
    intent = await orchestrator.classify_intent("你好")
    print(f"Intent: {intent.intent}, Confidence: {intent.confidence}")

    # 测试路由决策
    decision = await orchestrator.route_request(
        user_message="我昨晚睡得不好,请帮我分析一下原因",
        conversation_history=[],
        user_profile={}
    )
    print(f"Provider: {decision.provider}")
    print(f"Complexity: {decision.complexity}")
    print(f"Reason: {decision.reason}")

# 运行测试
asyncio.run(test())

# 预期输出:
# Intent: greeting, Confidence: 0.95
# Provider: gpt-4o-mini
# Complexity: 6
# Reason: 中等复杂度(6),使用mini模型
```

### 3. 检查数据库连接

```bash
# 连接PostgreSQL
docker exec -it peakstate-postgres psql -U peakstate_user -d peakstate

# 列出所有表
\dt

# 退出
\q
```

---

## 🛠️ 开发工作流

### 后端开发

```bash
cd backend

# 安装新依赖
poetry add package-name

# 运行测试
poetry run pytest

# 代码格式化
poetry run black app/
poetry run isort app/

# 类型检查
poetry run mypy app/

# 启动开发服务器(带热重载)
poetry run uvicorn app.main:app --reload
```

### 前端开发(即将创建)

```bash
cd frontend

# 安装依赖
npm install

# iOS开发
npm run ios

# Android开发
npm run android

# 启动Metro bundler
npm start
```

### Docker开发(推荐)

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 清理所有数据(慎用!)
docker-compose down -v
```

---

## 📚 常用命令

### 数据库迁移

```bash
cd backend

# 创建新迁移
poetry run alembic revision --autogenerate -m "描述"

# 应用迁移
poetry run alembic upgrade head

# 回滚迁移
poetry run alembic downgrade -1
```

### 缓存管理

```bash
# 清空Redis缓存
docker exec -it peakstate-redis redis-cli -a peakstate_dev_redis FLUSHALL

# 查看所有键
docker exec -it peakstate-redis redis-cli -a peakstate_dev_redis KEYS '*'
```

### 向量数据库

```bash
# 访问Qdrant Web UI
open http://localhost:6333/dashboard

# 通过API查询集合
curl http://localhost:6333/collections
```

---

## 🐛 故障排查

### 问题1: Docker服务启动失败

```bash
# 检查端口占用
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :6333  # Qdrant

# 停止占用进程或修改端口
# 编辑 docker-compose.yml
```

### 问题2: Poetry安装依赖失败

```bash
# 清除缓存
poetry cache clear pypi --all

# 重新安装
poetry install --no-cache
```

### 问题3: OpenAI API调用失败

```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试API连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 问题4: 数据库连接错误

```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 查看日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

---

## 📖 下一步

恭喜您成功启动了PeakState!接下来建议:

1. ✅ **阅读架构文档**: [docs/AI_ARCHITECTURE.md](docs/AI_ARCHITECTURE.md)
2. ✅ **了解API接口**: http://localhost:8000/docs
3. ✅ **查看项目结构**: 理解代码组织
4. ⬜ **创建数据模型**: 设计User、Conversation等表
5. ⬜ **实现MCP服务器**: 健康数据和日历工具
6. ⬜ **开发前端应用**: React Native界面

---

## 🤝 获取帮助

- **文档**: [README.md](README.md)
- **API文档**: http://localhost:8000/docs
- **技术架构**: [docs/AI_ARCHITECTURE.md](docs/AI_ARCHITECTURE.md)
- **问题反馈**: 联系技术团队

---

**Happy Coding! 🎯**
