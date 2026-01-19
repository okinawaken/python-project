"""WebSocket API"""
from app.core.websocket_manager import websocket_manager
from app.storage.database import get_db
from app.storage.task_store import TaskStore
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        task_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 端点，用于实时推送任务状态

    连接到: ws://localhost:8000/api/ws/tasks/{task_id}
    """
    # 验证任务是否存在
    task = await TaskStore.get_by_id(db, task_id)
    if not task:
        await websocket.close(code=4004, reason=f"Task {task_id} not found")
        return

    # 接受连接
    await websocket_manager.connect(websocket, task_id)

    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": f"已连接到任务 {task_id}"
        })

        # 保持连接，接收客户端消息（心跳等）
        while True:
            try:
                data = await websocket.receive_json()

                # 处理心跳
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "task_id": task_id
                    })

            except Exception as e:
                logger.error(f"WebSocket 接收消息异常: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket 断开连接: task_id={task_id}")
    finally:
        websocket_manager.disconnect(websocket, task_id)
