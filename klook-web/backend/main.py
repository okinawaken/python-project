"""FastAPI 应用入口"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import health, config, task, program, websocket, log
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    from app.storage.database import init_db
    await init_db()
    logger.info("✅ 数据库初始化完成")
    logger.info(f"🚀 {settings.app_name} v{settings.version} 启动成功")
    logger.info(f"📍 服务地址: http://{settings.host}:{settings.port}")
    logger.info(f"📚 API 文档: http://{settings.host}:{settings.port}/docs")

    yield

    # 关闭时执行
    logger.info(f"👋 {settings.app_name} 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(config.router, prefix="/api", tags=["配置管理"])
app.include_router(program.router, prefix="/api", tags=["优惠券项目"])
app.include_router(task.router, prefix="/api", tags=["任务管理"])
app.include_router(log.router, prefix="/api", tags=["日志管理"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
