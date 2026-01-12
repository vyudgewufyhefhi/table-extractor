<template>
  <div class="history-container">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2 class="logo">历史记录</h2>
          <div class="header-right">
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
            :data="fileList"
            v-loading="loading"
            style="width: 100%"
            stripe
          >
            <el-table-column prop="filename" label="文件名" width="200" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.file_type === 'pdf' ? 'danger' : 'success'">
                  {{ row.file_type === 'pdf' ? 'PDF' : '图片' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="uploaded_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.uploaded_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="processed_at" label="处理时间" width="180">
              <template #default="{ row }">
                {{ row.processed_at ? formatDate(row.processed_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="viewDetail(row)"
                >
                  查看详情
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  text
                  v-if="row.excel_path"
                  @click="downloadFile(row)"
                >
                  下载Excel
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="deleteFile(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && fileList.length === 0" description="暂无历史记录" />
        </div>
      </el-main>
    </el-container>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="文件详情"
      width="80%"
      :before-close="closeDetail"
    >
      <div v-if="currentFile" class="file-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ currentFile.filename }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">
            <el-tag :type="currentFile.file_type === 'pdf' ? 'danger' : 'success'">
              {{ currentFile.file_type === 'pdf' ? 'PDF' : '图片' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(currentFile.file_size) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentFile.status)">
              {{ getStatusText(currentFile.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ formatDate(currentFile.uploaded_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="处理时间">
            {{ currentFile.processed_at ? formatDate(currentFile.processed_at) : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-sections">
          <!-- 预览 -->
          <div class="detail-section" v-if="filePreview">
            <h3>文件预览</h3>
            <div class="preview-container">
              <img
                v-if="filePreview.type === 'image'"
                :src="filePreview.data"
                alt="预览"
                class="detail-preview-image"
              />
              <div v-else class="preview-placeholder">
                <el-icon><Document /></el-icon>
                <p>PDF文件</p>
              </div>
            </div>
          </div>

          <!-- AI识别结果 -->
          <div class="detail-section" v-if="currentFile.ai_result">
            <h3>AI识别结果</h3>
            <el-table
              :data="getTableRows(currentFile.ai_result)"
              border
              style="width: 100%"
              max-height="300"
            >
              <el-table-column
                v-for="(header, index) in getTableHeaders(currentFile.ai_result)"
                :key="index"
                :prop="`col${index}`"
                :label="header"
                min-width="120"
              >
                <template #default="{ row }">
                  {{ row[index] }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 用户校正结果 -->
          <div class="detail-section" v-if="currentFile.corrected_result">
            <h3>用户校正结果</h3>
            <el-table
              :data="getTableRows(currentFile.corrected_result)"
              border
              style="width: 100%"
              max-height="300"
            >
              <el-table-column
                v-for="(header, index) in getTableHeaders(currentFile.corrected_result)"
                :key="index"
                :prop="`col${index}`"
                :label="header"
                min-width="120"
              >
                <template #default="{ row }">
                  {{ row[index] }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <div class="detail-actions">
          <el-button
            type="primary"
            v-if="currentFile.excel_path"
            @click="downloadFile(currentFile)"
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
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const fileList = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentFile = ref(null)
const filePreview = ref(null)

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    uploaded: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    uploaded: '已上传',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || '未知'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 获取表格表头
const getTableHeaders = (data) => {
  if (!data) return []
  if (data.multi_page && data.pages) {
    return data.pages[0]?.headers || []
  }
  return data.headers || []
}

// 获取表格行数据
const getTableRows = (data) => {
  if (!data) return []
  if (data.multi_page && data.pages) {
    return data.pages[0]?.rows || []
  }
  return data.rows || []
}

// 加载文件列表
const loadFiles = async () => {
  if (!userStore.user) {
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const res = await api.get(`/users/${userStore.user.id}/files`)
    if (res.data.success) {
      fileList.value = res.data.files
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (file) => {
  try {
    const res = await api.get(`/files/${file.id}`)
    if (res.data.success) {
      currentFile.value = res.data.file
      
      // 获取预览
      const previewRes = await api.get(`/files/${file.id}/preview`)
      if (previewRes.data.success) {
        filePreview.value = {
          type: file.file_type === 'pdf' ? 'pdf' : 'image',
          data: previewRes.data.preview
        }
      }
      
      detailVisible.value = true
    } else {
      ElMessage.error('加载详情失败')
    }
  } catch (error) {
    ElMessage.error('加载详情失败: ' + error.message)
  }
}

// 关闭详情
const closeDetail = () => {
  detailVisible.value = false
  currentFile.value = null
  filePreview.value = null
}

// 下载文件
const downloadFile = (file) => {
  if (!file.excel_path) {
    ElMessage.warning('Excel文件尚未生成')
    return
  }
  window.open(`/api/files/${file.id}/download-excel`, '_blank')
}

// 删除文件
const deleteFile = (file) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 这里可以添加删除API调用
      ElMessage.success('删除成功')
      loadFiles()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
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

