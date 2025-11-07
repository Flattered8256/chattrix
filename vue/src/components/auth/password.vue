<template>
  <div class="password-container">
    <!-- 显示状态 -->
    <div class="current-password">
      <div class="password-info">
        <span class="password-label">密码</span>
        <span class="password-value">************</span>
      </div>
      <button class="edit-button" @click="openModal">
        修改密码
      </button>
    </div>
    
    <!-- 模态框 -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">修改密码</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleChangePassword">
            <div class="form-group">
              <label for="old_password" class="form-label">当前密码</label>
              <input
                id="old_password"
                v-model="form.old_password"
                type="password"
                class="form-input"
                placeholder="请输入当前密码"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="new_password" class="form-label">新密码</label>
              <input
                id="new_password"
                v-model="form.new_password"
                type="password"
                class="form-input"
                placeholder="请输入新密码"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="confirm_password" class="form-label">确认新密码</label>
              <input
                id="confirm_password"
                v-model="form.confirm_password"
                type="password"
                class="form-input"
                placeholder="请再次输入新密码"
                required
              />
            </div>
            
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
            
            <div class="form-actions">
              <button 
                type="submit" 
                class="save-button"
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="loading-spinner-small"></span>
                {{ isLoading ? '修改中...' : '修改密码' }}
              </button>
              <button type="button" class="cancel-button" @click="closeModal">
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 使用通用提示框组件 -->
    <Toast 
      v-if="notification.message"
      :message="notification.message"
      :type="notification.type"
      :duration="notification.duration"
      @close="clearNotification"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '../../store/auth'
import type { ChangePasswordRequest } from '../../api/auth'
import Toast from '../utils/toast.vue'

// 表单数据
const form = reactive<ChangePasswordRequest>({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 状态管理
const authStore = useAuthStore()

// 组件状态
const isLoading = ref(false)
const errorMessage = ref('')
const isModalOpen = ref(false)

// 通知状态
const notification = reactive({
  message: '',
  type: 'success' as 'success' | 'error',
  duration: 3000
})

// 打开模态框
const openModal = () => {
  isModalOpen.value = true
  errorMessage.value = ''
  // 重置表单
  form.old_password = ''
  form.new_password = ''
  form.confirm_password = ''
}

// 关闭模态框
const closeModal = () => {
  isModalOpen.value = false
  errorMessage.value = ''
}

// 显示通知
const showNotification = (msg: string, type: 'success' | 'error' = 'success', duration = 3000) => {
  notification.message = msg
  notification.type = type
  notification.duration = duration
}

// 清除通知
const clearNotification = () => {
  notification.message = ''
}

// 处理密码修改
const handleChangePassword = async () => {
  // 重置消息
  errorMessage.value = ''
  
  // 基本验证
  if (!form.old_password) {
    errorMessage.value = '请输入当前密码'
    return
  }
  
  if (!form.new_password) {
    errorMessage.value = '请输入新密码'
    return
  }
  
  if (form.new_password !== form.confirm_password) {
    errorMessage.value = '两次输入的新密码不一致'
    return
  }
  
  if (form.new_password.length < 6) {
    errorMessage.value = '新密码长度至少为6位'
    return
  }
  
  isLoading.value = true
  
  try {
    const result = await authStore.changePassword(form)
    
    if (result.success) {
      // 密码修改成功
      closeModal()
      showNotification('密码修改成功')
    } else {
      errorMessage.value = result.error || '密码修改失败'
    }
  } catch (error) {
    errorMessage.value = '密码修改过程中发生错误'
    console.error('Change password error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 密码容器 */
.password-container {
  position: relative;
  width: 100%;
  background-color: transparent;
  padding: 16px; /* 修改为与用户名组件一致的padding */
  border-radius: 8px;
}

/* 当前密码显示 */
.current-password {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background-color: transparent;
}

.password-info {
  display: flex;
  align-items: center;
  background-color: transparent;
}

/* 密码标签 - 加大加粗 */
.password-label {
  color: #657786;
  font-size: 18px;
  font-weight: bold;
  margin-right: 8px;
}

/* 密码掩码显示 */
.password-value {
  color: #14171a;
  font-size: 16px;
  font-weight: 500;
}

/* 修改密码按钮 - 绿色矩形 */
.edit-button {
  padding: 8px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.edit-button:hover {
  background-color: #45a049;
}

/* 模态框遮罩层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 模态框内容 */
.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

/* 模态框头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e8ed;
}

/* 模态框标题 */
.modal-title {
  margin: 0;
  color: #14171a;
  font-size: 18px;
  font-weight: 600;
}

/* 模态框关闭按钮 */
.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #657786;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.modal-close:hover {
  background-color: rgba(245, 248, 250, 0.5);
}

/* 模态框主体 */
.modal-body {
  padding: 20px;
}

/* 表单组 */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 1rem;
}

.save-button {
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.save-button:hover:not(:disabled) {
  background-color: #66b1ff;
}

.save-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.cancel-button {
  padding: 8px 16px;
  background-color: transparent;
  color: #657786;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background-color: #f5f8fa;
}

/* 错误消息 */
.error-message {
  color: #f56c6c;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #fef0f0;
  border-radius: 4px;
  border: 1px solid #fde2e2;
}

/* 小型加载动画 */
.loading-spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 动画定义 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .password-label {
    color: #8899a6;
  }
  
  .password-value {
    color: #e1e8ed;
  }
  
  .modal-content {
    background-color: #242424;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  .modal-header {
    border-bottom: 1px solid #38444d;
  }
  
  .modal-title {
    color: #ffffff;
  }
  
  .modal-close {
    color: #8899a6;
  }
  
  .modal-close:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  .form-label {
    color: #8899a6;
  }
  
  .form-input {
    background-color :#242424;
    border-color: #38444d;
    color: #ffffff;
  }
  
  .form-input:focus {
    border-color: #1da1f2;
    box-shadow: 0 0 0 2px rgba(29, 161, 242, 0.2);
  }
  
  .cancel-button {
    color: #8899a6;
    border-color: #38444d;
  }
  
  .cancel-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  .error-message {
    color: #f56c6c;
    background-color: rgba(245, 108, 108, 0.1);
    border: 1px solid rgba(245, 108, 108, 0.2);
  }
  
  .loading-spinner-small {
    border: 2px solid #38444d;
    border-top: 2px solid #ffffff;
  }
  .save-button:disabled {
    background-color: #253340;
    cursor: not-allowed;
  }
}
</style>