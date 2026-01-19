"""应用配置管理"""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "Klook Web"
    version: str = "0.1.0"
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./klook-web.db"

    # Klook API
    klook_base_url: str = "https://www.klook.cn"

    # CORS 配置
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 项目根目录
    @property
    def base_dir(self) -> Path:
        return Path(__file__).parent.parent.parent.parent

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
