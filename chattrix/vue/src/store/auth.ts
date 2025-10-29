import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest, UserUpdateRequest, ChangePasswordRequest } from '../api/auth'
import { 
  login as apiLogin, 
  register as apiRegister, 
  logout as apiLogout,
  getCurrentUser as apiGetCurrentUser,
  updateProfile as apiUpdateProfile,
  updateProfileWithAvatar as apiUpdateProfileWithAvatar,
  refreshToken as apiRefreshToken,
   changePassword as apiChangePassword
} from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userId = computed(() => user.value?.id || null)
  const username = computed(() => user.value?.username || '')
  const userAvatar = computed(() => user.value?.user_avatar || '')
  const userStatus = computed(() => user.value?.user_status || 'offline')

  // 登录
  const login = async (credentials: LoginRequest) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiLogin(credentials)
      const  data  = response.data
      
      // 保存用户信息和令牌
      user.value = data.user
      accessToken.value = data.access
      refreshToken.value = data.refresh
      
      // 保存到本地存储
      localStorage.setItem('accessToken', data.access)
      localStorage.setItem('refreshToken', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 注册
const register = async (userData: RegisterRequest) => {
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await apiRegister(userData)
    const  data  = response.data
    
    // 注册成功后自动登录
    user.value = data
    
    return { success: true }
  } catch (err: any) {
    // 改进错误处理，提取更具体的错误信息
    let errorMessage = '注册失败'
    
    if (err.status === 400) {
      // 处理 400 错误（如用户名已存在）
      if (err.data?.message) {
        errorMessage = err.data.message
      } else if (err.data?.username?.[0]) {
        // Django REST framework 风格的错误格式
        errorMessage = err.data.username[0]
      }
    } else if (err.message) {
      // 其他类型的错误
      errorMessage = err.message
    }
    
    // 错误消息中英文映射，提供更好的中文用户体验
    const errorMessageMap: Record<string, string> = {
      'A user with that username already exists.': '该用户名已存在',
      'This field is required.': '此字段为必填项',
      'Passwords do not match.': '两次输入的密码不一致',
      'Password too short.': '密码长度不足',
      'Invalid username.': '无效的用户名'
      // 可以根据实际需要添加更多映射
    }
    
    // 检查是否有对应的中文错误消息
    if (errorMessageMap[errorMessage]) {
      errorMessage = errorMessageMap[errorMessage]
    }
    
    error.value = errorMessage
    return { success: false, error: error.value }
  } finally {
    isLoading.value = false
  }
}

  // 登出
  const logout = async () => {
    if (!refreshToken.value) {
      clearAuth()
      return { success: true }
    }

    isLoading.value = true
    error.value = ''
    
    try {
      await apiLogout(refreshToken.value)
      clearAuth()
      return { success: true }
    } catch (err: any) {
      // 即使登出API调用失败，也要清除本地数据
      clearAuth()
      return { success: true }
    } finally {
      isLoading.value = false
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async () => {
    if (!accessToken.value) return null

    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetCurrentUser()
      const  data  = response.data
      
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
      
      return data
    } catch (err: any) {
      error.value = err.message || '获取用户信息失败'
      // 如果获取用户信息失败，可能是令牌过期，尝试刷新
      if (err.status === 401) {
        await refreshAccessToken()
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

// 更新用户资料
const updateProfile = async (userData: UserUpdateRequest) => {
  isLoading.value = true
  error.value = ''
  
  try {
    let response;
    // 检查是否包含文件上传
    if (userData.user_avatar instanceof File) {
      // 使用专门处理文件上传的方法
      response = await apiUpdateProfileWithAvatar(userData);
    } else {
      // 普通更新请求
      response = await apiUpdateProfile(userData);
    }
    
    const  data  = response.data
    
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
    
    return { success: true }
  } catch (err: any) {
    error.value = err.message || '更新资料失败'
    return { success: false, error: error.value }
  } finally {
    isLoading.value = false
  }
}

const changePassword = async (passwordData: ChangePasswordRequest) => {
  isLoading.value = true
  error.value = ''
  
  try {
    await apiChangePassword(passwordData)
    
    return { success: true }
  } catch (err: any) {
    // 改进错误处理，提取更具体的错误信息
    let errorMessage = '修改密码失败'
    
    if (err.status === 400) {
      // 处理 400 错误（如密码不匹配、密码太弱等）
      if (err.data?.message) {
        errorMessage = err.data.message
      } else if (err.data?.old_password?.[0]) {
        // Django REST framework 风格的错误格式
        errorMessage = err.data.old_password[0]
      } else if (err.data?.new_password?.[0]) {
        errorMessage = err.data.new_password[0]
      }
    } else if (err.message) {
      // 其他类型的错误
      errorMessage = err.message
    }
    
    // 错误消息中英文映射，提供更好的中文用户体验
    const errorMessageMap: Record<string, string> = {
      'Current password is incorrect.': '当前密码不正确',
      'New password must be different from old password.': '新密码不能与旧密码相同',
      'New password is too short.': '新密码长度不足',
      'New password is too common.': '新密码过于常见',
      'Passwords do not match.': '两次输入的密码不一致'
      // 可以根据实际需要添加更多映射
    }
    
    // 检查是否有对应的中文错误消息
    if (errorMessageMap[errorMessage]) {
      errorMessage = errorMessageMap[errorMessage]
    }
    
    error.value = errorMessage
    return { success: false, error: error.value }
  } finally {
    isLoading.value = false
  }
}

  // 刷新访问令牌
  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false

    try {
      const response = await apiRefreshToken()
      const  data  = response.data
      
      accessToken.value = data.access
      refreshToken.value = data.refresh
      
      localStorage.setItem('accessToken', data.access)
      localStorage.setItem('refreshToken', data.refresh)
      
      return true
    } catch (err) {
      // 刷新失败，需要重新登录
      clearAuth()
      return false
    }
  }

  // 初始化认证状态（从本地存储恢复）
  const initializeAuth = () => {
    const storedAccessToken = localStorage.getItem('accessToken')
    const storedRefreshToken = localStorage.getItem('refreshToken')
    const storedUser = localStorage.getItem('user')

    if (storedAccessToken) accessToken.value = storedAccessToken
    if (storedRefreshToken) refreshToken.value = storedRefreshToken
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        localStorage.removeItem('user')
      }
    }
  }

  // 清除认证信息
  const clearAuth = () => {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    error.value = ''
    
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  // 设置错误信息
  const setError = (message: string) => {
    error.value = message
  }

  // 清除错误信息
  const clearError = () => {
    error.value = ''
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    userId,
    username,
    userAvatar,
    userStatus,
    
    // 方法
    login,
    register,
    logout,
    getCurrentUser,
    updateProfile,
    changePassword, 
    refreshAccessToken,
    initializeAuth,
    clearAuth,
    setError,
    clearError
  }
})