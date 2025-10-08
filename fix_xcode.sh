#!/bin/bash

echo "🔧 修复 Xcode 项目配置..."

cd /Users/apple/Desktop/PeakState/frontend

# 1. 清理旧的构建文件
echo "📦 清理旧的构建文件..."
rm -rf ios/App/build
rm -rf ios/App/DerivedData
rm -rf ios/App/Pods
rm -rf ios/App/Podfile.lock

# 2. 重新构建前端
echo "🏗️  重新构建前端..."
npm run build

# 3. 使用 Capacitor 更新 iOS 项目（不使用 pod install）
echo "📱 更新 iOS 项目..."
npx cap copy ios
npx cap update ios

# 4. 打开 Xcode 项目
echo "✅ 准备完成！正在打开 Xcode..."
open ios/App/App.xcodeproj

echo ""
echo "📋 接下来的步骤："
echo "1. 在 Xcode 中，点击 Product → Clean Build Folder (Cmd+Shift+K)"
echo "2. 配置 Signing & Capabilities（添加你的 Apple ID）"
echo "3. 选择你的 iPhone 设备"
echo "4. 点击运行按钮 ▶️"
echo ""
echo "如果还有错误，请截图给我！"
