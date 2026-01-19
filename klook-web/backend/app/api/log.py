"""日志管理 API"""
from typing import Optional

from app.models.log import (
    LogCreate,
    LogResponse,
    LogListResponse,
    LogLevel
)
from app.storage.database import get_db
from app.storage.log_store import LogStore
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
        log: LogCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    创建日志

    - **task_id**: 任务 ID
    - **level**: 日志级别 (debug, info, warning, error, critical)
    - **message**: 日志消息
    """
    db_log = await LogStore.create(db, log)
    await db.commit()
    return db_log


@router.get("/logs", response_model=LogListResponse)
async def get_logs(
        task_id: Optional[int] = Query(None, description="按任务 ID 筛选"),
        level: Optional[LogLevel] = Query(None, description="按日志级别筛选"),
        limit: int = Query(100, ge=1, le=1000, description="每页数量"),
        offset: int = Query(0, ge=0, description="偏移量"),
        db: AsyncSession = Depends(get_db)
):
    """
    获取日志列表

    支持分页和筛选：
    - **task_id**: 按任务 ID 筛选（可选）
    - **level**: 按日志级别筛选（可选）
    - **limit**: 每页数量（1-1000，默认100）
    - **offset**: 偏移量（默认0）
    """
    logs, total = await LogStore.get_all(
        db,
        task_id=task_id,
        level=level,
        limit=limit,
        offset=offset
    )

    return LogListResponse(
        total=total,
        logs=logs
    )


@router.get("/logs/{log_id}", response_model=LogResponse)
async def get_log(
        log_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    获取单个日志

    - **log_id**: 日志 ID
    """
    log = await LogStore.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"日志 ID {log_id} 不存在"
        )
    return log


@router.get("/tasks/{task_id}/logs", response_model=LogListResponse)
async def get_task_logs(
        task_id: int,
        level: Optional[LogLevel] = Query(None, description="按日志级别筛选"),
        limit: int = Query(100, ge=1, le=1000, description="每页数量"),
        offset: int = Query(0, ge=0, description="偏移量"),
        db: AsyncSession = Depends(get_db)
):
    """
    获取任务的日志列表

    - **task_id**: 任务 ID
    - **level**: 按日志级别筛选（可选）
    - **limit**: 每页数量（1-1000，默认100）
    - **offset**: 偏移量（默认0）
    """
    logs, total = await LogStore.get_by_task_id(
        db,
        task_id=task_id,
        level=level,
        limit=limit,
        offset=offset
    )

    return LogListResponse(
        total=total,
        logs=logs
    )


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
        log_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    删除日志

    - **log_id**: 日志 ID
    """
    success = await LogStore.delete_by_id(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"日志 ID {log_id} 不存在"
        )
    await db.commit()


@router.delete("/tasks/{task_id}/logs", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_logs(
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    删除任务的所有日志

    - **task_id**: 任务 ID
    """
    await LogStore.delete_by_task_id(db, task_id)
    await db.commit()


@router.delete("/logs", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_logs(db: AsyncSession = Depends(get_db)):
    """
    删除所有日志

    ⚠️ 警告：此操作将删除系统中的所有日志，不可恢复！
    """
    await LogStore.delete_all(db)
    await db.commit()
