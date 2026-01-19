"""配置存储服务"""
from typing import Optional

from app.models.config import ConfigCreate, ConfigUpdate
from app.storage.models import ConfigDB
from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class ConfigStore:
    """配置存储服务"""

    @staticmethod
    async def create(db: AsyncSession, config: ConfigCreate) -> ConfigDB:
        """创建配置"""
        db_config = ConfigDB(
            name=config.name,
            headers=config.headers
        )
        db.add(db_config)
        await db.flush()
        await db.refresh(db_config)
        logger.info(f"创建配置: {config.name}")
        return db_config

    @staticmethod
    async def get_by_id(db: AsyncSession, config_id: int) -> Optional[ConfigDB]:
        """根据 ID 获取配置"""
        result = await db.execute(
            select(ConfigDB).where(ConfigDB.id == config_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[ConfigDB]:
        """根据名称获取配置"""
        result = await db.execute(
            select(ConfigDB).where(ConfigDB.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[ConfigDB]:
        """获取所有配置"""
        result = await db.execute(select(ConfigDB).order_by(ConfigDB.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update(
            db: AsyncSession,
            config_id: int,
            config_update: ConfigUpdate
    ) -> Optional[ConfigDB]:
        """更新配置"""
        db_config = await ConfigStore.get_by_id(db, config_id)
        if not db_config:
            return None

        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_config, field, value)

        await db.flush()
        await db.refresh(db_config)
        logger.info(f"更新配置: {db_config.name}")
        return db_config

    @staticmethod
    async def delete_by_id(db: AsyncSession, config_id: int) -> bool:
        """删除配置"""
        result = await db.execute(
            delete(ConfigDB).where(ConfigDB.id == config_id)
        )
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"删除配置 ID: {config_id}")
        return deleted

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """统计配置数量"""
        result = await db.execute(select(ConfigDB))
        return len(list(result.scalars().all()))
