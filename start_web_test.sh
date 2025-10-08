#!/bin/bash

echo "🌐 启动 PeakState Web 测试服务器"
echo "=================================="
echo ""
echo "📱 你的 Mac IP 地址："
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo ""
echo "   http://$IP:5173"
echo ""
echo "=================================="
echo ""
echo "📝 请按以下步骤操作："
echo ""
echo "1. 在 iPhone Safari 浏览器中访问上面的地址"
echo "2. 确保 iPhone 和 Mac 在同一 WiFi 网络"
echo "3. 点击 '连接Apple Health' 按钮测试功能"
echo ""
echo "=================================="
echo ""
echo "⚠️  注意："
echo "   - 需要另开一个终端启动后端服务"
echo "   - 后端命令："
echo "     cd /Users/apple/Desktop/PeakState/backend"
echo "     uvicorn app.main:app --reload --host 0.0.0.0"
echo ""
echo "=================================="
echo ""
echo "🚀 正在启动前端服务器..."
echo ""

cd /Users/apple/Desktop/PeakState/frontend
npm run dev -- --host
