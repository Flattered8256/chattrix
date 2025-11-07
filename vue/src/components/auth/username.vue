<template>
  <div class="username-container">
    <!-- 显示状态 -->
    <div class="current-username">
      <div class="username-info">
        <span class="username-label">用户名</span>
        <span class="username-value">{{ currentUsername }}</span>
      </div>
      <button class="edit-button" @click="openModal">
        更换用户名
      </button>
    </div>
    
    <!-- 模态框 -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">更换用户名</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUsername">
            <div class="form-group">
              <label for="new_username" class="form-label">新用户名</label>
              <input
                id="new_username"
                ref="usernameInput"
                v-model="newUsername"
                type="text"
                class="form-input"
                placeholder="输入新用户名"
                @keydown.enter="saveUsername"
                @keydown.escape="closeModal"
                maxlength="20"
                required
              />
            </div>
            
            <div v-if="error" class="error-message">{{ error }}</div>
            
            <div v-if="!error && newUsername" class="username-hint">
              用户名长度 {{ newUsername.length }}/20
            </div>
            
            <div class="form-actions">
              <button 
                type="submit" 
                class="save-button"
                :disabled="!isFormValid || isSaving"
              >
                <span v-if="isSaving" class="loading-spinner-small"></span>
                {{ isSaving ? '保存中...' : '保存' }}
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
import { ref, computed, nextTick, onUnmounted, reactive } from 'vue';
import { useAuthStore } from '../../store/auth';
import type { User } from '../../api/auth';
import Toast from '../utils/toast.vue';

// 定义props
interface Props {
  user?: User | null;
}

const props = withDefaults(defineProps<Props>(), {
  user: null
});

// 定义emits
const emit = defineEmits<{
  usernameUpdated: [user: User];
  error: [message: string];
}>();

// 引用auth store
const authStore = useAuthStore();

// 输入框引用
const usernameInput = ref<HTMLInputElement | null>(null);

// 组件状态
const isModalOpen = ref(false);
const newUsername = ref('');
const isSaving = ref(false);
const error = ref('');

// 通知状态
const notification = reactive({
  message: '',
  type: 'success' as 'success' | 'error',
  duration: 3000
})

// 计算属性
const currentUsername = computed(() => {
  if (props.user?.username) {
    return props.user.username;
  }
  return authStore.user?.username || '';
});

const isFormValid = computed(() => {
  return newUsername.value.trim().length > 0 && 
         newUsername.value.trim().length <= 20 && 
         newUsername.value.trim() !== currentUsername.value;
});

// 打开模态框
const openModal = () => {
  isModalOpen.value = true;
  newUsername.value = currentUsername.value;
  error.value = '';
  
  // 聚焦到输入框
  nextTick(() => {
    if (usernameInput.value) {
      usernameInput.value.focus();
      usernameInput.value.select();
    }
  });
};

// 关闭模态框
const closeModal = () => {
  isModalOpen.value = false;
  newUsername.value = '';
  error.value = '';
};

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

// 保存新用户名
const saveUsername = async () => {
  const trimmedUsername = newUsername.value.trim();
  
  // 验证用户名
  if (!trimmedUsername) {
    error.value = '用户名不能为空';
    return;
  }
  
  if (trimmedUsername.length > 20) {
    error.value = '用户名不能超过20个字符';
    return;
  }
  
  if (trimmedUsername === currentUsername.value) {
    error.value = '新用户名与当前用户名相同';
    return;
  }
  
  // 验证用户名格式（只允许字母、数字、下划线）
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  if (!usernameRegex.test(trimmedUsername)) {
    error.value = '用户名只能包含字母、数字和下划线';
    return;
  }
  
  isSaving.value = true;
  error.value = '';
  
  try {
    // 调用auth store中的更新个人资料方法
    const result = await authStore.updateProfile({ username: trimmedUsername });
    
    if (result.success && authStore.user) {
      // 关闭模态框
      closeModal();
      // 显示成功消息
      showNotification('用户名更新成功！');
      // 触发用户名更新事件
      emit('usernameUpdated', authStore.user);
    } else {
      throw new Error('更新失败');
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '更新失败，请重试';
    error.value = errorMessage;
    emit('error', errorMessage);
  } finally {
    isSaving.value = false;
  }
};

// 清理定时器
const cleanup = () => {
  // 定时器逻辑已移至Toast组件中
};

// 组件卸载时清理定时器
onUnmounted(cleanup);
</script>

<style scoped>
/* 用户名容器 */
.username-container {
  position: relative;
  width: 100%;
  background-color: transparent;
  padding: 16px;
  border-radius: 8px;
}

/* 当前用户名显示 */
.current-username {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background-color: transparent;
}

.username-info {
  display: flex;
  align-items: center;
  background-color: transparent;
}

/* 用户名标签 - 加大加粗 */
.username-label {
  color: #657786;
  font-size: 18px;
  font-weight: bold;
  margin-right: 8px;
}

.username-value {
  color: #14171a;
  font-size: 16px;
  font-weight: 500;
}

/* 更换用户名按钮 - 绿色矩形 */
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

/* 用户名提示 */
.username-hint {
  color: #657786;
  font-size: 12px;
  text-align: right;
  background-color: transparent;
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
  .username-label {
    color: #8899a6;
  }
  
  .username-value {
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
  
  .username-hint {
    color: #8899a6;
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