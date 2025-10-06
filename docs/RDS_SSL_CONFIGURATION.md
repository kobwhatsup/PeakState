# 🔐 阿里云RDS SSL配置文档

## ✅ 当前配置状态

### 1. SSL连接已启用
- **SSL模式**: `verify-ca` (验证CA证书)
- **CA证书路径**: `backend/ssl/ApsaraDB-CA-Chain.pem`
- **SSL状态**: ✅ 已开启
- **连接加密**: ✅ 已加密

### 2. 数据库连接信息

```bash
# backend/.env
DATABASE_URL=postgresql://peakstate_user:Kob7758258*@pgm-2zenr70bu8bp2xgyqo.pg.rds.aliyuncs.com:5432/peakstate?sslmode=verify-ca&sslrootcert=ssl/ApsaraDB-CA-Chain.pem
```

**连接参数说明**:
- `sslmode=verify-ca`: 验证服务器证书由受信任的CA签发
- `sslrootcert=ssl/ApsaraDB-CA-Chain.pem`: CA证书链文件路径

### 3. SSL模式对比

| SSL模式 | 安全级别 | 说明 | 推荐 |
|---------|---------|------|------|
| `disable` | 无 | 不使用SSL | ❌ 不推荐 |
| `allow` | 低 | 优先非SSL，失败时尝试SSL | ❌ 不推荐 |
| `prefer` | 低 | 优先SSL，失败时使用非SSL | ❌ 不推荐 |
| `require` | 中 | 强制SSL但不验证证书 | ⚠️ 可用但不够安全 |
| `verify-ca` | 高 | 验证CA证书 | ✅ **当前使用** |
| `verify-full` | 最高 | 验证CA证书+主机名 | ✅ 生产环境推荐 |

---

## 📋 配置步骤回顾

### 步骤1: 在阿里云控制台开启SSL

1. 登录阿里云RDS控制台
2. 进入RDS实例 `PeakState_PostgreSQL`
3. 点击左侧菜单 **数据安全性** → **SSL**
4. 点击 **开启SSL** 按钮
5. 下载CA证书 `ApsaraDB-CA-Chain.pem`

### 步骤2: 部署CA证书

```bash
# 创建ssl目录
mkdir -p backend/ssl

# 将下载的证书放入ssl目录
# ApsaraDB-CA-Chain.pem → backend/ssl/
```

### 步骤3: 更新数据库连接配置

```bash
# backend/.env
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库?sslmode=verify-ca&sslrootcert=ssl/ApsaraDB-CA-Chain.pem
```

### 步骤4: 验证SSL连接

```bash
cd backend
source venv/bin/activate
python test_rds_sqlalchemy.py
```

**预期输出**:
```
✅ SSL状态: on
✅ 数据库连接成功!
```

---

## 🔒 安全最佳实践

### 1. 证书管理

- ✅ CA证书已通过`.gitignore`保护 (`.gitignore:110: *.pem`)
- ✅ 证书文件不会被提交到Git仓库
- ⚠️ 证书有效期至: **2026-10-06 15:07:19**
- 📅 建议在2026年9月底更新证书

### 2. 证书更新流程

当证书接近过期时:

1. **下载新证书**:
   - 阿里云RDS控制台 → 数据安全性 → SSL
   - 点击"配置或更新证书"
   - 下载新的CA证书

2. **替换证书文件**:
   ```bash
   # 备份旧证书
   cp backend/ssl/ApsaraDB-CA-Chain.pem backend/ssl/ApsaraDB-CA-Chain.pem.bak

   # 替换为新证书
   cp ~/Downloads/ApsaraDB-CA-Chain.pem backend/ssl/
   ```

3. **重启服务**:
   ```bash
   # 重启后端服务以加载新证书
   # 具体命令取决于部署方式
   ```

### 3. 故障排查

#### 问题: SSL连接失败

**症状**:
```
psycopg2.OperationalError: could not connect to server: SSL error
```

**解决方案**:
1. 检查证书路径是否正确
2. 验证证书文件是否存在且可读
3. 确认RDS实例SSL已开启
4. 检查sslmode参数配置

#### 问题: 证书验证失败

**症状**:
```
psycopg2.OperationalError: SSL error: certificate verify failed
```

**解决方案**:
1. 重新下载CA证书
2. 检查证书是否过期
3. 确认使用的是正确的CA证书链

---

## 🛠️ 测试工具

### 1. Python测试脚本

```bash
cd backend
source venv/bin/activate
python test_rds_sqlalchemy.py
```

### 2. 手动psql测试

```bash
psql "postgresql://peakstate_user:密码@pgm-2zenr70bu8bp2xgyqo.pg.rds.aliyuncs.com:5432/peakstate?sslmode=verify-ca&sslrootcert=backend/ssl/ApsaraDB-CA-Chain.pem"

# 在psql中检查SSL状态
peakstate=> \conninfo
peakstate=> SHOW ssl;
```

### 3. OpenSSL测试

```bash
# 测试SSL握手
openssl s_client -connect pgm-2zenr70bu8bp2xgyqo.pg.rds.aliyuncs.com:5432 -starttls postgres -CAfile backend/ssl/ApsaraDB-CA-Chain.pem
```

---

## 📊 配置检查清单

部署前检查:

- [x] RDS实例已开启SSL
- [x] CA证书已下载到 `backend/ssl/`
- [x] `.env`文件包含SSL配置参数
- [x] SSL证书在`.gitignore`中被排除
- [x] 测试脚本验证SSL连接成功

生产环境额外检查:

- [ ] 使用`verify-full`模式（最高安全级别）
- [ ] 设置证书过期提醒
- [ ] 定期审计数据库连接日志
- [ ] 配置数据库连接池SSL参数

---

## 📚 相关文档

- [阿里云RDS SSL官方文档](https://help.aliyun.com/document_detail/95715.html)
- [PostgreSQL SSL Support](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [psycopg2 SSL连接](https://www.psycopg.org/docs/module.html#psycopg2.connect)
- 项目安全文档: [SECURITY.md](../SECURITY.md)

---

## ✅ 配置完成确认

**日期**: 2025-10-06
**配置人**: Claude Code
**RDS实例**: PeakState_PostgreSQL
**SSL状态**: ✅ 已启用
**证书有效期**: 2026-10-06
**连接测试**: ✅ 通过
