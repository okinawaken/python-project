<template>
  <div class="config-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置管理</span>
          <el-space>
            <el-button @click="loadConfigs" :loading="loading">
              <el-icon>
                <Refresh/>
              </el-icon>
              刷新
            </el-button>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon>
                <Plus/>
              </el-icon>
              新建配置
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 配置列表 -->
      <el-table
          v-loading="loading"
          :data="configs"
          style="width: 100%"
          :default-sort="{ prop: 'created_at', order: 'descending' }"
      >
        <el-table-column prop="id" label="ID" width="80"/>
        <el-table-column prop="name" label="配置名称" min-width="150"/>
        <el-table-column label="Headers" min-width="300">
          <template #default="{ row }">
            <el-tag
                v-for="(value, key) in row.headers"
                :key="key"
                style="margin-right: 5px; margin-bottom: 5px"
                size="small"
            >
              {{ key }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="viewConfig(row)">
                查看
              </el-button>
              <el-button size="small" type="primary" @click="editConfig(row)">
                编辑
              </el-button>
              <el-button size="small" type="success" @click="validateConfig(row.id)">
                验证
              </el-button>
              <el-button size="small" type="danger" @click="deleteConfig(row)">
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && configs.length === 0" description="暂无配置，点击新建配置开始"/>
    </el-card>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="600px"
        @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入配置名称"/>
        </el-form-item>
        <el-form-item label="Headers" prop="headers">
          <div style="margin-bottom: 10px">
            <el-button type="primary" size="small" @click="showImportDialog" plain>
              <el-icon>
                <Upload/>
              </el-icon>
              从 curl 导入
            </el-button>
          </div>
          <el-input
              v-model="headersText"
              type="textarea"
              :rows="10"
              placeholder='请输入 JSON 格式的 Headers，或点击上方"从 curl 导入"按钮'
              @blur="validateJson"
          />
          <div v-if="jsonError" style="color: red; font-size: 12px; margin-top: 5px">
            {{ jsonError }}
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 查看配置详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="配置详情" width="600px">
      <el-form label-width="100px">
        <el-form-item label="ID">
          <el-input :value="viewingConfig?.id" disabled/>
        </el-form-item>
        <el-form-item label="配置名称">
          <el-input :value="viewingConfig?.name" disabled/>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input :value="formatDate(viewingConfig?.created_at)" disabled/>
        </el-form-item>
        <el-form-item label="更新时间">
          <el-input :value="formatDate(viewingConfig?.updated_at)" disabled/>
        </el-form-item>
        <el-form-item label="Headers">
          <el-input
              :value="JSON.stringify(viewingConfig?.headers, null, 2)"
              type="textarea"
              :rows="15"
              readonly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入 curl 命令对话框 -->
    <el-dialog
        v-model="importDialogVisible"
        title="从 curl 命令导入 Headers"
        width="700px"
        @close="handleImportDialogClose"
    >
      <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
      >
        从浏览器开发者工具中复制完整的 curl 命令，粘贴到下方文本框
      </el-alert>

      <el-input
          v-model="curlCommand"
          type="textarea"
          :rows="12"
          placeholder="粘贴 curl 命令，例如：
curl 'https://www.klook.cn/v1/promosrv/program/...' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Content-Type: application/json' \
  ..."
      />

      <div v-if="importError" style="margin-top: 10px">
        <el-alert
            :title="importError"
            type="error"
            :closable="false"
        />
      </div>

      <div v-if="importSuccess" style="margin-top: 10px">
        <el-alert
            :title="importSuccess"
            type="success"
            :closable="false"
        />
      </div>

      <template #footer>
        <el-space>
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleImportCurl" :loading="importing">
            解析并导入
          </el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Plus, Upload, Refresh} from '@element-plus/icons-vue'
import {configApi} from '../api/config'
import {formatHeaders, parseCurlCommand, validateParsedCurl} from '../utils/curlParser'

// 数据
const loading = ref(false)
const configs = ref([])
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const viewingConfig = ref(null)

// 导入功能相关
const importDialogVisible = ref(false)
const curlCommand = ref('')
const importing = ref(false)
const importError = ref('')
const importSuccess = ref('')

// 表单数据
const form = ref({
  id: null,
  name: '',
  headers: {}
})

const headersText = ref('')
const jsonError = ref('')

