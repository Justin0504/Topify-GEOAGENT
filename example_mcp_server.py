#!/usr/bin/env python3
"""
MCP 服务器示例 - 天气查询工具
==============================

这是一个完整的 MCP (Model Context Protocol) 服务器示例。
MCP 是 Anthropic 开发的标准协议，用于让 AI 应用调用外部工具。

使用方式：
1. 安装依赖: pip install mcp requests
2. 在 Claude Desktop 配置文件中添加此服务器
3. 重启 Claude Desktop

Claude Desktop 配置示例 (claude_desktop_config.json):
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/example_mcp_server.py"],
      "env": {
        "WEATHER_API_KEY": "your-api-key"
      }
    }
  }
}
"""

# ============================================================
# 第 1 部分：导入依赖
# ============================================================

import os                          # 读取环境变量
import json                        # JSON 处理
import asyncio                     # 异步编程（MCP 要求）
from typing import Any             # 类型注解

# MCP SDK 核心组件
try:
    from mcp.server import Server                    # MCP 服务器类
    from mcp.server.stdio import stdio_server        # stdio 通信（与客户端通过管道通信）
    from mcp.types import Tool, TextContent          # 工具定义和返回类型
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("请安装 MCP SDK: pip install mcp")

# 用于实际 API 调用
import requests


# ============================================================
# 第 2 部分：配置
# ============================================================

# 从环境变量读取配置（Claude Desktop 会传递这些变量）
API_KEY = os.environ.get("WEATHER_API_KEY", "demo_key")
BASE_URL = "https://api.weatherapi.com/v1"


# ============================================================
# 第 3 部分：业务逻辑函数（与 MCP 无关的纯 Python 函数）
# ============================================================

def get_current_weather(city: str) -> dict:
    """
    获取当前天气（实际的业务逻辑）
    这部分代码与 MCP 协议无关，是纯粹的 Python 代码
    """
    try:
        # 模拟 API 调用（实际使用时替换为真实 API）
        # response = requests.get(f"{BASE_URL}/current.json", params={"key": API_KEY, "q": city})
        # return response.json()
        
        # 这里用模拟数据演示
        return {
            "city": city,
            "temperature": 22,
            "condition": "晴天",
            "humidity": 65,
            "wind": "东北风 3级"
        }
    except Exception as e:
        return {"error": str(e)}


def get_weather_forecast(city: str, days: int = 3) -> dict:
    """获取天气预报"""
    # 模拟数据
    return {
        "city": city,
        "forecast": [
            {"day": "今天", "high": 25, "low": 18, "condition": "晴"},
            {"day": "明天", "high": 23, "low": 17, "condition": "多云"},
            {"day": "后天", "high": 20, "low": 15, "condition": "小雨"},
        ][:days]
    }


# ============================================================
# 第 4 部分：MCP 服务器定义（核心部分）
# ============================================================

if MCP_AVAILABLE:
    
    # 4.1 创建 MCP 服务器实例
    # 参数是服务器名称，用于标识
    server = Server("weather-tool")
    
    
    # 4.2 定义工具列表（告诉 AI 有哪些工具可用）
    # 使用 @server.list_tools() 装饰器
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """
        返回所有可用工具的列表
        每个工具包含：name（名称）、description（描述）、inputSchema（参数定义）
        """
        return [
            # 工具 1：获取当前天气
            Tool(
                name="get_weather",                    # 工具名称（AI 调用时使用）
                description="获取指定城市的当前天气信息，包括温度、天气状况、湿度等",  # 描述（帮助 AI 理解何时使用）
                inputSchema={                          # JSON Schema 定义参数
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，如 '北京'、'上海'、'New York'"
                        }
                    },
                    "required": ["city"]               # 必填参数
                }
            ),
            
            # 工具 2：获取天气预报
            Tool(
                name="get_forecast",
                description="获取指定城市未来几天的天气预报",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        },
                        "days": {
                            "type": "integer",
                            "description": "预报天数（1-7天）",
                            "default": 3
                        }
                    },
                    "required": ["city"]
                }
            )
        ]
    
    
    # 4.3 定义工具调用处理（AI 调用工具时执行）
    # 使用 @server.call_tool() 装饰器
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """
        处理工具调用请求
        
        参数:
            name: 工具名称（如 "get_weather"）
            arguments: 工具参数（如 {"city": "北京"}）
        
        返回:
            TextContent 列表（返回给 AI 的结果）
        """
        
        # 根据工具名称分发处理
        if name == "get_weather":
            # 调用业务逻辑函数
            city = arguments.get("city", "北京")
            result = get_current_weather(city)
            
            # 格式化返回结果
            if "error" in result:
                text = f"❌ 获取天气失败: {result['error']}"
            else:
                text = f"""🌤️ {result['city']} 当前天气

🌡️ 温度: {result['temperature']}°C
☁️ 天气: {result['condition']}
💧 湿度: {result['humidity']}%
🌬️ 风力: {result['wind']}
"""
            
        elif name == "get_forecast":
            city = arguments.get("city", "北京")
            days = arguments.get("days", 3)
            result = get_weather_forecast(city, days)
            
            # 格式化预报结果
            forecast_lines = []
            for day in result["forecast"]:
                forecast_lines.append(
                    f"  • {day['day']}: {day['low']}°C ~ {day['high']}°C, {day['condition']}"
                )
            
            text = f"""📅 {result['city']} 天气预报

{chr(10).join(forecast_lines)}
"""
            
        else:
            text = f"❌ 未知工具: {name}"
        
        # 返回 TextContent（MCP 协议要求的格式）
        return [TextContent(type="text", text=text)]


# ============================================================
# 第 5 部分：MCP 服务器启动（入口点）
# ============================================================

async def main():
    """
    启动 MCP 服务器
    
    stdio_server() 创建标准输入/输出通信通道
    这是 MCP 协议的通信方式：通过 stdin/stdout 与客户端交换 JSON-RPC 消息
    """
    if not MCP_AVAILABLE:
        print("MCP SDK 未安装，无法启动服务器")
        return
    
    # 使用 stdio 通信（Claude Desktop 通过管道与此服务器通信）
    async with stdio_server() as (read_stream, write_stream):
        # 运行服务器，监听请求
        await server.run(
            read_stream,                              # 读取来自客户端的请求
            write_stream,                             # 发送响应给客户端
            server.create_initialization_options()    # 初始化选项
        )


# ============================================================
# 第 6 部分：独立运行测试（不依赖 MCP 客户端）
# ============================================================

def run_standalone_test():
    """
    独立运行模式，用于测试业务逻辑
    不需要 Claude Desktop，直接在命令行测试
    """
    print("=" * 50)
    print("天气工具 - 独立测试模式")
    print("=" * 50)
    
    # 测试获取当前天气
    print("\n📍 测试: 获取北京天气")
    result = get_current_weather("北京")
    print(f"   结果: {result}")
    
    # 测试获取天气预报
    print("\n📍 测试: 获取上海3天预报")
    result = get_weather_forecast("上海", 3)
    print(f"   结果: {result}")
    
    print("\n✅ 测试完成!")


# ============================================================
# 第 7 部分：程序入口
# ============================================================

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # 如果 MCP SDK 可用，启动 MCP 服务器
        asyncio.run(main())
    else:
        # 否则运行独立测试
        run_standalone_test()

