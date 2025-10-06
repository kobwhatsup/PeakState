# 后端服务启动状态报告

**更新时间**: 2025-10-06
**状态**: 需要修复配置不一致问题

---

## ✅ 已完成

1. **虚拟环境配置**: ✅ 完成
   - Python 3.11虚拟环境已创建
   - 所有依赖包已安装

2. **环境变量配置**: ✅ 完成
   - `.env`文件已创建
   - 有效的Fernet加密密钥已生成
   - 测试API密钥已配置

3. **代码修复**:
   - ✅ 添加`verify_access_token()`函数
   - ✅ 添加`verify_refresh_token()`函数
   - ✅ 修复User模型的CoachType SQLEnum使用
   - ✅ 修复HealthData模型的`metadata`保留字冲突(改为`extra_data`)
   - ✅ 添加JSONB类型导入

4. **测试脚本创建**: ✅ 完成
   - `test_app.py`用于验证应用加载

---

## 🔴 待修复问题

### 问题1: CoachType枚举定义不一致 (高优先级)

**错误信息**:
```
AttributeError: type object 'CoachType' has no attribute 'SAGE'
```

**原因**:
- `app/models/user.py` 中的CoachType定义:
  ```python
  class CoachType(str, SQLEnum):
      MENTOR = "mentor"
      COACH = "coach"
      DOCTOR = "doctor"
      ZEN = "zen"
  ```

- `app/ai/prompts.py` 中期望的CoachType值:
  ```python
  CoachType.SAGE  # 智者
  CoachType.COMPANION  # 伙伴
  CoachType.EXPERT  # 专家
  ```

**解决方案**: 统一两处的CoachType定义

#### 选项A: 修改models/user.py (推荐)
```python
class CoachType(str, Enum):
    """AI教练类型"""
    SAGE = "sage"          # 智者型
    COMPANION = "companion"  # 伙伴型
    EXPERT = "expert"      # 专家型
```

#### 选项B: 修改ai/prompts.py
将所有`CoachType.SAGE/COMPANION/EXPERT`改为`CoachType.MENTOR/COACH/DOCTOR`

**推荐**: 选项A,因为Sage/Companion/Expert与产品文档描述一致。

---

### 问题2: 数据库未运行 (中优先级)

虽然应用可以加载,但实际使用需要:
- PostgreSQL数据库运行
- Redis运行
- 数据库迁移执行

---

## 🛠️ 修复步骤

### 步骤1: 统一CoachType定义

编辑 `/Users/apple/Desktop/PeakState/backend/app/models/user.py`:

```python
# 第14-18行,修改为:
class CoachType(str, Enum):
    """AI教练类型"""
    SAGE = "sage"          # 智者型 - 温和睿智,启发式引导
    COMPANION = "companion"  # 伙伴型 - 亲切自然,温暖陪伴
    EXPERT = "expert"      # 专家型 - 专业精准,数据驱动
```

同时修改默认值(第59行):
```python
coach_selection: Mapped[str] = mapped_column(
    String(20),
    default="companion",  # 默认伙伴型
    nullable=False,
    comment="AI教练类型选择"
)
```

### 步骤2: 验证应用加载

```bash
cd /Users/apple/Desktop/PeakState/backend
source venv/bin/activate
python test_app.py
```

**预期输出**:
```
✅ FastAPI应用加载成功!
✅ 应用名称: PeakState
✅ 总路由数: XX

📋 已注册的API端点:
  POST       /api/v1/auth/register
  POST       /api/v1/auth/login
  POST       /api/v1/auth/refresh
  GET        /api/v1/auth/me
  PUT        /api/v1/auth/me
  POST       /api/v1/chat/send
  GET        /api/v1/chat/history/{id}
  GET        /api/v1/chat/conversations
  POST       /api/v1/chat/new
  DELETE     /api/v1/chat/{id}
  POST       /api/v1/chat/debug/routing
  ...
```

### 步骤3: 启动数据库服务 (Docker)

```bash
cd /Users/apple/Desktop/PeakState
docker-compose up -d postgres redis
```

### 步骤4: 运行数据库迁移

```bash
cd backend
source venv/bin/activate
python3 -m alembic upgrade head
```

### 步骤5: 启动FastAPI服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤6: 访问API文档

打开浏览器访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 完整启动检查清单

- [ ] 修复CoachType定义不一致
- [ ] 验证应用加载成功(`python test_app.py`)
- [ ] 启动PostgreSQL和Redis (`docker-compose up -d`)
- [ ] 运行数据库迁移 (`alembic upgrade head`)
- [ ] 启动FastAPI服务器 (`uvicorn...`)
- [ ] 访问Swagger UI文档
- [ ] 测试用户注册接口
- [ ] 测试用户登录接口
- [ ] 测试聊天接口(需要真实API密钥)

---

## 🔑 API密钥配置 (可选)

要启用真实的AI对话功能,需要配置有效的API密钥:

### OpenAI (必需)

1. 访问 https://platform.openai.com/api-keys
2. 创建新密钥
3. 编辑`.env`,替换`OPENAI_API_KEY=sk-test-key`为实际密钥

### Anthropic (可选)

1. 访问 https://console.anthropic.com/
2. 创建新密钥
3. 编辑`.env`,替换`ANTHROPIC_API_KEY=sk-ant-test-key`为实际密钥

**详细指南**: 查看 [API_KEYS_SETUP.md](./API_KEYS_SETUP.md)

---

## 📚 相关文档

- [AI_CHAT_SETUP.md](./AI_CHAT_SETUP.md) - AI对话功能设置指南
- [API_KEYS_SETUP.md](./API_KEYS_SETUP.md) - API密钥获取指南
- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - 认证系统使用指南

---

## 💡 快速修复命令

如果你想快速修复CoachType问题,可以运行:

```bash
cd /Users/apple/Desktop/PeakState/backend

# 备份原文件
cp app/models/user.py app/models/user.py.backup

# 使用sed修改(Mac系统)
sed -i '' 's/MENTOR = "mentor"/SAGE = "sage"/g' app/models/user.py
sed -i '' 's/COACH = "coach"/COMPANION = "companion"/g' app/models/user.py
sed -i '' 's/DOCTOR = "doctor"/EXPERT = "expert"/g' app/models/user.py
sed -i '' 's/ZEN = "zen"//g' app/models/user.py
sed -i '' 's/default="coach"/default="companion"/g' app/models/user.py

# 添加注释
sed -i '' 's/SAGE = "sage"/SAGE = "sage"          # 智者型/g' app/models/user.py
sed -i '' 's/COMPANION = "companion"/COMPANION = "companion"  # 伙伴型/g' app/models/user.py
sed -i '' 's/EXPERT = "expert"/EXPERT = "expert"      # 专家型/g' app/models/user.py

# 验证修改
python test_app.py
```

---

## 🎯 下一步建议

1. **立即**: 修复CoachType定义不一致问题
2. **5分钟后**: 启动服务器并访问Swagger UI
3. **10分钟后**: 测试用户注册和登录
4. **20分钟后**: 配置真实API密钥并测试AI对话
5. **30分钟后**: 完整的端到端对话测试

---

**预计修复时间**: 5-10分钟
**预计总启动时间**: 20-30分钟(含数据库和API密钥配置)
