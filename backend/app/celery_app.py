"""
Celery应用配置
用于异步任务处理
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import get_settings

settings = get_settings()

# 创建Celery应用
celery_app = Celery(
    "peakstate",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.environment",
        "app.tasks.briefing"
    ]
)

# Celery配置
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=["json"],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    # 任务结果过期时间（1天）
    result_expires=86400,
    # 任务执行时间限制
    task_time_limit=300,  # 5分钟硬限制
    task_soft_time_limit=240,  # 4分钟软限制
    # 任务重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Worker配置
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每小时采集环境数据
    "collect-environment-data": {
        "task": "app.tasks.environment.collect_environment_data_for_all_users",
        "schedule": crontab(minute=0),  # 每小时整点执行
        "options": {
            "expires": 3300,  # 55分钟内有效
        }
    },
    # 早间简报（每天7点）
    "morning-briefing": {
        "task": "app.tasks.briefing.send_morning_briefing",
        "schedule": crontab(hour=7, minute=0),  # 每天7:00执行
        "options": {
            "expires": 7200,  # 2小时内有效
        }
    },
    # 晚间回顾（每天22点）
    "evening-review": {
        "task": "app.tasks.briefing.send_evening_review",
        "schedule": crontab(hour=22, minute=0),  # 每天22:00执行
        "options": {
            "expires": 7200,  # 2小时内有效
        }
    },
}


if __name__ == "__main__":
    celery_app.start()
