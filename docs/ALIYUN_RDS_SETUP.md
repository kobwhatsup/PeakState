# 🔧 阿里云RDS PostgreSQL配置指南

本文档详细说明如何将PeakState连接到阿里云RDS PostgreSQL数据库。

---

## 📋 前置准备

### 1. 阿里云账号准备
- ✅ 已注册阿里云账号
- ✅ 已完成实名认证
- ✅ 账户有足够余额

### 2. 推荐配置
| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| **实例规格** | 2核4G | 入门级,支持1000+用户 |
| **存储空间** | 50GB SSD | 可自动扩容 |
| **数据库版本** | PostgreSQL 15 | 最新稳定版 |
| **地域** | 华东1(杭州) | 根据用户分布选择 |
| **可用区** | 单可用区 | 开发/测试环境 |
| **计费方式** | 按量付费 | 前期测试,稳定后转包年包月 |

**预估成本**: ¥400-500/月

---

## 🚀 Step 1: 创建RDS实例

### 1.1 登录阿里云控制台

```
1. 访问: https://www.aliyun.com/
2. 点击右上角"控制台"
3. 搜索"RDS" → 进入"云数据库RDS"
```

### 1.2 创建实例

```
点击"创建实例"

【基础配置】
- 商品类型: 云数据库RDS PostgreSQL版
- 版本: PostgreSQL 15
- 系列: 基础版 (高可用版更贵但更稳定)
- 规格: 2核4G (pg.n2.medium.1)
- 存储: 50GB SSD云盘

【网络配置】
- 地域: 华东1(杭州)
- 可用区: 随机分配
- 网络类型: 专有网络VPC (推荐)
- 虚拟交换机: 自动创建或选择已有

【实例配置】
- 实例名称: peakstate-prod-db
- 资源组: 默认资源组

【购买时长】
- 计费方式: 按量付费 (测试期)

【确认订单】
点击"立即购买" → 支付
```

**等待5-10分钟,实例创建完成**

---

## 🔐 Step 2: 配置数据库安全

### 2.1 设置白名单

```
1. 进入RDS实例详情页
2. 左侧菜单: "数据安全性" → "白名单设置"
3. 点击"修改"

【添加白名单】
- 开发本地测试: 添加你的公网IP
  查看IP: curl ifconfig.me
  例如: 123.45.67.89

- 生产环境: 添加ECS服务器IP
  例如: 172.16.0.0/12 (VPC内网段)

- 临时开发: 0.0.0.0/0 (⚠️ 不安全,仅测试用)

4. 点击"确定"
```

### 2.2 创建数据库账号

```
1. 左侧菜单: "账号管理"
2. 点击"创建账号"

【账号信息】
- 数据库账号: peakstate_user
- 账号类型: 普通账号
- 密码: 设置强密码 (至少12位,包含大小写字母+数字+特殊字符)
  例如: PeakState@2025#Secure
- 确认密码: 再输入一次

3. 点击"确定"
```

### 2.3 创建数据库

```
1. 左侧菜单: "数据库管理"
2. 点击"创建数据库"

【数据库信息】
- 数据库名称: peakstate
- 支持字符集: UTF8
- 授权账号: peakstate_user
- 账号权限: 读写

3. 点击"创建"
```

---

## 🌐 Step 3: 获取连接信息

### 3.1 内网地址(推荐,ECS访问)

```
实例详情页 → "基本信息" → "连接信息"

内网地址: pgm-2zenr70bu8bp2xgy.pg.rds.aliyuncs.com
内网端口: 5432
```

### 3.2 外网地址(开发测试)

```
如果需要从本地连接:

1. "数据库连接" → "申请外网地址"
2. 等待1分钟获得外网地址
3. 复制外网地址

外网地址: rm-xxxxxxxxxxxxx.pg.rds.aliyuncs.com (不同于内网)
外网端口: 5432

⚠️ 注意: 外网访问有安全风险,生产环境应禁用
```

---

## ⚙️ Step 4: 配置PeakState连接RDS

### 4.1 更新环境变量

编辑 `.env` 文件:

```bash
# ============ 阿里云RDS PostgreSQL配置 ============

# RDS连接信息 (从阿里云控制台复制)
ALIYUN_RDS_HOST=rm-xxxxxxxxxxxxx.pg.rds.aliyuncs.com  # 替换为你的实例地址
ALIYUN_RDS_PORT=5432
ALIYUN_RDS_USER=peakstate_user
ALIYUN_RDS_PASSWORD=PeakState@2025#Secure  # 替换为你设置的密码
ALIYUN_RDS_DATABASE=peakstate
ALIYUN_RDS_SSL_MODE=require  # 强制SSL连接

# 自动生成的DATABASE_URL (优先使用RDS)
DATABASE_URL=postgresql://${ALIYUN_RDS_USER}:${ALIYUN_RDS_PASSWORD}@${ALIYUN_RDS_HOST}:${ALIYUN_RDS_PORT}/${ALIYUN_RDS_DATABASE}?sslmode=${ALIYUN_RDS_SSL_MODE}

# 连接池配置 (生产环境)
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

**完整示例** (替换实际值):
```bash
ALIYUN_RDS_HOST=rm-bp1abc123def.pg.rds.aliyuncs.com
ALIYUN_RDS_PORT=5432
ALIYUN_RDS_USER=peakstate_user
ALIYUN_RDS_PASSWORD=YourStrongPassword@2025
ALIYUN_RDS_DATABASE=peakstate
ALIYUN_RDS_SSL_MODE=require

