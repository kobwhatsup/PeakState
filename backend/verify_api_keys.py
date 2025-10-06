#!/usr/bin/env python3
"""
验证OpenAI和Anthropic API密钥是否配置正确
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 60)
print("API密钥验证工具")
print("=" * 60)

# 检查环境变量
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

print("\n📋 环境变量检查:")
print(f"  OPENAI_API_KEY: {'✅ 已设置' if openai_key else '❌ 未设置'}")
if openai_key:
    print(f"    - 格式: {'✅ 正确 (sk-...)' if openai_key.startswith('sk-') else '❌ 错误'}")
    print(f"    - 长度: {len(openai_key)} 字符")
    print(f"    - 预览: {openai_key[:10]}...{openai_key[-4:]}")

print(f"\n  ANTHROPIC_API_KEY: {'✅ 已设置' if anthropic_key else '❌ 未设置'}")
if anthropic_key:
    print(f"    - 格式: {'✅ 正确 (sk-ant-...)' if anthropic_key.startswith('sk-ant-') else '❌ 错误'}")
    print(f"    - 长度: {len(anthropic_key)} 字符")
    print(f"    - 预览: {anthropic_key[:12]}...{anthropic_key[-4:]}")

# 测试OpenAI连接
print("\n🔍 测试OpenAI API连接...")
if openai_key and openai_key != "sk-test-key":
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API works!'"}],
            max_tokens=10
        )

        print("  ✅ OpenAI API 连接成功!")
        print(f"  ✅ 响应: {response.choices[0].message.content}")
        print(f"  ✅ Token使用: {response.usage.total_tokens}")

    except Exception as e:
        print(f"  ❌ OpenAI API 连接失败: {e}")
else:
    print("  ⚠️  跳过(使用测试密钥或未配置)")

# 测试Anthropic连接
print("\n🔍 测试Anthropic API连接...")
if anthropic_key and anthropic_key != "sk-ant-test-key":
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'API works!'"}]
        )

        print("  ✅ Anthropic API 连接成功!")
        print(f"  ✅ 响应: {response.content[0].text}")
        print(f"  ✅ Token使用: {response.usage.input_tokens + response.usage.output_tokens}")

    except Exception as e:
        print(f"  ❌ Anthropic API 连接失败: {e}")
else:
    print("  ⚠️  跳过(使用测试密钥或未配置)")

print("\n" + "=" * 60)
print("验证完成!")
print("=" * 60)

# 给出建议
print("\n💡 建议:")
if not openai_key or openai_key == "sk-test-key":
    print("  1. 配置OpenAI API密钥 (必需)")
    print("     - 访问: https://platform.openai.com/api-keys")
    print("     - 在.env中设置: OPENAI_API_KEY=sk-proj-...")

if not anthropic_key or anthropic_key == "sk-ant-test-key":
    print("  2. 配置Anthropic API密钥 (可选,用于情感支持场景)")
    print("     - 访问: https://console.anthropic.com/")
    print("     - 在.env中设置: ANTHROPIC_API_KEY=sk-ant-...")

if (openai_key and openai_key != "sk-test-key") and (anthropic_key and anthropic_key != "sk-ant-test-key"):
    print("  ✅ 所有API密钥配置完成!")
    print("  ✅ 可以启动服务器并测试AI对话功能")
    print("\n  启动命令:")
    print("    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

print()
