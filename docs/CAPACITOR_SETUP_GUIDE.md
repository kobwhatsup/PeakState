# Capacitor 移动APP打包指南

本指南将帮助您将PeakState Web应用打包成iOS和Android原生APP，并上架到App Store和Google Play。

## 📱 为什么选择Capacitor？

- ✅ **零重构**：直接使用现有React代码，无需重写
- ✅ **跨平台**：一套代码同时生成iOS和Android APP
- ✅ **原生功能**：访问相机、推送通知、健康数据API
- ✅ **真机调试**：支持Live Reload，在真机上实时调试
- ✅ **快速上架**：几小时内可生成安装包

## 🚀 第一步：安装Capacitor

### 1.1 安装核心依赖

```bash
cd /Users/apple/Desktop/PeakState/frontend

# 安装Capacitor核心库
npm install @capacitor/core @capacitor/cli

# 初始化Capacitor配置
npx cap init
```

**配置信息：**
- App name: `PeakState`
- App ID (包名): `com.peakstate.app` (建议使用反向域名)
- Web asset directory: `dist`

### 1.2 安装平台插件

```bash
# iOS平台
npm install @capacitor/ios

# Android平台
npm install @capacitor/android
```

## 📦 第二步：配置构建

### 2.1 更新package.json

在`frontend/package.json`中添加构建脚本：

```json
{
  "scripts": {
    "build": "tsc && vite build",
    "cap:ios": "npm run build && npx cap sync ios && npx cap open ios",
    "cap:android": "npm run build && npx cap sync android && npx cap open android",
    "cap:sync": "npm run build && npx cap sync"
  }
}
```

### 2.2 配置Vite构建路径

确保`vite.config.ts`中的base配置正确：

```typescript
export default defineConfig({
  base: './', // 使用相对路径，适配移动端
  // ... 其他配置
})
```

## 📱 第三步：添加平台

### 3.1 添加iOS平台

```bash
npx cap add ios
```

这将创建`ios/`目录，包含Xcode项目文件。

**系统要求：**
- macOS
- Xcode 14+（从Mac App Store下载）
- CocoaPods（运行`sudo gem install cocoapods`）

### 3.2 添加Android平台

```bash
npx cap add android
```

这将创建`android/`目录，包含Android Studio项目文件。

