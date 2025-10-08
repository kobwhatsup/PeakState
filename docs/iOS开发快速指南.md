# 🍎 PeakState iOS 开发快速指南

## 📍 项目位置

```bash
/Users/apple/Desktop/PeakState/frontend/ios/App/App.xcworkspace
```

**⚠️ 重要：永远打开 `.xcworkspace` 文件，不要打开 `.xcodeproj`**

---

## 🚀 每日开发流程

### 方式1: 纯 iOS 开发（无需终端）

```bash
1. 打开 Xcode.xcworkspace
2. 选择模拟器（iPhone 17 Pro）
3. 点击 ▶️ 运行
4. 在模拟器中测试
```

### 方式2: React + iOS 同步开发（推荐）

**终端窗口1 - 运行 Vite 开发服务器：**
```bash
cd /Users/apple/Desktop/PeakState/frontend
npm run dev
```

**每次修改 React 代码后：**
```bash
npm run build:mobile
```

**Xcode：**
```
按 ⌘ + R 重新运行应用
```

---

## 🎯 常用 Xcode 快捷键

### 基础操作
| 功能 | 快捷键 | 说明 |
|-----|-------|------|
| 运行应用 | `⌘ + R` | 编译并在模拟器运行 |
| 停止应用 | `⌘ + .` | 停止当前运行 |
| 清理编译 | `⌘ + Shift + K` | 清除缓存重新编译 |
| 完全清理 | `⌘ + Shift + Option + K` | 深度清理 |

### 界面控制
| 功能 | 快捷键 |
|-----|-------|
| 显示/隐藏导航器 | `⌘ + 0` |
| 显示/隐藏检查器 | `⌘ + Option + 0` |
| 显示/隐藏调试区 | `⌘ + Shift + Y` |
| 全屏编辑器 | `⌘ + Shift + Enter` |

### 搜索
| 功能 | 快捷键 |
|-----|-------|
| 快速打开文件 | `⌘ + Shift + O` |
| 全局搜索 | `⌘ + Shift + F` |
| 当前文件搜索 | `⌘ + F` |

### 模拟器控制
| 功能 | 快捷键 |
|-----|-------|
| 主屏幕 | `⌘ + H` |
| 锁屏 | `⌘ + L` |
| 旋转左 | `⌘ + ←` |
| 旋转右 | `⌘ + →` |
| 截图 | `⌘ + S` |
| 摇晃设备 | `⌘ + Ctrl + Z` |

---

## 🔧 常见问题快速解决

### 问题1: Build Failed（编译失败）

**快速修复（按顺序尝试）：**

```bash
# 方法1: Xcode 清理
⌘ + Shift + K (Clean Build Folder)

# 方法2: 删除派生数据
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 方法3: 重新安装 node_modules
cd /Users/apple/Desktop/PeakState/frontend
rm -rf node_modules
npm install

# 方法4: 重新构建
npm run build:mobile
```

### 问题2: 模拟器无法启动

```bash
# 关闭所有模拟器
killall Simulator

# 重新打开 Xcode
# 选择 Xcode → Developer Tools → Simulator
# 手动启动模拟器
```

### 问题3: Signing 错误

**在 Xcode 中：**
1. 选择项目（蓝色图标 App）
2. 点击 **Signing & Capabilities**
3. 取消勾选 "Automatically manage signing"
4. 重新勾选
5. 重新选择 Team

### 问题4: Web 内容未更新

```bash
# 重新构建 Web 资源
cd /Users/apple/Desktop/PeakState/frontend
npm run build

# 同步到 iOS
npx cap sync ios

# 在 Xcode 清理
⌘ + Shift + K

# 重新运行
⌘ + R
```

---

## 📱 模拟器使用技巧

### 切换不同设备

1. 点击 Xcode 顶部设备选择器
2. 选择：
   - **iPhone 17 Pro** - 最新旗舰（推荐）
   - **iPhone Air** - 轻薄版
   - **iPad Pro 11-inch** - 测试平板布局

### 模拟器设置

**打开设置 App：**
```
模拟器 → Home → Settings
```

**常用设置：**
- **Appearance** → 切换深色/浅色模式
- **Developer** → UI Automation（可选）

### 测试不同场景

