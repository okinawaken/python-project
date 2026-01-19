"""任务相关数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"  # 等待中
    COUNTDOWN = "countdown"  # 倒计时中
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class ProgramType(str, Enum):
    """优惠券类型（预设）"""
    HOTEL_50_OFF = "8a6d71f"  # 酒店产品_5折优惠券
    DISNEY_30_OFF = "be10a4c"  # 香港迪士尼立减30元券


class TaskBase(BaseModel):
    """任务基础模型"""
    config_id: int = Field(..., description="配置 ID")
    program_uuid: str = Field(..., description="优惠券项目 UUID")
    target_time: datetime = Field(..., description="抢购目标时间")
    network_compensation: int = Field(default=250, ge=0, le=2000, description="网络延迟补偿（毫秒）")
    max_retries: int = Field(default=3, ge=1, le=20, description="最大重试次数")
    retry_interval: int = Field(default=500, ge=0, le=5000, description="重试间隔（毫秒）")


class TaskCreate(TaskBase):
    """创建任务的请求模型"""
    pass


class TaskUpdate(BaseModel):
    """更新任务的请求模型"""
    target_time: Optional[datetime] = None
    network_compensation: Optional[int] = None
    max_retries: Optional[int] = None
    retry_interval: Optional[int] = None
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int
    status: TaskStatus
    result: Optional[dict] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: list[TaskResponse]


class TaskExecutionLog(BaseModel):
    """任务执行日志"""
    task_id: int
    level: Literal["info", "warning", "error"]
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