**系统要求：**
- Android Studio（从[官网](https://developer.android.com/studio)下载）
- Java JDK 11+

## 🔨 第四步：首次构建

### 4.1 构建Web资源

```bash
npm run build
```

### 4.2 同步到原生项目

```bash
npx cap sync
```

这会：
1. 复制`dist/`目录到原生项目
2. 安装原生插件
3. 更新配置文件

## 📲 第五步：真机/模拟器调试

### 5.1 iOS调试

```bash
# 打开Xcode
npx cap open ios
```

在Xcode中：
1. 选择模拟器或连接iPhone
2. 点击▶️运行按钮
3. 应用会自动安装并启动

**真机调试需要：**
- Apple开发者账号（免费账号也可以，但每7天需要重新签名）
- 在Xcode中配置Team签名

### 5.2 Android调试

```bash
# 打开Android Studio
npx cap open android
```

在Android Studio中：
1. 等待Gradle同步完成
2. 选择模拟器或连接Android手机
3. 点击▶️运行按钮

**真机调试需要：**
- 在手机设置中启用"开发者选项"
- 启用"USB调试"

## 🔌 第六步：添加原生功能（可选）

### 6.1 健康数据集成

```bash
# iOS HealthKit
npm install @capacitor-community/health
```

### 6.2 推送通知

```bash
npm install @capacitor/push-notifications
```

### 6.3 本地存储

```bash
npm install @capacitor/preferences
```

### 6.4 状态栏样式

```bash
npm install @capacitor/status-bar
```

在`App.tsx`中使用：

```typescript
import { StatusBar, Style } from '@capacitor/status-bar';

useEffect(() => {
  // 设置状态栏为浅色主题
  StatusBar.setStyle({ style: Style.Light });
}, []);
```

## 🎨 第七步：配置APP图标和启动屏

### 7.1 准备资源

**APP图标：**
- 尺寸：1024x1024px
- 格式：PNG（无透明通道）
- 位置：`frontend/public/icon.png`

**启动屏：**
- iOS：2732x2732px
- Android：1242x2688px
- 位置：`frontend/public/splash.png`

### 7.2 使用Capacitor资源生成器

```bash
npm install -D @capacitor/assets

# 生成所有尺寸的图标和启动屏
npx capacitor-assets generate
```

## 📝 第八步：配置权限

### 8.1 iOS权限配置

编辑`ios/App/App/Info.plist`：

```xml
<key>NSHealthShareUsageDescription</key>
<string>PeakState需要访问您的健康数据以提供个性化建议</string>

<key>NSHealthUpdateUsageDescription</key>
<string>PeakState需要记录您的精力管理数据</string>

<key>NSCameraUsageDescription</key>
<string>PeakState需要访问相机以扫描二维码</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>PeakState需要访问相册以保存图片</string>
```

### 8.2 Android权限配置

编辑`android/app/src/main/AndroidManifest.xml`：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

## 🚀 第九步：生成发布版本

### 9.1 iOS发布构建

1. 在Xcode中选择 `Product > Archive`
2. 等待构建完成
3. 在Organizer中选择Archive，点击`Distribute App`
4. 选择发布方式：
   - **App Store Connect**：提交到App Store审核
   - **Ad Hoc**：内部测试分发
   - **Development**：开发测试

### 9.2 Android发布构建

```bash
cd android

# 生成发布密钥（首次）
keytool -genkey -v -keystore peakstate-release.keystore -alias peakstate -keyalg RSA -keysize 2048 -validity 10000

# 在Android Studio中
# Build > Generate Signed Bundle / APK
# 选择Android App Bundle (AAB)
# 选择release构建类型
# 填入密钥信息
```

## 📲 第十步：上架应用商店

### 10.1 App Store上架

**准备材料：**
1. Apple开发者账号（$99/年）
2. APP图标（1024x1024px）
3. 截图（多种设备尺寸）
4. 应用描述、关键词
5. 隐私政策URL

**提交流程：**
1. 访问[App Store Connect](https://appstoreconnect.apple.com)
2. 创建新APP
3. 上传Archive
4. 填写APP信息
5. 提交审核（通常2-3天）

### 10.2 Google Play上架

**准备材料：**
1. Google Play开发者账号（$25一次性）
2. 应用图标（512x512px）
3. 功能图片、截图
4. 应用描述
5. 隐私政策URL

**提交流程：**
1. 访问[Google Play Console](https://play.google.com/console)
2. 创建应用
3. 上传AAB文件
4. 填写商店信息
5. 提交审核（通常1-2天）

## 🔄 日常开发工作流

### 开发时

```bash
# 在浏览器中开发（推荐）
npm run dev

# 需要测试原生功能时
npm run cap:ios   # iOS
npm run cap:android   # Android
```

### 更新代码后

```bash
# 重新构建并同步
npm run cap:sync
```

### Live Reload（真机实时预览）

1. 确保手机和电脑在同一WiFi
2. 修改`capacitor.config.ts`：

```typescript
const config: CapacitorConfig = {
  server: {
    url: 'http://192.168.3.9:3000', // 你的电脑IP
    cleartext: true
  }
}
```

3. 运行`npm run dev`
4. 在手机上安装APP，自动连接到开发服务器

## 🐛 常见问题

### Q1: iOS构建失败 - "No profiles for..."

**解决：**
在Xcode中：
1. 选择项目 > Signing & Capabilities
2. 勾选 "Automatically manage signing"
3. 选择你的Team

### Q2: Android构建慢

**解决：**
增加Gradle内存限制，编辑`android/gradle.properties`：

```
org.gradle.jvmargs=-Xmx4096m
```

### Q3: 白屏/黑屏问题

**解决：**
检查`capacitor.config.ts`中的`webDir`是否正确：

```typescript
webDir: 'dist'
```

### Q4: 原生插件不工作

**解决：**
```bash
# 清理并重新同步
npx cap sync
```

## 📚 推荐资源

- [Capacitor官方文档](https://capacitorjs.com/docs)
- [iOS人机界面指南](https://developer.apple.com/design/human-interface-guidelines/)
- [Android设计指南](https://m3.material.io/)
- [App Store审核指南](https://developer.apple.com/app-store/review/guidelines/)

## 🎯 下一步行动

1. ✅ 修复设备预览问题（已完成）
2. ⏭️ 安装Capacitor并配置
3. ⏭️ 在模拟器/真机测试
4. ⏭️ 添加原生功能（健康数据、推送通知）
5. ⏭️ 准备上架资源（图标、截图、描述）
6. ⏭️ 提交到应用商店

---

**预计时间投入：**
- 环境配置：1小时
- 首次构建和测试：2小时
- 原生功能集成：3-4小时
- 上架准备：2-3小时
- **总计：1-2天**

需要帮助？随时问我！
