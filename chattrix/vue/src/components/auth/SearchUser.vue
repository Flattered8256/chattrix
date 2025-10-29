<template>
  <div class="search-user-component">
    <!-- 搜索框 -->
    <div class="search-input-wrapper" @click="openModal">
      <input 
        type="text" 
        v-model="searchId" 
        placeholder="输入用户ID搜索用户" 
        class="search-input"
        readonly
      />
      <button class="search-button" @click.stop="openModal">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
    </div>

    <!-- 模态框 -->
    <div v-if="isModalOpen" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>搜索用户</h3>
          <button class="close-button" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="search-form">
            <input 
              type="text" 
              v-model="searchId" 
              placeholder="请输入10位用户ID" 
              class="form-input"
              @keypress.enter="handleSearch"
            />
            <button 
              class="submit-button" 
              @click="handleSearch"
              :disabled="isSearching"
            >
              {{ isSearching ? '搜索中...' : '搜索' }}
            </button>
          </div>

          <!-- 搜索结果 -->
          <div v-if="searchResult" class="search-result">
            <div class="user-info">
              <!-- 使用 Avatar_look 组件替代直接的 img 标签 -->
              <Avatar_look :user="searchResult" size="large" />
              <div class="user-details">
                <h4>{{ searchResult.username }}</h4>
                <p v-if="searchResult.user_status" class="user-status">
                  状态: {{ getUserStatusText(searchResult.user_status) }}
                </p>
              </div>
            </div>
            
            <div class="action-buttons">
              <button 
                class="send-request-button" 
                @click="handleSendFriendRequest"
                :disabled="isSendingRequest"
              >
                {{ isSendingRequest ? '发送中...' : '发送好友请求' }}
              </button>
            </div>
          </div>

          <!-- 无结果提示 -->
          <div v-else-if="hasSearched && !searchResult" class="no-result">
            未找到该用户
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 提示组件 -->
    <Toast 
      v-if="toastMessage"
      :message="toastMessage"
      :type="toastType"
      @close="closeToast"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { User } from '../../api/auth'
import { searchUser } from '../../api/auth'
import { sendFriendRequest } from '../../api/friends'
import Toast from '../utils/toast.vue'
// 导入 Avatar_look 组件
import Avatar_look from './Avatar_look.vue'

// 组件状态
const isModalOpen = ref(false)
const searchId = ref('')
const searchResult = ref<User | null>(null)
const hasSearched = ref(false)
const isSearching = ref(false)
const isSendingRequest = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('error')

// 打开模态框
const openModal = () => {
  isModalOpen.value = true
}

// 关闭模态框
const closeModal = () => {
  isModalOpen.value = false
  searchResult.value = null
  hasSearched.value = false
  // 保留搜索框内容，方便用户再次搜索
}

// 显示 Toast 提示
const showToast = (message: string, type: 'success' | 'error' = 'error') => {
  toastMessage.value = message
  toastType.value = type
}

// 关闭 Toast 提示
const closeToast = () => {
  toastMessage.value = ''
}

// 处理搜索用户
const handleSearch = async () => {
  // 重置 Toast 消息
  closeToast()
  
  // 基本验证
  if (!searchId.value.trim()) {
    showToast('请输入用户ID')
    return
  }
  
  // 验证是否为10位数字
  const userId = parseInt(searchId.value.trim())
  if (isNaN(userId) || searchId.value.trim().length !== 10) {
    showToast('用户ID必须是10位数字')
    return
  }
  
  isSearching.value = true
  
  try {
    const response = await searchUser({ id: userId })
    searchResult.value = response.data
    hasSearched.value = true
    showToast('搜索成功', 'success')
  } catch (error: any) {
    searchResult.value = null
    hasSearched.value = true
    
    // 处理错误消息
    let errorMessage = '搜索用户失败'
    if (error.status === 400) {
      errorMessage = '无效的用户ID格式'
    } else if (error.status === 404) {
      errorMessage = '未找到该用户'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showToast(errorMessage)
  } finally {
    isSearching.value = false
  }
}

// 处理发送好友请求
const handleSendFriendRequest = async () => {
  if (!searchResult.value) return
  
  isSendingRequest.value = true
  
  try {
    await sendFriendRequest(searchResult.value.id)
    showToast('好友请求已发送', 'success')
    // 发送成功后关闭模态框
    setTimeout(() => {
      closeModal()
    }, 2000)
  } catch (error: any) {
    // 处理错误消息
    let errorMessage = '发送好友请求失败'
    if (error.status === 400) {
      errorMessage = '好友请求已存在或对方已是您的好友'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showToast(errorMessage)
  } finally {
    isSendingRequest.value = false
  }
}

// 获取用户状态文本
const getUserStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'online': '在线',
    'offline': '离线',
    'away': '离开'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
/* 搜索框样式 */
.search-user-component {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #f8f9fa;
  cursor: pointer;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
  background-color: #fff;
}

.search-button {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.25rem;
}

.search-icon {
  width: 16px;
  height: 16px;
}

/* 模态框样式 */
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

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-button:hover {
  background-color: #f5f5f5;
}

.modal-body {
  padding: 1.5rem;
}

/* 搜索表单样式 */
.search-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.form-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover:not(:disabled) {
  background-color: #66b1ff;
}

.submit-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

/* 搜索结果样式 */
.search-result {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-details h4 {
  margin: 0 0 0.25rem 0;
  color: #333;
}

.user-status {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.send-request-button {
  padding: 0.5rem 1.5rem;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-request-button:hover:not(:disabled) {
  background-color: #85ce61;
}

.send-request-button:disabled {
  background-color: #b3e19d;
  cursor: not-allowed;
}

/* 无结果提示样式 */
.no-result {
  text-align: center;
  padding: 2rem;
  color: #999;
}
</style>