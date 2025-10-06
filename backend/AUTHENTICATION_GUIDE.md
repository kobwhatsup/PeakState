# PeakState 认证系统使用指南

## 📚 概览

已完成的认证系统包括数据模型、用户CRUD操作、JWT认证和完整的API端点。

## 🗄️ 数据模型

### User (用户)
- **文件**: `app/models/user.py`
- **字段**:
  - `id`: UUID主键
  - `phone_number`: 手机号(登录凭证,唯一索引)
  - `hashed_password`: bcrypt加密密码
  - `coach_selection`: AI教练类型(mentor/coach/doctor/zen)
  - `is_subscribed`: 订阅状态
  - `subscription_end_date`: 订阅到期时间
  - `is_trial`: 试用状态
  - `trial_end_date`: 试用到期时间
  - `morning_briefing_enabled/time`: 早报配置
  - `evening_review_enabled/time`: 晚间复盘配置
  - `created_at`, `updated_at`, `last_login_at`: 时间戳

### Conversation (对话)
- **文件**: `app/models/conversation.py`
- **字段**:
  - `id`: UUID主键
  - `user_id`: 用户ID(外键)
  - `messages`: JSONB数组存储对话消息
  - `ai_provider_used`: 使用的AI提供商
  - `message_count`: 消息总数
  - `total_tokens_used`: token使用量
  - `intent_classification`: 对话意图分类

### HealthData (健康数据)
- **文件**: `app/models/health_data.py`
- **字段**:
  - `id`: UUID主键
  - `user_id`: 用户ID(外键)
  - `data_type`: 数据类型(sleep_duration/hrv/heart_rate等)
  - `value`: 数据值
  - `source`: 数据来源(apple_health/google_fit等)
  - `encrypted_data`: 加密的原始数据
  - `recorded_at`: 数据采集时间
  - **索引**: user_id + data_type + recorded_at 联合索引

## 🔐 认证流程

### 1. 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone_number": "13800138000",
  "password": "securepassword123",
  "coach_selection": "coach"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**说明**:
- 手机号必须11位且格式正确(1[3-9]xxxxxxxxx)
- 密码至少6位
- 新用户自动获得7天试用期
- 返回JWT访问令牌和刷新令牌

### 2. 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "phone_number": "13800138000",
  "password": "securepassword123"
}
```

**响应**: 同注册响应

### 3. 刷新令牌
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

**响应**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

### 4. 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGc...
```

**响应**:
```json
{
  "id": "uuid",
  "phone_number": "13800138000",
  "coach_selection": "coach",
  "timezone": "Asia/Shanghai",
  "is_subscribed": false,
  "is_trial": true,
  "trial_end_date": "2025-10-13T13:40:00Z",
  "morning_briefing_enabled": true,
  "morning_briefing_time": "07:00",
  "evening_review_enabled": true,
  "evening_review_time": "22:00",
  "created_at": "2025-10-06T13:40:00Z",
  "last_login_at": "2025-10-06T13:45:00Z"
}
```

### 5. 更新用户信息
```http
PUT /api/v1/auth/me
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "coach_selection": "zen",
  "morning_briefing_time": "08:00",
  "evening_review_time": "21:30"
}
```

## 🗂️ 数据库迁移

### 初始化迁移
```bash
cd backend
python3 -m alembic revision --autogenerate -m "Your migration message"
```

### 执行迁移
```bash
python3 -m alembic upgrade head
```

### 回滚迁移
```bash
python3 -m alembic downgrade -1
```

### 查看迁移历史
```bash
python3 -m alembic history
```

### 当前迁移状态
```bash
python3 -m alembic current
```

## ☁️ Aliyun RDS配置

### 环境变量配置
在 `.env` 文件中添加:

