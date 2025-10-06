# 🔒 环境变量安全使用指南

## 为什么需要 `.env` 文件?

`.env` 文件用于存储**真实的API密钥和敏感配置**,这些信息:
- ✅ 需要在本地运行应用时使用
- ❌ 绝对不能提交到Git
- ❌ 绝对不能出现在代码或文档中

---

## 🛡️ 多层安全防护体系

### 第1层: `.gitignore` 自动忽略
```bash
# .gitignore 已包含:
.env
.env.local
.env.*.local
```
**作用**: 防止 `git add` 时意外添加

### 第2层: Pre-commit Hook 主动阻止
```bash
# .git/hooks/pre-commit
# 检测到 .env 文件时会报错并阻止提交
```
**作用**: 即使用 `git add -f .env` 强制添加,也会被拦截

### 第3层: 密钥模式扫描
```bash
# 扫描所有文件内容中的密钥模式
# 包括: sk-proj-, sk-ant-api03-, AKIA, ghp_ 等
```
**作用**: 防止密钥硬编码在代码/文档中

### 第4层: 环境变量优先级
```
系统环境变量 > .env 文件 > 代码默认值
```
**作用**: 生产环境可以用系统变量覆盖本地配置

---

## ✅ 正确的使用流程

### 步骤1: 复制模板并填写密钥

```bash
# 1. 复制 .env.example 为 .env
cp .env.example .env

# 2. 编辑 .env (使用任何编辑器)
nano .env
# 或
open -e .env
# 或
code .env

# 3. 填入真实密钥
OPENAI_API_KEY=sk-proj-你从OpenAI网站复制的完整密钥
ANTHROPIC_API_KEY=sk-ant-api03-你从Anthropic网站复制的完整密钥
```

### 步骤2: 验证安全性

```bash
# 运行安全检查脚本
./scripts/verify_env_security.sh
```

**期望输出**:
```
✅ .env 文件存在
✅ .env 在 .gitignore 中 (安全)
✅ .env 未被 Git 追踪 (安全)
✅ 所有必要配置项已填写
🎉 环境变量安全检查通过!
```

### 步骤3: 测试API连接

```bash
cd backend
source venv/bin/activate  # 或 poetry shell
python test_ai_apis.py
```

**期望输出**:
```
✅ OpenAI API 连接成功!
✅ Anthropic API 连接成功!
🎉 所有API连接正常!
```

---

## ❌ 常见错误示例

### 错误1: 在代码中硬编码密钥

```python
# ❌ 错误 - 永远不要这样做!
api_key = "sk-proj-abc123..."

# ✅ 正确 - 从环境变量读取
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### 错误2: 在文档中记录真实密钥

```markdown
❌ 错误:
OPENAI_API_KEY=sk-proj-nRlxa...  ← 即使截断也会被检测

✅ 正确:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
# 或
OPENAI_API_KEY=<从OpenAI获取>
```

### 错误3: 提交 `.env` 文件

```bash
# ❌ 错误
git add -f .env
git commit -m "Add config"

# ✅ 正确
# .env 永远不应该被提交!
# 如果意外staged,立即unstage:
git reset HEAD .env
```

---

## 🔄 密钥轮换流程

建议每3个月轮换一次API密钥:

```bash
# 1. 在OpenAI/Anthropic网站生成新密钥
#    (保留旧密钥先不删除,确保新密钥工作后再删)

# 2. 更新 .env 文件中的密钥
nano .env

# 3. 测试新密钥
cd backend && python test_ai_apis.py

# 4. 确认工作后,在网站上删除旧密钥

# 5. (可选) 提交一个无关的改动来记录轮换日期
echo "$(date): Rotated API keys" >> .key_rotation_log
git add .key_rotation_log
git commit -m "chore: API key rotation on $(date +%Y-%m-%d)"
```

---

## 🚨 密钥泄露应急响应

如果不小心提交了密钥到Git:

### 立即执行 (5分钟内):

```bash
# 1. 撤销OpenAI密钥
open https://platform.openai.com/api-keys
# 找到泄露的密钥 → 点击 Delete

# 2. 撤销Anthropic密钥
open https://console.anthropic.com/settings/keys
# 找到泄露的密钥 → 点击 Revoke

# 3. 生成新密钥并更新 .env
nano .env
```

### 清理Git历史 (10分钟内):

```bash
# 方法1: 如果刚刚提交 (推荐)
git reset --soft HEAD~1  # 撤销最后一次提交
git reset HEAD .env      # unstage .env
# 移除文件中的密钥
git add <files>
git commit -m "fix: Remove sensitive data"
git push --force

# 方法2: 如果是历史提交
# 参考 SECURITY.md 中的详细步骤
```

---

## 📊 安全检查清单

开发时每次提交前检查:

- [ ] `.env` 未被staged (`git status` 不应显示.env)
- [ ] 代码中无硬编码密钥 (搜索 `sk-proj-`, `sk-ant-`)
- [ ] 文档中无真实密钥 (使用 `xxxx` 占位符)
- [ ] Pre-commit hook 通过
- [ ] 运行 `./scripts/verify_env_security.sh` 通过

---

## 🎓 最佳实践

### 1. 使用环境变量管理工具

**本地开发**:
```bash
# .env 文件 (已在 .gitignore)
OPENAI_API_KEY=sk-proj-xxx
```

**生产环境** (推荐):
```bash
# 使用系统环境变量或密钥管理服务
export OPENAI_API_KEY=sk-proj-xxx

# 或使用 Docker secrets
docker secret create openai_key <key_file>

# 或使用云服务密钥管理
# - AWS Secrets Manager
# - Google Cloud Secret Manager
# - Azure Key Vault
# - Aliyun KMS
```

### 2. 最小权限原则

为每个环境创建独立的API密钥:
- 开发环境: 有限额度的密钥
- 测试环境: 独立密钥
- 生产环境: 独立密钥 + 使用限制

### 3. 监控和审计

```bash
# 定期检查API使用量
# OpenAI: https://platform.openai.com/usage
# Anthropic: https://console.anthropic.com/usage

# 发现异常立即撤销密钥
```

---

## 📞 获取帮助

遇到问题时:

1. **查看文档**: [SECURITY.md](../SECURITY.md)
2. **运行检查**: `./scripts/verify_env_security.sh`
3. **查看日志**: `git log --all -- .env` (应该为空)

---

## ⚡ 快速参考命令

```bash
# 创建 .env
cp .env.example .env && nano .env

# 安全检查
./scripts/verify_env_security.sh

# 测试API
cd backend && python test_ai_apis.py

# 验证 .env 未被追踪
git check-ignore -v .env  # 应输出 .gitignore:106:.env

# 查看staged文件
git diff --cached --name-only  # 不应包含 .env
```

---

**记住: 当你看到真实密钥在代码/文档中时,立即红色警报! 🚨**
