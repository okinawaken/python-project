"""SQLAlchemy 数据库模型"""
from datetime import datetime

from app.storage.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey


class ConfigDB(Base):
    """配置表"""
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="配置名称")
    headers = Column(JSON, nullable=False, comment="HTTP 请求头（JSON）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class TaskDB(Base):
    """任务表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("configs.id", ondelete="CASCADE"), nullable=False, comment="配置 ID")
    program_uuid = Column(String(50), nullable=False, comment="优惠券项目 UUID")
    target_time = Column(DateTime, nullable=False, comment="抢购目标时间")
    network_compensation = Column(Integer, default=200, comment="网络延迟补偿（毫秒）")
    max_retries = Column(Integer, default=0, comment="最大重试次数")
    retry_interval = Column(Integer, default=0, comment="重试间隔（毫秒）")
    status = Column(String(20), default="pending", comment="任务状态")
    result = Column(JSON, nullable=True, comment="执行结果（JSON）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")


class ProgramDB(Base):
    """优惠券项目表"""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(100), nullable=False, unique=True, comment="项目 UUID")
    name = Column(String(200), nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class LogDB(Base):
    """日志表"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, comment="任务 ID")
    level = Column(String(20), nullable=False, comment="日志级别")
    message = Column(Text, nullable=False, comment="日志消息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
