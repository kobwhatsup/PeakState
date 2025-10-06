"""
核心配置管理
使用Pydantic Settings进行环境变量管理和验证
"""

from typing import List, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ============ 应用基础配置 ============
    APP_NAME: str = "PeakState"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # ============ 数据库配置 ============
    DATABASE_URL: str = Field(
        default="postgresql://peakstate_user:password@localhost:5432/peakstate",
        description="PostgreSQL连接URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Aliyun RDS配置
    ALIYUN_RDS_HOST: Optional[str] = None
    ALIYUN_RDS_PORT: int = 5432
    ALIYUN_RDS_USER: Optional[str] = None
    ALIYUN_RDS_PASSWORD: Optional[str] = None
    ALIYUN_RDS_DATABASE: Optional[str] = None
    ALIYUN_RDS_SSL_MODE: str = "require"  # require | verify-ca | verify-full
    ALIYUN_RDS_SSL_CA_PATH: Optional[str] = None

    # ============ Redis配置 ============
    REDIS_URL: str = Field(
        default="redis://:password@localhost:6379/0",
        description="Redis连接URL"
    )
    REDIS_CACHE_DB: int = 1
    REDIS_CELERY_DB: int = 0

    # ============ Qdrant向量数据库 ============
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "health_knowledge"
    QDRANT_EMBEDDING_DIM: int = 384  # MiniLM模型维度

    # ============ AI模型配置 ============
    # OpenAI - 使用最新GPT-5系列
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API密钥")
    OPENAI_MODEL_MAIN: str = "gpt-5"  # GPT-5 旗舰模型
    OPENAI_MODEL_MINI: str = "gpt-5-nano"  # GPT-5 nano 最快速、最经济
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    # Anthropic Claude - 使用最新Sonnet 4系列
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API密钥")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"  # Claude Sonnet 4 (2025-05-14)
    ANTHROPIC_MAX_TOKENS: int = 8000  # Claude Sonnet 4支持更大输出

    # 本地模型
    LOCAL_MODEL_PATH: str = "./models/phi-3.5-mini-instruct"
    LOCAL_MODEL_NAME: str = "microsoft/Phi-3.5-mini-instruct"
    USE_LOCAL_MODEL: bool = True
    LOCAL_MODEL_DEVICE: str = Field(default="cpu", pattern="^(cpu|cuda|mps)$")

    # AI路由策略
    AI_ROUTE_LOCAL_THRESHOLD: int = Field(default=3, ge=0, le=10)
    AI_ROUTE_MINI_THRESHOLD: int = Field(default=6, ge=0, le=10)
    AI_COST_OPTIMIZATION: bool = True

    # ============ 安全配置 ============
    JWT_SECRET_KEY: str = Field(
        default="dev_secret_key_change_in_production_min_32_chars",
        min_length=32
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ENCRYPTION_KEY: str = Field(default="", min_length=32)
    DATA_ENCRYPTION_ENABLED: bool = True

    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:19006"]
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ============ 云服务配置 ============
    # 阿里云OSS
    ALIYUN_OSS_ACCESS_KEY_ID: Optional[str] = None
    ALIYUN_OSS_ACCESS_KEY_SECRET: Optional[str] = None
    ALIYUN_OSS_BUCKET_NAME: Optional[str] = None
    ALIYUN_OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"

    # Sentry错误追踪
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None  # 默认使用APP_ENV

    # ============ 第三方服务 ============
    APPLE_SHARED_SECRET: Optional[str] = None
    APPLE_BUNDLE_ID: str = "com.peakstate.app"
    GOOGLE_PLAY_BILLING_KEY: Optional[str] = None

    # ============ 业务配置 ============
    SUBSCRIPTION_PRICE_MONTHLY: int = 30000  # 300元(分)
    SUBSCRIPTION_PRICE_YEARLY: int = 299800  # 2998元(分)
    FREE_TRIAL_DAYS: int = 7

    MORNING_BRIEFING_TIME: str = "07:00"
    EVENING_REVIEW_TIME: str = "22:00"
    TIMEZONE: str = "Asia/Shanghai"

    HEALTH_DATA_RETENTION_DAYS: int = 180
    SYNC_INTERVAL_MINUTES: int = 30

    # ============ MCP服务器配置 ============
    MCP_HEALTH_SERVER_PORT: int = 8001
    MCP_CALENDAR_SERVER_PORT: int = 8002
    MCP_SERVER_HOST: str = "0.0.0.0"

    # ============ Celery配置 ============
    CELERY_BROKER_URL: Optional[str] = None  # 默认使用REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # 默认使用REDIS_URL
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "Asia/Shanghai"

    # ============ 监控配置 ============
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    # ============ 开发工具 ============
    RELOAD: bool = True
    DOCS_ENABLED: bool = True
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    PROFILING_ENABLED: bool = False
    SQL_ECHO: bool = False

    # ============ 辅助属性 ============
    @property
    def api_prefix(self) -> str:
        """API路径前缀"""
        return f"/api/{self.API_VERSION}"

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.APP_ENV == "development"

    @property
    def database_pool_config(self) -> dict:
        """数据库连接池配置"""
        return {
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "echo": self.SQL_ECHO,
        }

    @model_validator(mode='after')
    def set_defaults(self):
        """设置依赖于其他字段的默认值"""
        if self.CELERY_BROKER_URL is None:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if self.CELERY_RESULT_BACKEND is None:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        if self.SENTRY_ENVIRONMENT is None:
            self.SENTRY_ENVIRONMENT = self.APP_ENV
        return self


# 全局配置实例
settings = Settings()


# 开发环境下打印配置(敏感信息脱敏)
if settings.is_development:
    import json
    config_dict = settings.model_dump()

    # 脱敏处理
    sensitive_keys = ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]
    for key in config_dict:
        if any(sensitive in key.upper() for sensitive in sensitive_keys):
            if config_dict[key] and isinstance(config_dict[key], str):
                config_dict[key] = config_dict[key][:8] + "..." if len(config_dict[key]) > 8 else "***"

    print("\n" + "="*50)
    print("PeakState Configuration (Development)")
    print("="*50)
    print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    print("="*50 + "\n")
