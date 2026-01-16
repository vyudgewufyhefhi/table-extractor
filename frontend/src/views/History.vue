<template>
  <div class="history-container">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2 class="logo">历史记录</h2>
          <div class="header-right">
            <el-button @click="$router.back()">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <el-button type="primary" @click="$router.push('/')">
              <el-icon><Plus /></el-icon>
              新建任务
            </el-button>
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userStore.user?.username }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="history-content">
          <el-table
            :data="recordList"
            v-loading="loading"
            style="width: 100%"
            stripe
          >
            <el-table-column prop="title" label="标题" width="220" align="center" />
            <el-table-column prop="created_at" label="创建时间" width="220" align="center">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="viewRecord(row)"
                >
                  查看文本
                </el-button>
                <el-button
                  type="success"
                  size="default"
                  v-if="row.excel_path"
                  @click="downloadExcel(row)"
                >
                  下载Excel
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && recordList.length === 0" description="暂无历史记录" />
        </div>
      </el-main>
    </el-container>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="记录详情"
      width="80%"
      :before-close="closeDetail"
    >
      <div v-if="currentRecord" class="file-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题">{{ currentRecord.title }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentRecord.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-sections">
          <div class="detail-section">
            <h3>原始文本</h3>
            <el-input
              v-model="currentRecord.raw_text"
              type="textarea"
              :rows="16"
              readonly
              class="record-textarea"
            />
          </div>
        </div>

        <div class="detail-actions">
          <el-button
            type="primary"
            v-if="currentRecord.excel_path"
            @click="downloadExcel(currentRecord)"
          >
            下载Excel
          </el-button>
          <el-button @click="closeDetail">关闭</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, User, ArrowDown } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const recordList = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentRecord = ref(null)

// 格式化日期：格式为 2026年01月16日13:45:30
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  // 使用本地时间，格式化为：2026年01月16日13:45:30
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}年${month}月${day}日${hours}:${minutes}:${seconds}`
}

// 加载记录列表
const loadFiles = async () => {
  if (!userStore.user) {
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const res = await api.get(`/users/${userStore.user.id}/manual-records`)
    if (res.data.success) {
      recordList.value = res.data.records
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 查看记录详情
const viewRecord = (record) => {
  currentRecord.value = record
  detailVisible.value = true
}

// 关闭详情
const closeDetail = () => {
  detailVisible.value = false
  currentRecord.value = null
}

// 下载Excel
const downloadExcel = (record) => {
  if (!record.excel_path) {
    ElMessage.warning('Excel文件尚未生成')
    return
  }
  window.open(`/api/manual/${record.id}/download-excel`, '_blank')
}

// 处理用户命令
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  }
}

onMounted(() => {
  if (!userStore.user) {
    router.push('/login')
  } else {
    loadFiles()
  }
})
</script>

<style scoped>
.history-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;
  line-height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 100%;
}

.logo {
  margin: 0;
  font-size: 20px;
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  padding: 20px;
  background: #f5f7fa;
}

.history-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.file-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-sections {
  margin-top: 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.preview-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #f5f7fa;
  text-align: center;
}

.detail-preview-image {
  max-width: 100%;
  height: auto;
}

.preview-placeholder {
  padding: 40px;
  color: #909399;
}

.detail-actions {
  margin-top: 20px;
  text-align: right;
}
</style>

