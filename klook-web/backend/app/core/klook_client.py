"""Klook API 客户端（重构自原 klook/api.py）"""
import httpx
from loguru import logger


class KlookClient:
    """Klook API 客户端"""

    def __init__(self, base_url: str = "https://www.klook.cn"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_user_profile(
            self,
            headers: dict[str, str]
    ) -> tuple[bool, dict]:
        """
        获取用户信息

        Args:
            headers: 请求头（包含认证信息）

        Returns:
            (是否成功, 响应数据)
        """
        url = f"{self.base_url}/v3/userserv/user/profile_service/get_simple_profile_by_token"

        try:
            response = await self.client.get(
                url=url,
                headers=headers
            )

            logger.info(f"获取用户信息 API 响应: status={response.status_code}")

            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                if success:
                    logger.info(f"获取用户信息成功: user_id={result.get('result', {}).get('user_id')}")
                else:
                    logger.warning(f"获取用户信息失败: {result.get('error', {}).get('message')}")
                return success, result
            else:
                logger.error(f"获取用户信息请求失败: HTTP {response.status_code}")
                return False, {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            logger.error(f"获取用户信息请求异常: {e}")
            return False, {"error": str(e)}

    async def manual_redeem(
            self,
            program_uuid: str,
            headers: dict[str, str]
    ) -> tuple[bool, dict]:
        """
        手动兑换优惠券

        Args:
            program_uuid: 优惠券项目 UUID
            headers: 请求头（包含认证信息）

        Returns:
            (是否成功, 响应数据)
        """
        url = f"{self.base_url}/v2/promosrv/program/manual_redeem"

        try:
            response = await self.client.post(
                url=url,
                headers=headers,
                json={"program_uuid": program_uuid}
            )

            logger.info(f"API 响应: status={response.status_code}, body={response.text[:200]}")

            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                return success, result
            else:
                return False, {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            logger.error(f"请求异常: {e}")
            return False, {"error": str(e)}

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
