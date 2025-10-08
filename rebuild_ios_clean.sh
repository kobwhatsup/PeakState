#!/bin/bash

echo "🚀 完全重建 iOS 项目 - 不使用 CocoaPods"
echo "================================================"
echo ""

cd /Users/apple/Desktop/PeakState/frontend

# 1. 删除旧的 iOS 项目
echo "🗑️  第 1 步：删除旧的 iOS 项目..."
if [ -d "ios" ]; then
    rm -rf ios
    echo "   ✅ 旧项目已删除"
else
    echo "   ℹ️  没有旧项目需要删除"
fi
echo ""

# 2. 重新构建前端
echo "🏗️  第 2 步：重新构建前端..."
npm run build
if [ $? -eq 0 ]; then
    echo "   ✅ 前端构建成功"
else
    echo "   ❌ 前端构建失败"
    exit 1
fi
echo ""

# 3. 使用 Capacitor 重新添加 iOS 平台
echo "📱 第 3 步：添加 iOS 平台..."
npx cap add ios
if [ $? -eq 0 ]; then
    echo "   ✅ iOS 平台添加成功"
else
    echo "   ❌ iOS 平台添加失败"
    exit 1
fi
echo ""

# 4. 复制 web 资源
echo "📋 第 4 步：复制 web 资源..."
npx cap copy ios
if [ $? -eq 0 ]; then
    echo "   ✅ web 资源复制成功"
else
    echo "   ❌ web 资源复制失败"
    exit 1
fi
echo ""

# 5. 验证项目结构
echo "🔍 第 5 步：验证项目结构..."
if [ -f "ios/App/App.xcodeproj/project.pbxproj" ]; then
    echo "   ✅ Xcode 项目文件存在"
else
    echo "   ❌ Xcode 项目文件不存在"
    exit 1
fi
echo ""

echo "================================================"
echo "✅ iOS 项目重建完成！"
echo ""
echo "📝 接下来的步骤："
echo "1. 打开 Xcode（即将自动打开）"
echo "2. 在 Xcode 中："
echo "   • 选择 TARGETS → App → Signing & Capabilities"
echo "   • 勾选 'Automatically manage signing'"
echo "   • 添加你的 Apple ID 账号"
echo "   • 选择 Team"
echo "   • 如果 Bundle ID 冲突，修改为：com.yourname.peakstate"
echo "3. 连接你的 iPhone"
echo "4. 选择设备并点击 ▶️ 运行"
echo ""
echo "🎯 预期结果："
echo "   • 应用成功安装到 iPhone"
echo "   • 显示健康数据同步测试界面"
echo "   • 可以测试模拟健康数据同步"
echo ""
echo "正在打开 Xcode..."

sleep 2
open ios/App/App.xcodeproj

echo ""
echo "✨ 准备完成！请在 Xcode 中继续配置。"
