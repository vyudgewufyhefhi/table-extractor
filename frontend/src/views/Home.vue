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

      <el-main class="main-container single-column">
        <div class="panel-content full-width">
          <!-- 提示词区域 -->
          <h3 class="panel-title">步骤一：复制提示词，喂给AI</h3>
          <el-alert
            title="请将以下提示词完整复制后，粘贴到AI中运行。"
            type="warning"
            show-icon
            class="prompt-alert"
          />
          <div class="prompt-area">
            <el-input
              v-model="promptText"
              type="textarea"
              :rows="8"
              readonly
            />
            <div class="prompt-actions">
              <el-button type="primary" @click="copyPrompt">复制提示词</el-button>
              <span class="prompt-tips">
                建议：左屏打开本工具，右屏打开 PDF 阅读器，方便对照检查。
              </span>
            </div>
          </div>

          <!-- 粘贴文本区域 -->
          <h3 class="panel-title">步骤二：将AI返回的纯文本粘贴到下方</h3>
          <el-alert
            title="要求：AI需返回纯文本，每一行对应表格中的一行，各列之间用一个或多个空格分隔。"
            type="warning"
            show-icon
            class="prompt-alert"
          />
          <el-input
            v-model="manualText"
            type="textarea"
            :rows="18"
            placeholder="在此粘贴AI返回的表格文本，每行一条记录，列与列之间用空格分隔……"
            class="manual-textarea"
          />
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :loading="generating"
              @click="handleManualGenerate"
            >
              生成Excel
            </el-button>
            <el-button size="large" @click="clearManualText">清空文本</el-button>
          </div>

          <!-- 预览解析后的表格 -->
          <div class="edit-area" v-if="tablePreview.headers.length" ref="previewAreaRef">
            <div class="edit-header">
              <span>预览：解析后的表格（仅供检查）</span>
            </div>
            <div class="table-editor">
              <el-table
                :data="tablePreview.rows"
                border
                style="width: 100%"
                max-height="300"
              >
                <el-table-column
                  v-for="(header, index) in tablePreview.headers"
                  :key="index"
                  :prop="`col${index}`"
                  :label="header || `列${index + 1}`"
                  min-width="120"
                  align="center"
                >
                  <template #default="{ row }">
                    {{ row[index] }}
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="excel-preview" v-if="lastRecord">
              <div class="excel-header">
                <span>最近一次生成：{{ formatLastRecordTime(lastRecord) }}</span>
                <div>
                  <el-button type="primary" size="large" @click="downloadLastExcel">
                    下载Excel
                  </el-button>
                  <el-button type="success" size="large" @click="saveToHistory" :disabled="saving">
                    {{ saving ? '保存中...' : '存入历史记录' }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

// ---- 新增：手动文本模式 ----
const promptText = ref(`提取出我上传的文件中的表格，如果每页都有相同的表头，保留一个就行。
表格中每个数据可能占多行，甚至存在分页现象，请保证数据的完整性，不要被水印干扰。
即使数据缺失，显示"-"、"/"等占位符，也需要原样返回，不要省略。
请将所有表格按行展开为纯文本，每一行对应原表格中的一行记录。
同一行中的不同单元格之间使用一个或多个空格分隔，不要使用制表符或逗号。
不要输出额外说明、标题或注释，只输出纯文本内容。`)

// 从localStorage恢复文本
const manualText = ref(localStorage.getItem('manual_text_input') || '')
const generating = ref(false)
const tablePreview = reactive({
  headers: [],
  rows: []
})
const lastRecord = ref(null)
const previewAreaRef = ref(null)
const saving = ref(false)

// 监听文本变化，保存到localStorage
watch(manualText, (newVal) => {
  if (newVal) {
    localStorage.setItem('manual_text_input', newVal)
  } else {
    localStorage.removeItem('manual_text_input')
  }
})

const copyPrompt = async () => {
  try {
    await navigator.clipboard.writeText(promptText.value)
    ElMessage.success('提示词已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

const clearManualText = () => {
  manualText.value = ''
  localStorage.removeItem('manual_text_input')
  tablePreview.headers = []
  tablePreview.rows = []
}

const handleManualGenerate = async () => {
  if (!manualText.value.trim()) {
    ElMessage.warning('请先粘贴AI返回的文本')
    return
  }

  if (!userStore.user) {
    ElMessage.error('请先登录')
    router.push('/login')
    return
  }

  generating.value = true
  try {
    const res = await api.post('/manual/parse', {
      user_id: userStore.user.id,
      raw_text: manualText.value
    })

    if (res.data.success) {
      ElMessage.success('解析并生成Excel成功！')
      const data = res.data.data
      // 存储临时数据（不保存到历史记录）
      lastRecord.value = {
        title: data.title,
        excel_path: data.excel_path,
        excel_filename: data.excel_filename,
        table_data: data.table_data,
        raw_text: data.raw_text
      }
      // 显示预览
      if (data.table_data) {
        tablePreview.headers = data.table_data.headers || []
        tablePreview.rows = data.table_data.rows || []
      }
      // 等待DOM更新后，自动滚动到预览区域
      await nextTick()
      setTimeout(() => {
        if (previewAreaRef.value) {
          previewAreaRef.value.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          })
        }
      }, 200)
    } else {
      ElMessage.error(res.data.error || '解析失败')
    }
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.error || error.message))
  } finally {
    generating.value = false
  }
}

