#!/bin/bash

echo "🔧 修复 Capacitor 框架链接问题..."

cd /Users/apple/Desktop/PeakState/frontend

# 1. 清理所有构建文件
echo "🧹 清理构建文件..."
rm -rf ios/App/build
rm -rf ios/App/DerivedData
rm -rf ios/App/Pods
rm -rf ios/App/Podfile.lock

# 2. 重新安装 Capacitor
echo "📦 重新安装 Capacitor..."
npm install @capacitor/core @capacitor/ios @capacitor/cli

# 3. 重新构建前端
echo "🏗️  构建前端..."
npm run build

# 4. 完全重新创建 iOS 平台
echo "📱 重新创建 iOS 平台..."
npx cap copy ios

# 5. 尝试同步（这会自动添加框架）
echo "🔄 同步 Capacitor..."
npx cap sync ios 2>/dev/null || true

echo ""
echo "✅ 修复完成！"
echo ""
echo "现在请："
echo "1. 打开 Xcode: open ios/App/App.xcodeproj"
echo "2. Product → Clean Build Folder (Cmd+Shift+K)"
echo "3. 尝试运行"
echo ""

# 打开 Xcode
open ios/App/App.xcodeproj
