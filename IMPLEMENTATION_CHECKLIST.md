# ✅ PeakState实施检查清单

完整的阿里云RDS配置和前后端对接步骤清单。

---

## 📦 Part 1: 阿里云RDS数据库配置 (1-2小时)

### Step 1: 购买RDS实例 (30分钟)

- [ ] 登录阿里云控制台
- [ ] 创建RDS PostgreSQL 15实例
  - 规格: 2核4G
  - 存储: 50GB SSD
  - 地域: 华东1(杭州)
- [ ] 等待实例创建完成(5-10分钟)

**参考文档**: [docs/ALIYUN_RDS_SETUP.md](docs/ALIYUN_RDS_SETUP.md)

---

### Step 2: 配置安全设置 (15分钟)

- [ ] 设置白名单
  ```bash
  # 查看你的公网IP
  curl ifconfig.me
  # 将此IP添加到白名单
  ```

- [ ] 创建数据库账号
  - 账号名: `peakstate_user`
  - 密码: 强密码(12位以上)

- [ ] 创建数据库
  - 数据库名: `peakstate`
  - 字符集: UTF8
  - 授权账号: `peakstate_user`

---

### Step 3: 配置PeakState连接 (15分钟)

- [ ] 获取RDS连接信息
  - 复制内网/外网地址
  - 记录端口(默认5432)

- [ ] 更新 `.env` 文件

```bash
# 编辑 .env
nano .env

# 添加/更新以下配置:
ALIYUN_RDS_HOST=rm-xxxxxxxxxxxxx.pg.rds.aliyuncs.com
ALIYUN_RDS_PORT=5432
ALIYUN_RDS_USER=peakstate_user
ALIYUN_RDS_PASSWORD=你的密码
ALIYUN_RDS_DATABASE=peakstate
ALIYUN_RDS_SSL_MODE=require

# 更新DATABASE_URL
DATABASE_URL=postgresql://peakstate_user:你的密码@rm-xxxxxxxxxxxxx.pg.rds.aliyuncs.com:5432/peakstate?sslmode=require
```

- [ ] 保存文件

---

### Step 4: 测试连接 (10分钟)

```bash
cd backend

# 测试RDS连接
python test_rds_connection.py

# 期望输出:
# ✅ 连接成功!
# ✅ 数据库版本: PostgreSQL 15.x
# ✅ 读写权限正常
# 🎉 阿里云RDS连接测试成功!
```

**如果失败**: 检查白名单、密码、数据库名

---

### Step 5: 执行数据库迁移 (10分钟)

```bash
cd backend

# 1. 查看待执行的迁移
alembic history

# 2. 执行迁移
alembic upgrade head

# 期望输出:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema

# 3. 验证表是否创建成功
python -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    tables = await conn.fetch(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\")
    print('📊 创建的表:')
    for t in tables:
        print(f'  ✓ {t[\"tablename\"]}')
    await conn.close()

asyncio.run(check())
"

# 期望看到:
# ✓ users
# ✓ conversations
# ✓ health_data
# ✓ alembic_version
```

- [ ] 数据库迁移成功
- [ ] 所有表创建完成

---

### Step 6: 启动后端服务 (5分钟)

```bash
cd backend

# 安装依赖(如果还没安装)
pip install -r requirements.txt  # 或 poetry install

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 期望输出:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

- [ ] 后端服务启动成功
- [ ] 访问 http://localhost:8000/docs 可见API文档
- [ ] 访问 http://localhost:8000/health 返回健康状态

---

## 🎨 Part 2: 前端开发和对接 (3-4小时)

### Step 1: 安装前端依赖 (5分钟)

```bash
cd frontend

# 安装核心依赖
npm install axios zustand

# 安装开发依赖
npm install -D @types/node
```

- [ ] 依赖安装成功

---

### Step 2: 创建环境变量配置 (2分钟)

```bash
# 创建 frontend/.env
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
EOF
```

- [ ] `.env` 文件创建成功

---

### Step 3: 创建API服务层 (30分钟)

创建以下文件(代码见文档):

- [ ] `src/api/client.ts` - Axios配置
- [ ] `src/api/types.ts` - TypeScript类型
- [ ] `src/api/auth.ts` - 认证API
- [ ] `src/api/chat.ts` - 聊天API

**完整代码**: [docs/FRONTEND_BACKEND_INTEGRATION.md](docs/FRONTEND_BACKEND_INTEGRATION.md)

---

### Step 4: 创建状态管理 (30分钟)

创建以下文件:

- [ ] `src/store/authStore.ts` - 认证状态
- [ ] `src/store/chatStore.ts` - 聊天状态

---

### Step 5: 创建自定义Hooks (15分钟)

- [ ] `src/hooks/useAuth.ts` - 认证Hook
- [ ] `src/hooks/useChat.ts` - 聊天Hook

---

### Step 6: 集成到现有组件 (60分钟)

#### 修改 `OnboardingElite.tsx`:

```typescript
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export function OnboardingElite({ onComplete }: Props) {
  const { register, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [selectedCoach, setSelectedCoach] = useState<'sage' | 'companion' | 'expert'>('sage');

  const handleComplete = async () => {
    try {
      await register({
        email,
        username,
        password,
        coach_type: selectedCoach,
      });
      onComplete(selectedCoach);
    } catch (err) {
      console.error('注册失败:', err);
    }
  };

  // ... 现有UI代码,添加表单输入
}
```

#### 修改 `ChatInterfaceElite.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../hooks/useAuth';

export function ChatInterfaceElite({ coachType, onStartFocus }: Props) {
  const { user } = useAuth();
  const { messages, sendMessage, isSending, createNewConversation } = useChat();
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    // 创建新会话
    createNewConversation();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSending) return;

    try {
      await sendMessage(inputValue);
      setInputValue('');
    } catch (err) {
      console.error('发送消息失败:', err);
    }
  };

  return (
    <div className="chat-container">
      {/* 消息列表 */}
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="content">{msg.content}</div>
            <div className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
          </div>
        ))}
        {isSending && <div className="typing-indicator">AI正在思考...</div>}
      </div>

      {/* 输入框 */}
      <div className="input-area">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="输入消息..."
          disabled={isSending}
        />
        <button onClick={handleSendMessage} disabled={isSending || !inputValue.trim()}>
          发送
        </button>
      </div>
    </div>
  );
}
```

- [ ] OnboardingElite集成认证
- [ ] ChatInterfaceElite集成聊天API
- [ ] FocusModeElite保持现有功能

---

### Step 7: 启动前端服务 (2分钟)

```bash
cd frontend

