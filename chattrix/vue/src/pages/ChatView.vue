<template>
  <div class="chat-view">
    <!-- 移动端：根据是否选择了聊天显示不同组件 -->
    <div class="mobile-layout" v-if="isMobile">
      <chat_list v-if="!showChatView" @select-chat="handleSelectChat" />
      <chat v-else @back="handleBack" />
    </div>
    
    <!-- 桌面端：水平排列两个组件 -->
    <div class="desktop-layout" v-else>
      <div class="chat-list-panel">
        <chat_list @select-chat="handleSelectChat" />
      </div>
      <div class="chat-panel">
        <chat />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted} from 'vue';
import chat_list from '../components/chat/chat_list.vue';
import chat from '../components/chat/chat.vue';
import { useChatStore } from '../store/chat';

// 状态管理
const chatStore = useChatStore();
const showChatView = ref(false);
const isMobile = ref(false);
let savedScrollY = 0;

// 计算当前是否为移动设备
const checkIsMobile = () => {
  isMobile.value = window.innerWidth < 768;
  // 如果是桌面端，始终显示聊天视图
  if (!isMobile.value) {
    showChatView.value = true;
  }
};

// 处理聊天选择事件
const handleSelectChat = () => {
  savedScrollY = window.scrollY;
  showChatView.value = true;
  if (isMobile.value) {
    document.body.classList.add('mobile-chat-open');
  }
};

// 处理返回事件
const handleBack = () => {
  showChatView.value = false;
  chatStore.currentChatRoomId = null;
  if (isMobile.value) {
    document.body.classList.remove('mobile-chat-open');
    window.scrollTo(0, savedScrollY);
  }
};

// 监听窗口大小变化
const handleResize = () => {
  checkIsMobile();
};

// 组件挂载时初始化
onMounted(() => {
  checkIsMobile();
  window.addEventListener('resize', handleResize);
  
  // 如果在移动设备上已经有选中的聊天，则显示聊天视图
  if (isMobile.value && chatStore.currentChatRoom) {
    showChatView.value = true;
  }
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.chat-view {
  width: 100%;
  height: 100%;
}

/* 桌面端布局 */
.desktop-layout {
  display: flex;
  height: 100%;
}

.chat-list-panel {
  width: 300px;
  flex-shrink: 0;
  border-right: 1px solid #e1e8ed;
}

.chat-panel {
  flex: 1;
  min-width: 0;
}

/* 移动端布局 */
.mobile-layout {
  height: 100%;
  position: relative;

}

/* 响应式断点 */
@media (max-width: 767px) {
  .desktop-layout {
    display: none;
  }
}

@media (min-width: 768px) {
  .mobile-layout {
    display: none;
  }
}
</style>