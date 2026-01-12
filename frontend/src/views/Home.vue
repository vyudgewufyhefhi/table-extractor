<template>
  <div class="home-container">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <h2 class="logo">表格提取工具</h2>
          <div class="header-right">
            <el-button type="text" @click="$router.push('/history')">
              <el-icon><Document /></el-icon>
              历史记录
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

      <el-container class="main-container">
        <!-- 左侧：文件上传和识别区域 -->
        <el-aside width="50%" class="left-panel">
          <div class="panel-content">
            <h3 class="panel-title">文件上传</h3>
            
            <!-- 文件上传区域 -->
            <el-upload
              ref="uploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              :multiple="true"
              accept=".pdf,.png,.jpg,.jpeg"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、PNG、JPG 格式，可批量上传
                </div>
              </template>
            </el-upload>

            <!-- 文件列表 -->
            <div class="file-list" v-if="fileList.length > 0">
              <div class="file-item" v-for="(file, index) in fileList" :key="index">
                <div class="file-info">
                  <el-icon><Document /></el-icon>
                  <span class="file-name">{{ file.name }}</span>
                  <el-tag :type="getFileStatusType(file.status)" size="small">
                    {{ getFileStatusText(file.status) }}
                  </el-tag>
                </div>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="removeFile(index)"
                >
                  删除
                </el-button>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons" v-if="fileList.length > 0">
              <el-button
                type="primary"
                size="large"
                :loading="recognizing"
                @click="handleRecognize"
                :disabled="recognizing || fileList.length === 0"
              >
                <el-icon v-if="!recognizing"><Search /></el-icon>
                {{ recognizing ? '识别中...' : '开始识别' }}
              </el-button>
              <el-button
                size="large"
                @click="clearFiles"
                :disabled="recognizing"
              >
                清空文件
              </el-button>
            </div>
          </div>
        </el-aside>

        <!-- 右侧：预览和编辑区域 -->
        <el-main class="right-panel">
          <div class="panel-content">
            <h3 class="panel-title">预览与编辑</h3>
            
            <!-- 文件选择器（批量上传时） -->
            <div class="file-selector" v-if="recognizedFiles.length > 1">
              <el-select v-model="currentFileIndex" placeholder="选择要查看的文件">
                <el-option
                  v-for="(file, index) in recognizedFiles"
                  :key="index"
                  :label="file.filename"
                  :value="index"
                />
              </el-select>
            </div>

            <!-- 预览区域 -->
            <div class="preview-area" v-if="currentPreview">
              <div class="preview-header">
                <span>文件预览</span>
                <el-button
                  type="text"
                  size="small"
                  @click="togglePreviewSize"
                >
                  {{ previewFullscreen ? '缩小' : '全屏' }}
                </el-button>
              </div>
              <div class="preview-content" :class="{ 'fullscreen': previewFullscreen }">
                <img
                  v-if="currentPreview.type === 'image'"
                  :src="currentPreview.data"
                  alt="预览"
                  class="preview-image"
                />
                <div v-else class="preview-placeholder">
                  <el-icon><Document /></el-icon>
                  <p>PDF预览</p>
                </div>
              </div>
            </div>

            <!-- 识别结果编辑区域 -->
            <div class="edit-area" v-if="currentFileData">
              <div class="edit-header">
                <span>表格数据编辑</span>
                <el-button
                  type="primary"
                  size="small"
                  @click="handleGenerateExcel"
                  :disabled="!currentFileData.ai_result"
                >
                  生成Excel
                </el-button>
              </div>
              
              <div class="table-editor">
                <el-table
                  :data="editableTableData.rows"
                  border
                  style="width: 100%"
                  max-height="400"
                >
                  <el-table-column
                    v-for="(header, index) in editableTableData.headers"
                    :key="index"
                    :prop="`col${index}`"
                    :label="header"
                    min-width="120"
                  >
                    <template #default="{ row }">
                      <el-input
                        v-model="row[index]"
                        size="small"
                        @change="handleDataChange"
                      />
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <!-- Excel预览 -->
              <div class="excel-preview" v-if="currentFileData.excel_path">
                <div class="excel-header">
                  <span>Excel文件已生成</span>
                  <div>
                    <el-button
                      type="primary"
                      size="small"
                      @click="downloadExcel"
                    >
                      下载
                    </el-button>
                    <el-button
                      size="small"
                      @click="copyExcelLink"
                    >
                      复制链接
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <el-empty
              v-if="!currentPreview && !currentFileData"
              description="请上传文件开始使用"
            />
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const uploadRef = ref(null)
const fileList = ref([])
const recognizedFiles = ref([])
const currentFileIndex = ref(0)
const recognizing = ref(false)
const previewFullscreen = ref(false)
const editableTableData = ref({ headers: [], rows: [] })

