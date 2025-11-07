<template>
  <div class="chat-messages" ref="messagesContainer" @scroll="handleScroll">
    <div v-if="isMessagesLoading" class="loading-messages">加载消息中...</div>
    <div
      v-else-if="currentChatRoom && messages.length === 0"
      class="empty-messages"
    >
      暂无消息，开始聊天吧！
    </div>
    <div v-else-if="!currentChatRoom" class="no-chat-selected-content">
      <p>从左侧列表选择一个聊天开始对话</p>
    </div>
    <div v-else class="messages-list">
      <!-- 加载更多提示 -->
      <div v-if="isLoadingMore" class="loading-more">加载更多消息中...</div>

      <div v-if="hasMoreMessages" class="no-more-messages">没有更多消息了</div>

      <!-- 消息列表 -->
      <template v-for="message in messages" :key="message.id">
        <MessageItem
          :message="message"
          :current-user-id="currentUserId"
          :current-user="currentUser"
          @preview-media="handlePreviewMedia"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from "vue";
import MessageItem from "./MessageItem.vue";
import { useMessagesStore } from "../../store/messages"; // 新增
import { useAuthStore } from "../../store/auth"; // 新增
// 定义 Props
interface Props {
  currentChatRoom?: any;
}

// 定义 Emits
interface Emits {
  (e: "preview-media", url: string, type: "image" | "video"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Store 引用
const messagesStore = useMessagesStore(); // 新增
const authStore = useAuthStore(); // 新增

// 组件引用
const messagesContainer = ref<HTMLDivElement | null>(null);

// 组件状态 - 新增
const isLoadingMore = ref(false);
const lastAnchorMessageId = ref<number | null>(null);

// 计算属性
const currentUserId = computed(() => authStore.user?.id || 0);
const currentUser = computed(() => authStore.user);
const messages = computed(() => {
  return props.currentChatRoom
    ? messagesStore.messages[props.currentChatRoom.id] || []
    : [];
});
const isMessagesLoading = computed(() => {
  return props.currentChatRoom
    ? messagesStore.isMessagesLoading.get(props.currentChatRoom.id) || false
    : false;
});
const paginationState = computed(() => {
  return props.currentChatRoom
    ? messagesStore.paginationState[props.currentChatRoom.id]
    : null;
});

// 修改原有的 hasMoreMessages 计算属性
const hasMoreMessages = computed(() => {
  return (
    props.currentChatRoom &&
    paginationState.value &&
    !paginationState.value.hasMore &&
    messages.value.length > 0
  );
});
// 加载聊天消息 - 新增
const loadMessages = async (roomId: number) => {
  if (!roomId) return;

  try {
    if (
      !messagesStore.messages[roomId] ||
      messagesStore.messages[roomId].length === 0
    ) {
      await messagesStore.getRoomMessages(roomId);
    }

    nextTick(() => {
      scrollToBottom();
    });
  } catch (error: any) {
    console.error("加载消息失败:", error);
  }
};

// 加载更多消息 - 新增（从 chat.vue 移动过来）
const loadMoreMessages = async () => {
  if (!props.currentChatRoom || isLoadingMore.value) return;

  const roomId = props.currentChatRoom.id;
  const pagination = paginationState.value;

  if (!pagination || !pagination.hasMore || pagination.isLoadingMore) return;

  // 记录当前锚点消息ID
  lastAnchorMessageId.value = getAnchorMessageId();
  console.log("加载前锚点消息ID:", lastAnchorMessageId.value);

  isLoadingMore.value = true;

  try {
    const result = await messagesStore.getRoomMessages(roomId, true);
    if (!result.success && result.error) {
      console.error("加载更多消息失败:", result.error);
    } else {
      // 等待DOM更新
      await new Promise((resolve) => setTimeout(resolve, 100));
      await nextTick();
      await new Promise((resolve) => setTimeout(resolve, 50));

      if (lastAnchorMessageId.value) {
        await restoreScrollPosition(lastAnchorMessageId.value);
      } else {
        // 备用方案
        fallbackScrollRestore();
      }
    }
  } catch (error: any) {
    console.error("加载更多消息失败:", error);
  } finally {
    isLoadingMore.value = false;
    lastAnchorMessageId.value = null;
  }
};
// 处理滚动事件
const handleScroll = () => {
  if (!messagesContainer.value || !props.currentChatRoom || isLoadingMore.value)
    return;

  const { scrollTop } = messagesContainer.value;
  // 当滚动到距离顶部200px时开始加载更多消息
  if (scrollTop < 200) {
    loadMoreMessages(); // 直接调用内部方法，不再emit
  }
};

// 处理媒体预览
const handlePreviewMedia = (url: string, type: "image" | "video") => {
  emit("preview-media", url, type);
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    requestAnimationFrame(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop =
          messagesContainer.value.scrollHeight;
      }
    });
  }
};

