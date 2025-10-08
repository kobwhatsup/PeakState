"""
测试MCP工具注册和Schema导出
"""

import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def test_tool_registry():
    """测试工具注册表"""
    from app.mcp.base import get_global_registry

    registry = get_global_registry()

    print("=" * 60)
    print("🔧 MCP工具注册表测试")
    print("=" * 60)
    print()

    # 1. 检查工具数量
    print(f"1️⃣ 已注册工具数量: {len(registry)}")
    print()

    # 2. 列出所有工具
    print("2️⃣ 工具列表:")
    for tool in registry.get_all_tools():
        print(f"   - {tool.name}: {tool.description[:50]}...")
    print()

    # 3. 导出Claude API格式
    print("3️⃣ Claude API格式 (tools schema):")
    tools_schema = registry.get_tools_schema()

    for i, tool in enumerate(tools_schema, 1):
        print(f"\n   Tool {i}: {tool['name']}")
        print(f"   Description: {tool['description'][:100]}...")
        print(f"   Input schema keys: {list(tool['input_schema']['properties'].keys())}")

    print()
    print("=" * 60)
    print("✅ 工具注册表测试完成")
    print("=" * 60)

    return tools_schema


def test_tools_schema_export():
    """测试通过__init__.py导出的工具Schema"""
    from app.mcp import get_health_tools_schema

    print()
    print("=" * 60)
    print("📤 测试工具Schema导出")
    print("=" * 60)
    print()

    tools = get_health_tools_schema()

    print(f"导出的工具数量: {len(tools)}")
    print()

    # 打印完整Schema (格式化)
    print("完整Schema (JSON格式):")
    print(json.dumps(tools, indent=2, ensure_ascii=False)[:1000])
    print("...")

    print()
    print("✅ Schema导出成功")

    return tools


if __name__ == "__main__":
    # 运行测试
    test_tool_registry()
    test_tools_schema_export()

    print()
    print("🎉 所有测试通过！MCP工具已成功注册并可供Claude API使用。")