// 表单验证规则
const rules = {
  name: [
    {required: true, message: '请输入配置名称', trigger: 'blur'},
    {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
  ],
  headers: [
    {required: true, message: '请输入 Headers', trigger: 'blur'}
  ]
}

// 计算属性
const dialogTitle = ref('')

// 方法
const loadConfigs = async () => {
  loading.value = true
  try {
    const data = await configApi.getAll()
    configs.value = data.items
  } catch (error) {
    ElMessage.error('加载配置列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新建配置'
  form.value = {
    id: null,
    name: '',
    headers: {}
  }
  headersText.value = '{\n  "Authorization": "Bearer YOUR_TOKEN",\n  "User-Agent": "Mozilla/5.0"\n}'
  jsonError.value = ''
  dialogVisible.value = true
}

const editConfig = (config) => {
  isEdit.value = true
  dialogTitle.value = '编辑配置'
  form.value = {
    id: config.id,
    name: config.name,
    headers: {...config.headers}
  }
  headersText.value = JSON.stringify(config.headers, null, 2)
  jsonError.value = ''
  dialogVisible.value = true
}

const viewConfig = (config) => {
  viewingConfig.value = config
  viewDialogVisible.value = true
}

const validateJson = () => {
  try {
    const parsed = JSON.parse(headersText.value)
    if (typeof parsed !== 'object' || Array.isArray(parsed)) {
      jsonError.value = 'Headers 必须是一个 JSON 对象'
      return false
    }
    form.value.headers = parsed
    jsonError.value = ''
    return true
  } catch (error) {
    jsonError.value = 'JSON 格式错误: ' + error.message
    return false
  }
}

const handleSubmit = async () => {
  if (!validateJson()) {
    return
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await configApi.update(form.value.id, {
        name: form.value.name,
        headers: form.value.headers
      })
      ElMessage.success('配置更新成功')
    } else {
      await configApi.create({
        name: form.value.name,
        headers: form.value.headers
      })
      ElMessage.success('配置创建成功')
    }
    dialogVisible.value = false
    await loadConfigs()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除配置 "${config.name}" 吗？此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await configApi.delete(config.id)
    ElMessage.success('配置删除成功')
    await loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const validateConfig = async (id) => {
  try {
    const result = await configApi.validate(id)
    if (result.valid) {
      // 验证成功，显示用户信息
      const userInfo = result.user_info
      const message = `
        <div style="text-align: left;">
          <p><strong>配置验证成功！</strong></p>
          <p style="margin: 10px 0 5px 0;">用户信息：</p>
          <ul style="margin: 0; padding-left: 20px;">
            <li>用户ID: ${userInfo.user_id || '-'}</li>
            <li>手机号: ${userInfo.mobile || '-'}</li>
            <li>邮箱: ${userInfo.email || '-'}</li>
            <li>地区: ${userInfo.user_residence || '-'}</li>
            <li>会员等级: ${userInfo.membership_level || 0}</li>
          </ul>
        </div>
      `
      ElMessageBox.alert(message, '验证成功', {
        confirmButtonText: '确定',
        type: 'success',
        dangerouslyUseHTMLString: true
      })
    } else {
      ElMessageBox.alert(
          `${result.message}${result.error_code ? `\n错误代码: ${result.error_code}` : ''}`,
          '验证失败',
          {
            confirmButtonText: '确定',
            type: 'warning'
          }
      )
    }
  } catch (error) {
    ElMessage.error('验证失败: ' + error.message)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  jsonError.value = ''
}

// 导入功能相关方法
const showImportDialog = () => {
  importDialogVisible.value = true
  curlCommand.value = ''
  importError.value = ''
  importSuccess.value = ''
}

const handleImportCurl = () => {
  if (!curlCommand.value.trim()) {
    importError.value = '请输入 curl 命令'
    return
  }

  importing.value = true
  importError.value = ''
  importSuccess.value = ''

  try {
    // 解析 curl 命令
    const parsed = parseCurlCommand(curlCommand.value)

    // 验证解析结果
    const validation = validateParsedCurl(parsed)
    if (!validation.valid) {
      importError.value = validation.message
      return
    }

    // 格式化 headers 并填充到表单
    headersText.value = formatHeaders(parsed.headers)
    form.value.headers = parsed.headers
    jsonError.value = ''

    // 显示成功消息并立即关闭对话框
    ElMessage.success('Headers 导入成功！')
    importDialogVisible.value = false
  } catch (error) {
    importError.value = '解析失败: ' + error.message
    console.error('解析错误:', error)
  } finally {
    importing.value = false
  }
}

const handleImportDialogClose = () => {
  curlCommand.value = ''
  importError.value = ''
  importSuccess.value = ''
}

// 生命周期
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.config-view {
  max-width: 1400px;
  margin: 20px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>