// 基于锚点消息恢复滚动位置
const restoreScrollPosition = async (anchorMessageId: number) => {
  if (!messagesContainer.value) return;

  await nextTick();

  const anchorElement = document.getElementById(`message-${anchorMessageId}`);
  if (!anchorElement) {
    console.warn("锚点元素未找到，使用备用方案");
    fallbackScrollRestore();
    return;
  }

  const container = messagesContainer.value;
  const anchorRect = anchorElement.getBoundingClientRect();
  const containerRect = container.getBoundingClientRect();

  const currentAnchorOffset = anchorRect.top - containerRect.top;
  const targetScrollTop = anchorElement.offsetTop - currentAnchorOffset;

  container.scrollTop = targetScrollTop;

  setTimeout(() => {
    if (messagesContainer.value) {
      const finalAnchorElement = document.getElementById(
        `message-${anchorMessageId}`
      );
      if (finalAnchorElement) {
        const finalAnchorRect = finalAnchorElement.getBoundingClientRect();
        const finalContainerRect =
          messagesContainer.value.getBoundingClientRect();
        const finalOffset = finalAnchorRect.top - finalContainerRect.top;

        if (Math.abs(finalOffset - currentAnchorOffset) > 10) {
          messagesContainer.value.scrollTop =
            finalAnchorElement.offsetTop - currentAnchorOffset;
        }
      }
    }
  }, 150);
};

// 备用滚动恢复方案
const fallbackScrollRestore = () => {
  if (!messagesContainer.value) return;

  const container = messagesContainer.value;
  const messages = container.querySelectorAll(".message-item");
  if (messages.length > 10) {
    const targetMessage = messages[10] as HTMLElement;
    if (targetMessage) {
      container.scrollTop = targetMessage.offsetTop - 50;
    }
  }
};

// 获取锚点消息ID
const getAnchorMessageId = (): number | null => {
  if (!messagesContainer.value || !messages.value.length) return null;

  const container = messagesContainer.value;
  const containerRect = container.getBoundingClientRect();
  const containerTop = containerRect.top;

  for (const message of messages.value) {
    const element = document.getElementById(`message-${message.id}`);
    if (element) {
      const elementRect = element.getBoundingClientRect();
      if (
        elementRect.top >= containerTop &&
        elementRect.top < containerTop + container.clientHeight * 0.3
      ) {
        return message.id;
      }
    }
  }

  return messages.value[0]?.id || null;
};

// 监听当前聊天房间变化
watch(
  () => messages.value.length, // 只监听长度变化
  (newLength, oldLength) => {
    if (
      props.currentChatRoom &&
      !isLoadingMore.value &&
      newLength > oldLength
    ) {
      nextTick(() => {
        scrollToBottom();
      });
    }
  }
);

// 监听当前房间消息变化
watch(
  messages,
  (newMessages, oldMessages) => {
    if (props.currentChatRoom && !isLoadingMore.value) {
      // 只有当消息增加且不是在加载更多时才滚动到底部（处理新消息）
      if (
        oldMessages &&
        newMessages &&
        newMessages.length > oldMessages.length
      ) {
        nextTick(() => {
          scrollToBottom();
        });
      }
    }
  },
  { deep: true }
);

// 生命周期
onMounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener("scroll", handleScroll);
  }

  // 当组件首次挂载时，如果已有选中的聊天房间，自动加载消息并滚动到底部
  if (props.currentChatRoom) {
    loadMessages(props.currentChatRoom.id);
  }
});

onUnmounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener("scroll", handleScroll);
  }
});

// 暴露方法给父组件
defineExpose({
  scrollToBottom,
  restoreScrollPosition,
  getAnchorMessageId,
  fallbackScrollRestore,
});
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding: 16px;
  background-color: var(--color-bg-primary);
}

.loading-messages,
.empty-messages,
.no-chat-selected-content,
.loading-more,
.no-more-messages {
  text-align: center;
  color: var(--color-text-tertiary);
  padding: 10px 20px;
  font-size: 14px;
}

.loading-more,
.no-more-messages {
  margin: 10px 0;
  border-radius: 10px;
  font-size: 12px;
}

.loading-more {
  background-color: var(--color-bg-secondary);
}

.no-more-messages {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 767px) {
  .chat-messages {
    padding: 12px;
  }
}
</style>
