# 📱 iPhone 健康数据同步测试指南

## 🔧 第一步：安装 CocoaPods（必需）

当前问题：Xcode workspace 文件为空是因为缺少 CocoaPods 依赖。

### 选项A：使用 gem 安装（推荐）

打开 Mac 的"终端"应用，执行：

```bash
# 安装 CocoaPods
sudo gem install cocoapods
```

输入你的 Mac 密码（输入时不会显示），按回车。

### 选项B：使用 Homebrew 安装

如果选项A失败，使用 Homebrew：

```bash
# 先安装 Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 使用 Homebrew 安装 CocoaPods
brew install cocoapods
```

---

## 🔨 第二步：安装项目依赖

CocoaPods 安装完成后，在终端中执行：

```bash
# 进入 iOS 项目目录
cd /Users/apple/Desktop/PeakState/frontend/ios/App

# 安装依赖（会下载健康数据插件等）
pod install
```

你会看到类似输出：
```
Analyzing dependencies
Downloading dependencies
Installing Capacitor (7.0.0)
Installing CapacitorCordova (7.0.0)
Installing capacitor-health (7.0.0)
...
Pod installation complete!
```

---

## 📂 第三步：打开正确的 Xcode 项目

依赖安装完成后：

```bash
# 打开 workspace（不是 xcodeproj）
open /Users/apple/Desktop/PeakState/frontend/ios/App/App.xcworkspace
```

⚠️ **重要：** 必须打开 `.xcworkspace` 文件，不要打开 `.xcodeproj`！

---

## ⚙️ 第四步：配置 Xcode 签名

在 Xcode 中：

### 4.1 选择项目
1. 点击左侧项目导航器中最顶部的 **App**（蓝色图标）
2. 在中间区域选择 **TARGETS** 下的 **App**
3. 点击顶部的 **Signing & Capabilities** 标签

### 4.2 配置 Team
1. 找到 **Team** 下拉菜单（在 "Automatically manage signing" 下方）
2. 点击下拉菜单：
   - 如果有 Apple 开发者账号，选择你的 Team
   - 如果没有，点击 **Add Account...**
   - 使用你的 Apple ID 登录（免费账号也可以用于开发）
3. 登录后选择你的个人 Team

### 4.3 检查 Bundle Identifier
- 确保 **Bundle Identifier** 是唯一的
- 如果显示红色错误，修改为：`com.你的名字.peakstate`
- 例如：`com.zhang.peakstate`

### 4.4 添加 HealthKit Capability
1. 点击 **+ Capability** 按钮（在 Signing 区域上方）
2. 搜索并添加 **HealthKit**
3. 确认 HealthKit 已添加到列表中

---

## 📱 第五步：连接 iPhone

### 5.1 物理连接
1. 用数据线连接 iPhone 到 Mac
2. iPhone 上如果弹出"信任此电脑"，点击**信任**
3. 输入 iPhone 密码

### 5.2 选择设备
1. 在 Xcode 顶部工具栏，点击设备选择器（显示 "Any iOS Device"）
2. 从列表中选择你的 iPhone 设备名称

---

## 🚀 第六步：构建并运行

### 6.1 首次构建
1. 点击 Xcode 左上角的 **▶️ 播放按钮**（或按 `Cmd + R`）
2. 等待构建完成（首次可能需要 2-3 分钟）

### 6.2 信任开发者证书（首次必需）
构建完成后，iPhone 上会显示应用图标，但点击后提示"未受信任的开发者"：

1. 打开 iPhone 的 **设置**
2. 进入 **通用 → VPN与设备管理**（或 **设备管理**）
3. 找到你的开发者证书（通常是你的 Apple ID）
4. 点击 **信任 "你的Apple ID"**
5. 在弹窗中再次点击 **信任**

### 6.3 启动应用
1. 返回 iPhone 主屏幕
2. 找到 **PeakState** 应用图标
3. 点击启动

---

## 🏥 第七步：测试健康数据同步

### 7.1 授权健康数据
应用启动后：

1. 看到"健康数据同步测试"页面
2. 点击蓝色的 **"连接Apple Health"** 按钮
3. iOS 弹出权限窗口，向下滚动查看所有选项
4. **重要：** 确保以下数据类型都被允许读取（打开开关）：
   - ✅ 睡眠分析
   - ✅ 步数
   - ✅ 心率
   - ✅ 活动能量
   - ✅ 距离
5. 点击右上角 **"允许"**

