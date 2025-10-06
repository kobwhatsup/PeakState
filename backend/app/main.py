"""
PeakState FastAPI主应用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator
import time

from app.core.config import settings
from app.core.database import init_db, close_db

# 导入路由
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化资源,关闭时清理资源
    """
    # 启动时执行
    print("🚀 Starting PeakState Backend...")

    # 初始化数据库 (暂时禁用以测试API)
    # if settings.is_development:
    #     await init_db()
    #     print("✅ Database initialized")

    # 这里可以添加其他初始化逻辑
    # - 预加载AI模型
    # - 连接消息队列
    # - 初始化缓存

    print(f"✅ PeakState Backend started on {settings.APP_ENV} environment")

    yield  # 应用运行中

    # 关闭时执行
    print("🛑 Shutting down PeakState Backend...")
    await close_db()
    print("✅ Database connections closed")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="AI精力管理教练 - 后端API服务",
    version="1.0.0",
    docs_url=settings.DOCS_URL if settings.DOCS_ENABLED else None,
    redoc_url=settings.REDOC_URL if settings.DOCS_ENABLED else None,
    openapi_url=f"{settings.api_prefix}/openapi.json" if settings.DOCS_ENABLED else None,
    lifespan=lifespan
)


# ============ 中间件配置 ============

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间到响应头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Prometheus监控
if settings.PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app)


# ============ 异常处理 ============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证错误处理
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "errors": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理
    """
    # 生产环境隐藏详细错误信息
    detail = str(exc) if settings.is_development else "服务器内部错误"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器错误",
            "detail": detail
        }
    )


# ============ 基础路由 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "message": "Welcome to PeakState API 🎯"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "timestamp": time.time()
    }


@app.get(f"{settings.api_prefix}/info")
async def api_info():
    """API信息"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "api_version": settings.API_VERSION,
        "environment": settings.APP_ENV,
        "features": {
            "ai_models": {
                "local": settings.USE_LOCAL_MODEL,
                "openai": bool(settings.OPENAI_API_KEY),
                "claude": bool(settings.ANTHROPIC_API_KEY)
            },
            "mcp_servers": {
                "health": f"http://{settings.MCP_SERVER_HOST}:{settings.MCP_HEALTH_SERVER_PORT}",
                "calendar": f"http://{settings.MCP_SERVER_HOST}:{settings.MCP_CALENDAR_SERVER_PORT}"
            },
            "rag_enabled": True,
            "encryption_enabled": settings.DATA_ENCRYPTION_ENABLED
        }
    }


# ============ 注册API路由 ============
app.include_router(
    api_router,
    prefix=settings.api_prefix
)

# TODO: 后续添加更多路由
# app.include_router(
#     chat.router,
#     prefix=f"{settings.api_prefix}/chat",
#     tags=["AI对话"]
# )
#
# app.include_router(
#     health.router,
#     prefix=f"{settings.api_prefix}/health",
#     tags=["健康数据"]
# )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
