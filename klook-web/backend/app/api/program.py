"""优惠券项目管理 API"""
from app.models.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramListResponse
)
from app.storage.database import get_db
from app.storage.program_store import ProgramStore
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
        program: ProgramCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    创建新优惠券项目

    - **uuid**: 项目 UUID（唯一）
    - **name**: 项目名称
    - **description**: 项目描述（可选）
    """
    # 检查 UUID 是否已存在
    existing = await ProgramStore.get_by_uuid(db, program.uuid)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目 UUID '{program.uuid}' 已存在"
        )

    db_program = await ProgramStore.create(db, program)
    return db_program


@router.get("/programs", response_model=ProgramListResponse)
async def list_programs(db: AsyncSession = Depends(get_db)):
    """获取所有优惠券项目列表"""
    programs = await ProgramStore.get_all(db)
    return {
        "total": len(programs),
        "items": programs
    }


@router.get("/programs/{program_id}", response_model=ProgramResponse)
async def get_program(
        program_id: int,
        db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取优惠券项目详情"""
    db_program = await ProgramStore.get_by_id(db, program_id)
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {program_id} 不存在"
        )
    return db_program


@router.put("/programs/{program_id}", response_model=ProgramResponse)
async def update_program(
        program_id: int,
        program: ProgramUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    更新优惠券项目

    可以只更新部分字段：
    - **name**: 项目名称
    - **description**: 项目描述
    """
    db_program = await ProgramStore.update(db, program_id, program)
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {program_id} 不存在"
        )
    return db_program


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
        program_id: int,
        db: AsyncSession = Depends(get_db)
):
    """删除优惠券项目"""
    deleted = await ProgramStore.delete_by_id(db, program_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {program_id} 不存在"
        )
    return None
