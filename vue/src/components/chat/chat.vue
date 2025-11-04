<template>
  <div class="chat-container">
    <!-- 聊天头部组件 -->
    <ChatHeader 
      :chat-room="currentChatRoom"
      :is-mobile="isMobile"
      @back="handleBack"
    />

      <!-- 消息列表组件 -->
    <MessageList
      ref="messageListRef"
      :current-chat-room="currentChatRoom"
      @preview-media="previewMedia"
    />
    <!-- 消息发送器 -->
    <MessageSender
      :disabled="isSending"
      @send-text="onSendText"
      @send-file="onSendFile"
    />

    <!-- 媒体预览组件 -->
    <MediaPreview
      v-model:show="showMediaPreview"
      :preview-url="previewUrl"
      :preview-type="previewType"
      alt-text="聊天图片预览"
      @close="closeMediaPreview"
    />

    <!-- Toast提示组件 -->
    <Toast
      v-if="showToast"
      :message="toastMessage"
      :type="toastType"
      @close="closeToast"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted} from 'vue';
import { useChatStore } from '../../store/chat';
import { useMessagesStore } from '../../store/messages';
import MessageList from './MessageList.vue'; 
import Toast from '../utils/toast.vue';
import ChatHeader from './ChatHeader.vue';
import MessageSender from './MessageSend.vue';
import type { SendMessageRequest } from '../../api/messages';
import MediaPreview from './MediaPreview.vue';
// 定义消息类型
type MsgType = 'text' | 'image' | 'video' | 'file';

// 定义组件事件
const emit = defineEmits(['back']);



const chatStore = useChatStore();
const messagesStore = useMessagesStore(); 

// 组件状态
const isSending = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('error');

const isMobile = ref(false);
const showMediaPreview = ref(false);
const previewUrl = ref('');
const previewType = ref<'image' | 'video'>('image');

const messageListRef = ref(); // MessageList组件引用
// 处理移动设备视口高度计算
const updateViewportHeight = () => {
  // 设置自定义属性，考虑移动浏览器的地址栏
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
};

// 添加窗口大小变化监听
const checkIfMobile = () => {
  isMobile.value = window.innerWidth <= 767; // 与CSS中响应式断点保持一致
  // 每次检查时更新视口高度
  if (isMobile.value) {
    updateViewportHeight();
  }
};

// 初始化时检查和设置
updateViewportHeight();
checkIfMobile();

// 添加事件监听
window.addEventListener('resize', () => {
  checkIfMobile();
  updateViewportHeight();
});

// 处理方向变化（对于移动设备特别重要）
window.addEventListener('orientationchange', updateViewportHeight);


// 计算属性
const currentChatRoom = computed(() => chatStore.currentChatRoom);


// 处理返回按钮点击
const handleBack = () => {
  emit('back');
};

// 组件挂载时，确保设置为正在查看聊天
onMounted(() => {
  messagesStore.isUserViewingChat = true;
});

// 组件卸载时，确保设置为不再查看聊天
onUnmounted(() => {
  messagesStore.isUserViewingChat = false;
});


async function onSendText(content: string) {
  await realSend({ content, messages_type: 'text', room_type: 'private' })
}

async function onSendFile(file: File, type: MsgType) {
  await realSend({ file, messages_type: type, room_type: 'private' })
}

/** 统一调接口 */
async function realSend(req: SendMessageRequest) {
  if (!currentChatRoom.value) return
  isSending.value = true
  try {
    const { success, error } = await messagesStore.sendMessage(currentChatRoom.value.id, req)
    if (!success) throw new Error(error || '未知错误')
    // 成功后再滚动
    nextTick(() => scrollToBottom())
  } catch (e: any) {
    showToastMessage('发送失败: ' + e.message)
  } finally {
    isSending.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  messageListRef.value?.scrollToBottom();
};
// 显示Toast提示
const showToastMessage = (message: string, type: 'success' | 'error' = 'error') => {
  toastMessage.value = message;
  toastType.value = type;
  showToast.value = true;
  
  // 3秒后自动关闭
  setTimeout(() => {
    closeToast();
  }, 3000);
};

// 关闭Toast提示
const closeToast = () => {
  showToast.value = false;
};

// 预览媒体文件
const previewMedia = (url: string, type: 'image' | 'video') => {
  previewUrl.value = url;
  previewType.value = type;
  showMediaPreview.value = true;
};

// 关闭媒体预览
const closeMediaPreview = () => {
  showMediaPreview.value = false;
};


</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  /* 防止出现额外的滚动条 */
  overflow: hidden;
}

/* 响应式设计 */
@media (max-width: 767px) {
  /* 使用自定义vh单位，解决移动浏览器地址栏影响 */
  .chat-container {
    height: calc(100vh - 60px);
    /* 兼容iOS和Android的视口高度 */
    height: calc(var(--vh, 1vh) * 100 - 60px);
    /* 添加固定定位，使聊天窗口在屏幕上保持固定 */
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
  }

}
</style>