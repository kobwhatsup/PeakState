"""
MCP (Model Context Protocol) 工具基类
提供工具注册、Schema定义和执行框架
"""

import logging
from typing import Dict, Any, Callable, List, Optional, Awaitable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """
    MCP工具定义

    每个工具包含：
    - name: 工具名称（AI调用时使用）
    - description: 工具描述（帮助AI理解工具用途）
    - input_schema: 输入参数Schema（JSON Schema格式）
    - handler: 异步处理函数
    """

    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具功能描述")
    input_schema: Dict[str, Any] = Field(..., description="输入参数Schema")
    handler: Callable[..., Awaitable[Dict[str, Any]]] = Field(
        ...,
        description="异步处理函数"
    )

    model_config = {"arbitrary_types_allowed": True}


class MCPToolRegistry:
    """
    MCP工具注册表

    管理所有可用工具，提供：
    - 工具注册
    - Schema导出（Claude API格式）
    - 工具执行
    """

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        logger.info("🔧 MCPToolRegistry initialized")

    def register(self, tool: MCPTool) -> None:
        """
        注册工具

        Args:
            tool: MCP工具对象
        """
        self._tools[tool.name] = tool
        logger.info(f"✅ Registered tool: {tool.name}")

    def register_function(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[..., Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        便捷方法：直接注册函数为工具

        Args:
            name: 工具名称
            description: 工具描述
            input_schema: 输入Schema
            handler: 处理函数
        """
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
        self.register(tool)

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            工具对象或None
        """
        return self._tools.get(name)

    def get_all_tools(self) -> List[MCPTool]:
        """获取所有工具"""
        return list(self._tools.values())

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        导出Claude API兼容的tools格式

        Returns:
            工具Schema列表，格式：
            [
                {
                    "name": "tool_name",
                    "description": "tool description",
                    "input_schema": {
                        "type": "object",
                        "properties": {...},
                        "required": [...]
                    }
                },
                ...
            ]
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self._tools.values()
        ]

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        **context
    ) -> Dict[str, Any]:
        """
        执行工具

        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
            **context: 上下文参数（如db, user_id等）

        Returns:
            工具执行结果

        Raises:
            ValueError: 工具不存在
            Exception: 工具执行失败
        """
        tool = self.get_tool(tool_name)

        if not tool:
            error_msg = f"Tool '{tool_name}' not found"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        try:
            logger.info(f"🔧 Executing tool: {tool_name}")
            logger.debug(f"   Input: {tool_input}")

            # 执行工具处理函数
            result = await tool.handler(**tool_input, **context)

            logger.info(f"✅ Tool executed: {tool_name}")
            logger.debug(f"   Output: {result}")

            return result

        except Exception as e:
            logger.error(f"❌ Tool execution failed: {tool_name} - {e}", exc_info=True)
            raise

    def __len__(self) -> int:
        """工具数量"""
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<MCPToolRegistry(tools={len(self._tools)})>"


# 全局工具注册表单例
_global_registry: Optional[MCPToolRegistry] = None


def get_global_registry() -> MCPToolRegistry:
    """获取全局工具注册表"""
    global _global_registry

    if _global_registry is None:
        _global_registry = MCPToolRegistry()

    return _global_registry
