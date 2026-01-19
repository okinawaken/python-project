"""高精度定时器（重构自原 klook/main.py 的倒计时逻辑）"""
import asyncio
import time
from datetime import datetime
from typing import Callable, Optional

from loguru import logger


class PrecisionTimer:
    """高精度定时器，支持毫秒级精度"""

    def __init__(
            self,
            target_time: datetime,
            network_compensation: int = 200,
            callback: Optional[Callable] = None
    ):
        """
        Args:
            target_time: 目标触发时间
            network_compensation: 网络延迟补偿（毫秒）
            callback: 触发时的回调函数（异步）
        """
        self.target_time = target_time
        self.network_compensation = network_compensation
        self.callback = callback

        # 计算实际触发时间戳（提前补偿网络延迟）
        self.target_timestamp = target_time.timestamp() - (network_compensation / 1000.0)

        self._cancelled = False

    async def countdown(self, progress_callback: Optional[Callable] = None):
        """
        执行倒计时，支持进度回调

        Args:
            progress_callback: 倒计时进度回调，接收剩余秒数
        """
        logger.info(f"开始倒计时，目标时间: {self.target_time}, 补偿: {self.network_compensation}ms")

        while not self._cancelled:
            remaining = self.target_timestamp - time.time()

            if remaining <= 0:
                logger.info("倒计时结束，触发执行")
                break

            # 回调进度
            if progress_callback:
                try:
                    await progress_callback(remaining)
                except Exception as e:
                    logger.error(f"进度回调异常: {e}")

            # 根据剩余时间动态调整睡眠间隔
            sleep_interval = self._calculate_sleep_interval(remaining)
            await asyncio.sleep(sleep_interval)

        # 触发回调
        if not self._cancelled and self.callback:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback()
                else:
                    self.callback()
            except Exception as e:
                logger.error(f"定时器回调异常: {e}")

    def _calculate_sleep_interval(self, remaining: float) -> float:
        """
        根据剩余时间计算睡眠间隔（与原逻辑一致）

        Args:
            remaining: 剩余秒数

        Returns:
            睡眠间隔（秒）
        """
        if remaining >= 60:
            return 10.0  # 剩余 >= 60 秒，每 10 秒检查一次
        elif remaining >= 2:
            return 1.0  # 剩余 >= 2 秒，每秒检查一次
        elif remaining >= 0.5:
            return 0.1  # 剩余 >= 0.5 秒，每 0.1 秒检查一次
        else:
            return 0.01  # 最后 0.5 秒内，每 0.01 秒检查一次（10ms 精度）

    def cancel(self):
        """取消定时器"""
        self._cancelled = True
        logger.info("定时器已取消")

    @property
    def remaining_seconds(self) -> float:
        """获取剩余秒数"""
        return max(0, self.target_timestamp - time.time())