DATABASE_URL=postgresql://peakstate_user:YourStrongPassword@2025@rm-bp1abc123def.pg.rds.aliyuncs.com:5432/peakstate?sslmode=require
```

### 4.2 下载SSL证书(可选但推荐)

```bash
# 1. 从阿里云下载RDS CA证书
# 控制台: "数据安全性" → "SSL" → "下载证书"

# 2. 保存证书到项目
mkdir -p backend/ssl
mv ~/Downloads/ApsaraDB-CA-Chain.pem backend/ssl/rds-ca-cert.pem

# 3. 更新.env配置
ALIYUN_RDS_SSL_CA_PATH=./backend/ssl/rds-ca-cert.pem
ALIYUN_RDS_SSL_MODE=verify-ca  # 升级到验证证书
```

### 4.3 更新后端配置代码

后端代码已支持RDS配置,无需修改。验证 `backend/app/core/config.py`:

```python
# 阿里云RDS配置 (已存在)
ALIYUN_RDS_HOST: Optional[str] = None
ALIYUN_RDS_PORT: int = 5432
ALIYUN_RDS_USER: Optional[str] = None
ALIYUN_RDS_PASSWORD: Optional[str] = None
ALIYUN_RDS_DATABASE: Optional[str] = None
ALIYUN_RDS_SSL_MODE: str = "require"
ALIYUN_RDS_SSL_CA_PATH: Optional[str] = None
```

---

## 🧪 Step 5: 测试连接

### 5.1 使用psql命令行测试

```bash
# 安装PostgreSQL客户端 (如果未安装)
# macOS
brew install postgresql@15

# 测试连接
psql "postgresql://peakstate_user:YourPassword@rm-xxxxx.pg.rds.aliyuncs.com:5432/peakstate?sslmode=require"

# 成功连接后会看到:
peakstate=>

# 测试基本命令
\l          # 列出所有数据库
\dt         # 列出所有表 (初始为空)
\q          # 退出
```

### 5.2 使用Python测试连接

创建测试脚本 `backend/test_rds_connection.py`:

```python
#!/usr/bin/env python3
"""测试阿里云RDS PostgreSQL连接"""
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def test_rds_connection():
    """测试RDS连接"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL 未配置")
        return False

    print(f"🔍 测试连接到: {database_url.split('@')[1].split('?')[0]}")

    try:
        # 建立连接
        conn = await asyncpg.connect(database_url)

        # 测试查询
        version = await conn.fetchval('SELECT version()')

        print(f"\n✅ 连接成功!")
        print(f"✅ 数据库版本: {version.split(',')[0]}")

        # 测试创建表权限
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_time TIMESTAMP DEFAULT NOW()
            )
        """)

        await conn.execute("INSERT INTO connection_test DEFAULT VALUES")
        count = await conn.fetchval("SELECT COUNT(*) FROM connection_test")

        print(f"✅ 读写权限正常 (测试记录数: {count})")

        # 清理测试表
        await conn.execute("DROP TABLE connection_test")

        await conn.close()

        print("\n🎉 阿里云RDS连接测试成功!")
        return True

    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n请检查:")
        print("  1. DATABASE_URL 是否正确")
        print("  2. 白名单是否包含你的IP")
        print("  3. 账号密码是否正确")
        print("  4. 数据库是否已创建")
        return False

if __name__ == "__main__":
    asyncio.run(test_rds_connection())
```

运行测试:
```bash
cd backend
python test_rds_connection.py
```

---

## 🔄 Step 6: 执行数据库迁移

### 6.1 确认Alembic配置

检查 `backend/alembic.ini`:
```ini
# 确认使用环境变量
sqlalchemy.url =
```

检查 `backend/migrations/env.py`:
```python
# 应该从环境变量读取
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace('%', '%%')
)
```

### 6.2 执行迁移

```bash
cd backend

# 1. 检查当前迁移状态
alembic current

# 2. 查看待执行的迁移
alembic history

# 3. 执行所有迁移到最新版本
alembic upgrade head

# 期望输出:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
# INFO  [alembic.runtime.migration] Running upgrade complete

# 4. 验证表是否创建成功
psql $DATABASE_URL -c "\dt"

# 应该看到:
#  Schema |        Name        | Type  |      Owner
# --------+--------------------+-------+-----------------
#  public | alembic_version   | table | peakstate_user
#  public | conversations     | table | peakstate_user
#  public | health_data       | table | peakstate_user
#  public | users             | table | peakstate_user
```

### 6.3 创建初始管理员用户(可选)

```python
# backend/scripts/create_admin.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    hashed_password = pwd_context.hash("Admin@2025")

    await conn.execute("""
        INSERT INTO users (
            email, username, hashed_password,
            is_active, is_superuser, coach_type
        ) VALUES (
            'admin@peakstate.com', 'admin', $1,
            true, true, 'sage'
        ) ON CONFLICT (email) DO NOTHING
    """, hashed_password)

    print("✅ 管理员账号创建成功")
    print("   邮箱: admin@peakstate.com")
    print("   密码: Admin@2025")

    await conn.close()

