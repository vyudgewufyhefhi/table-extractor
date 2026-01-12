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
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  function loadUserFromStorage() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
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

