<script setup lang="ts">
import { computed, ref,watch } from 'vue'
import { useFriendsStore } from '../../store/friends'

import ExpandIcon from '../../assets/展开.svg' // 导入展开图标
import AvatarLook from '../auth/Avatar_look.vue' // 导入AvatarLook组件
import Toast from '../utils/toast.vue' // 导入Toast组件

// 初始化store
const friendsStore = useFriendsStore()


// 用于存储展开状态的Map
const expandedFriends = ref<Map<number, boolean>>(new Map())
const nicknameModalVisible = ref<boolean>(false)
const currentFriendId = ref<number>(0)
const newNickname = ref<string>('')
const showToast = ref<boolean>(false)
const toastMessage = ref<string>('')
const toastType = ref<'success' | 'error'>('success')

// 从store获取数据
const friends = computed(() => {
  return friendsStore.friends || []
})

const pendingFriendRequests = computed(() => friendsStore.pendingFriendRequests || [])

const error = computed(() => friendsStore.error)

const acceptFriendRequest = friendsStore.acceptFriendRequest
const rejectFriendRequest = friendsStore.rejectFriendRequest
const removeFriend = friendsStore.removeFriend
const blockFriend = friendsStore.blockFriend
const setFriendNickname = friendsStore.setFriendNickname

// 显示toast提示
const showToastMessage = (message: string, type: 'success' | 'error' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
}

// 关闭toast
const closeToast = () => {
  showToast.value = false
}

// 展开/收起好友项
const toggleFriendExpand = (friendId: number) => {
  expandedFriends.value.set(friendId, !expandedFriends.value.get(friendId))
}
// 监听错误变化并显示提示
watch(error, (newError) => {
  if (newError) {
    showToastMessage(newError, 'error')
  }
})
// 打开备注对话框
const openNicknameModal = (friendId: number, currentNickname?: string) => {
  currentFriendId.value = friendId
  newNickname.value = currentNickname || ''
  nicknameModalVisible.value = true
}

// 保存备注
const saveNickname = async () => {
  if (newNickname.value.trim()) {
    try {
      await setFriendNickname(currentFriendId.value, newNickname.value.trim())
      nicknameModalVisible.value = false
      showToastMessage('备注设置成功', 'success')
    } catch (err) {
      showToastMessage('备注设置失败', 'error')
    }
  }
}

// 确认删除好友
const confirmRemoveFriend = async (friendId: number) => {
  if (confirm('确定要删除这个好友吗？')) {
    try {
      await removeFriend(friendId)
      showToastMessage('好友删除成功', 'success')
    } catch (err) {
      showToastMessage('好友删除失败', 'error')
    }
  }
}

// 确认屏蔽好友
const confirmBlockFriend = async (friendId: number) => {
  if (confirm('确定要屏蔽这个好友吗？')) {
    try {
      await blockFriend(friendId)
      showToastMessage('好友已屏蔽', 'success')
    } catch (err) {
      showToastMessage('屏蔽好友失败', 'error')
    }
  }
}

// 接受好友请求
const handleAcceptFriendRequest = async (requestId: number) => {
  try {
    await acceptFriendRequest(requestId)
    showToastMessage('已接受好友请求', 'success')
  } catch (err) {
    showToastMessage('接受好友请求失败', 'error')
  }
}

// 拒绝好友请求
const handleRejectFriendRequest = async (requestId: number) => {
  try {
    await rejectFriendRequest(requestId)
    showToastMessage('已拒绝好友请求', 'success')
  } catch (err) {
    showToastMessage('拒绝好友请求失败', 'error')
  }
}





</script>