**测试竖屏/横屏：**
```
⌘ + ← 或 ⌘ + →
```

**测试网络状态：**
```
Settings → Developer → Network Link Conditioner
```

---

## 🎨 自定义应用外观

### 修改应用名称

**文件位置：** `ios/App/App/Info.plist`

找到这行并修改：
```xml
<key>CFBundleDisplayName</key>
<string>PeakState</string>  ← 改为"峰值状态"
```

### 修改启动画面颜色

**文件位置：** `frontend/capacitor.config.ts`

```typescript
SplashScreen: {
  backgroundColor: '#2B69B6',  ← 修改这里的颜色
  launchShowDuration: 2000,
},
```

### 修改状态栏样式

**文件位置：** `frontend/capacitor.config.ts`

```typescript
StatusBar: {
  style: 'LIGHT',  // 'LIGHT' 或 'DARK'
  backgroundColor: '#2B69B6',
},
```

---

## 📊 查看应用日志

### 在 Xcode 中查看

1. 按 `⌘ + Shift + Y` 打开调试区
2. 选择 **Console** 标签
3. 查看实时日志输出

### 过滤日志

在控制台底部的搜索框中输入：
```
[Capacitor]  ← 查看 Capacitor 相关日志
[DeviceFrame]  ← 查看设备预览日志
App init  ← 查看应用初始化日志
```

### 清空日志

右键点击控制台 → **Clear Console**

---

## 🔄 Git 版本控制建议

### 应该提交的文件

```
✅ ios/App/App.xcodeproj/
✅ ios/App/App/Info.plist
✅ ios/App/Podfile
✅ capacitor.config.ts
```

### 不要提交的文件（已在 .gitignore）

```
❌ ios/App/Pods/
❌ ios/App/App.xcworkspace/xcuserdata/
❌ ios/App/DerivedData/
❌ dist/
```

---

## 📚 学习资源

### 官方文档
- [Capacitor iOS 文档](https://capacitorjs.com/docs/ios)
- [Apple Developer 文档](https://developer.apple.com/documentation/)
- [Xcode 帮助](https://help.apple.com/xcode/)

### 视频教程
- 搜索："Xcode 入门教程"
- 搜索："iOS 模拟器使用"
- 搜索："Capacitor iOS 开发"

### 社区
- [Capacitor Discord](https://discord.gg/capacitor)
- [Stack Overflow - Xcode](https://stackoverflow.com/questions/tagged/xcode)
- [V2EX iOS 板块](https://v2ex.com/go/apple)

---

## ✅ 每日开发检查清单

**开始工作前：**
- [ ] 拉取最新代码 (`git pull`)
- [ ] 安装依赖 (`npm install`)
- [ ] 启动开发服务器 (`npm run dev`)

**开发过程中：**
- [ ] 修改 React 代码
- [ ] 保存文件
- [ ] 构建并同步 (`npm run build:mobile`)
- [ ] 在 Xcode 运行测试 (`⌘ + R`)

**完成工作后：**
- [ ] 测试所有功能正常
- [ ] 提交代码 (`git add` + `git commit`)
- [ ] 推送到远程 (`git push`)

---

## 🆘 需要帮助？

**遇到问题时的步骤：**

1. **查看错误信息**
   - 打开 Xcode 调试区 (`⌘ + Shift + Y`)
   - 复制完整错误信息

2. **尝试快速修复**
   - 清理编译 (`⌘ + Shift + K`)
   - 重启 Xcode
   - 重启模拟器

3. **搜索解决方案**
   - 复制错误信息到 Google
   - 添加关键词 "Xcode" 或 "Capacitor iOS"

4. **寻求帮助**
   - Stack Overflow（英文）
   - V2EX（中文）
   - 项目 Issues

---

## 🎯 下一步建议

### 立即可以做的
1. ✅ 熟悉 Xcode 界面和快捷键
2. ✅ 在不同模拟器上测试应用
3. ✅ 修改启动画面颜色
4. ✅ 查看应用日志输出

### 进阶学习
1. 📱 自定义应用图标
2. 🎨 优化启动画面设计
3. 🔔 添加推送通知功能
4. 📸 集成相机功能

---

**最后更新：** 2025年10月7日
**适用版本：** Xcode 26.0.1, Capacitor 7.4.3
