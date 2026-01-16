import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import { dirname } from 'path'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// 读取根目录的.env文件（如果存在）
const rootEnvPath = path.resolve(__dirname, '..', '.env')
let rootEnv = {}
if (fs.existsSync(rootEnvPath)) {
  const envContent = fs.readFileSync(rootEnvPath, 'utf-8')
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim()
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...valueParts] = trimmed.split('=')
      if (key && valueParts.length > 0) {
        rootEnv[key.trim()] = valueParts.join('=').trim()
      }
    }
  })
}

export default defineConfig(({ command, mode }) => {
  // 加载环境变量（Vite会自动加载.env文件）
  const env = loadEnv(mode, process.cwd(), '')
  
  // 合并根目录的.env变量（优先级更高）
  const mergedEnv = { ...env, ...rootEnv }
  
  // 获取API地址（根据部署模式）
  const getApiUrl = () => {
    // 如果手动指定了VITE_API_URL，优先使用
    if (mergedEnv.VITE_API_URL && mergedEnv.VITE_API_URL.trim()) {
      return mergedEnv.VITE_API_URL.trim()
    }
    
    // 根据部署模式自动生成
    const deployMode = (mergedEnv.DEPLOY_MODE || 'local').toLowerCase()
    
    if (deployMode === 'cloud') {
      const publicDomain = (mergedEnv.PUBLIC_DOMAIN || '').trim()
      const publicIp = (mergedEnv.PUBLIC_IP || '').trim()
      const backendPort = mergedEnv.PORT || '5000'
      
      if (publicDomain) {
        // 优先使用HTTPS
        return `https://${publicDomain}/api`
      } else if (publicIp) {
        return `http://${publicIp}:${backendPort}/api`
      }
    }
    
    // 默认本地开发
    return 'http://localhost:5000'
  }
  
  const apiUrl = getApiUrl()
  
  // 获取代理目标地址（本地开发时固定为 localhost:5000）
  const getProxyTarget = () => {
    // 在开发环境中，总是使用本地代理
    if (command === 'serve') {
      return 'http://localhost:5000'
    }
    // 生产环境使用配置的API地址（去掉 /api 前缀）
    if (apiUrl.includes('/api')) {
      return apiUrl.replace('/api', '')
    }
    return apiUrl
  }
  
  const proxyTarget = getProxyTarget()
  
  // 在开发环境中，不设置 VITE_API_URL，让前端使用相对路径 /api（通过代理）
  // 在生产环境中，使用配置的 API 地址
  const clientApiUrl = command === 'serve' ? '' : apiUrl
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    server: {
      port: parseInt(mergedEnv.VITE_PORT || '5173'),
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          // 保留 /api 前缀（因为后端路由都是以 /api 开头的）
          rewrite: (path) => path
        }
      }
    },
    // 将环境变量暴露给客户端
    // 开发环境：不设置 VITE_API_URL，让前端使用相对路径 /api
    // 生产环境：使用配置的 API 地址
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(clientApiUrl)
    }
  }
})




