"""
MCP工具输入输出Schema定义
使用JSON Schema格式，兼容Claude API
"""

from typing import Dict, Any


# ============ 健康数据工具Schema ============

READ_SLEEP_DATA_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "days": {
            "type": "integer",
            "description": "查询天数，默认7天",
            "minimum": 1,
            "maximum": 90,
            "default": 7
        }
    },
    "required": []
}

READ_HRV_DATA_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "days": {
            "type": "integer",
            "description": "查询天数，默认7天",
            "minimum": 1,
            "maximum": 90,
            "default": 7
        }
    },
    "required": []
}

READ_ACTIVITY_SUMMARY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "date": {
            "type": "string",
            "description": "查询日期，格式YYYY-MM-DD，默认today",
            "default": "today",
            "pattern": "^(today|yesterday|\\d{4}-\\d{2}-\\d{2})$"
        }
    },
    "required": []
}

ANALYZE_ENERGY_TREND_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "days": {
            "type": "integer",
            "description": "分析天数，默认7天",
            "minimum": 1,
            "maximum": 90,
            "default": 7
        }
    },
    "required": []
}


# ============ 日历工具Schema (Week 1 Day 5) ============

GET_TODAY_SCHEDULE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "include_past": {
            "type": "boolean",
            "description": "是否包含已过去的事件",
            "default": False
        }
    },
    "required": []
}

ANALYZE_WORKLOAD_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "days": {
            "type": "integer",
            "description": "分析天数，默认7天",
            "minimum": 1,
            "maximum": 30,
            "default": 7
        }
    },
    "required": []
}

SUGGEST_REST_TIME_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "date": {
            "type": "string",
            "description": "建议日期，格式YYYY-MM-DD，默认today",
            "default": "today",
            "pattern": "^(today|tomorrow|\\d{4}-\\d{2}-\\d{2})$"
        },
        "duration_minutes": {
            "type": "integer",
            "description": "休息时长（分钟），默认15分钟",
            "minimum": 5,
            "maximum": 120,
            "default": 15
        }
    },
    "required": []
}
