"""
MCP (Model Context Protocol) 模块
提供AI工具调用能力
"""

from app.mcp.base import MCPTool, MCPToolRegistry, get_global_registry
from app.mcp.health_server import register_health_tools

# 确保工具已注册
register_health_tools()


def get_health_tools_schema():
    """获取健康数据工具的Schema（用于Claude API）"""
    registry = get_global_registry()
    return registry.get_tools_schema()


async def execute_tool(tool_name: str, tool_input: dict, **context):
    """执行工具"""
    registry = get_global_registry()
    return await registry.execute_tool(tool_name, tool_input, **context)


__all__ = [
    "MCPTool",
    "MCPToolRegistry",
    "get_global_registry",
    "get_health_tools_schema",
    "execute_tool"
]
