"""配置相关数据模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConfigBase(BaseModel):
    """配置基础模型"""
    name: str = Field(..., description="配置名称")
    headers: dict[str, str] = Field(..., description="HTTP 请求头")


class ConfigCreate(ConfigBase):
    """创建配置的请求模型"""
    pass


class ConfigUpdate(BaseModel):
    """更新配置的请求模型"""
    name: Optional[str] = None
    headers: Optional[dict[str, str]] = None


class ConfigResponse(ConfigBase):
    """配置响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigListResponse(BaseModel):
    """配置列表响应"""
    total: int
    items: list[ConfigResponse]
