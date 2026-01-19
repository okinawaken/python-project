<template>
  <el-dialog
      v-model="dialogVisible"
      :title="`任务 #${taskId} - 实时监控`"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @close="handleClose"
  >
    <!-- 连接状态 -->
    <el-alert
        v-if="!isConnected && !isClosed"
        title="正在连接 WebSocket..."
        type="info"
        :closable="false"
        show-icon
    />

    <el-alert
        v-if="isConnected"
        title="WebSocket 已连接"
        type="success"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
    />

    <!-- 任务状态 -->
    <div class="status-section">
      <el-tag :type="statusTagType" size="large" effect="dark">
        {{ statusText }}
      </el-tag>
    </div>

    <!-- 倒计时显示 -->
    <div v-if="currentStatus === 'countdown'" class="countdown-section">
      <div class="countdown-display">
        <span class="countdown-value">{{ formattedRemaining }}</span>
        <span class="countdown-unit">秒</span>
      </div>
      <el-progress
          :percentage="countdownProgress"
          :color="progressColor"
          :stroke-width="20"
      />
    </div>

    <!-- 执行中动画 -->
    <div v-if="currentStatus === 'executing' || currentStatus === 'retry'" class="executing-section">
      <el-icon class="is-loading" :size="60" color="#409eff">
        <Loading/>
      </el-icon>
      <p style="margin-top: 20px; font-size: 16px; color: #606266;">
        {{ currentMessage }}
      </p>
    </div>

    <!-- 结果显示 -->
    <div v-if="currentStatus === 'success'" class="result-section success">
      <el-icon :size="80" color="#67c23a">
        <SuccessFilled/>
      </el-icon>
      <p style="margin-top: 20px; font-size: 18px; font-weight: bold;">
        🎉 抢购成功！
      </p>
      <el-descriptions v-if="result" :column="1" border style="margin-top: 20px;">
        <el-descriptions-item
            v-for="(value, key) in result"
            :key="key"
            :label="key"
        >
          {{ typeof value === 'object' ? JSON.stringify(value) : value }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div v-if="currentStatus === 'failed'" class="result-section failed">
      <el-icon :size="80" color="#f56c6c">
        <CircleCloseFilled/>
      </el-icon>
      <p style="margin-top: 20px; font-size: 18px; font-weight: bold; color: #f56c6c;">
        ❌ 抢购失败
      </p>
      <p style="margin-top: 10px; color: #909399;">{{ currentMessage }}</p>
      <el-descriptions v-if="result" :column="1" border style="margin-top: 20px;">
        <el-descriptions-item label="失败详情">
          <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto;">{{ typeof result === 'object' ? JSON.stringify(result, null, 2) : result }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div v-if="currentStatus === 'cancelled'" class="result-section cancelled">
      <el-icon :size="80" color="#909399">
        <WarningFilled/>
      </el-icon>
      <p style="margin-top: 20px; font-size: 18px; font-weight: bold; color: #909399;">
        🚫 任务已取消
      </p>
    </div>

    <!-- 消息日志 -->
    <el-card v-if="messages.length > 0" style="margin-top: 20px;" shadow="never">
      <template #header>
        <span>执行日志</span>
      </template>
      <el-timeline>
        <el-timeline-item
            v-for="(msg, index) in messages"
            :key="index"
            :timestamp="msg.timestamp"
            :type="msg.type"
        >
          {{ msg.text }}
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 操作按钮 -->
    <template #footer>
      <el-button
          v-if="currentStatus === 'countdown' || currentStatus === 'executing'"
          type="danger"
          @click="handleCancel"
          :loading="cancelling"
      >
        取消任务
      </el-button>
      <el-button
          v-if="['success', 'failed', 'cancelled'].includes(currentStatus)"
          type="primary"
          @click="handleClose"
      >
        关闭
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
import {ElMessage} from 'element-plus'
import {CircleCloseFilled, Loading, SuccessFilled, WarningFilled} from '@element-plus/icons-vue'
import {TaskWebSocket} from '@/utils/websocket'
import {taskApi} from '@/api/task'

const props = defineProps({
  taskId: {
    type: Number,
    required: true
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'task-completed'])

const dialogVisible = ref(props.visible)
const isConnected = ref(false)
const isClosed = ref(false)
const currentStatus = ref('connecting') // connecting, countdown, executing, retry, success, failed, cancelled
const currentMessage = ref('')
const remaining = ref(0)
const totalTime = ref(0)
const result = ref(null)
const messages = ref([])
const cancelling = ref(false)

let ws = null

// 监听 visible prop 的变化，同步更新 dialogVisible
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  // 如果对话框被重新打开，重置关闭状态并重新初始化 WebSocket
  if (newVal) {
    isClosed.value = false
    if (!isConnected.value) {
      initWebSocket()
    }
  }
})

