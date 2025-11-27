<template>
  <div class="register-form">
    <h2 class="form-title">用户注册</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username" class="form-label">用户名</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          class="form-input"
          placeholder="请输入用户名"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="password" class="form-label">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          class="form-input"
          placeholder="请输入密码"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="password_confirm" class="form-label">确认密码</label>
        <input
          id="password_confirm"
          v-model="form.password_confirm"
          type="password"
          class="form-input"
          placeholder="请再次输入密码"
          required
        />
      </div>
      
      <button 
        type="submit" 
        class="submit-button"
        :disabled="isLoading"
      >
        {{ isLoading ? '注册中...' : '注册' }}
      </button>
    </form>
    
    <div class="form-footer">
      <p class="redirect-text">
        已有账号？
        <router-link to="/login" class="redirect-link">立即登录</router-link>
      </p>
    </div>
  </div>
  
  <!-- Toast 提示组件 -->
  <Toast 
    v-if="toastMessage"
    :message="toastMessage"
    :type="toastType"
    @close="closeToast"
  />
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import type { RegisterRequest } from '../../api/auth'
import Toast from '../utils/toast.vue'

// 表单数据
const form = reactive<RegisterRequest>({
  username: '',
  password: '',
  password_confirm: ''
})

// 状态管理
const authStore = useAuthStore()
const router = useRouter()

// 组件状态
const isLoading = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

// 显示 Toast 提示
const showToast = (message: string, type: 'success' | 'error' = 'error') => {
  toastMessage.value = message
  toastType.value = type
}

// 关闭 Toast 提示
const closeToast = () => {
  toastMessage.value = ''
}

// 处理注册
const handleRegister = async () => {
  // 重置 Toast 消息
  closeToast()
  
  // 基本验证
  if (!form.username.trim()) {
    showToast('请输入用户名')
    return
  }
  
  if (!form.password) {
    showToast('请输入密码')
    return
  }
  
  if (form.password !== form.password_confirm) {
    showToast('两次输入的密码不一致')
    return
  }
  
  if (form.password.length < 6) {
    showToast('密码长度至少为6位')
    return
  }
  
  isLoading.value = true
  
  try {
    const result = await authStore.register(form)
    
    if (result.success) {
      // 注册成功，显示成功提示
      showToast('注册成功，请登录', 'success')
      // 2秒后跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      showToast(result.error || '注册失败')
    }
  } catch (error) {
    showToast('注册过程中发生错误')
    console.error('Register error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--surface-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--shadow-color);
  transition: all 0.3s ease;
}

.form-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--text-color);
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-sizing: border-box;
  background-color: var(--surface-color);
  color: var(--text-color);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.submit-button {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.submit-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.submit-button:disabled {
  background-color: var(--primary-disabled);
  cursor: not-allowed;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.redirect-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.redirect-link {
  color: var(--primary-color);
  text-decoration: none;
}

.redirect-link:hover {
  text-decoration: underline;
}

/* 深色模式特定样式 */
@media (prefers-color-scheme: dark) {
  .form-input {
    /* 确保输入框在深色模式下有正确的文本颜色 */
    color-scheme: dark;
  }
}
</style>