// 格式化最后一条记录的时间
const formatLastRecordTime = (record) => {
  if (!record || !record.title) return '-'
  // title 格式为 2026年01月16日13:45:30
  return record.title
}

const downloadLastExcel = () => {
  if (!lastRecord.value || !lastRecord.value.excel_path) return
  // 如果已保存到历史记录，使用历史记录下载接口
  if (lastRecord.value.id) {
    window.open(`/api/manual/${lastRecord.value.id}/download-excel`, '_blank')
  } else {
    // 临时文件，使用临时下载接口
    const filename = lastRecord.value.title + '.xlsx'
    const downloadUrl = `/api/manual/download-temp?path=${encodeURIComponent(lastRecord.value.excel_path)}&filename=${encodeURIComponent(filename)}`
    window.open(downloadUrl, '_blank')
  }
}

const saveToHistory = async () => {
  if (!lastRecord.value || !userStore.user) {
    ElMessage.error('请先登录')
    return
  }

  if (!lastRecord.value.excel_path) {
    ElMessage.error('Excel文件不存在')
    return
  }

  saving.value = true
  try {
    const res = await api.post('/manual/save', {
      user_id: userStore.user.id,
      title: lastRecord.value.title,
      raw_text: lastRecord.value.raw_text,
      table_data: lastRecord.value.table_data,
      excel_path: lastRecord.value.excel_path
    })

    if (res.data.success) {
      ElMessage.success('已保存到历史记录')
      // 更新lastRecord，使其包含record_id，这样下载可以直接使用历史记录的接口
      lastRecord.value.id = res.data.record.id
    } else {
      ElMessage.error(res.data.error || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
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

// 组件卸载：当前模式无需定时器清理，保留空钩子以备后续扩展
onUnmounted(() => {})
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;
  line-height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  padding: 20px;
}

.single-column {
  background: #f5f7fa;
}

.panel-content {
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: calc(100vh - 100px);
  overflow: auto;
}

.full-width {
  width: 100%;
  margin: 0 auto;
  max-width: 1200px;
}

.panel-title {
  margin-bottom: 20px;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.prompt-alert {
  margin-bottom: 10px;
}

.prompt-area {
  margin-bottom: 20px;
}

.prompt-actions {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.prompt-tips {
  font-size: 13px;
  color: #606266;
}

.manual-textarea {
  width: 100%;
  font-family: Consolas, 'Courier New', monospace;
}

.edit-area {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 600;
  color: #303133;
}

.table-editor {
  margin-bottom: 20px;
  max-height: 300px;
  overflow: auto;
}

.excel-preview {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.excel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #606266;
}
</style>

