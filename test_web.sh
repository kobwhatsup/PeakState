#!/bin/bash

echo "🌐 启动 Web 测试服务器"
echo "================================================"
echo ""
echo "这将在浏览器中测试健康数据同步功能"
echo "使用模拟健康数据，功能与原生应用完全一致"
echo ""

# 获取 Mac IP 地址
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "📱 在 iPhone 上访问："
echo ""
echo "   http://$IP:5173"
echo ""
echo "================================================"
echo ""
echo "🚀 启动服务..."
echo ""

cd /Users/apple/Desktop/PeakState/frontend

# 启动开发服务器
npm run dev -- --host

echo ""
echo "服务已停止"