// 状态文本
const statusText = computed(() => {
  const statusMap = {
    connecting: '连接中',
    countdown: '倒计时中',
    executing: '正在执行',
    retry: '重试中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[currentStatus.value] || '未知状态'
})

// 状态标签类型
const statusTagType = computed(() => {
  const typeMap = {
    connecting: 'info',
    countdown: 'warning',
    executing: 'primary',
    retry: 'warning',
    success: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[currentStatus.value] || 'info'
})

// 格式化剩余时间
const formattedRemaining = computed(() => {
  if (remaining.value >= 60) {
    const minutes = Math.floor(remaining.value / 60)
    const seconds = (remaining.value % 60).toFixed(3)
    return `${minutes}:${seconds.padStart(6, '0')}`
  }
  return remaining.value.toFixed(3)
})

// 倒计时进度
const countdownProgress = computed(() => {
  if (totalTime.value === 0) return 0
  const progress = ((totalTime.value - remaining.value) / totalTime.value) * 100
  return Math.min(Math.max(progress, 0), 100)
})

// 进度条颜色
const progressColor = computed(() => {
  if (remaining.value > 10) return '#67c23a'
  if (remaining.value > 3) return '#e6a23c'
  return '#f56c6c'
})

// 添加消息到日志
const addMessage = (text, type = 'primary') => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const milliseconds = String(now.getMilliseconds()).padStart(3, '0')
  const timestamp = `${hours}:${minutes}:${seconds}.${milliseconds}`

  messages.value.push({
    text,
    type,
    timestamp
  })
}

// 初始化 WebSocket
const initWebSocket = () => {
  ws = new TaskWebSocket(props.taskId)

  ws.onConnected = (message) => {
    isConnected.value = true
    currentStatus.value = 'countdown'
    addMessage('任务已启动', 'success')

    if (message.target_time) {
      const targetTime = new Date(message.target_time)
      const now = new Date()
      totalTime.value = (targetTime - now) / 1000
      remaining.value = totalTime.value
    }
  }

  ws.onCountdown = (message) => {
    currentStatus.value = 'countdown'
    remaining.value = message.remaining
    currentMessage.value = message.message

    // 只在特定时刻记录日志，避免日志过多
    if (
        remaining.value === 60 ||
        remaining.value === 30 ||
        remaining.value === 10 ||
        remaining.value === 5 ||
        remaining.value < 1
    ) {
      addMessage(message.message, 'warning')
    }
  }

  ws.onExecuting = (message) => {
    currentStatus.value = 'executing'
    currentMessage.value = message.message
    addMessage(message.message, 'primary')
  }

  ws.onRetry = (message) => {
    currentStatus.value = 'retry'
    currentMessage.value = message.message

    // 构建详细的重试信息
    let retryMessage = `第 ${message.retry_count} 次重试`
    if (message.result) {
      // 如果有详细的结果信息，添加到日志中
      const resultStr = typeof message.result === 'object'
          ? JSON.stringify(message.result)
          : message.result
      retryMessage += ` - ${resultStr}`
    } else if (message.error) {
      // 如果是异常信息
      retryMessage += ` - ${message.error}`
    }

    addMessage(retryMessage, 'warning')
  }

  ws.onSuccess = (message) => {
    currentStatus.value = 'success'
    currentMessage.value = message.message
    result.value = message.result
    addMessage('抢购成功！', 'success')
    ElMessage.success('抢购成功！')
    emit('task-completed', true)
  }

  ws.onFailed = (message) => {
    currentStatus.value = 'failed'
    currentMessage.value = message.message
    result.value = message.result  // 保存最后一次的失败结果

    // 构建详细的失败信息
    let failedMessage = message.message
    if (message.result) {
      const resultStr = typeof message.result === 'object'
          ? JSON.stringify(message.result)
          : message.result
      failedMessage += ` - ${resultStr}`
    }

    addMessage(failedMessage, 'danger')
    ElMessage.error('抢购失败')
    emit('task-completed', false)
  }

  ws.onCancelled = (message) => {
    currentStatus.value = 'cancelled'
    currentMessage.value = message.message
    addMessage('任务已取消', 'info')
    ElMessage.info('任务已取消')
  }

  ws.onError = (error) => {
    console.error('WebSocket 错误:', error)
    ElMessage.error('WebSocket 连接错误')
  }

  ws.onDisconnected = () => {
    isConnected.value = false
    // 只有在非主动关闭的情况下才显示重连提示
    if (!isClosed.value && !['success', 'failed', 'cancelled'].includes(currentStatus.value)) {
      ElMessage.warning('WebSocket 连接断开，正在尝试重连...')
    }
  }

  ws.connect()
}

// 取消任务
const handleCancel = async () => {
  try {
    cancelling.value = true
    await taskApi.cancel(props.taskId)
    ElMessage.success('任务已取消')
  } catch (error) {
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  } finally {
    cancelling.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  isClosed.value = true
  if (ws) {
    ws.disconnect()
  }
  emit('update:visible', false)
}

onMounted(() => {
  initWebSocket()
})

onBeforeUnmount(() => {
  if (ws) {
    ws.disconnect()
  }
})
</script>

<style scoped>
.status-section {
  text-align: center;
  margin-bottom: 30px;
}

.countdown-section {
  text-align: center;
  padding: 20px 0;
}

.countdown-display {
  margin-bottom: 30px;
}

.countdown-value {
  font-size: 72px;
  font-weight: bold;
  color: #409eff;
  font-family: 'Monaco', 'Courier New', monospace;
}

.countdown-unit {
  font-size: 24px;
  color: #909399;
  margin-left: 10px;
}

.executing-section {
  text-align: center;
  padding: 40px 0;
}

.result-section {
  text-align: center;
  padding: 40px 0;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>