### 7.2 查看同步结果
授权成功后：

1. 卡片标题变为 **"健康数据已连接"** ✅
2. 自动开始同步最近 7 天的健康数据
3. 几秒后显示同步结果：
   ```
   ✅ 成功同步 XX 条健康数据记录
   睡眠: X | 步数: X | 心率: X | 活动: X
   ```

### 7.3 手动同步
点击 **"立即同步健康数据"** 按钮可手动触发同步

---

## 🐛 常见问题排查

### 问题1：Xcode workspace 打开后一片空白
**原因：** 缺少 CocoaPods 依赖
**解决：** 按照第一步和第二步安装 CocoaPods 并运行 `pod install`

### 问题2：构建失败 - "No code signing identities found"
**原因：** 没有配置签名
**解决：** 在 Signing & Capabilities 中添加 Apple ID 账号

### 问题3：iPhone 上提示"未受信任的开发者"
**原因：** 首次安装需要手动信任
**解决：** 设置 → 通用 → VPN与设备管理 → 信任开发者

### 问题4：权限窗口没有弹出
**原因：** 健康应用未设置或权限被拒绝
**解决：**
- 打开 iPhone 的"健康"应用，完成初始设置
- 检查：健康 → 右上角头像 → 隐私 → 应用 → PeakState

### 问题5：同步失败，显示网络错误
**原因：** 后端服务未启动或网络不通
**解决：**
- 确保后端正在运行：`uvicorn app.main:app --reload`
- iPhone 和 Mac 在同一 WiFi 网络
- 检查防火墙设置

### 问题6：没有健康数据可同步
**原因：** iPhone 健康应用中没有数据
**解决：**
- 打开"健康"应用手动添加测试数据
- 或者戴着 Apple Watch 走几步路
- 或者使用其他健康应用产生数据

---

## 🔍 查看调试日志

### 在 Xcode 中查看
1. 点击 Xcode 底部的 **Show/Hide Debug Area** 按钮（或按 `Cmd + Shift + Y`）
2. 在控制台中查看日志输出：
   ```
   健康数据权限: { granted: true }
   同步睡眠数据: 找到 X 条记录
   同步步数数据: 找到 X 条记录
   ✅ 健康数据同步成功
   ```

### 在 iPhone 上查看
1. iPhone 连接 Mac
2. 打开 Mac 的 **控制台** 应用（Console.app）
3. 左侧选择你的 iPhone 设备
4. 搜索 "PeakState" 查看应用日志

---

## ✅ 测试完成清单

- [ ] CocoaPods 已安装
- [ ] `pod install` 执行成功
- [ ] Xcode workspace 可以正常打开
- [ ] 签名配置完成
- [ ] HealthKit capability 已添加
- [ ] 应用成功安装到 iPhone
- [ ] 开发者证书已信任
- [ ] 健康数据权限已授予
- [ ] 同步功能正常工作
- [ ] 可以看到同步的数据记录数

---

## 🔄 测试完成后恢复正常流程

编辑文件：`/Users/apple/Desktop/PeakState/frontend/src/App.tsx`

找到第 19 行，将：
```typescript
const [appState, setAppState] = useState<AppState>("healthSync");
const [isLoading, setIsLoading] = useState(false);
```

改回：
```typescript
const [appState, setAppState] = useState<AppState>("onboarding");
const [isLoading, setIsLoading] = useState(true);
```

然后重新构建：
```bash
cd /Users/apple/Desktop/PeakState/frontend
npm run build
npx cap sync ios
```

在 Xcode 中重新运行即可。

---

## 📞 需要帮助？

如果遇到任何问题：
1. 查看上面的"常见问题排查"部分
2. 检查 Xcode 控制台的错误信息
3. 确保后端服务正在运行
4. 检查网络连接

---

## 🎯 下一步开发建议

测试成功后，可以继续开发：

1. **集成到设置页面**
   - 将健康同步功能添加到用户设置
   - 显示上次同步时间
   - 提供手动同步按钮

2. **后台自动同步**
   - 实现每日自动同步
   - 使用 iOS Background Tasks API
   - 在应用启动时检查并同步

3. **数据展示**
   - 在主界面显示健康数据摘要
   - 创建健康数据图表和趋势
   - 结合 AI 提供个性化建议

4. **更多数据类型**
   - 体重、血压
   - 营养数据
   - 运动记录
   - 正念时长

祝测试顺利！🚀
