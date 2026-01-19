<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用 Klook Web 抢购助手</span>
        </div>
      </template>

      <el-space direction="vertical" :size="20" style="width: 100%">
        <el-alert
            title="项目状态"
            type="success"
            description="后端 API 已就绪，前端界面正在开发中..."
            show-icon
            :closable="false"
        />

        <div class="status-section">
          <h3>系统状态</h3>
          <el-space wrap>
            <el-tag type="success" size="large">后端: {{ backendStatus }}</el-tag>
            <el-tag type="info" size="large">前端: {{ frontendVersion }}</el-tag>
          </el-space>
        </div>

        <div class="quick-links">
          <h3>快速开始</h3>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/config')">
              配置管理
            </el-button>
            <el-button type="warning" @click="$router.push('/program')">
              优惠券项目
            </el-button>
            <el-button type="success" @click="$router.push('/task')">
              任务管理
            </el-button>
            <el-button type="info" @click="$router.push('/log')">
              日志查看
            </el-button>
            <el-button @click="checkBackend">
              测试后端连接
            </el-button>
          </el-space>
        </div>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {ElMessage} from 'element-plus'
import axios from 'axios'

const backendStatus = ref('未连接')
const frontendVersion = ref('0.1.0')

const checkBackend = async () => {
  try {
    const response = await axios.get('/api/health')
    if (response.data.status === 'healthy') {
      backendStatus.value = '已连接'
      ElMessage.success('后端连接成功')
    }
  } catch (error) {
    backendStatus.value = '连接失败'
    ElMessage.error('后端连接失败: ' + error.message)
  }
}

onMounted(() => {
  checkBackend()
})
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 20px auto;
}

.welcome-card {
  border-radius: 8px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.status-section,
.quick-links {
  margin-top: 20px;
}

h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style>