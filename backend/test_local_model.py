"""
测试本地Phi-3.5模型集成
独立测试脚本，不依赖数据库连接
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.ai.local_models import get_local_model_manager


async def test_local_model():
    """测试本地模型加载和推理"""

    print("=" * 60)
    print("🧪 测试本地Phi-3.5模型")
    print("=" * 60)
    print()

    # 获取模型管理器
    manager = get_local_model_manager()

    # 测试1: 检查设备
    print(f"1️⃣ 设备检测: {manager.device}")
    print()

    # 测试2: 加载模型
    print("2️⃣ 加载模型中...")
    try:
        await manager.load_model()
        print(f"✅ 模型加载成功: {manager.model_name}")
        print()
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 测试3: 简单问答
    test_cases = [
        {
            "prompt": "你好，请简单介绍一下你自己。",
            "expected": "greeting response"
        },
        {
            "prompt": "什么是健康的睡眠时间？",
            "expected": "health advice"
        },
        {
            "prompt": "2 + 2 = ?",
            "expected": "math calculation"
        }
    ]

    print("3️⃣ 推理测试:")
    print()

    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}: {test['prompt']}")
        print("-" * 50)

        try:
            response = await manager.generate(
                prompt=test['prompt'],
                max_new_tokens=256,
                temperature=0.7
            )

            print(f"✅ 响应: {response[:200]}...")
            print()

        except Exception as e:
            print(f"❌ 推理失败: {e}")
            print()

    # 测试4: 性能统计
    print("4️⃣ 性能统计:")
    print("-" * 50)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_local_model())
