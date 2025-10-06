#!/usr/bin/env python3
"""
测试OpenAI和Anthropic API直接连接
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_openai():
    """测试OpenAI API"""
    print("\n" + "="*60)
    print("测试 OpenAI GPT-5 Nano")
    print("="*60)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = await client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",  # 使用最新版本号
            messages=[
                {"role": "user", "content": "请用一句话介绍你自己"}
            ],
            max_completion_tokens=100  # GPT-5使用新参数名
        )

        print(f"✅ OpenAI API 连接成功!")
        print(f"✅ 模型: {response.model}")
        print(f"✅ 回复: {response.choices[0].message.content}")
        print(f"✅ Token使用: {response.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"❌ OpenAI API 连接失败: {e}")
        return False


async def test_anthropic():
    """测试Anthropic API"""
    print("\n" + "="*60)
    print("测试 Anthropic Claude Sonnet 4")
    print("="*60)

    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "请用一句话介绍你自己"}
            ]
        )

        print(f"✅ Anthropic API 连接成功!")
        print(f"✅ 模型: {response.model}")
        print(f"✅ 回复: {response.content[0].text}")
        print(f"✅ Token使用: {response.usage.input_tokens + response.usage.output_tokens}")
        return True

    except Exception as e:
        print(f"❌ Anthropic API 连接失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🔍 开始测试AI API连接...")

    openai_ok = await test_openai()
    anthropic_ok = await test_anthropic()

    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"OpenAI API: {'✅ 正常' if openai_ok else '❌ 失败'}")
    print(f"Anthropic API: {'✅ 正常' if anthropic_ok else '❌ 失败'}")

    if openai_ok and anthropic_ok:
        print("\n🎉 所有API连接正常! 可以开始使用PeakState AI功能了!")
        print("\n📝 后续步骤:")
        print("  1. 访问 http://localhost:8000/docs 查看完整API文档")
        print("  2. 配置数据库以启用完整功能")
        print("  3. 测试完整的对话流程")
    else:
        print("\n⚠️  部分API连接失败,请检查API密钥配置")


if __name__ == "__main__":
    asyncio.run(main())
