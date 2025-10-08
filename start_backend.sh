#!/bin/bash

echo "🔥 启动 PeakState 后端服务器"
echo "=================================="
echo ""
echo "📊 后端服务地址："
echo "   http://0.0.0.0:8000"
echo "   http://localhost:8000"
echo ""
echo "📖 API 文档："
echo "   http://localhost:8000/docs"
echo ""
echo "=================================="
echo ""
echo "🚀 正在启动..."
echo ""

cd /Users/apple/Desktop/PeakState/backend

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 已激活虚拟环境"
fi

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0
