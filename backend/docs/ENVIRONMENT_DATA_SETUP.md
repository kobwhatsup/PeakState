# 环境数据采集配置指南

## 概述

环境数据采集是PeakState精力管理系统的重要组成部分。通过采集天气、温度、气压、湿度、空气质量等环境数据，系统可以更准确地预测和分析用户的精力状态。

## 架构设计

```
┌─────────────────┐
│  Weather API    │  (OpenWeather / 和风天气)
│  (Third-party)  │
└────────┬────────┘
         │ HTTP API
         ▼
┌─────────────────┐
│ WeatherService  │  (app/services/weather.py)
│  - 获取天气数据  │
│  - 数据转换     │
│  - 数据存储     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Celery Tasks    │  (app/tasks/environment.py)
│  - 定时采集     │
│  - 批量处理     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ EnvironmentData │  (Database Table)
│  - user_id      │
│  - location     │
│  - temperature  │
│  - weather      │
│  - pressure     │
│  - humidity     │
│  - air_quality  │
└─────────────────┘
```

## 1. 配置天气API

### 选项A: OpenWeather API (推荐)

1. 注册OpenWeather账号：https://openweathermap.org/api

2. 获取免费API密钥（每月60,000次调用）

3. 在 `.env` 文件中配置：
   ```bash
   WEATHER_API_KEY=your_openweather_api_key
   WEATHER_PROVIDER=openweather
   ```

### 选项B: 和风天气 API (国内推荐)

1. 注册和风天气账号：https://dev.qweather.com/

2. 获取免费API密钥（每天1,000次调用）

3. 在 `.env` 文件中配置：
   ```bash
   WEATHER_API_KEY=your_qweather_api_key
   WEATHER_PROVIDER=qweather
   ```

## 2. 安装依赖

确保已安装所有必需的Python包：

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

主要依赖：
- `httpx==0.28.1` - HTTP客户端，用于API请求
- `celery==5.4.0` - 异步任务队列
- `redis==5.2.1` - Celery消息代理

## 3. 启动Redis

Celery需要Redis作为消息代理：

```bash
# macOS (Homebrew)
brew services start redis

# 或使用Docker
docker run -d -p 6379:6379 redis:latest
```

验证Redis运行状态：
```bash
redis-cli ping
# 应该返回: PONG
```

## 4. 启动Celery Worker

在后台启动Celery worker来处理定时任务：

```bash
cd backend
source venv/bin/activate

# 启动worker
celery -A app.celery_app worker --loglevel=info

# 在另一个终端启动定时任务调度器
celery -A app.celery_app beat --loglevel=info
```

### 使用Supervisor管理Celery (生产环境推荐)

1. 安装Supervisor：
   ```bash
   pip install supervisor
   ```

2. 创建配置文件 `/etc/supervisor/conf.d/celery.conf`：
   ```ini
   [program:celery_worker]
   command=/path/to/venv/bin/celery -A app.celery_app worker --loglevel=info
   directory=/path/to/PeakState/backend
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/celery/worker.err.log
   stdout_logfile=/var/log/celery/worker.out.log

   [program:celery_beat]
   command=/path/to/venv/bin/celery -A app.celery_app beat --loglevel=info
   directory=/path/to/PeakState/backend
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/celery/beat.err.log
   stdout_logfile=/var/log/celery/beat.out.log
   ```

3. 启动Supervisor：
   ```bash
   supervisorctl reread
   supervisorctl update
   supervisorctl start all
   ```

## 5. 定时任务配置

在 `app/celery_app.py` 中已配置以下定时任务：

### 环境数据采集
- **任务**: `collect-environment-data`
- **频率**: 每小时整点执行
- **功能**: 为所有活跃用户采集当前位置的环境数据

### 早间简报 (Phase 2)
- **任务**: `morning-briefing`
- **时间**: 每天 7:00
- **功能**: 发送今日精力预测和建议

### 晚间回顾 (Phase 2)
- **任务**: `evening-review`
- **时间**: 每天 22:00
- **功能**: 回顾今日精力状态，提供改进建议

## 6. 手动触发任务

可以通过Celery API手动触发任务进行测试：

