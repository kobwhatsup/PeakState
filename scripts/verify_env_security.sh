#!/bin/bash

# 环境变量安全验证脚本
# 使用方法: ./scripts/verify_env_security.sh

set -e

echo "🔒 环境变量安全检查"
echo "========================================"
echo ""

# 检查1: .env文件存在性
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在"
    echo "   请复制 .env.example 并填入真实密钥:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi
echo "✅ .env 文件存在"

# 检查2: .env在.gitignore中
if git check-ignore -q .env; then
    echo "✅ .env 在 .gitignore 中 (安全)"
else
    echo "❌ 危险: .env 不在 .gitignore 中!"
    echo "   立即添加到 .gitignore:"
    echo "   echo '.env' >> .gitignore"
    exit 1
fi

# 检查3: .env未被Git追踪
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ 严重错误: .env 已被 Git 追踪!"
    echo "   立即从Git中移除:"
    echo "   git rm --cached .env"
    echo "   git commit -m 'Remove .env from Git'"
    exit 1
fi
echo "✅ .env 未被 Git 追踪 (安全)"

# 检查4: .env包含必要的密钥
required_keys=(
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "JWT_SECRET_KEY"
    "POSTGRES_PASSWORD"
    "REDIS_PASSWORD"
)

missing_keys=()
placeholder_keys=()

for key in "${required_keys[@]}"; do
    if ! grep -q "^${key}=" .env; then
        missing_keys+=("$key")
    elif grep -q "^${key}=.*\(your-.*-here\|xxxx\|<.*>\)" .env; then
        placeholder_keys+=("$key")
    fi
done

if [ ${#missing_keys[@]} -gt 0 ]; then
    echo "❌ 缺少以下配置项:"
    printf '   - %s\n' "${missing_keys[@]}"
    exit 1
fi

if [ ${#placeholder_keys[@]} -gt 0 ]; then
    echo "⚠️  以下配置项仍为占位符,需要替换为真实值:"
    printf '   - %s\n' "${placeholder_keys[@]}"
    echo ""
    echo "   编辑 .env 文件并填入真实密钥"
    exit 1
fi

echo "✅ 所有必要配置项已填写"

# 检查5: 密钥格式验证
openai_key=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2)
anthropic_key=$(grep "^ANTHROPIC_API_KEY=" .env | cut -d'=' -f2)

if [[ ! "$openai_key" =~ ^sk-proj-[A-Za-z0-9_-]{20,}$ ]]; then
    echo "⚠️  OpenAI API key 格式可能不正确"
    echo "   期望格式: sk-proj-xxxx..."
    echo "   当前开头: ${openai_key:0:15}..."
fi

if [[ ! "$anthropic_key" =~ ^sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{20,}$ ]]; then
    echo "⚠️  Anthropic API key 格式可能不正确"
    echo "   期望格式: sk-ant-api03-xxxx..."
    echo "   当前开头: ${anthropic_key:0:20}..."
fi

# 检查6: 密钥长度
if [ ${#openai_key} -lt 50 ]; then
    echo "⚠️  OpenAI API key 长度过短 (${#openai_key} 字符)"
    echo "   请确认是否复制完整"
fi

if [ ${#anthropic_key} -lt 50 ]; then
    echo "⚠️  Anthropic API key 长度过短 (${#anthropic_key} 字符)"
    echo "   请确认是否复制完整"
fi

echo ""
echo "========================================"
echo "🎉 环境变量安全检查通过!"
echo ""
echo "下一步:"
echo "  1. 测试API连接: cd backend && python test_ai_apis.py"
echo "  2. 启动应用: docker-compose up -d"
echo ""
echo "⚠️  重要提醒:"
echo "  - 永远不要提交 .env 文件到 Git"
echo "  - 定期轮换 API 密钥 (建议每3个月)"
echo "  - 密钥泄露后立即撤销并重新生成"
echo ""
