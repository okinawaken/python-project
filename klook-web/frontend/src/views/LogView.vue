<template>
  <div class="log-view">
    <!-- 日志列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志查看</span>
          <el-space>
            <el-button @click="loadLogs" :icon="Refresh">刷新</el-button>
            <el-button
                type="danger"
                :icon="Delete"
                @click="handleClearTaskLogs"
                :disabled="!filterTaskId"
            >
              清空当前任务日志
            </el-button>
            <el-button
                type="danger"
                :icon="Delete"
                @click="handleClearAllLogs"
                plain
            >
              清空全部日志
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 筛选器 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="任务筛选">
          <el-select
              v-model="filterTaskId"
              @change="handleFilterChange"
              placeholder="全部任务"
              clearable
              filterable
              style="width: 200px"
          >
            <el-option
                v-for="task in tasks"
                :key="task.id"
                :label="`任务 ${task.id} - ${task.program_uuid.substring(0, 8)}`"
                :value="task.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日志级别">
          <el-select
              v-model="filterLevel"
              @change="handleFilterChange"
              placeholder="全部级别"
              clearable
              style="width: 150px"
          >
            <el-option label="调试 (DEBUG)" value="debug"/>
            <el-option label="信息 (INFO)" value="info"/>
            <el-option label="警告 (WARNING)" value="warning"/>
            <el-option label="错误 (ERROR)" value="error"/>
            <el-option label="严重 (CRITICAL)" value="critical"/>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-text type="info" size="small">
            共 {{ total }} 条日志
          </el-text>
        </el-form-item>
      </el-form>

      <!-- 日志表格 -->
      <el-table
          v-loading="loading"
          :data="logs"
          style="width: 100%"
          :height="tableHeight"
          stripe
      >
        <el-table-column prop="id" label="ID" width="80"/>

        <el-table-column label="任务 ID" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.task_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ getLevelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="消息" min-width="400">
          <template #default="{ row }">
            <div class="log-message" :class="'level-' + row.level">
              {{ row.message }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(row)"
                link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 20px; display: flex; justify-content: flex-end">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[50, 100, 200, 500]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Delete, Refresh} from '@element-plus/icons-vue'
import {logApi} from '../api/log.js'
import {taskApi} from '../api/task.js'

// 响应式数据
const loading = ref(false)
const logs = ref([])
const tasks = ref([])
const total = ref(0)

// 筛选条件
const filterTaskId = ref(null)
const filterLevel = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(100)

// 表格高度（自适应）
const tableHeight = computed(() => {
  return window.innerHeight - 350
})

// 方法
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    }

    if (filterTaskId.value) {
      params.task_id = filterTaskId.value
    }

    if (filterLevel.value) {
      params.level = filterLevel.value
    }

    const data = await logApi.getAll(params)
    logs.value = data.logs
    total.value = data.total
  } catch (error) {
    ElMessage.error('加载日志列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadTasks = async () => {
  try {
    const data = await taskApi.getAll()
    tasks.value = data.items || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadLogs()
}

const handlePageChange = () => {
  loadLogs()
}

const handleDelete = async (log) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除这条日志吗？`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await logApi.delete(log.id)
    ElMessage.success('删除成功')
    loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleClearTaskLogs = async () => {
  if (!filterTaskId.value) {
    ElMessage.warning('请先选择要清空日志的任务')
    return
  }

  try {
    await ElMessageBox.confirm(
        `确定要清空任务 ${filterTaskId.value} 的所有日志吗？此操作不可恢复！`,
        '确认清空',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await logApi.deleteByTaskId(filterTaskId.value)
    ElMessage.success('清空成功')
    loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

const handleClearAllLogs = async () => {
  try {
    await ElMessageBox.confirm(
        '确定要清空所有日志吗？此操作将删除系统中的所有日志，不可恢复！',
        '⚠️ 危险操作警告',
        {
          confirmButtonText: '确定清空',
          cancelButtonText: '取消',
          type: 'error',
          distinguishCancelAndClose: true
        }
    )

    await logApi.deleteAll()
    ElMessage.success('所有日志已清空')
    loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getLevelType = (level) => {
  const types = {
    debug: 'info',
    info: '',
    warning: 'warning',
    error: 'danger',
    critical: 'danger'
  }
  return types[level] || ''
}

const getLevelLabel = (level) => {
  const labels = {
    debug: 'DEBUG',
    info: 'INFO',
    warning: 'WARNING',
    error: 'ERROR',
    critical: 'CRITICAL'
  }
  return labels[level] || level.toUpperCase()
}

// 生命周期
onMounted(() => {
  loadLogs()
  loadTasks()
})
</script>

<style scoped>
.log-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-message {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-all;
}

.log-message.level-debug {
  color: #909399;
}

.log-message.level-info {
  color: #303133;
}

.log-message.level-warning {
  color: #E6A23C;
}

.log-message.level-error {
  color: #F56C6C;
  font-weight: 500;
}

.log-message.level-critical {
  color: #F56C6C;
  font-weight: 700;
  background-color: #FEF0F0;
  padding: 2px 4px;
  border-radius: 2px;
}
</style>