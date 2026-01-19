# 后端 Dockerfile - 使用 uv 管理依赖
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 同步依赖（不包括开发依赖，使用 --frozen 确保使用锁文件）
RUN uv sync --frozen --no-dev

# 复制后端应用代码
COPY klook-web/backend/app ./app
COPY klook-web/backend/main.py ./main.py

# 暴露端口
EXPOSE 8000

# 启动命令（使用 uv run 运行应用）
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]