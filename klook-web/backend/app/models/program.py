"""优惠券项目相关数据模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProgramBase(BaseModel):
    """优惠券项目基础模型"""
    uuid: str = Field(..., description="项目 UUID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class ProgramCreate(ProgramBase):
    """创建优惠券项目的请求模型"""
    pass


class ProgramUpdate(BaseModel):
    """更新优惠券项目的请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None


class ProgramResponse(ProgramBase):
    """优惠券项目响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgramListResponse(BaseModel):
    """优惠券项目列表响应"""
    total: int
    items: list[ProgramResponse]
