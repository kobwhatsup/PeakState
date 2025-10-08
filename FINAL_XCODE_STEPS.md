# 🎉 完美解决！现在可以在 Xcode 中测试了

## ✅ 已完成的工作

1. ✅ 安装了 CocoaPods 依赖管理器
2. ✅ 重新创建了干净的 iOS 项目
3. ✅ 安装了所有必需的 Capacitor 插件（包括 HealthKit）
4. ✅ 添加了健康数据访问权限

---

## 📱 在 Xcode 中打开并运行（重要！）

### ⚠️ 关键步骤：打开正确的文件

**必须打开 `.xcworkspace` 文件，不是 `.xcodeproj` 文件！**

1. **双击打开这个文件：**
   ```
   /Users/apple/Desktop/PeakState/frontend/ios/App/App.xcworkspace
   ```

   **不要打开：** ~~App.xcodeproj~~（打开这个会出错）

2. **为什么？**
   - 使用 CocoaPods 后，必须使用 `.xcworkspace`
   - 这个文件包含了主项目和 Pods 项目
   - `.xcodeproj` 单独打开会缺少依赖

---

## 🚀 运行步骤

1. **打开 workspace 后，选择目标设备：**
   - 点击 Xcode 顶部工具栏的设备选择器
   - 选择任意 iPhone 模拟器（推荐 iPhone 15 Pro）

2. **点击播放按钮 ▶️**
   - 第一次构建需要 1-2 分钟
   - 等待编译完成

3. **App 启动后：**
   - 会直接显示"健康数据同步"界面
   - 点击"请求权限"按钮
   - 会同步模拟的健康数据（睡眠、步数、心率等）

---

## 📊 模拟数据说明

因为在模拟器中运行，使用的是模拟健康数据：

- **睡眠时长：** 6.5-8.5 小时/天
- **步数：** 5,000-10,000 步/天
- **心率：** 60-100 bpm
- **活动消耗：** 200-500 卡路里/天

模拟数据会自动上传到后端，可以在数据库中查看。

---

## 🍎 在真实 iPhone 上测试（可选）

如果想在真实 iPhone 上测试真实的 HealthKit 数据：

1. **配置签名：**
   - 在 Xcode 中，选择项目 → TARGETS → App
   - 点击 "Signing & Capabilities" 标签
   - Team: 选择你的 Apple ID
   - Bundle Identifier: 保持默认或修改为唯一的 ID

2. **连接 iPhone：**
   - 用数据线连接 iPhone 到 Mac
   - 在设备选择器中选择你的 iPhone
   - 点击运行

3. **信任开发者：**
   - iPhone 上会提示"不受信任的开发者"
   - 设置 → 通用 → VPN与设备管理 → 信任你的 Apple ID

4. **授权健康数据：**
   - App 会请求访问健康数据
   - 在弹出的对话框中允许读取睡眠、步数、心率等数据
   - 会读取你的真实 HealthKit 数据！

---

## 🔧 如果遇到错误

### 错误："No such module 'Capacitor'"
**原因：** 打开了 `.xcodeproj` 而不是 `.xcworkspace`
**解决：** 关闭 Xcode，打开 `App.xcworkspace`

### 错误："The sandbox is not in sync with the Podfile.lock"
**原因：** Pod 依赖没有正确安装
**解决：**
```bash
cd /Users/apple/Desktop/PeakState/frontend/ios/App
export LANG=en_US.UTF-8
pod install
```
然后重新打开 `App.xcworkspace`

### 错误："Signing for 'App' requires a development team"
**原因：** 没有配置开发者签名
**解决：** 在 Signing & Capabilities 中选择你的 Apple ID

---

## ✨ 成功标志

看到这些说明构建成功：

1. ✅ Build Succeeded（构建成功）
2. ✅ 模拟器中 App 正常启动
3. ✅ 显示健康数据同步界面
4. ✅ 可以点击"请求权限"并看到模拟数据

---

## 📝 下一步

测试完成后，如果需要：

1. **恢复正常 App 流程：** 告诉我，我会修改代码让 App 从引导界面开始
2. **查看上传的数据：** 检查后端数据库中的 `environment_data` 表
3. **添加更多功能：** 继续开发其他健康相关功能

---

**现在可以双击打开 `App.xcworkspace` 并点击播放按钮了！** 🚀
