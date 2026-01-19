<template>
  <div class="task-view">
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总任务数" :value="stats.total"/>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待执行" :value="stats.by_status?.pending || 0">
            <template #suffix>
              <el-icon color="#909399">
                <Clock/>
              </el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="执行中" :value="(stats.by_status?.countdown || 0) + (stats.by_status?.running || 0)">
            <template #suffix>
              <el-icon color="#409EFF">
                <Loading/>
              </el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已完成" :value="stats.by_status?.completed || 0">
            <template #suffix>
              <el-icon color="#67C23A">
                <Check/>
              </el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-space>
            <el-button @click="loadTasks" :icon="Refresh">刷新</el-button>
            <el-button type="primary" @click="showCreateDialog" :icon="Plus">
              新建任务
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 筛选器 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="状态筛选">
          <el-select v-model="filterStatus" @change="loadTasks" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="待执行" value="pending"/>
            <el-option label="倒计时中" value="countdown"/>
            <el-option label="执行中" value="running"/>
            <el-option label="已完成" value="completed"/>
            <el-option label="失败" value="failed"/>
            <el-option label="已取消" value="cancelled"/>
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 任务表格 -->
      <el-table
          v-loading="loading"
          :data="tasks"
          style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80"/>
        <el-table-column label="配置" width="150">
          <template #default="{ row }">
            <el-tag>{{ getConfigName(row.config_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="program_uuid" label="优惠券" min-width="180">
          <template #default="{ row }">
            {{ getProgramName(row.program_uuid) }}
          </template>
        </el-table-column>
        <el-table-column label="目标时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.target_time) }}
          </template>
        </el-table-column>
        <el-table-column label="延迟补偿" width="100">
          <template #default="{ row }">
            {{ row.network_compensation }}ms
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="viewTask(row)">查看</el-button>
              <el-button
                  v-if="row.status === 'pending'"
                  size="small"
                  type="success"
                  @click="startTask(row.id)"
              >
                启动
              </el-button>
              <el-button
                  v-if="['pending', 'countdown'].includes(row.status)"
                  size="small"
                  type="warning"
                  @click="cancelTask(row.id)"
              >
                取消
              </el-button>
              <el-button
                  v-if="!['countdown', 'running'].includes(row.status)"
                  size="small"
                  type="danger"
                  @click="deleteTask(row)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务，点击新建任务开始"/>
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog
        v-model="dialogVisible"
        title="新建抢购任务"
        width="600px"
        @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="选择配置" prop="config_id">
          <el-select v-model="form.config_id" placeholder="请选择配置" style="width: 100%">
            <el-option
                v-for="config in configs"
                :key="config.id"
                :label="config.name"
                :value="config.id"
            />
          </el-select>
          <el-link type="primary" @click="goToConfig" style="margin-top: 5px">
            还没有配置？去创建 →
          </el-link>
        </el-form-item>

        <el-form-item label="优惠券项目" prop="program_uuid">
          <el-select v-model="form.program_uuid" placeholder="请选择优惠券项目" style="width: 100%">
            <el-option
                v-for="program in programs"
                :key="program.uuid"
                :label="program.name"
                :value="program.uuid"
            >
              <div style="display: flex; flex-direction: column">
                <span>{{ program.name }}</span>
                <span style="font-size: 12px; color: #999">{{ program.description }}</span>
              </div>
            </el-option>
          </el-select>
          <el-link type="primary" @click="goToProgram" style="margin-top: 5px">
            还没有优惠券项目？去创建 →
          </el-link>
        </el-form-item>

        <el-form-item label="抢购时间" prop="target_time">
          <el-date-picker
              v-model="form.target_time"
              type="datetime"
              placeholder="选择日期时间"
              style="width: 100%"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
          />
          <div style="margin-top: 5px; font-size: 12px; color: #999">
            注意：时间精度为秒级，实际执行时会根据网络延迟补偿提前发送请求
          </div>
        </el-form-item>

        <el-form-item label="网络延迟补偿" prop="network_compensation">
          <el-slider
              v-model="form.network_compensation"
              :min="0"
              :max="2000"
              :step="50"
              show-input
              :show-input-controls="false"
              style="width: calc(100% - 120px)"
          />
          <span style="margin-left: 10px">毫秒</span>
          <div style="margin-top: 5px; font-size: 12px; color: #999">
            建议设置为 100-200ms，根据网络情况调整
          </div>
        </el-form-item>

        <el-form-item label="最大重试次数" prop="max_retries">
          <el-slider
              v-model="form.max_retries"
              :min="1"
              :max="20"
              :step="1"
              show-input
              :show-input-controls="false"
              style="width: calc(100% - 120px)"
          />
          <span style="margin-left: 10px">次</span>
          <div style="margin-top: 5px; font-size: 12px; color: #999">
            抢购失败后的最大重试次数，建议 3-10 次
          </div>
        </el-form-item>

        <el-form-item label="重试间隔" prop="retry_interval">
          <el-slider
              v-model="form.retry_interval"
              :min="0"
              :max="5000"
              :step="50"
              show-input
              :show-input-controls="false"
              style="width: calc(100% - 120px)"
          />
          <span style="margin-left: 10px">毫秒</span>
          <div style="margin-top: 5px; font-size: 12px; color: #999">
            每次重试之间的等待时间，建议 300-1000ms，设置为 0 表示立即重试
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            创建任务
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 查看任务详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="任务详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ viewingTask?.id }}</el-descriptions-item>
        <el-descriptions-item label="配置">
          {{ getConfigName(viewingTask?.config_id) }}
        </el-descriptions-item>
        <el-descriptions-item label="优惠券">
          {{ getProgramName(viewingTask?.program_uuid) }}
        </el-descriptions-item>
        <el-descriptions-item label="目标时间">
          {{ formatDate(viewingTask?.target_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="网络延迟补偿">
          {{ viewingTask?.network_compensation }}ms
        </el-descriptions-item>
        <el-descriptions-item label="最大重试次数">
          {{ viewingTask?.max_retries }}次
        </el-descriptions-item>
        <el-descriptions-item label="重试间隔">
          {{ viewingTask?.retry_interval }}ms
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(viewingTask?.status)">
            {{ getStatusLabel(viewingTask?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(viewingTask?.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" v-if="viewingTask?.started_at">
          {{ formatDate(viewingTask?.started_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" v-if="viewingTask?.completed_at">
          {{ formatDate(viewingTask?.completed_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="执行结果" v-if="viewingTask?.result">
          <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto;">{{ JSON.stringify(viewingTask?.result, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 任务倒计时对话框 -->
    <TaskCountdown
        v-if="countdownTaskId"
        :task-id="countdownTaskId"
        :visible="countdownVisible"
        @update:visible="countdownVisible = $event"
        @task-completed="handleTaskCompleted"
    />
  </div>
</template>

<script setup>
import {onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Check, Clock, Loading, Plus, Refresh} from '@element-plus/icons-vue'
import {taskApi} from '../api/task'
import {configApi} from '../api/config'
import {programApi} from '../api/program'
import TaskCountdown from '../components/TaskCountdown.vue'

const router = useRouter()

// 数据
const loading = ref(false)
const tasks = ref([])
const configs = ref([])
const programs = ref([])
const stats = ref({total: 0, by_status: {}})
const filterStatus = ref('')

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const viewingTask = ref(null)

// 倒计时对话框状态
const countdownVisible = ref(false)
const countdownTaskId = ref(null)

// 监听对话框关闭，刷新任务列表
watch(countdownVisible, async (newVal, oldVal) => {
  // 当对话框从打开变为关闭时，刷新列表
  if (oldVal === true && newVal === false) {
    await loadTasks()
    await loadStats()
  }
})

// 表单数据
const form = ref({
  config_id: null,
  program_uuid: '',
  target_time: '',
  network_compensation: 250,
  max_retries: 3,
  retry_interval: 500
})

// 表单验证规则
const rules = {
  config_id: [
    {required: true, message: '请选择配置', trigger: 'change'}
  ],
  program_uuid: [
    {required: true, message: '请选择优惠券项目', trigger: 'change'}
  ],
  target_time: [
    {required: true, message: '请选择抢购时间', trigger: 'change'}
  ],
  network_compensation: [
    {required: true, message: '请设置网络延迟补偿', trigger: 'blur'}
  ],
  max_retries: [
    {required: true, message: '请设置最大重试次数', trigger: 'blur'}
  ],
  retry_interval: [
    {required: true, message: '请设置重试间隔', trigger: 'blur'}
  ]
}

// 方法
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    const data = await taskApi.getAll(params)
    tasks.value = data.items
  } catch (error) {
    ElMessage.error('加载任务列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    stats.value = await taskApi.getStats()
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadConfigs = async () => {
  try {
    const data = await configApi.getAll()
    configs.value = data.items
  } catch (error) {
    ElMessage.error('加载配置列表失败: ' + error.message)
  }
}

const loadPrograms = async () => {
  try {
    const data = await programApi.getAll()
    programs.value = data.items
  } catch (error) {
    ElMessage.error('加载优惠券列表失败: ' + error.message)
  }
}

const showCreateDialog = async () => {
  if (configs.value.length === 0) {
    ElMessageBox.confirm(
        '还没有配置，是否前往创建配置？',
        '提示',
        {
          confirmButtonText: '去创建',
          cancelButtonText: '取消',
          type: 'warning'
        }
    ).then(() => {
      router.push('/config')
    }).catch(() => {
    })
    return
  }

  form.value = {
    config_id: configs.value[0]?.id || null,
    program_uuid: programs.value[0]?.uuid || '',
    target_time: '',
    network_compensation: 250,
    max_retries: 3,
    retry_interval: 500
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await taskApi.create(form.value)
    ElMessage.success('任务创建成功')
    dialogVisible.value = false
    await loadTasks()
    await loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const startTask = async (id) => {
  try {
    await taskApi.start(id)
    // 打开倒计时对话框
    countdownTaskId.value = id
    countdownVisible.value = true
    // 刷新任务列表
    await loadTasks()
    await loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '启动失败: ' + error.message)
  }
}

const handleTaskCompleted = async (success) => {
  // 任务完成后不自动关闭对话框，让用户查看完整的执行结果
  // 只刷新任务列表和统计信息
  await loadTasks()
  await loadStats()
}

const cancelTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '取消确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await taskApi.cancel(id)
    ElMessage.success('任务已取消')
    await loadTasks()
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败: ' + error.message)
    }
  }
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除任务 ID ${task.id} 吗？此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await taskApi.delete(task.id)
    ElMessage.success('任务删除成功')
    await loadTasks()
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const viewTask = (task) => {
  // 如果任务正在执行中，打开倒计时对话框查看实时进度
  if (['countdown', 'running'].includes(task.status)) {
    countdownTaskId.value = task.id
    countdownVisible.value = true
  } else {
    // 否则显示静态详情
    viewingTask.value = task
    viewDialogVisible.value = true
  }
}

const goToConfig = () => {
  router.push('/config')
}

const goToProgram = () => {
  router.push('/program')
}

const getConfigName = (configId) => {
  const config = configs.value.find(c => c.id === configId)
  return config ? config.name : `配置 #${configId}`
}

const getProgramName = (uuid) => {
  const program = programs.value.find(p => p.uuid === uuid)
  return program ? program.name : uuid
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '待执行',
    countdown: '倒计时中',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    countdown: 'warning',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadTasks(),
    loadStats(),
    loadConfigs(),
    loadPrograms()
  ])
})
</script>

<style scoped>
.task-view {
  max-width: 1600px;
  margin: 20px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>