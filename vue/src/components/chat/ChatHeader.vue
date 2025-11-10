<template>
  <div class="chat-header">
    <!-- 移动端返回按钮 -->
    <button v-if="isMobile && chatRoom" class="back-button" @click="handleBack">
      ←
    </button>
    
    <div v-if="chatRoom" class="chat-partner-info">
      <Avatar_look
        :user="{
          id: chatStore.getChatRoomDisplayInfo(chatRoom).id,
          username: chatStore.getChatRoomDisplayInfo(chatRoom).name,
          user_avatar: chatStore.getChatRoomDisplayInfo(chatRoom).avatar
        }"
        size="medium"
      />
      <div class="partner-details">
        <span class="partner-name">{{ chatStore.getChatRoomDisplayInfo(chatRoom).name }}</span>
      </div>
    </div>
    <div v-else class="no-chat-selected">
      请选择一个聊天
    </div>
  </div>
</template>

<script setup lang="ts">

import type { PrivateChatRoom, GroupChatRoom } from '../../api/chat';
import Avatar_look from '../auth/Avatar_look.vue';
import { useChatStore } from '../../store/chat';

const chatStore = useChatStore();
// 定义组件属性
interface Props {
  chatRoom: PrivateChatRoom | GroupChatRoom | null | undefined;
  isMobile: boolean;
}

defineProps<Props>();

// 定义组件事件
const emit = defineEmits(['back']);



// 处理返回按钮点击
const handleBack = () => {
  emit('back');
};
</script>

<style scoped>
.chat-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fff;
}

.back-button {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    margin-right: 10px;
    padding: 5px;
    color: #213547;
  }

  .back-button:hover {
    color: #747bff;
  }

  /* 夜间模式样式 */
  @media (prefers-color-scheme: dark) {
    .chat-header {
      border-bottom-color: #333;
      background-color: #2a2a2a;
    }
    
    .back-button {
      color: rgba(255, 255, 255, 0.87);
    }
    
    .back-button:hover {
      color: #fff;
    }
    
    .partner-name {
      color: rgba(255, 255, 255, 0.87);
    }
    
    .no-chat-selected {
      color: #aaa;
    }
  }

.chat-partner-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.partner-details {
  margin-left: 10px;
}

.partner-name {
  font-weight: 500;
  font-size: 16px;
}

.no-chat-selected {
  flex: 1;
  text-align: center;
  color: #888;
  font-size: 16px;
}
</style>