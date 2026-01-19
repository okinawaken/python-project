"""WebSocket 连接管理器"""
from typing import Dict, Set

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """管理 WebSocket 连接"""

    def __init__(self):
        # 存储所有活跃连接：{task_id: Set[WebSocket]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: int):
        """接受新连接"""
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()

        self.active_connections[task_id].add(websocket)
        logger.info(f"WebSocket 连接建立: task_id={task_id}, 连接数={len(self.active_connections[task_id])}")

    def disconnect(self, websocket: WebSocket, task_id: int):
        """断开连接"""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)

            # 如果该任务没有连接了，删除记录
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

            logger.info(f"WebSocket 连接断开: task_id={task_id}")

    async def send_message(self, task_id: int, message: dict):
        """发送消息给指定任务的所有连接"""
        if task_id not in self.active_connections:
            return

        # 移除断开的连接
        disconnected = set()

        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.add(connection)

        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection, task_id)

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for task_id in list(self.active_connections.keys()):
            await self.send_message(task_id, message)

    def get_connection_count(self, task_id: int = None) -> int:
        """获取连接数"""
        if task_id is not None:
            return len(self.active_connections.get(task_id, set()))

        return sum(len(connections) for connections in self.active_connections.values())


# 全局 WebSocket 管理器实例
websocket_manager = ConnectionManager()
