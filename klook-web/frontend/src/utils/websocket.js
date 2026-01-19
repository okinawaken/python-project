/**
 * WebSocket 连接管理工具
 */
export class TaskWebSocket {
    constructor(taskId) {
        this.taskId = taskId
        this.ws = null
        this.reconnectTimer = null
        this.reconnectAttempts = 0
        this.maxReconnectAttempts = 5
        this.reconnectDelay = 3000
        this.heartbeatTimer = null
        this.heartbeatInterval = 30000 // 30秒心跳

        // 回调函数
        this.onConnected = null
        this.onCountdown = null
        this.onExecuting = null
        this.onRetry = null
        this.onSuccess = null
        this.onFailed = null
        this.onCancelled = null
        this.onError = null
        this.onDisconnected = null
    }

    /**
     * 连接 WebSocket
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('WebSocket 已连接')
            return
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = import.meta.env.VITE_API_BASE_URL
            ? import.meta.env.VITE_API_BASE_URL.replace(/^https?:\/\//, '')
            : 'localhost:8000'

        const wsUrl = `${protocol}//${host}/api/ws/tasks/${this.taskId}`

        console.log('正在连接 WebSocket:', wsUrl)
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
            console.log('WebSocket 连接成功')
            this.reconnectAttempts = 0
            this.startHeartbeat()
        }

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)
                this.handleMessage(message)
            } catch (error) {
                console.error('解析 WebSocket 消息失败:', error)
            }
        }

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error)
            if (this.onError) {
                this.onError(error)
            }
        }

        this.ws.onclose = (event) => {
            console.log('WebSocket 连接关闭:', event.code, event.reason)
            this.stopHeartbeat()

            if (this.onDisconnected) {
                this.onDisconnected(event)
            }

            // 尝试重连（除非是正常关闭）
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect()
            }
        }
    }

    /**
     * 处理接收到的消息
     */
    handleMessage(message) {
        console.log('收到 WebSocket 消息:', message)

        switch (message.type) {
            case 'connected':
                if (this.onConnected) {
                    this.onConnected(message)
                }
                break

            case 'task_started':
                if (this.onConnected) {
                    this.onConnected(message)
                }
                break

            case 'countdown':
                if (this.onCountdown) {
                    this.onCountdown(message)
                }
                break

            case 'executing':
                if (this.onExecuting) {
                    this.onExecuting(message)
                }
                break

            case 'retry':
                if (this.onRetry) {
                    this.onRetry(message)
                }
                break

            case 'success':
                if (this.onSuccess) {
                    this.onSuccess(message)
                }
                break

            case 'failed':
                if (this.onFailed) {
                    this.onFailed(message)
                }
                break

            case 'cancelled':
                if (this.onCancelled) {
                    this.onCancelled(message)
                }
                break

            case 'pong':
                // 心跳响应，无需处理
                break

            case 'error':
                console.error('任务执行错误:', message.message)
                if (this.onError) {
                    this.onError(message)
                }
                break

            default:
                console.warn('未知消息类型:', message.type)
        }
    }

    /**
     * 发送消息
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message))
        } else {
            console.warn('WebSocket 未连接，无法发送消息')
        }
    }

    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.stopHeartbeat()
        this.heartbeatTimer = setInterval(() => {
            this.send({type: 'ping'})
        }, this.heartbeatInterval)
    }

    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer)
            this.heartbeatTimer = null
        }
    }

    /**
     * 安排重连
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            return
        }

        this.reconnectAttempts++
        console.log(`${this.reconnectDelay / 1000}秒后尝试第 ${this.reconnectAttempts} 次重连...`)

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null
            this.connect()
        }, this.reconnectDelay)
    }

    /**
     * 断开连接
     */
    disconnect() {
        this.stopHeartbeat()

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect')
            this.ws = null
        }

        // 重置重连计数
        this.reconnectAttempts = 0
    }

    /**
     * 检查连接状态
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN
    }
}