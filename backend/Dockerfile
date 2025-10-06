# 多阶段构建 - 优化镜像大小

# ============ 基础阶段 ============
FROM python:3.11-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

# ============ 依赖阶段 ============
FROM base as dependencies

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装项目依赖(不包括dev依赖)
RUN poetry install --no-root --without dev

# ============ 开发阶段 ============
FROM dependencies as development

# 安装开发依赖
RUN poetry install --no-root

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 开发环境启动命令(支持热重载)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============ 生产阶段 ============
FROM dependencies as production

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制应用代码
COPY --chown=appuser:appuser . .

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 暴露端口
EXPOSE 8000

# 生产环境启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
