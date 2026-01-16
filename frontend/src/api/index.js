import axios from 'axios'
import { ElMessage } from 'element-plus'

// 使用环境变量配置API地址
const getBaseURL = () => {
  // 如果配置了VITE_API_URL，使用配置的URL
  if (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.trim()) {
    const apiUrl = import.meta.env.VITE_API_URL.trim()
    // 如果是完整URL（包含http://或https://），直接使用
    if (apiUrl.startsWith('http://') || apiUrl.startsWith('https://')) {
      return apiUrl
    }
    // 否则作为路径使用
    return apiUrl
  }
  
  // 生产环境：尝试从window.location推断
  if (import.meta.env.PROD) {
    // 如果当前页面是完整URL，使用相对路径
    return '/api'
  }
  
  // 开发环境：使用相对路径（由vite代理处理）
  return '/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 只有非登录接口的401错误才认为是token过期
    // 登录接口返回的401不应该触发这个逻辑（实际上登录接口现在返回200了）
    const isLoginRequest = error.config?.url?.includes('/login')
    
    // 处理401未授权错误（token过期）
    if (error.response?.status === 401 && !isLoginRequest) {
      // 避免重复提示（如果已经在登录页就不跳转）
      if (window.location.pathname !== '/login') {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 清除用户store状态
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }
    
    // 处理404用户不存在等错误
    if (error.response?.status === 404) {
      const errorMsg = error.response?.data?.error || '资源不存在'
      // 如果是用户不存在，清除登录状态
      if (errorMsg.includes('用户不存在') || errorMsg.includes('账户不存在')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        if (window.location.pathname !== '/login') {
          ElMessage.error('用户信息已失效，请重新登录')
          window.location.href = '/login'
          return Promise.reject(error)
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export default api