<template>
  <div class="friends-list">
    <!-- 好友请求区域 -->
    <div v-if="pendingFriendRequests?.length > 0" class="friend-requests-section">
      <h3>好友请求 ({{ pendingFriendRequests?.length }})</h3>
      <div v-for="request in pendingFriendRequests" :key="request.id" class="friend-request-item">
         <div class="friend-info">
          <AvatarLook 
            :user="request.sender_info" 
            size="medium"
          />
          <div class="friend-details">
            <div class="friend-name">{{ request.sender_info?.username  }}</div>
          </div>
        </div>
        <div class="request-actions">
          <button @click="handleAcceptFriendRequest(request.id)" class="accept-btn">接受</button>
          <button @click="handleRejectFriendRequest(request.id)" class="reject-btn">拒绝</button>
        </div>
      </div>
    </div>

    <!-- 好友列表区域 -->
    <div v-if="friends.length > 0" class="friends-section">
      <h3>我的好友</h3>
      <div v-for="friend in friends" :key="friend.id" class="friend-item">
        <div class="friend-info">
          <AvatarLook 
            :user="friend.friend_info" 
            size="medium"
          />
          <div class="friend-details">
            <div class="friend-name">{{ friend.nickname || friend.friend_info?.username || '用户' }}</div>
          </div>
        </div>
        <!-- 展开按钮 -->
        <button 
          class="expand-btn"
          @click="toggleFriendExpand(friend.id)"
          :class="{ expanded: expandedFriends.get(friend.id) }"
        >
          <img :src="ExpandIcon" alt="展开" />
        </button>
        <!-- 展开菜单 -->
        <div 
          v-if="expandedFriends.get(friend.id)"
          class="friend-actions-menu"
        >
          <button 
            class="action-btn note-btn"
            @click="openNicknameModal(friend.id)"
          >
            设置备注
          </button>
          <button 
            class="action-btn block-btn"
            @click="confirmBlockFriend(friend.id)"
          >
            屏蔽好友
          </button>
          <button 
            class="action-btn delete-btn"
            @click="confirmRemoveFriend(friend.id)"
          >
            删除好友
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="friends.length === 0 && (!pendingFriendRequests || pendingFriendRequests.length === 0)" class="empty-state">
      <p>暂无好友</p>
      <p class="empty-hint">通过搜索添加好友开始聊天吧！</p>
    </div>

    <!-- 备注对话框 -->
    <div v-if="nicknameModalVisible" class="modal-overlay" @click="nicknameModalVisible = false">
      <div class="modal-content" @click.stop>
        <h3>设置好友备注</h3>
        <input
          v-model="newNickname"
          type="text"
          placeholder="请输入备注名称"
          class="nickname-input"
          @keyup.enter="saveNickname"
        />
        <div class="modal-actions">
          <button @click="nicknameModalVisible = false" class="cancel-btn">取消</button>
          <button @click="saveNickname" class="confirm-btn">确定</button>
        </div>
      </div>
    </div>

    <!-- Toast组件 -->
    <Toast 
      v-if="showToast" 
      :message="toastMessage" 
      :type="toastType" 
      @close="closeToast" 
    />
  </div>
</template>

<style scoped>
/* 现有样式保持不变 */
.friends-list {
  padding: 10px 0;
}

.friend-requests-section,
.friends-section {
  margin-bottom: 20px;
}

.friend-requests-section h3,
.friends-section h3 {
  margin-bottom: 15px;
  color: #555;
  font-size: 18px;
  font-weight: 500;
}

.friend-request-item,
.friend-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background-color 0.2s ease;
  position: relative;
}

.friend-request-item:hover,
.friend-item:hover {
  background-color: #f5f5f5;
}

.friend-info {
  display: flex;
  align-items: center;
  flex: 1;
  margin-right: 12px;
}

.friend-details {
  flex: 1;
  margin-left: 12px; 
}

.friend-name {
  font-size: 16px;
  color: #333;
  margin-bottom: 4px;
}

/* 展开按钮样式 */
.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.expand-btn:hover {
  background-color: #e0e0e0;
}

.expand-btn img {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.expand-btn.expanded img {
  transform: rotate(90deg);
}

/* 展开菜单样式 */
.friend-actions-menu {
  position: absolute;
  right: 10px;
  top: 100%;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  text-align: left;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
  background-color: #f5f5f5;
}

.note-btn:hover {
  color: #2196f3;
}

.block-btn:hover {
  color: #ff9800;
}

.delete-btn:hover {
  color: #f44336;
}

.request-actions {
  display: flex;
  gap: 8px;
}

.accept-btn,
.reject-btn,
.retry-btn,
.cancel-btn,
.confirm-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.accept-btn {
  background-color: #4caf50;
  color: white;
}

.accept-btn:hover {
  background-color: #45a049;
}

.reject-btn,
.cancel-btn {
  background-color: #f44336;
  color: white;
}

.reject-btn:hover,
.cancel-btn:hover {
  background-color: #d32f2f;
}

.retry-btn,
.confirm-btn {
  background-color: #2196f3;
  color: white;
}

.retry-btn:hover,
.confirm-btn:hover {
  background-color: #1976d2;
}

.retry-btn {
  margin-top: 10px;
}

.empty-state,
.loading-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.error-state {
  color: #f44336;
}

/* 备注对话框样式 */
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
  z-index: 1001;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 300px;
}

.modal-content h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.nickname-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>