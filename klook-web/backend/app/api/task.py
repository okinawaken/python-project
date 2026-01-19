"""任务管理 API"""
from datetime import datetime

from app.models.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatus
)
from app.storage.config_store import ConfigStore
from app.storage.database import get_db
from app.storage.task_store import TaskStore
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        task: TaskCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    创建新任务

    - **config_id**: 配置 ID（必须存在）
    - **program_uuid**: 优惠券项目 UUID
    - **target_time**: 抢购目标时间
    - **network_compensation**: 网络延迟补偿（毫秒，默认200）
    """
    # 验证配置是否存在
    config = await ConfigStore.get_by_id(db, task.config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 ID {task.config_id} 不存在"
        )

    # 验证目标时间不能是过去时间
    if task.target_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标时间必须是未来时间"
        )

    db_task = await TaskStore.create(db, task)
    return db_task


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
        status: str = None,
        limit: int = None,
        db: AsyncSession = Depends(get_db)
):
    """
    获取任务列表

    - **status**: 按状态筛选（pending/countdown/running/completed/failed/cancelled）
    - **limit**: 限制返回数量
    """
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {status}"
            )

    tasks = await TaskStore.get_all(db, status=task_status, limit=limit)
    return {
        "total": len(tasks),
        "items": tasks
    }


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取任务详情"""
    db_task = await TaskStore.get_by_id(db, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    return db_task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task: TaskUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    更新任务

    可以只更新部分字段：
    - **target_time**: 目标时间
    - **network_compensation**: 网络延迟补偿
    - **status**: 任务状态
    """
    # 如果更新目标时间，验证不能是过去时间
    if task.target_time and task.target_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标时间必须是未来时间"
        )

    db_task = await TaskStore.update(db, task_id, task)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    return db_task


@router.post("/tasks/{task_id}/start")
async def start_task(
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    启动任务

    启动任务执行器，开始倒计时和抢购流程
    """
    from app.services.task_executor import task_executor

    db_task = await TaskStore.get_by_id(db, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )

    if db_task.status != TaskStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"只能启动待执行(pending)状态的任务，当前状态: {db_task.status}"
        )

    # 验证目标时间
    if db_task.target_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标时间已过，无法启动任务"
        )

    # 启动任务执行器
    success = await task_executor.start_task(task_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="任务启动失败"
        )

    return {
        "message": "任务已启动，通过 WebSocket 可以实时查看进度",
        "task_id": task_id,
        "websocket_url": f"/api/ws/tasks/{task_id}"
    }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    取消任务

    停止任务执行器，取消倒计时
    """
    from app.services.task_executor import task_executor

    db_task = await TaskStore.get_by_id(db, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )

    if db_task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法取消已完成/失败/已取消的任务，当前状态: {db_task.status}"
        )

    # 取消任务执行器
    await task_executor.cancel_task(task_id)

    # 更新任务状态
    db_task = await TaskStore.update_status(db, task_id, TaskStatus.CANCELLED)

    return {
        "message": "任务已取消",
        "task_id": task_id,
        "status": db_task.status
    }


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    删除任务

    注意：只能删除未启动或已完成的任务
    """
    db_task = await TaskStore.get_by_id(db, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )

    if db_task.status in [TaskStatus.COUNTDOWN.value, TaskStatus.RUNNING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法删除正在执行的任务，请先取消任务。当前状态: {db_task.status}"
        )

    deleted = await TaskStore.delete_by_id(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    return None


@router.get("/tasks/stats/summary")
async def get_task_stats(db: AsyncSession = Depends(get_db)):
    """
    获取任务统计信息

    返回各状态的任务数量
    """
    total = await TaskStore.count(db)
    pending = await TaskStore.count(db, TaskStatus.PENDING)
    countdown = await TaskStore.count(db, TaskStatus.COUNTDOWN)
    running = await TaskStore.count(db, TaskStatus.RUNNING)
    completed = await TaskStore.count(db, TaskStatus.COMPLETED)
    failed = await TaskStore.count(db, TaskStatus.FAILED)
    cancelled = await TaskStore.count(db, TaskStatus.CANCELLED)

    return {
        "total": total,
        "by_status": {
            "pending": pending,
            "countdown": countdown,
            "running": running,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled
        }
    }
