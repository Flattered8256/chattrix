<template>
  <button 
    class="logout-button"
    @click="handleLogout"
    :disabled="isLoading"
  >
    {{ isLoading ? '登出中...' : '登出' }}
  </button>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../store/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const isLoading = authStore.isLoading

// 处理登出逻辑
const handleLogout = async () => {
  try {
    const result = await authStore.logout()
    if (result.success) {
      // 登出成功后重定向到登录页面
      router.push({ name: 'login' })
    }
  } catch (error) {
    console.error('登出失败:', error)
    // 即使发生错误，也清除认证信息并重定向
    authStore.clearAuth()
    router.push({ name: 'login' })
  }
}
</script>

<style scoped>
.logout-button {
  /* 基本样式 */
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
  text-align: center;
  /* 矩形样式 */
  box-shadow: 0 2px 4px rgba(255, 77, 79, 0.2);
}

.logout-button:hover:not(:disabled) {
  background-color: #ff7875;
  box-shadow: 0 4px 8px rgba(255, 77, 79, 0.3);
  transform: translateY(-1px);
}

.logout-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(255, 77, 79, 0.2);
}

.logout-button:disabled {
  background-color: #f5f5f5;
  color: #bfbfbf;
  cursor: not-allowed;
  box-shadow: none;
}
</style>