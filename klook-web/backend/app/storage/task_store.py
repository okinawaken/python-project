"""任务存储服务"""
from datetime import datetime
from typing import Optional

from app.models.task import TaskCreate, TaskUpdate, TaskStatus
from app.storage.models import TaskDB
from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class TaskStore:
    """任务存储服务"""

    @staticmethod
    async def create(db: AsyncSession, task: TaskCreate) -> TaskDB:
        """创建任务"""
        db_task = TaskDB(
            config_id=task.config_id,
            program_uuid=task.program_uuid,
            target_time=task.target_time,
            network_compensation=task.network_compensation,
            max_retries=task.max_retries,
            retry_interval=task.retry_interval,
            status=TaskStatus.PENDING.value
        )
        db.add(db_task)
        await db.flush()
        await db.refresh(db_task)
        logger.info(f"创建任务 ID: {db_task.id}, 目标时间: {task.target_time}")
        return db_task

    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int) -> Optional[TaskDB]:
        """根据 ID 获取任务"""
        result = await db.execute(
            select(TaskDB).where(TaskDB.id == task_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
            db: AsyncSession,
            status: Optional[TaskStatus] = None,
            limit: Optional[int] = None
    ) -> list[TaskDB]:
        """
        获取所有任务

        Args:
            status: 按状态筛选
            limit: 限制返回数量
        """
        query = select(TaskDB).order_by(TaskDB.created_at.desc())

        if status:
            query = query.where(TaskDB.status == status.value)

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_config(db: AsyncSession, config_id: int) -> list[TaskDB]:
        """获取指定配置的所有任务"""
        result = await db.execute(
            select(TaskDB)
            .where(TaskDB.config_id == config_id)
            .order_by(TaskDB.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(
            db: AsyncSession,
            task_id: int,
            task_update: TaskUpdate
    ) -> Optional[TaskDB]:
        """更新任务"""
        db_task = await TaskStore.get_by_id(db, task_id)
        if not db_task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and isinstance(value, TaskStatus):
                setattr(db_task, field, value.value)
            else:
                setattr(db_task, field, value)

        await db.flush()
        await db.refresh(db_task)
        logger.info(f"更新任务 ID: {task_id}")
        return db_task

    @staticmethod
    async def update_status(
            db: AsyncSession,
            task_id: int,
            status: TaskStatus,
            result: Optional[dict] = None
    ) -> Optional[TaskDB]:
        """
        更新任务状态

        Args:
            task_id: 任务 ID
            status: 新状态
            result: 执行结果（可选）
        """
        db_task = await TaskStore.get_by_id(db, task_id)
        if not db_task:
            return None

        db_task.status = status.value

        # 更新时间戳
        if status == TaskStatus.RUNNING and not db_task.started_at:
            db_task.started_at = datetime.now()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            db_task.completed_at = datetime.now()

        # 更新结果
        if result is not None:
            db_task.result = result

        await db.flush()
        await db.refresh(db_task)
        logger.info(f"任务 ID {task_id} 状态更新为: {status.value}")
        return db_task

    @staticmethod
    async def delete_by_id(db: AsyncSession, task_id: int) -> bool:
        """删除任务"""
        result = await db.execute(
            delete(TaskDB).where(TaskDB.id == task_id)
        )
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"删除任务 ID: {task_id}")
        return deleted

    @staticmethod
    async def count(db: AsyncSession, status: Optional[TaskStatus] = None) -> int:
        """统计任务数量"""
        query = select(TaskDB)
        if status:
            query = query.where(TaskDB.status == status.value)

        result = await db.execute(query)
        return len(list(result.scalars().all()))

    @staticmethod
    async def get_pending_tasks(db: AsyncSession) -> list[TaskDB]:
        """获取所有待执行的任务（pending 或 countdown 状态）"""
        result = await db.execute(
            select(TaskDB)
            .where(TaskDB.status.in_([TaskStatus.PENDING.value, TaskStatus.COUNTDOWN.value]))
            .order_by(TaskDB.target_time)
        )
        return list(result.scalars().all())