# 启动开发服务器
npm run dev

# 期望输出:
# VITE v6.3.5  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

- [ ] 前端服务启动成功
- [ ] 访问 http://localhost:5173 可见页面

---

## 🧪 Part 3: 端到端测试 (30分钟)

### 测试流程

1. **注册新用户**
   - [ ] 打开 http://localhost:5173
   - [ ] 填写注册信息(email, username, password)
   - [ ] 选择教练类型(智者/伙伴/专家)
   - [ ] 点击完成
   - [ ] 检查: 自动跳转到聊天界面

2. **发送消息**
   - [ ] 在聊天输入框输入: "你好,我是新用户"
   - [ ] 点击发送
   - [ ] 检查: AI回复正常显示
   - [ ] 检查: 回复符合选择的教练人设

3. **查看历史**
   - [ ] 刷新页面
   - [ ] 检查: 历史消息正常加载

4. **测试不同复杂度**
   - [ ] 简单问候: "早上好" (应路由到GPT-5 Nano)
   - [ ] 情感支持: "我今天很累,怎么办" (应路由到Claude Sonnet 4)
   - [ ] 复杂分析: "请分析我最近一周的精力状态" (应路由到GPT-5)

5. **测试教练人设**
   - [ ] 智者(Sage): 启发式回答
   - [ ] 伙伴(Companion): 温暖陪伴式回答
   - [ ] 专家(Expert): 数据驱动式回答

---

## 📊 完成检查

### 后端检查

- [ ] RDS数据库运行正常
- [ ] 后端服务运行在 http://localhost:8000
- [ ] API文档可访问 http://localhost:8000/docs
- [ ] 数据库表创建成功
- [ ] 用户注册API工作正常
- [ ] 聊天API工作正常
- [ ] AI路由正常(检查日志)

### 前端检查

- [ ] 前端服务运行在 http://localhost:5173
- [ ] 注册流程完整
- [ ] 聊天界面功能正常
- [ ] 消息发送/接收正常
- [ ] 状态持久化(刷新页面后保持登录)
- [ ] 错误处理正常

### 功能检查

- [ ] 用户可以注册
- [ ] 用户可以登录
- [ ] 用户可以选择教练类型
- [ ] 用户可以发送消息
- [ ] AI回复正常
- [ ] 历史记录保存
- [ ] 不同教练人设有区别

---

## 🚨 常见问题

### 问题1: 前端无法连接后端

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查CORS配置
# backend/app/core/config.py
CORS_ORIGINS=http://localhost:5173  # 确保包含前端地址
```

### 问题2: 401 Unauthorized

```bash
# 检查token是否正确保存
# 浏览器控制台执行:
localStorage.getItem('access_token')

# 检查后端JWT配置
# .env文件
JWT_SECRET_KEY=your-secret-key  # 确保配置
```

### 问题3: 数据库连接失败

```bash
# 重新测试RDS连接
cd backend
python test_rds_connection.py

# 检查白名单
curl ifconfig.me  # 确保IP在白名单中
```

---

## 📝 下一步

完成以上检查后:

1. ✅ **基础功能可用** - 用户可以注册、聊天
2. ⏭️ **添加健康数据集成** - Week 10-11
3. ⏭️ **实现主动对话** - Week 12
4. ⏭️ **添加高级功能** - Week 13-14

---

**完成时间估计**: 4-6小时
**文档参考**:
- [阿里云RDS配置详解](docs/ALIYUN_RDS_SETUP.md)
- [前后端对接指南](docs/FRONTEND_BACKEND_INTEGRATION.md)
- [项目进度报告](PROJECT_PROGRESS_REPORT.md)

**遇到问题?** 查看文档或检查日志:
- 后端日志: 终端输出
- 前端日志: 浏览器控制台(F12)
- 数据库日志: 阿里云RDS控制台

---

**准备好开始了吗?** 🚀
从 Part 1 Step 1 开始,按顺序完成每个步骤!