```python
from app.tasks.environment import collect_environment_data_for_user

# 为单个用户采集环境数据
result = collect_environment_data_for_user.delay(
    user_id="your_user_id",
    location="Beijing"
)

# 查看任务状态
print(result.status)
print(result.result)
```

或通过FastAPI endpoint：

```bash
# TODO: 后续添加管理API endpoint
POST /api/v1/admin/tasks/environment/collect
{
  "user_id": "xxx",
  "location": "Beijing"
}
```

## 7. 监控和日志

### 查看Celery任务日志

```bash
# Worker日志
tail -f /var/log/celery/worker.out.log

# Beat调度器日志
tail -f /var/log/celery/beat.out.log
```

### 使用Flower监控Celery

Flower是Celery的Web监控工具：

```bash
pip install flower

celery -A app.celery_app flower --port=5555
```

访问 http://localhost:5555 查看任务执行情况。

### 数据库查询

检查环境数据是否正常采集：

```sql
-- 查看最近采集的环境数据
SELECT
    user_id,
    location,
    temperature,
    weather,
    air_quality,
    recorded_at
FROM environment_data
ORDER BY recorded_at DESC
LIMIT 10;

-- 统计每个用户的数据采集次数
SELECT
    user_id,
    COUNT(*) as data_count,
    MIN(recorded_at) as first_record,
    MAX(recorded_at) as last_record
FROM environment_data
GROUP BY user_id;
```

## 8. API调用限制

### OpenWeather 免费版限制
- 每分钟: 60次
- 每月: 60,000次
- 建议策略: 每小时采集一次，支持约1000个活跃用户

### 和风天气免费版限制
- 每天: 1,000次
- 建议策略: 每2-3小时采集一次，或只在用户活跃时采集

### 优化建议

1. **用户活跃度过滤**：只为最近7天有活动的用户采集
2. **位置聚合**：同一城市的用户共享环境数据
3. **缓存机制**：1小时内同一位置的数据复用
4. **降级策略**：API超限时使用历史数据估算

## 9. 故障排查

### 问题: Celery任务不执行

**检查项**：
1. Redis是否运行？`redis-cli ping`
2. Celery worker是否启动？`celery -A app.celery_app inspect active`
3. Celery beat是否启动？检查beat日志

**解决方法**：
```bash
# 重启Redis
sudo systemctl restart redis

# 重启Celery
supervisorctl restart celery_worker
supervisorctl restart celery_beat
```

### 问题: 天气API返回401/403错误

**原因**: API密钥无效或过期

**解决方法**：
1. 检查 `.env` 中的 `WEATHER_API_KEY` 是否正确
2. 登录天气服务提供商网站验证密钥状态
3. 检查API调用次数是否超限

### 问题: 环境数据未保存到数据库

**检查项**：
1. 数据库连接是否正常？
2. `environment_data` 表是否存在？
3. 查看应用日志中的错误信息

**解决方法**：
```bash
# 运行数据库迁移
cd backend
alembic upgrade head

# 检查表结构
psql -h your_host -U your_user -d peakstate -c "\d environment_data"
```

## 10. 测试

运行环境数据集成测试：

```bash
cd backend
source venv/bin/activate
python3 test_environment_integration.py
```

测试会验证：
1. ✅ 天气API调用是否正常
2. ✅ 环境数据存储是否成功
3. ✅ 精力预测是否集成环境数据

## 11. 后续优化方向 (Phase 2+)

1. **智能采集策略**
   - 根据用户活跃时间调整采集频率
   - 位置变化检测，触发实时采集
   - 天气剧烈变化时增加采集频率

2. **数据分析**
   - 环境因素与精力状态的相关性分析
   - 个性化环境敏感度建模
   - 天气预报集成，提前预测精力影响

3. **扩展数据源**
   - 光照强度 (需要硬件集成或估算)
   - 噪音水平 (城市噪音数据)
   - 花粉指数 (过敏影响)
   - 紫外线指数

4. **多地点支持**
   - 家庭/工作地点自动识别
   - 出差/旅行地点跟踪
   - 时区自动调整

## 参考资料

- [OpenWeather API文档](https://openweathermap.org/api)
- [和风天气API文档](https://dev.qweather.com/docs/api/)
- [Celery官方文档](https://docs.celeryproject.org/)
- [Flower监控工具](https://flower.readthedocs.io/)
