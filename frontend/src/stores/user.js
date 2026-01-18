import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  
  const isLoggedIn = computed(() => !!user.value)
  
  async function login(username, password) {
    try {
      const response = await api.post('/login', { username, password })
      if (response.data.success) {
        // 清除之前用户的数据（如果有）
        const oldUserId = user.value?.id
        if (oldUserId && oldUserId !== response.data.user.id) {
          localStorage.removeItem(`manual_text_input_${oldUserId}`)
          localStorage.removeItem(`table_preview_${oldUserId}`)
          localStorage.removeItem(`last_record_${oldUserId}`)
        }
        
        user.value = response.data.user
        token.value = response.data.token || 'authenticated'
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        return { success: true }
      }
      return { success: false, error: response.data.error }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || '登录失败' }
    }
  }
  
  async function register(username, password) {
    try {
      const response = await api.post('/register', { username, password })
      if (response.data.success) {
        return { success: true, message: response.data.message }
      }
      return { success: false, error: response.data.error }
    } catch (error) {
      return { success: false, error: error.response?.data?.error || '注册失败' }
    }
  }
  
  function logout() {
    // 清除当前用户的所有数据
    const currentUserId = user.value?.id
    if (currentUserId) {
      // 清除该用户的文本输入数据
      localStorage.removeItem(`manual_text_input_${currentUserId}`)
      // 清除该用户的预览数据
      localStorage.removeItem(`table_preview_${currentUserId}`)
      localStorage.removeItem(`last_record_${currentUserId}`)
    }
    // 清除通用数据（兼容旧版本）
    localStorage.removeItem('manual_text_input')
    
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  function loadUserFromStorage() {
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')
    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser)
        token.value = storedToken
      } catch (e) {
        // 如果解析失败，清除无效数据
        localStorage.removeItem('user')
        localStorage.removeItem('token')
        user.value = null
        token.value = null
      }
    } else {
      // 如果token或user缺失，清除所有
      if (!storedToken && storedUser) {
        localStorage.removeItem('user')
        user.value = null
      }
      if (!storedUser && storedToken) {
        localStorage.removeItem('token')
        token.value = null
      }
    }
  }
  
  // 初始化时加载用户信息
  loadUserFromStorage()
  
  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    loadUserFromStorage
  }
})




