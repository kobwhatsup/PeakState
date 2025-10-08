# ⚡ 快速开始 - iPhone 测试指南

## 🚀 只需 3 步！

### 1️⃣ 启动后端（终端 1）

```bash
/Users/apple/Desktop/PeakState/start_backend.sh
```

或者：

```bash
cd /Users/apple/Desktop/PeakState/backend
uvicorn app.main:app --reload --host 0.0.0.0
```

---

### 2️⃣ 启动前端（终端 2）

```bash
/Users/apple/Desktop/PeakState/start_web_test.sh
```

或者：

```bash
cd /Users/apple/Desktop/PeakState/frontend
npm run dev -- --host
```

---

### 3️⃣ 在 iPhone 访问

```
http://192.168.3.9:5173
```

**注意：** 确保 iPhone 和 Mac 在同一 WiFi！

---

## 📱 测试健康数据同步

1. 打开 iPhone Safari
2. 访问上面的地址
3. 点击 "连接Apple Health" 按钮
4. 看到同步结果：
   ```
   ✅ 成功同步 28 条健康数据记录
   睡眠: 7 | 步数: 7 | 心率: 7 | 活动: 7
   ```

---

## 📚 详细文档

- **完整指南：** [WEB_TEST_NOW.md](WEB_TEST_NOW.md)
- **问题排查：** 见上面文档的故障排查部分

---

## 🆘 常见问题

### Q: 无法访问？
**A:** 检查 iPhone 和 Mac 是否在同一 WiFi

### Q: IP 地址变了？
**A:** 运行 `ipconfig getifaddr en0` 获取新 IP

### Q: 后端报错？
**A:** 确保虚拟环境已激活，依赖已安装

---

## ✅ 成功标志

看到这个界面就成功了：

```
┌─────────────────────────────────┐
│  健康数据同步测试                │
│                                 │
│  [连接Apple Health]             │
│                                 │
│  测试步骤：                      │
│  1. 点击"连接Apple Health"按钮   │
│  ...                            │
└─────────────────────────────────┘
```

---

**现在就开始吧！** 🎉