asyncio.run(create_admin())
```

---

## 🛡️ Step 7: 安全最佳实践

### 7.1 生产环境安全检查清单

- [ ] **关闭外网地址** (仅内网ECS访问)
- [ ] **严格白名单** (不使用 0.0.0.0/0)
- [ ] **强密码** (12位以上,定期轮换)
- [ ] **启用SSL** (sslmode=require 或 verify-ca)
- [ ] **最小权限** (普通账号,非超级用户)
- [ ] **备份策略** (自动备份,保留7天)
- [ ] **监控告警** (CPU、内存、连接数)

### 7.2 启用自动备份

```
1. RDS控制台 → "备份恢复"
2. "备份设置"
   - 备份周期: 每天
   - 备份时间: 凌晨3:00-4:00 (业务低峰期)
   - 日志备份: 开启
   - 备份保留: 7天

3. 点击"确定"
```

### 7.3 监控配置

```
1. "监控与报警" → "报警规则"
2. 创建以下报警:
   - CPU使用率 > 80%
   - 内存使用率 > 85%
   - 连接数使用率 > 80%
   - 磁盘空间使用率 > 80%

3. 配置通知方式: 短信 + 邮件
```

---

## 📊 Step 8: 性能优化

### 8.1 连接池配置

```python
# backend/app/core/database.py 已配置
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,              # 常驻连接数
    max_overflow=40,           # 最大额外连接数
    pool_timeout=30,           # 获取连接超时(秒)
    pool_recycle=3600,         # 连接回收时间(秒)
    pool_pre_ping=True,        # 连接前检查
    echo=settings.DEBUG        # SQL日志
)
```

### 8.2 查询优化

```sql
-- 在RDS中创建索引(可选,已在迁移中定义)
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_health_data_user ON health_data(user_id);
CREATE INDEX idx_health_data_date ON health_data(date DESC);
```

---

## 🚨 常见问题排查

### 问题1: 连接被拒绝

```
错误: could not connect to server: Connection refused

解决:
1. 检查白名单是否包含你的IP
   curl ifconfig.me  # 查看你的公网IP
2. 确认使用正确的地址(内网/外网)
3. 检查端口是否正确(5432)
```

### 问题2: 密码认证失败

```
错误: password authentication failed for user "peakstate_user"

解决:
1. 确认密码是否正确(注意特殊字符需URL编码)
2. 在RDS控制台重置密码
3. 更新.env文件中的密码
```

### 问题3: SSL连接失败

```
错误: SSL connection has been closed unexpectedly

解决:
1. 降低SSL模式: sslmode=require (不验证证书)
2. 或下载并配置CA证书
3. 确认RDS实例SSL已启用
```

### 问题4: 连接数耗尽

```
错误: remaining connection slots are reserved

解决:
1. RDS控制台查看当前连接数
2. 检查是否有连接泄漏
3. 调整 pool_size 和 max_overflow
4. 考虑升级实例规格
```

---

## 📝 完整配置示例

```bash
# .env 完整RDS配置示例

# ============ 阿里云RDS PostgreSQL ============
ALIYUN_RDS_HOST=rm-bp1abc123def456.pg.rds.aliyuncs.com
ALIYUN_RDS_PORT=5432
ALIYUN_RDS_USER=peakstate_user
ALIYUN_RDS_PASSWORD=YourStrongPassword@2025!
ALIYUN_RDS_DATABASE=peakstate
ALIYUN_RDS_SSL_MODE=require
# ALIYUN_RDS_SSL_CA_PATH=./backend/ssl/rds-ca-cert.pem  # 可选

# 自动生成的连接字符串
DATABASE_URL=postgresql://peakstate_user:YourStrongPassword@2025!@rm-bp1abc123def456.pg.rds.aliyuncs.com:5432/peakstate?sslmode=require

# 连接池配置
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

---

## ✅ 配置完成检查清单

- [ ] RDS实例已创建并运行中
- [ ] 数据库 `peakstate` 已创建
- [ ] 用户 `peakstate_user` 已创建并授权
- [ ] 白名单已配置(包含开发机IP或ECS IP)
- [ ] `.env` 文件已更新连接信息
- [ ] `test_rds_connection.py` 测试通过
- [ ] `alembic upgrade head` 执行成功
- [ ] 表结构创建成功(\dt 可见表)
- [ ] SSL连接正常(sslmode=require)
- [ ] 备份策略已配置
- [ ] 监控告警已设置

---

## 🔗 相关资源

- [阿里云RDS PostgreSQL官方文档](https://help.aliyun.com/product/26090.html)
- [PostgreSQL官方文档](https://www.postgresql.org/docs/15/)
- [Alembic数据库迁移文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy异步引擎文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

**配置完成后,请继续前端开发部分!** 🚀
