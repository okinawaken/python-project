"""健康检查 API"""
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "klook-web-backend"
    }


@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "Klook Web API",
        "version": "0.1.0",
        "docs": "/docs"
    }
