#!/usr/bin/env python3
"""
测试FastAPI应用加载
"""

try:
    print("正在导入FastAPI应用...")
    from app.main import app

    print("✅ FastAPI应用加载成功!")
    print(f"✅ 应用名称: {app.title}")
    print(f"✅ 总路由数: {len(app.routes)}")

    # 列出所有API路由
    print("\n📋 已注册的API端点:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ','.join(route.methods)
            print(f"  {methods:10s} {route.path}")

    print("\n✅ 应用已准备就绪,可以启动服务器!")
    print("\n启动命令:")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

except Exception as e:
    print(f"❌ 应用加载失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