```bash
# 阿里云RDS PostgreSQL
ALIYUN_RDS_HOST=rm-xxxxxxxxxxxxx.pg.rds.aliyuncs.com
ALIYUN_RDS_PORT=5432
ALIYUN_RDS_USER=peakstate_user
ALIYUN_RDS_PASSWORD=your_strong_rds_password
ALIYUN_RDS_DATABASE=peakstate
ALIYUN_RDS_SSL_MODE=require
ALIYUN_RDS_SSL_CA_PATH=/path/to/rds-ca-cert.pem

# 使用Aliyun RDS
DATABASE_URL=postgresql://${ALIYUN_RDS_USER}:${ALIYUN_RDS_PASSWORD}@${ALIYUN_RDS_HOST}:${ALIYUN_RDS_PORT}/${ALIYUN_RDS_DATABASE}?sslmode=${ALIYUN_RDS_SSL_MODE}
```

### SSL证书下载
1. 登录阿里云RDS控制台
2. 下载RDS PostgreSQL CA证书
3. 将证书放置到项目目录并更新 `ALIYUN_RDS_SSL_CA_PATH`

## 🔧 CRUD操作

### 创建用户 (内部使用)
```python
from app.crud.user import create_user
from app.schemas.user import UserRegister

user_data = UserRegister(
    phone_number="13800138000",
    password="password123",
    coach_selection="coach"
)
user = await create_user(db, user_data)
```

### 查询用户
```python
from app.crud.user import get_user_by_phone, get_user_by_id

# 按手机号查询
user = await get_user_by_phone(db, "13800138000")

# 按ID查询
user = await get_user_by_id(db, user_id)
```

### 更新用户
```python
from app.crud.user import update_user
from app.schemas.user import UserUpdate

update_data = UserUpdate(
    coach_selection="zen",
    morning_briefing_time="08:00"
)
user = await update_user(db, user_id, update_data)
```

### 认证用户
```python
from app.crud.user import authenticate_user

user = await authenticate_user(db, "13800138000", "password123")
if user:
    # 登录成功
    pass
```

### 更新订阅
```python
from app.crud.user import update_subscription

user = await update_subscription(
    db,
    user_id,
    subscription_type="monthly",
    duration_days=30
)
```

## 🧪 测试示例

### 使用curl测试注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000",
    "password": "password123",
    "coach_selection": "coach"
  }'
```

### 使用curl测试登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000",
    "password": "password123"
  }'
```

### 使用curl测试获取用户信息
```bash
# 替换YOUR_TOKEN为实际的access_token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 文件结构

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── conversation.py      # 对话模型
│   │   └── health_data.py       # 健康数据模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # 用户Pydantic模式
│   │   └── token.py             # 令牌Pydantic模式
│   ├── crud/
│   │   └── user.py              # 用户CRUD操作
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # API依赖注入
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── auth.py          # 认证API端点
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   └── security.py          # 安全工具
│   └── main.py                  # FastAPI应用
├── migrations/
│   ├── env.py                   # Alembic环境配置
│   └── versions/
│       └── 001_initial_schema.py  # 初始数据库迁移
├── alembic.ini                  # Alembic配置
└── .env.example                 # 环境变量模板
```

## 🚀 启动应用

```bash
cd backend
python3 app/main.py
```

访问API文档: http://localhost:8000/docs

## 🔑 JWT令牌配置

- **访问令牌有效期**: 7天 (604800秒)
- **刷新令牌有效期**: 30天
- **算法**: HS256
- **密钥**: 在 `.env` 中配置 `JWT_SECRET_KEY` (至少32位)

## 🛡️ 安全特性

1. **密码加密**: bcrypt哈希算法
2. **JWT双令牌**: access_token + refresh_token
3. **健康数据加密**: Fernet对称加密
4. **SSL连接**: Aliyun RDS强制SSL
5. **输入验证**: Pydantic自动验证
6. **SQL注入防护**: SQLAlchemy参数化查询

## 📝 后续工作

- [ ] 实现手机验证码功能
- [ ] 添加密码重置功能
- [ ] 实现用户注销(撤销令牌)
- [ ] 添加用户删除功能
- [ ] 实现对话API端点
- [ ] 实现健康数据同步API
- [ ] 添加订阅支付集成
