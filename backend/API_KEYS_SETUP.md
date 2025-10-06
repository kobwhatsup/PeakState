# API密钥配置指南

## ⚠️ 重要提醒

当前系统使用测试密钥,无法调用真实的AI服务。要启用完整的AI对话功能,需要配置真实的API密钥。

---

## 🔑 如何获取API密钥

### 1. OpenAI API密钥 (必需)

**获取步骤**:

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录或注册账号
3. 点击 "Create new secret key"
4. 输入密钥名称(例如: "PeakState Development")
5. 复制生成的密钥(格式: `sk-proj-xxxxx...`)

**定价** (2025年价格):
- GPT-4o: $2.50 / 1M input tokens, $10 / 1M output tokens
- GPT-4o-mini: $0.15 / 1M input tokens, $0.60 / 1M output tokens

**推荐充值**: $5-10 (足够测试和初期使用)

---

### 2. Anthropic API密钥 (可选,用于情感支持场景)

**获取步骤**:

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 登录或注册账号
3. 进入 Settings → API Keys
4. 点击 "Create Key"
5. 复制生成的密钥(格式: `sk-ant-xxxxx...`)

**定价**:
- Claude 3.5 Sonnet: $3 / 1M input tokens, $15 / 1M output tokens

**推荐充值**: $5 (可选,用于情感支持场景)

---

## 📝 配置步骤

### 方法1: 直接编辑.env文件 (推荐)

```bash
cd /Users/apple/Desktop/PeakState/backend
nano .env  # 或使用你喜欢的编辑器
```

找到以下行并替换:

```bash
# AI Models
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key-here
```

保存并退出。

### 方法2: 使用环境变量

```bash
export OPENAI_API_KEY="sk-proj-xxxxx..."
export ANTHROPIC_API_KEY="sk-ant-xxxxx..."
```

**注意**: 此方法仅在当前shell会话有效。

---

## ✅ 验证配置

### 1. 检查.env文件

```bash
cd /Users/apple/Desktop/PeakState/backend
cat .env | grep API_KEY
```

应该看到:
```
OPENAI_API_KEY=sk-proj-xxxxx...
ANTHROPIC_API_KEY=sk-ant-xxxxx...
```

### 2. 测试OpenAI连接

```bash
source venv/bin/activate
python -c "
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say hello'}],
        max_tokens=10
    )
    print('✅ OpenAI API连接成功!')
    print(f'Response: {response.choices[0].message.content}')
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

### 3. 测试Anthropic连接

```bash
python -c "
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

try:
    response = client.messages.create(
        model='claude-3-5-sonnet-20241022',
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'Say hello'}]
    )
    print('✅ Anthropic API连接成功!')
    print(f'Response: {response.content[0].text}')
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

---

## 🚨 故障排查

### 问题1: "Incorrect API key provided"

**原因**: API密钥错误或格式不正确

**解决**:
1. 检查密钥是否完整复制(包括`sk-`前缀)
2. 确认没有多余的空格或换行符
3. 重新生成新密钥

### 问题2: "You exceeded your current quota"

**原因**: API账户余额不足

**解决**:
1. 访问 [OpenAI Billing](https://platform.openai.com/account/billing) 充值
2. 或访问 [Anthropic Console](https://console.anthropic.com/) 充值

### 问题3: "Rate limit exceeded"

**原因**: 请求频率超过限制

**解决**:
1. 等待几分钟后重试
2. 降低请求频率
3. 升级API套餐

---

## 💰 成本优化建议

### 1. 启用本地模型 (推荐)

编辑`.env`:
```bash
USE_LOCAL_MODEL=true
AI_ROUTE_LOCAL_THRESHOLD=3  # 复杂度<3使用本地模型
```

**效果**: 约70%的请求使用免费的本地模型,大幅降低成本

### 2. 调整路由阈值

```bash
AI_ROUTE_LOCAL_THRESHOLD=4   # 提高阈值,更多请求使用本地模型
AI_ROUTE_MINI_THRESHOLD=7    # 更多请求使用便宜的mini模型
```

### 3. 仅使用OpenAI (跳过Anthropic)

如果预算紧张,可以只配置OpenAI密钥:
```bash
OPENAI_API_KEY=sk-proj-xxxxx...
# ANTHROPIC_API_KEY=  # 留空或注释掉
```

系统会自动fallback到OpenAI处理情感支持场景。

---

## 📊 预期成本

### 测试阶段 (10次完整对话)

| 场景 | Token数 | 成本 |
|------|---------|------|
| 简单问候 | 50 | $0.00001 (本地) |
| 精力咨询 | 500 | $0.0003 (mini) |
| 复杂分析 | 2000 | $0.005 (gpt-4o) |
| **总计** | ~5000 | **$0.02** |

### 正式使用 (每天10次对话)

| Provider | 每月请求 | 每月成本 |
|----------|----------|----------|
| 本地Phi-3.5 | 210次 (70%) | $0 |
| GPT-4o-mini | 75次 (25%) | $0.45 |
| Claude 3.5 | 9次 (3%) | $0.81 |
| GPT-4o | 6次 (2%) | $0.33 |
| **总计** | 300次 | **$1.59/月** |

**结论**: 即使是单用户测试,成本也非常低(<$2/月)

---

## 🔐 安全建议

1. **不要提交.env到Git**:
   - 已在.gitignore中配置
   - 双重检查: `git status` 不应显示.env

2. **定期轮换密钥**:
   - 建议每3个月更换一次
   - 测试环境和生产环境使用不同密钥

3. **监控使用情况**:
   - OpenAI: https://platform.openai.com/usage
   - Anthropic: https://console.anthropic.com/settings/usage

4. **设置使用限额**:
   - OpenAI: Settings → Limits → 设置每月上限
   - 推荐: 测试期$10,生产期$50

---

## 📚 相关文档

- [OpenAI API文档](https://platform.openai.com/docs)
- [Anthropic API文档](https://docs.anthropic.com/claude/reference)
- [AI_CHAT_SETUP.md](./AI_CHAT_SETUP.md) - 聊天功能测试指南
- [AI_ARCHITECTURE.md](../docs/AI_ARCHITECTURE.md) - AI架构详解

---

## ✨ 下一步

配置完成后,继续阅读:
- [AI_CHAT_SETUP.md](./AI_CHAT_SETUP.md) - 启动服务并测试API

如有问题,检查后端日志:
```bash
tail -f backend/logs/app.log
```
