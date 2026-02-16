import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserUpdate, LoginRequest } from '../api/superadmin'
import {
  login as apiLogin,
  getUserList as apiGetUserList,
  updateUser as apiUpdateUser,
  patchUser as apiPatchUser,
  deleteUser as apiDeleteUser
} from '../api/superadmin'

export const useSuperadminStore = defineStore('superadmin', () => {
  // 状态
  const users = ref<User[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')
  const isAuthenticated = computed(() => !!accessToken.value)

  // 登录
  const login = async (credentials: LoginRequest) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiLogin(credentials)
      const data = response.data
      
      // 保存令牌
      accessToken.value = data.access
      refreshToken.value = data.refresh
      
      // 保存到本地存储
      localStorage.setItem('superadminAccessToken', data.access)
      localStorage.setItem('superadminRefreshToken', data.refresh)
      
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    // 清除本地存储
    localStorage.removeItem('superadminAccessToken')
    localStorage.removeItem('superadminRefreshToken')
    
    // 重置状态
    accessToken.value = ''
    refreshToken.value = ''
    users.value = []
    error.value = ''
    
    return { success: true }
  }

  // 初始化认证状态（从本地存储恢复）
  const initializeAuth = () => {
    const storedAccessToken = localStorage.getItem('superadminAccessToken')
    const storedRefreshToken = localStorage.getItem('superadminRefreshToken')

    if (storedAccessToken) accessToken.value = storedAccessToken
    if (storedRefreshToken) refreshToken.value = storedRefreshToken
  }

  // 清除认证信息
  const clearAuth = () => {
    accessToken.value = ''
    refreshToken.value = ''
    error.value = ''
    
    localStorage.removeItem('superadminAccessToken')
    localStorage.removeItem('superadminRefreshToken')
  }

  // 计算属性
  const userCount = computed(() => users.value.length)
  const sortedUsers = computed(() => {
    return [...users.value].sort((a, b) => {
      return new Date(b.date_joined).getTime() - new Date(a.date_joined).getTime()
    })
  })

  // 获取用户列表
  const getUserList = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetUserList()
      const data = response.data
      
      users.value = data
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '获取用户列表失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 更新用户信息
  const updateUser = async (userId: number, userData: UserUpdate) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiUpdateUser(userId, userData)
      const data = response.data
      
      // 更新本地用户列表
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = data
      }
      
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '更新用户信息失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 部分更新用户信息
  const patchUser = async (userId: number, userData: Partial<UserUpdate>) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiPatchUser(userId, userData)
      const data = response.data
      
      // 更新本地用户列表
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = data
      }
      
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '更新用户信息失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 删除用户
  const deleteUser = async (userId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiDeleteUser(userId)
      
      // 从本地用户列表中移除
      users.value = users.value.filter(user => user.id !== userId)
      
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除用户失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 清除错误信息
  const clearError = () => {
    error.value = ''
  }

  // 重置状态
  const resetState = () => {
    users.value = []
    error.value = ''
  }

  return {
    // 状态
    users,
    isLoading,
    error,
    accessToken,
    refreshToken,
    
    // 计算属性
    userCount,
    sortedUsers,
    isAuthenticated,
    
    // 方法
    login,
    logout,
    getUserList,
    updateUser,
    patchUser,
    deleteUser,
    clearError,
    resetState,
    initializeAuth,
    clearAuth
  }
})