// 当前预览文件
const currentPreview = computed(() => {
  if (recognizedFiles.value.length === 0) return null
  const file = recognizedFiles.value[currentFileIndex.value]
  return file?.preview || null
})

// 当前文件数据
const currentFileData = computed(() => {
  if (recognizedFiles.value.length === 0) return null
  return recognizedFiles.value[currentFileIndex.value] || null
})

// 表格数据（用于显示）
const tableData = computed(() => {
  const file = currentFileData.value
  if (!file) {
    editableTableData.value = { headers: [], rows: [] }
    return { headers: [], rows: [] }
  }
  
  const data = file.corrected_result || file.ai_result
  if (!data) {
    editableTableData.value = { headers: [], rows: [] }
    return { headers: [], rows: [] }
  }
  
  // 处理多页表格
  let result
  if (data.multi_page && data.pages) {
    result = data.pages[0] || { headers: [], rows: [] }
  } else {
    result = data
  }
  
  // 更新可编辑数据（深拷贝）
  editableTableData.value = {
    headers: [...(result.headers || [])],
    rows: (result.rows || []).map(row => [...row])
  }
  
  return result
})

// 文件状态
const getFileStatusType = (status) => {
  const map = {
    uploaded: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getFileStatusText = (status) => {
  const map = {
    uploaded: '已上传',
    processing: '识别中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || '未知'
}

// 文件变化处理
const handleFileChange = (file, files) => {
  fileList.value = files
}

// 移除文件
const removeFile = (index) => {
  fileList.value.splice(index, 1)
  // 同时移除对应的识别结果
  if (index < recognizedFiles.value.length) {
    recognizedFiles.value.splice(index, 1)
    if (currentFileIndex.value >= recognizedFiles.value.length) {
      currentFileIndex.value = Math.max(0, recognizedFiles.value.length - 1)
    }
  }
}

// 清空文件
const clearFiles = () => {
  fileList.value = []
  recognizedFiles.value = []
  currentFileIndex.value = 0
}

// 开始识别
const handleRecognize = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  if (!userStore.user) {
    ElMessage.error('请先登录')
    router.push('/login')
    return
  }

  recognizing.value = true

  try {
    // 逐个上传并识别文件
    for (let i = 0; i < fileList.value.length; i++) {
      const file = fileList.value[i]
      
      // 更新文件状态
      file.status = 'processing'
      
      try {
        // 上传文件
        const formData = new FormData()
        formData.append('file', file.raw)
        formData.append('user_id', userStore.user.id)

        const uploadRes = await api.post('/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (!uploadRes.data.success) {
          throw new Error(uploadRes.data.error || '上传失败')
        }

        const fileRecord = uploadRes.data.file
        file.fileId = fileRecord.id

        // 获取预览
        const previewRes = await api.get(`/files/${fileRecord.id}/preview`)
        if (previewRes.data.success) {
          fileRecord.preview = {
            type: fileRecord.file_type === 'pdf' ? 'pdf' : 'image',
            data: previewRes.data.preview
          }
        }

        // 添加到识别文件列表（实时显示）
        recognizedFiles.value.push(fileRecord)

        // 开始识别
        const recognizeRes = await api.post(`/files/${fileRecord.id}/recognize`)
        
        if (recognizeRes.data.success) {
          file.status = 'completed'
          // 更新识别结果
          const updatedFile = recognizeRes.data.file
          const index = recognizedFiles.value.findIndex(f => f.id === fileRecord.id)
          if (index !== -1) {
            recognizedFiles.value[index] = updatedFile
            // 如果有预览，保留预览数据
            if (fileRecord.preview) {
              recognizedFiles.value[index].preview = fileRecord.preview
            }
          }
        } else {
          file.status = 'failed'
          ElMessage.error(`${file.name}: ${recognizeRes.data.error}`)
        }
      } catch (error) {
        file.status = 'failed'
        ElMessage.error(`${file.name}: ${error.message || '处理失败'}`)
      }
    }

    ElMessage.success('识别完成')
  } catch (error) {
    ElMessage.error('识别过程出错: ' + error.message)
  } finally {
    recognizing.value = false
  }
}

// 数据变化处理
const handleDataChange = async () => {
  const file = currentFileData.value
  if (!file || !file.id) return

  try {
    const data = {
      headers: [...editableTableData.value.headers],
      rows: editableTableData.value.rows.map(row => [...row])
    }
    
    await api.post(`/files/${file.id}/correct`, {
      corrected_data: data
    })
    
    // 更新本地数据
    const index = recognizedFiles.value.findIndex(f => f.id === file.id)
    if (index !== -1) {
      recognizedFiles.value[index].corrected_result = data
    }
    
    ElMessage.success('已保存')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 生成Excel
const handleGenerateExcel = async () => {
  const file = currentFileData.value
  if (!file || !file.id) return

  try {
    const res = await api.post(`/files/${file.id}/generate-excel`)
    if (res.data.success) {
      ElMessage.success('Excel生成成功')
      // 更新文件数据
      const index = recognizedFiles.value.findIndex(f => f.id === file.id)
      if (index !== -1) {
        recognizedFiles.value[index] = res.data.file
        if (recognizedFiles.value[index].preview) {
          recognizedFiles.value[index].preview = file.preview
        }
      }
    } else {
      ElMessage.error(res.data.error || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成失败: ' + error.message)
  }
}

// 下载Excel
const downloadExcel = () => {
  const file = currentFileData.value
  if (!file || !file.id) return
  
  window.open(`/api/files/${file.id}/download-excel`, '_blank')
}

// 复制Excel链接
const copyExcelLink = async () => {
  const file = currentFileData.value
  if (!file || !file.id) return
  
  const link = `${window.location.origin}/api/files/${file.id}/download-excel`
  try {
    await navigator.clipboard.writeText(link)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 切换预览大小
const togglePreviewSize = () => {
  previewFullscreen.value = !previewFullscreen.value
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
  }
})
</script>

<style scoped>
.home-container {
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

.main-container {
  flex: 1;
  overflow: hidden;
}

.left-panel,
.right-panel {
  border: 1px solid #e4e7ed;
  margin: 10px;
  border-radius: 8px;
  background: #fff;
  overflow: auto;
}

.panel-content {
  padding: 20px;
}

.panel-title {
  margin-bottom: 20px;
  font-size: 18px;
  color: #303133;
}

.upload-area {
  width: 100%;
}

.file-list {
  margin-top: 20px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.preview-area {
  margin-bottom: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preview-content {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #f5f7fa;
  max-height: 500px;
  overflow: auto;
}

.preview-content.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2000;
  max-height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  height: auto;
  display: block;
}

.preview-placeholder {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.file-selector {
  margin-bottom: 20px;
}

.edit-area {
  margin-top: 20px;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.table-editor {
  margin-bottom: 20px;
}

.excel-preview {
  margin-top: 20px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 4px;
}

.excel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

