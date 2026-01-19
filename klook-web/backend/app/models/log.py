"""日志相关数据模型"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogBase(BaseModel):
    """日志基础模型"""
    task_id: int = Field(..., description="任务 ID")
    level: LogLevel = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息")


class LogCreate(LogBase):
    """创建日志的请求模型"""
    pass


class LogResponse(LogBase):
    """日志响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """日志列表响应模型"""
    total: int = Field(..., description="总数")
    logs: list[LogResponse] = Field(..., description="日志列表")
