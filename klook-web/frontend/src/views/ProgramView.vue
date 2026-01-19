<template>
  <div class="program-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>优惠券项目管理</span>
          <el-space>
            <el-button @click="loadPrograms" :loading="loading">
              <el-icon>
                <Refresh/>
              </el-icon>
              刷新
            </el-button>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon>
                <Plus/>
              </el-icon>
              新建项目
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 项目列表 -->
      <el-table
          v-loading="loading"
          :data="programs"
          style="width: 100%"
          :default-sort="{ prop: 'created_at', order: 'descending' }"
      >
        <el-table-column prop="id" label="ID" width="80"/>
        <el-table-column prop="uuid" label="项目 UUID" min-width="200"/>
        <el-table-column prop="name" label="项目名称" min-width="180"/>
        <el-table-column prop="description" label="项目描述" min-width="200" show-overflow-tooltip/>
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="viewProgram(row)">
                查看
              </el-button>
              <el-button size="small" type="primary" @click="editProgram(row)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="deleteProgram(row)">
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && programs.length === 0" description="暂无项目，点击新建项目开始"/>
    </el-card>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="600px"
        @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="项目 UUID" prop="uuid">
          <el-input v-model="form.uuid" placeholder="请输入项目 UUID" :disabled="isEdit"/>
          <div style="font-size: 12px; color: #909399; margin-top: 5px">
            UUID 必须唯一，创建后不可修改
          </div>
        </el-form-item>
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称"/>
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入项目描述（可选）"
          />
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

    <!-- 查看项目详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="项目详情" width="600px">
      <el-form label-width="100px">
        <el-form-item label="ID">
          <el-input :value="viewingProgram?.id" disabled/>
        </el-form-item>
        <el-form-item label="项目 UUID">
          <el-input :value="viewingProgram?.uuid" disabled/>
        </el-form-item>
        <el-form-item label="项目名称">
          <el-input :value="viewingProgram?.name" disabled/>
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
              :value="viewingProgram?.description || '-'"
              type="textarea"
              :rows="3"
              disabled
          />
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input :value="formatDate(viewingProgram?.created_at)" disabled/>
        </el-form-item>
        <el-form-item label="更新时间">
          <el-input :value="formatDate(viewingProgram?.updated_at)" disabled/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Plus, Refresh} from '@element-plus/icons-vue'
import {programApi} from '../api/program'

// 数据
const loading = ref(false)
const programs = ref([])
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const viewingProgram = ref(null)

// 表单数据
const form = ref({
  id: null,
  uuid: '',
  name: '',
  description: ''
})

// 表单验证规则
const rules = {
  uuid: [
    {required: true, message: '请输入项目 UUID', trigger: 'blur'},
    {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入项目名称', trigger: 'blur'},
    {min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur'}
  ]
}

// 计算属性
const dialogTitle = ref('')

// 方法
const loadPrograms = async () => {
  loading.value = true
  try {
    const data = await programApi.getAll()
    programs.value = data.items
  } catch (error) {
    ElMessage.error('加载项目列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新建项目'
  form.value = {
    id: null,
    uuid: '',
    name: '',
    description: ''
  }
  dialogVisible.value = true
}

const editProgram = (program) => {
  isEdit.value = true
  dialogTitle.value = '编辑项目'
  form.value = {
    id: program.id,
    uuid: program.uuid,
    name: program.name,
    description: program.description || ''
  }
  dialogVisible.value = true
}

const viewProgram = (program) => {
  viewingProgram.value = program
  viewDialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await programApi.update(form.value.id, {
        name: form.value.name,
        description: form.value.description || null
      })
      ElMessage.success('项目更新成功')
    } else {
      await programApi.create({
        uuid: form.value.uuid,
        name: form.value.name,
        description: form.value.description || null
      })
      ElMessage.success('项目创建成功')
    }
    dialogVisible.value = false
    await loadPrograms()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const deleteProgram = async (program) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除项目 "${program.name}" 吗？此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await programApi.delete(program.id)
    ElMessage.success('项目删除成功')
    await loadPrograms()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
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
onMounted(() => {
  loadPrograms()
})
</script>

<style scoped>
.program-view {
  max-width: 1400px;
  margin: 20px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>