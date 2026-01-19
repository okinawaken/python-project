"""日志存储服务"""
from typing import Optional

from app.models.log import LogCreate, LogLevel
from app.storage.models import LogDB
from loguru import logger
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession


class LogStore:
    """日志存储服务"""

    @staticmethod
    async def create(db: AsyncSession, log: LogCreate) -> LogDB:
        """创建日志"""
        db_log = LogDB(
            task_id=log.task_id,
            level=log.level.value,
            message=log.message
        )
        db.add(db_log)
        await db.flush()
        await db.refresh(db_log)
        return db_log

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[LogDB]:
        """根据 ID 获取日志"""
        result = await db.execute(
            select(LogDB).where(LogDB.id == log_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_task_id(
            db: AsyncSession,
            task_id: int,
            level: Optional[LogLevel] = None,
            limit: Optional[int] = None,
            offset: int = 0
    ) -> tuple[list[LogDB], int]:
        """
        根据任务 ID 获取日志

        Args:
            task_id: 任务 ID
            level: 按日志级别筛选
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            (日志列表, 总数)
        """
        # 构建查询
        query = select(LogDB).where(LogDB.task_id == task_id)

        if level:
            query = query.where(LogDB.level == level.value)

        # 获取总数
        count_query = select(func.count()).select_from(query.alias())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 按创建时间倒序排序
        query = query.order_by(LogDB.created_at.desc())

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    @staticmethod
    async def get_all(
            db: AsyncSession,
            task_id: Optional[int] = None,
            level: Optional[LogLevel] = None,
            limit: Optional[int] = None,
            offset: int = 0
    ) -> tuple[list[LogDB], int]:
        """
        获取所有日志

        Args:
            task_id: 按任务 ID 筛选
            level: 按日志级别筛选
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            (日志列表, 总数)
        """
        query = select(LogDB)

        # 筛选条件
        if task_id is not None:
            query = query.where(LogDB.task_id == task_id)

        if level:
            query = query.where(LogDB.level == level.value)

        # 获取总数
        count_query = select(func.count()).select_from(query.alias())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 按创建时间倒序排序
        query = query.order_by(LogDB.created_at.desc())

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    @staticmethod
    async def delete_by_task_id(db: AsyncSession, task_id: int) -> int:
        """删除任务的所有日志"""
        result = await db.execute(
            delete(LogDB).where(LogDB.task_id == task_id)
        )
        deleted_count = result.rowcount
        logger.info(f"删除任务 {task_id} 的 {deleted_count} 条日志")
        return deleted_count

    @staticmethod
    async def delete_by_id(db: AsyncSession, log_id: int) -> bool:
        """删除日志"""
        result = await db.execute(
            delete(LogDB).where(LogDB.id == log_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def delete_all(db: AsyncSession) -> int:
        """删除所有日志"""
        result = await db.execute(delete(LogDB))
        deleted_count = result.rowcount
        logger.warning(f"删除了所有日志，共 {deleted_count} 条")
        return deleted_count
