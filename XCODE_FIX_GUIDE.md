# Xcode CocoaPods 错误修复指南

## 问题描述
构建时出现错误：`The sandbox is not in sync with the Podfile.lock. Run 'pod install'`

## 根本原因
Capacitor 7 自动创建了 CocoaPods 集成，但我们不需要使用 CocoaPods。需要从 Xcode 项目中完全移除 CocoaPods 引用。

---

## 修复步骤（请严格按顺序操作）

### 第一步：打开 Xcode 项目

1. 双击打开文件：
   ```
   /Users/apple/Desktop/PeakState/frontend/ios/App/App.xcodeproj
   ```

2. 等待 Xcode 完全加载项目

---

### 第二步：移除 CocoaPods 构建脚本

1. 在左侧项目导航器中，点击最顶部的蓝色 **App** 图标（项目名称）

2. 在中间区域，确保选择了 **TARGETS** 下的 **App**（不是 PROJECT）

3. 点击顶部的 **Build Phases** 标签

4. 你会看到多个构建阶段，找到这两个带有 `[CP]` 前缀的：
   - `[CP] Check Pods Manifest.lock`
   - `[CP] Embed Pods Frameworks`

5. **删除这两个脚本：**
   - 右键点击 `[CP] Check Pods Manifest.lock` → 选择 **Delete**
   - 右键点击 `[CP] Embed Pods Frameworks` → 选择 **Delete**
   - 点击确认删除

**视觉参考：**
```
Build Phases 标签下应该类似这样：
  ├── Dependencies
  ├── [CP] Check Pods Manifest.lock  ← 删除这个
  ├── Sources
  ├── Frameworks
  ├── [CP] Embed Pods Frameworks     ← 删除这个
  └── Resources
```

---

### 第三步：移除配置引用

1. 在左侧项目导航器中，再次点击最顶部的蓝色 **App** 图标

2. 这次确保选择 **PROJECT** 下的 **App**（不是 TARGETS）

3. 点击顶部的 **Info** 标签

4. 找到 **Configurations** 部分

5. 展开 **Debug** 和 **Release** 配置

6. 对于每个配置，你会看到两列：
   - 第一列是 App（项目）
   - 第二列是 App（target）

7. **将第二列（target）的配置设置为 None：**
   - Debug 行 → App (target) 列 → 下拉选择 **None**
   - Release 行 → App (target) 列 → 下拉选择 **None**

**视觉参考：**
```
Configurations:
  Debug
    ├── App (project):  None
    └── App (target):   None  ← 确保这里是 None

  Release
    ├── App (project):  None
    └── App (target):   None  ← 确保这里是 None
```

---

### 第四步：清理构建文件夹

1. 在 Xcode 顶部菜单，点击 **Product**

2. 按住 **Option** 键（⌥），你会看到 **Clean Build Folder** 选项（不是普通的 Clean）

3. 点击 **Clean Build Folder**

4. 等待清理完成（通常几秒钟）

---

### 第五步：重新构建

1. 点击 Xcode 左上角的 **▶️ 播放按钮**（或按 `⌘ + R`）

2. 第一次构建可能需要 1-2 分钟

3. **如果成功：**
   - App 会在模拟器中启动
   - 你会看到健康数据同步界面
   - 点击"请求权限"可以测试模拟数据

4. **如果仍然失败：**
   - 截图错误信息
   - 告诉我具体的错误内容

---

## 预期结果

✅ 构建成功，没有 CocoaPods 错误
✅ App 在模拟器中正常运行
✅ 可以看到健康数据同步界面
✅ 点击"请求权限"后可以同步模拟数据

---

## 常见问题

### Q1: 找不到 `[CP]` 开头的构建脚本？
**A:** 可能已经被删除了，直接跳到第三步。

### Q2: 删除后还是提示 CocoaPods 错误？
**A:** 确保完成了第三步（移除配置引用），然后重新清理构建文件夹。

### Q3: 模拟器没有显示健康数据界面？
**A:** 这是正常的，因为我们修改了代码直接显示健康同步界面。如果要恢复正常流程，告诉我即可。

### Q4: 我想在真实 iPhone 上测试怎么办？
**A:** 需要配置开发者签名：
1. 点击项目 → TARGETS → App → Signing & Capabilities
2. 选择你的 Apple ID 团队
3. 连接 iPhone
4. 选择 iPhone 作为目标设备
5. 点击运行

---

## 下一步

修复成功后，你可以：

1. **测试模拟健康数据：**
   - 点击"请求权限"
   - 查看模拟的睡眠、步数、心率数据
   - 数据会自动上传到后端

2. **在真实 iPhone 上测试：**
   - 按照上面 Q4 的步骤配置签名
   - 真实设备需要安装 `capacitor-health` 插件才能读取真实 HealthKit 数据
   - 目前使用的是模拟数据服务

3. **恢复正常 App 流程：**
   - 告诉我，我会修改代码让 App 回到正常的引导界面

---

**任何问题随时告诉我！** 📱
