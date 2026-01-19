"""配置管理 API"""
from app.models.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigListResponse
)
from app.storage.config_store import ConfigStore
from app.storage.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/configs", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
        config: ConfigCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    创建新配置

    - **name**: 配置名称（唯一）
    - **headers**: HTTP 请求头（JSON 对象）
    """
    # 检查名称是否已存在
    existing = await ConfigStore.get_by_name(db, config.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置名称 '{config.name}' 已存在"
        )

    db_config = await ConfigStore.create(db, config)
    return db_config


@router.get("/configs", response_model=ConfigListResponse)
async def list_configs(db: AsyncSession = Depends(get_db)):
    """获取所有配置列表"""
    configs = await ConfigStore.get_all(db)
    return {
        "total": len(configs),
        "items": configs
    }


@router.get("/configs/{config_id}", response_model=ConfigResponse)
async def get_config(
        config_id: int,
        db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取配置详情"""
    db_config = await ConfigStore.get_by_id(db, config_id)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 ID {config_id} 不存在"
        )
    return db_config


@router.put("/configs/{config_id}", response_model=ConfigResponse)
async def update_config(
        config_id: int,
        config: ConfigUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    更新配置

    可以只更新部分字段：
    - **name**: 配置名称
    - **headers**: HTTP 请求头
    """
    # 如果要更新名称，检查新名称是否已被其他配置使用
    if config.name:
        existing = await ConfigStore.get_by_name(db, config.name)
        if existing and existing.id != config_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置名称 '{config.name}' 已被其他配置使用"
            )

    db_config = await ConfigStore.update(db, config_id, config)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 ID {config_id} 不存在"
        )
    return db_config


@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
        config_id: int,
        db: AsyncSession = Depends(get_db)
):
    """删除配置"""
    deleted = await ConfigStore.delete_by_id(db, config_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 ID {config_id} 不存在"
        )
    return None


@router.post("/configs/{config_id}/validate")
async def validate_config(
        config_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    验证配置

    通过调用 Klook API 获取用户信息来测试 Headers 是否有效
    """
    from app.core.klook_client import KlookClient

    db_config = await ConfigStore.get_by_id(db, config_id)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 ID {config_id} 不存在"
        )

    # 基础验证：检查 headers 格式
    headers = db_config.headers
    if not isinstance(headers, dict):
        return {
            "valid": False,
            "message": "Headers 格式错误，必须是 JSON 对象"
        }

    # 使用 Klook API 进行实际验证
    async with KlookClient() as client:
        success, result = await client.get_user_profile(headers)

        if success:
            # 验证成功，返回用户信息
            user_info = result.get("result", {})
            return {
                "valid": True,
                "message": "配置验证成功",
                "user_info": {
                    "user_id": user_info.get("user_id"),
                    "mobile": user_info.get("mobile"),
                    "email": user_info.get("email"),
                    "user_residence": user_info.get("user_residence"),
                    "membership_level": user_info.get("membership_level")
                }
            }
        else:
            # 验证失败
            error_info = result.get("error", {})
            return {
                "valid": False,
                "message": f"配置验证失败: {error_info.get('message', '未知错误')}",
                "error_code": error_info.get("code", "")
            }
