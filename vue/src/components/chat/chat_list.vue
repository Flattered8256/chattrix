<template>
  <!-- 移动端空状态显示 -->
  <div v-if="isMobile && sortedChatRooms.length === 0" class="empty-state-mobile">
    <div class="empty-state-icon">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 2H4C2.9 2 2.01 2.9 2.01 4L2 22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM6 9H18V11H6V9ZM14 14H6V12H14V14ZM18 8H6V6H18V8Z" fill="#ccc"/>
      </svg>
    </div>
    <h3>暂无聊天记录</h3>
    <p>您还没有任何聊天消息，开始和好友聊天吧！</p>
  </div>
  
  <div class="chat-list-container">

    <div class="chat-list">
      <div
        v-for="room in sortedChatRooms"
        :key="room.id"
        class="chat-item"
        :class="{ active: room.id === chatStore.currentChatRoomId }"
        @click="handleChatItemClick(room.id)"
      >
        <!-- 头像组件 -->
        <Avatar_look
          :user="{
            id: chatStore.getChatRoomDisplayInfo(room).id,
            username: chatStore.getChatRoomDisplayInfo(room).name,
            user_avatar: chatStore.getChatRoomDisplayInfo(room).avatar
          }"
          size="medium"
        />
        
        <!-- 聊天信息 -->
        <div class="chat-info">
          <div class="chat-header">
            <span class="chat-username">{{ chatStore.getChatRoomDisplayInfo(room).name }}</span>
            <!-- 未读消息计数 -->
            <span
              v-if="getUnreadCount(room.id) > 0"
              class="unread-badge"
            >
              {{ getUnreadCount(room.id) }}
            </span>
          </div>
          <!-- 最近一条消息 -->
          <div class="last-message">
            <span class="message-content">{{ getLastMessage(room.id) }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- 添加toast组件用于显示错误信息 -->
    <Toast
      v-if="showToast"
      :message="toastMessage"
      :type="toastType"
      @close="closeToast"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';
import { useChatStore } from '../../store/chat';
import Avatar_look from '../auth/Avatar_look.vue';
import { useMessagesStore } from '../../store/messages';
// 导入toast组件
import Toast from '../utils/toast.vue';

// 移动端检测
const isMobile = ref(false);

// 检查是否为移动设备
const checkIsMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

// 监听窗口大小变化
onMounted(() => {
  checkIsMobile();
  window.addEventListener('resize', checkIsMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile);
});

// 定义组件事件
const emit = defineEmits(['select-chat']);

const chatStore = useChatStore();
const messagesStore = useMessagesStore();

// toast相关状态
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('error');


// 获取未读消息数量
const getUnreadCount = (roomId: number): number => {
  const count = messagesStore.unreadMessagesCount.get(roomId);
  return count || 0;
};


// 获取房间的最后一条消息
const getLastMessage = (roomId: number): string => {
  const roomMessages = messagesStore.messages[roomId];
  
  // 检查房间消息是否存在
  if (!roomMessages || roomMessages.length === 0) {
    return '';
  }
  
  // 获取最新的消息
  const lastMessage = roomMessages[roomMessages.length - 1];
  
  // 检查消息是否存在
  if (!lastMessage) {
    return '未知消息';
  }
  
  // 根据消息类型显示不同内容
  let messageContent = '';
  
  // 检查是否为图片消息
  if (lastMessage.messages_type === 'image') {
    messageContent = '[图片消息]';
  }
  // 检查是否为视频消息
  else if (lastMessage.messages_type === 'video') {
    messageContent = '[视频消息]';
  }
  // 检查是否为文件消息
  else if (lastMessage.messages_type === 'file') {
    messageContent = '[文件消息]';
  }
  // 文本消息处理
  else if (lastMessage.content) {
    // 限制消息长度，过长则显示省略号
    messageContent = lastMessage.content.length > 30 
      ? lastMessage.content.substring(0, 30) + '...'
      : lastMessage.content;
  }
  else {
    messageContent = '未知消息';
  }
  
  // 如果是群聊消息且不是自己发送的，显示发送者用户名
  if (lastMessage.room_type === 'group') {
    const senderName = lastMessage.sender?.username || '未知用户';
    return `${senderName}: ${messageContent}`;
  }
  
  return messageContent;
};

// 获取按最后消息时间排序的聊天房间列表
const sortedChatRooms = computed(() => {
  // 合并私聊和群聊房间
  const allRooms = [...chatStore.privateChatRooms, ...chatStore.groupChatRooms];
  
  return allRooms.sort((a, b) => {
    const messagesA = messagesStore.messages[a.id] || [];
    const messagesB = messagesStore.messages[b.id] || [];
    
    if (messagesA.length === 0 && messagesB.length === 0) {
      // 都没有消息时，按房间更新时间排序
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    } else if (messagesA.length === 0) {
      return 1; // 有消息的排在前面
    } else if (messagesB.length === 0) {
      return -1; // 有消息的排在前面
    } else {
      // 都有消息时，按最后消息时间排序
      const lastMessageA = messagesA[messagesA.length - 1];
      const lastMessageB = messagesB[messagesB.length - 1];
      return new Date(lastMessageB.timestamp).getTime() - new Date(lastMessageA.timestamp).getTime();
    }
  });
});

// 处理聊天项点击
const handleChatItemClick = (roomId: number) => {
  messagesStore.setCurrentChatRoom(roomId);
  // 触发选择聊天事件
  emit('select-chat');
};

// 显示toast提示
const showErrorToast = (message: string) => {
  toastMessage.value = message;
  toastType.value = 'error';
  showToast.value = true;
};

// 关闭toast提示
const closeToast = () => {
  showToast.value = false;
};

// 监听chatStore中的错误信息变化
watch(
  () => chatStore.error,
  (newError) => {
    if (newError) {
      showErrorToast(newError);
    }
  }
);


</script>

<style scoped>
/* 样式保持不变 */
.chat-list-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e1e8ed;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.chat-item:hover {
  background-color: #e8f5fd;
}

.chat-item.active {
  background-color: #e3f2fd;
}

.chat-info {
  flex: 1;
  margin-left: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-username {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.unread-badge {
  background-color: #ff4d4f;
  color: white;
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  min-width: 16px;
  text-align: center;
}

.loading-indicator {
  padding: 20px;
  text-align: center;
  color: #666;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* 移动端空状态样式 */
.empty-state-mobile {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  background-color: #ffffff;
  z-index: 10;
}

.empty-state-icon {
  margin-bottom: 16px;
}

.empty-state-mobile h3 {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.empty-state-mobile p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

/* 桌面端隐藏移动端空状态 */
@media (min-width: 768px) {
  .empty-state-mobile {
    display: none;
  }
}

/* 新增最后一条消息的样式 */
.last-message {
  margin-top: 4px;
}

.message-content {
  color: #666;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 夜间模式样式 */
@media (prefers-color-scheme: dark) {
  .chat-list-container {
    background-color: #2a2a2a;
  }
  
  .chat-item {
    border-bottom-color: #3a3a3a;
  }
  
  .chat-item:hover {
    background-color: #3a3a3a;
  }
  
  .chat-item.active {
    background-color: #2c3e50;
  }
  
  .chat-username {
    color: #e0e0e0;
  }
  
  .message-content {
    color: #b0b0b0;
  }
  
  /* 移动端空状态夜间模式样式 */
  .empty-state-mobile {
    background-color: #1a1a1a;
  }
  
  .empty-state-mobile h3 {
    color: #e0e0e0;
  }
  
  .empty-state-mobile p {
    color: #808080;
  }
}
</style>