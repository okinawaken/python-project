"""优惠券项目存储层"""
from typing import Optional

from app.models.program import ProgramCreate, ProgramUpdate
from app.storage.models import ProgramDB
from loguru import logger
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession


class ProgramStore:
    """优惠券项目存储操作"""

    @staticmethod
    async def create(db: AsyncSession, program: ProgramCreate) -> ProgramDB:
        """创建优惠券项目"""
        db_program = ProgramDB(
            uuid=program.uuid,
            name=program.name,
            description=program.description
        )
        db.add(db_program)
        await db.commit()
        await db.refresh(db_program)
        logger.info(f"创建优惠券项目: {program.name} (UUID: {program.uuid})")
        return db_program

    @staticmethod
    async def get_all(db: AsyncSession) -> list[ProgramDB]:
        """获取所有优惠券项目"""
        stmt = select(ProgramDB).order_by(ProgramDB.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, program_id: int) -> Optional[ProgramDB]:
        """根据 ID 获取优惠券项目"""
        stmt = select(ProgramDB).where(ProgramDB.id == program_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_uuid(db: AsyncSession, uuid: str) -> Optional[ProgramDB]:
        """根据 UUID 获取优惠券项目"""
        stmt = select(ProgramDB).where(ProgramDB.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
            db: AsyncSession,
            program_id: int,
            program: ProgramUpdate
    ) -> Optional[ProgramDB]:
        """更新优惠券项目"""
        # 构建更新数据
        update_data = program.model_dump(exclude_unset=True)
        if not update_data:
            return await ProgramStore.get_by_id(db, program_id)

        stmt = (
            update(ProgramDB)
            .where(ProgramDB.id == program_id)
            .values(**update_data)
        )
        result = await db.execute(stmt)

        if result.rowcount == 0:
            return None

        await db.commit()
        logger.info(f"更新优惠券项目 ID: {program_id}")
        return await ProgramStore.get_by_id(db, program_id)

    @staticmethod
    async def delete_by_id(db: AsyncSession, program_id: int) -> bool:
        """删除优惠券项目"""
        stmt = delete(ProgramDB).where(ProgramDB.id == program_id)
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount > 0:
            logger.info(f"删除优惠券项目 ID: {program_id}")
            return True
        return False

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """统计优惠券项目数量"""
        stmt = select(func.count()).select_from(ProgramDB)
        result = await db.execute(stmt)
        return result.scalar_one()
