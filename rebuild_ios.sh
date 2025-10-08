#!/bin/bash

echo "🔄 完全重建 iOS 项目（不使用 CocoaPods）..."

cd /Users/apple/Desktop/PeakState/frontend

# 1. 完全删除旧的 iOS 项目
echo "🗑️  删除旧的 iOS 项目..."
rm -rf ios

# 2. 重新构建前端
echo "🏗️  重新构建前端..."
npm run build

# 3. 重新添加 iOS 平台
echo "📱 重新添加 iOS 平台..."
npx cap add ios

# 4. 复制 web 资源
echo "📋 复制 web 资源..."
npx cap copy ios

# 5. 打开新项目
echo "✅ 完成！正在打开 Xcode..."
open ios/App/App.xcodeproj

echo ""
echo "📝 接下来在 Xcode 中："
echo "1. 选择 TARGETS → App → Signing & Capabilities"
echo "2. 添加你的 Apple ID 账号"
echo "3. 选择你的 iPhone 设备"
echo "4. 点击运行 ▶️"
echo ""
