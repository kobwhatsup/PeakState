# 浏览器开发者工具 - 移动端预览指南

在等待Capacitor配置完成期间，您可以使用Chrome DevTools快速预览和调试移动端效果。

## 🚀 快速开始

### 方法一：Chrome DevTools设备模拟器

1. **打开应用**
   ```
   访问：http://localhost:3000
   ```

2. **打开开发者工具**
   - Windows/Linux: `F12` 或 `Ctrl + Shift + I`
   - Mac: `Cmd + Option + I`

3. **启用设备工具栏**
   - 点击左上角的设备图标 📱
   - 或按快捷键：`Cmd + Shift + M` (Mac) / `Ctrl + Shift + M` (Windows)

4. **选择设备**
   - 从顶部下拉菜单选择 `iPhone 14 Pro`
   - 或其他iPhone/Android设备型号

### 方法二：使用内置设备预览器（推荐）

您的应用已经集成了设备预览功能！

1. **访问应用**
   ```
   http://localhost:3000
   ```

2. **使用快捷键切换**
   - `Cmd + D` (Mac) / `Ctrl + D` (Windows)：切换桌面/手机模式
   - `Cmd + R`：旋转设备（横屏/竖屏）
   - `Cmd + T`：打开设备选择面板

3. **点击右下角浮动按钮**
   - 打开设备选择面板
   - 选择不同的设备预设（30+ 种）
   - iPhone 12-15系列、Android设备、iPad等

## 📱 推荐测试设备

### iPhone系列
- iPhone 14 Pro (393 × 852) - 默认
- iPhone 14 Pro Max (430 × 932)
- iPhone 13 (390 × 844)
- iPhone SE (375 × 667)

### Android系列
- Pixel 7 (412 × 915)
- Samsung Galaxy S21 (360 × 800)
- OnePlus 9 Pro (412 × 919)

### 平板
- iPad Pro 12.9" (1024 × 1366)
- iPad Air (820 × 1180)

## 🎯 高级调试技巧

### 1. 触摸事件模拟

Chrome DevTools会自动将鼠标点击转换为触摸事件，但您也可以：

- 在Sources面板中设置断点
- 在Console中测试触摸API：
  ```javascript
  // 测试touch事件
  document.addEventListener('touchstart', (e) => {
    console.log('Touch detected:', e.touches[0]);
  });
  ```

### 2. 网络节流测试

模拟慢速移动网络：

1. 打开Network标签
2. 从 "No throttling" 下拉菜单选择：
   - Fast 3G
   - Slow 3G
   - Offline（测试离线功能）

### 3. 传感器模拟

测试设备方向、GPS等：

1. `Cmd + Shift + P` 打开命令面板
2. 输入 "sensors"
3. 选择 "Show Sensors"
4. 模拟设备旋转、地理位置等

### 4. 性能分析

检测移动端性能瓶颈：

1. 打开Performance标签
2. 勾选 "Enable CPU throttling" (4x slowdown)
3. 录制并分析页面性能

### 5. 响应式图片测试

查看不同DPR（设备像素比）下的图片：

1. 在Rendering标签中
2. 调整 "Emulate CSS media feature prefers-color-scheme"
3. 测试深色模式

## 🔍 调试常见问题

### 问题1：滚动不流畅

**检查：**
```javascript
// 在Console中运行
document.querySelector('.overflow-y-auto').style.overflowY
```

**解决：**
确保容器有正确的`overflow-y-auto`和固定高度。

### 问题2：元素被遮挡

**检查：**
使用Elements面板的 3D View：
1. `Cmd + Shift + P`
2. 输入 "3D View"
3. 查看z-index层级

### 问题3：安全区域不生效

**检查：**
```javascript
// 查看CSS变量
getComputedStyle(document.documentElement)
  .getPropertyValue('--safe-area-inset-top')
```

**解决：**
确保在设备预览模式下，CSS变量已正确设置。

## 📊 对比：DevTools vs 内置预览器 vs 真机

| 功能 | Chrome DevTools | 内置预览器 | Capacitor真机 |
|------|----------------|-----------|--------------|
| 快速切换 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 设备多样性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 真实触摸 | ❌ | ❌ | ✅ |
| 原生API | ❌ | ❌ | ✅ |
| 性能测试 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 调试便利性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🎨 UI验证清单

在提交到真机测试前，使用浏览器工具检查：

- [ ] 所有按钮 ≥ 44×44px（触摸目标）
- [ ] 文字在小屏幕可读（≥14px）
- [ ] 表单在视口内完整显示
- [ ] 滚动流畅无卡顿
- [ ] 弹窗/模态框不溢出
- [ ] 横屏模式正常工作
- [ ] 安全区域（刘海、底部）无遮挡
- [ ] 图片加载正常
- [ ] 动画不掉帧

## 🚀 工作流建议

### 日常开发
1. 使用内置设备预览器快速查看布局
2. 用Chrome DevTools深度调试细节
3. 定期在真机上验证体验

### 提交前验证
1. 在5-6种常用设备上测试
2. 测试横屏和竖屏
3. 测试慢速网络下的加载
4. 检查所有交互元素的触摸反馈

### 性能优化
1. 使用Lighthouse分析移动端性能
2. 确保First Contentful Paint < 1.8s
3. Time to Interactive < 3.9s
4. 图片启用lazy loading

## 📱 远程调试移动浏览器

如果需要在手机浏览器中调试：

### iOS (Safari)

1. iPhone设置：
   - 设置 > Safari > 高级 > 网页检查器：开启

2. Mac Safari：
   - Safari > 偏好设置 > 高级 > 显示开发菜单
   - 开发 > 选择你的iPhone > localhost

### Android (Chrome)

1. Android手机：
   - 设置 > 开发者选项 > USB调试：开启

2. Chrome浏览器：
   - 访问 `chrome://inspect`
   - 连接USB，允许调试
   - 点击inspect

## 🎯 下一步

完成浏览器预览优化后，建议：

1. ✅ 确认所有页面在移动端正确显示
2. ⏭️ 按照[Capacitor集成指南](./CAPACITOR_SETUP_GUIDE.md)安装原生环境
3. ⏭️ 在真机上测试触摸交互和性能
4. ⏭️ 集成原生功能（健康数据、推送通知）
5. ⏭️ 准备上架资源

---

**提示：** 浏览器预览是快速开发的好工具，但最终用户体验必须在真机上验证！
