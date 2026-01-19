"""任务执行服务"""
import asyncio

from app.core.klook_client import KlookClient
from app.core.timer import PrecisionTimer
from app.core.websocket_manager import websocket_manager
from app.models.log import LogCreate, LogLevel
from app.models.task import TaskStatus
from app.storage.config_store import ConfigStore
from app.storage.log_store import LogStore
from app.storage.task_store import TaskStore
from loguru import logger


class TaskExecutor:
    """任务执行器"""

    def __init__(self):
        # 存储运行中的任务：{task_id: asyncio.Task}
        self.running_tasks: dict[int, asyncio.Task] = {}
        # 存储定时器：{task_id: PrecisionTimer}
        self.timers: dict[int, PrecisionTimer] = {}

    async def start_task(self, task_id: int, db):
        """启动任务"""
        # 检查任务是否已在运行
        if task_id in self.running_tasks:
            logger.warning(f"任务 {task_id} 已在运行中")
            return False

        # 获取任务信息
        task = await TaskStore.get_by_id(db, task_id)
        if not task:
            logger.error(f"任务 {task_id} 不存在")
            return False

        # 获取配置
        config = await ConfigStore.get_by_id(db, task.config_id)
        if not config:
            logger.error(f"配置 {task.config_id} 不存在")
            return False

        # 创建异步任务
        task_coro = self._execute_task(task_id, task, config)
        async_task = asyncio.create_task(task_coro)
        self.running_tasks[task_id] = async_task

        logger.info(f"任务 {task_id} 已启动")
        return True

    async def _execute_task(self, task_id: int, task, config):
        """执行任务的核心逻辑"""
        from app.storage.database import async_session_maker

        try:
            # 记录日志：任务启动
            async with async_session_maker() as session:
                await LogStore.create(session, LogCreate(
                    task_id=task_id,
                    level=LogLevel.INFO,
                    message=f"任务启动，目标时间: {task.target_time.isoformat()}, 网络补偿: {task.network_compensation}ms"
                ))
                await session.commit()

            # 发送任务开始消息
            await websocket_manager.send_message(task_id, {
                "type": "task_started",
                "task_id": task_id,
                "target_time": task.target_time.isoformat(),
                "message": "任务已启动，开始倒计时"
            })

            # 创建高精度定时器
            async def progress_callback(remaining: float):
                """倒计时进度回调"""
                await websocket_manager.send_message(task_id, {
                    "type": "countdown",
                    "task_id": task_id,
                    "remaining": remaining,
                    "message": f"剩余 {remaining:.3f} 秒"
                })

            async def execute_callback():
                """到达目标时间，执行抢购"""
                await self._execute_redeem(task_id, task, config)

            # 创建定时器
            timer = PrecisionTimer(
                target_time=task.target_time,
                network_compensation=task.network_compensation,
                callback=execute_callback
            )
            self.timers[task_id] = timer

            # 更新任务状态为倒计时中
            async with async_session_maker() as session:
                await TaskStore.update_status(session, task_id, TaskStatus.COUNTDOWN)
                await session.commit()

            # 开始倒计时
            await timer.countdown(progress_callback)

            logger.info(f"任务 {task_id} 倒计时完成")

        except Exception as e:
            logger.error(f"任务 {task_id} 执行异常: {e}")
            await websocket_manager.send_message(task_id, {
                "type": "error",
                "task_id": task_id,
                "message": f"任务执行异常: {str(e)}"
            })

            # 更新任务状态为失败
            async with async_session_maker() as session:
                await TaskStore.update_status(
                    session,
                    task_id,
                    TaskStatus.FAILED,
                    {"error": str(e)}
                )
                await session.commit()

        finally:
            # 清理
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            if task_id in self.timers:
                del self.timers[task_id]

    async def _execute_redeem(self, task_id: int, task, config):
        """执行抢购逻辑"""
        from app.storage.database import async_session_maker

        logger.info(f"任务 {task_id} 开始执行抢购")

        # 记录日志：开始执行抢购
        async with async_session_maker() as session:
            await LogStore.create(session, LogCreate(
                task_id=task_id,
                level=LogLevel.INFO,
                message=f"倒计时完成，开始执行抢购（最大重试: {task.max_retries} 次，间隔: {task.retry_interval}ms）"
            ))
            await session.commit()

        # 更新任务状态为执行中
        async with async_session_maker() as session:
            await TaskStore.update_status(session, task_id, TaskStatus.RUNNING)
            await session.commit()

        await websocket_manager.send_message(task_id, {
            "type": "executing",
            "task_id": task_id,
            "message": "正在执行抢购..."
        })

        # 使用 Klook API 客户端执行抢购
        async with KlookClient() as client:
            max_retries = task.max_retries
            retry_count = 0
            last_result = None  # 保存最后一次的结果，用于最终失败时展示

            while retry_count < max_retries:
                retry_count += 1

                try:
                    success, result = await client.manual_redeem(
                        program_uuid=task.program_uuid,
                        headers=config.headers
                    )
                    last_result = result  # 保存每次的结果

                    if success:
                        # 抢购成功
                        logger.info(f"任务 {task_id} 抢购成功")

                        # 记录日志：抢购成功
                        async with async_session_maker() as session:
                            await LogStore.create(session, LogCreate(
                                task_id=task_id,
                                level=LogLevel.INFO,
                                message=f"抢购成功！第 {retry_count} 次尝试成功"
                            ))
                            await session.commit()

                        await websocket_manager.send_message(task_id, {
                            "type": "success",
                            "task_id": task_id,
                            "message": "抢购成功！",
                            "result": result
                        })

                        async with async_session_maker() as session:
                            await TaskStore.update_status(
                                session,
                                task_id,
                                TaskStatus.COMPLETED,
                                {"success": True, "result": result}
                            )
                            await session.commit()

                        return

                    else:
                        # 抢购失败，重试
                        logger.warning(f"任务 {task_id} 第 {retry_count} 次尝试失败: {result}")

                        # 记录日志：重试
                        async with async_session_maker() as session:
                            await LogStore.create(session, LogCreate(
                                task_id=task_id,
                                level=LogLevel.WARNING,
                                message=f"第 {retry_count}/{max_retries} 次尝试失败: {str(result)[:200]}"
                            ))
                            await session.commit()

                        await websocket_manager.send_message(task_id, {
                            "type": "retry",
                            "task_id": task_id,
                            "retry_count": retry_count,
                            "message": f"第 {retry_count} 次尝试失败，继续重试...",
                            "result": result
                        })

                        # 等待指定间隔后重试（毫秒转秒）
                        await asyncio.sleep(task.retry_interval / 1000)

                except Exception as e:
                    logger.error(f"任务 {task_id} 第 {retry_count} 次尝试异常: {e}")
                    last_result = {"error": str(e)}  # 保存异常信息

                    # 记录日志：异常
                    async with async_session_maker() as session:
                        await LogStore.create(session, LogCreate(
                            task_id=task_id,
                            level=LogLevel.ERROR,
                            message=f"第 {retry_count}/{max_retries} 次尝试异常: {str(e)}"
                        ))
                        await session.commit()

                    await websocket_manager.send_message(task_id, {
                        "type": "retry",
                        "task_id": task_id,
                        "retry_count": retry_count,
                        "message": f"第 {retry_count} 次尝试异常: {str(e)}",
                        "error": str(e)
                    })
                    await asyncio.sleep(task.retry_interval / 1000)

            # 所有重试都失败
            logger.error(f"任务 {task_id} 抢购失败，已重试 {max_retries} 次，最后错误: {last_result}")

            # 记录日志：最终失败
            async with async_session_maker() as session:
                await LogStore.create(session, LogCreate(
                    task_id=task_id,
                    level=LogLevel.ERROR,
                    message=f"抢购失败！已重试 {max_retries} 次均失败，最后错误: {str(last_result)[:200]}"
                ))
                await session.commit()

            await websocket_manager.send_message(task_id, {
                "type": "failed",
                "task_id": task_id,
                "message": f"抢购失败，已重试 {max_retries} 次",
                "result": last_result  # 包含最后一次的详细错误信息
            })

            async with async_session_maker() as session:
                await TaskStore.update_status(
                    session,
                    task_id,
                    TaskStatus.FAILED,
                    {"success": False, "retries": max_retries, "last_result": last_result}
                )
                await session.commit()

    async def cancel_task(self, task_id: int):
        """取消任务"""
        if task_id in self.timers:
            self.timers[task_id].cancel()
            logger.info(f"任务 {task_id} 已取消")

        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

        await websocket_manager.send_message(task_id, {
            "type": "cancelled",
            "task_id": task_id,
            "message": "任务已取消"
        })

    def is_running(self, task_id: int) -> bool:
        """检查任务是否在运行"""
        return task_id in self.running_tasks


# 全局任务执行器实例
task_executor = TaskExecutor()
