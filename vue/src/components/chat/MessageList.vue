<template>
  <div class="chat-messages" ref="messagesContainer" @scroll="handleScroll">
    <div v-if="isMessagesLoading" class="loading-messages">
      加载消息中...
    </div>
    <div v-else-if="currentChatRoom && messages.length === 0" class="empty-messages">
      暂无消息，开始聊天吧！
    </div>
    <div v-else-if="!currentChatRoom" class="no-chat-selected-content">
      <p>从左侧列表选择一个聊天开始对话</p>
    </div>
    <div v-else class="messages-list">

      
      <div v-if="hasMoreMessages" class="no-more-messages">
        没有更多消息了
      </div>
      
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
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue';
import MessageItem from './MessageItem.vue';
import { useMessagesStore } from '../../store/messages';  // 新增
import { useAuthStore } from '../../store/auth';          // 新增
// 定义 Props
interface Props {
  currentChatRoom?: any;

}

// 定义 Emits
interface Emits {
  (e: 'preview-media', url: string, type: 'image' | 'video'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Store 引用
const messagesStore = useMessagesStore();  // 新增
const authStore = useAuthStore();          // 新增


// 组件引用
const messagesContainer = ref<HTMLDivElement | null>(null);

// 组件状态 - 新增
const isLoadingMore = ref(false);
const lastAnchorMessageId = ref<number | null>(null);
const lastLoadMoreTime = ref<number | null>(null); // 防抖时间记录
const loadMoreDebounceTimer = ref<number | null>(null); // 防抖定时器ID

// 计算属性
const currentUserId = computed(() => authStore.user?.id || 0);
const currentUser = computed(() => authStore.user);
const messages = computed(() => {
  return props.currentChatRoom ? messagesStore.messages[props.currentChatRoom.id] || [] : [];
});
const isMessagesLoading = computed(() => {
  return props.currentChatRoom ? messagesStore.isMessagesLoading.get(props.currentChatRoom.id) || false : false;
});
const paginationState = computed(() => {
  return props.currentChatRoom ? messagesStore.paginationState[props.currentChatRoom.id] : null;
});

// 修改原有的 hasMoreMessages 计算属性
const hasMoreMessages = computed(() => {
  return props.currentChatRoom && 
         paginationState.value && 
         !paginationState.value.hasMore && 
         messages.value.length > 0;
});
// 加载聊天消息 - 新增
const loadMessages = async (roomId: number) => {
  if (!roomId) return;
  
  try {
    if (!messagesStore.messages[roomId] || messagesStore.messages[roomId].length === 0) {
      await messagesStore.getRoomMessages(roomId);
    }
    
    nextTick(() => {
      scrollToBottom();
    });
  } catch (error: any) {
    console.error('加载消息失败:', error);
  }
};

// 加载更多消息 - 优化版本，防止屏幕闪动
const loadMoreMessages = async () => {
  if (!props.currentChatRoom || isLoadingMore.value) return;
  
  const roomId = props.currentChatRoom.id;
  const pagination = paginationState.value;
  
  if (!pagination || !pagination.hasMore || pagination.isLoadingMore) return;
  
  // 记录当前锚点消息ID和滚动位置
  lastAnchorMessageId.value = getAnchorMessageId();
  
  // 记录加载前的容器信息
  const container = messagesContainer.value;
  if (!container) return;
  



  
  // 预计算并保存可见区域的关键信息
  const oldScrollTop = container.scrollTop;
  const oldScrollHeight = container.scrollHeight;

  // 关键优化：在数据加载期间保持容器最小高度，防止闪烁
  container.style.minHeight = `${container.offsetHeight}px`;

  isLoadingMore.value = true;
  lastLoadMoreTime.value = Date.now();
  
  try {
    // 防止在数据加载期间发生布局抖动
    container.style.willChange = 'scroll-position';
    container.style.pointerEvents = 'none'; // 临时禁用滚动交互以避免冲突
    

    const result = await messagesStore.getRoomMessages(roomId, true);
    
    if (!result.success && result.error) {
      console.error('加载更多消息失败:', result.error);
    } else {
      // 关键优化：使用requestAnimationFrame确保在DOM更新后立即调整滚动位置
      await nextTick();
      
      // 计算新的滚动位置，精确补偿新加载消息的高度
      const newScrollHeight = container.scrollHeight;
      const heightDifference = newScrollHeight - oldScrollHeight;
      
      // 强制重绘以确保新消息被正确渲染
      container.style.transform = 'translateZ(0)';
      
      // 关键优化：在DOM更新后立即设置滚动位置，不等待动画帧
      requestAnimationFrame(() => {
        // 直接设置滚动位置，补偿新加载的消息高度
        container.scrollTop = oldScrollTop + heightDifference;
        
        // 如果有锚点消息，进行精确调整
        if (lastAnchorMessageId.value) {
          // 立即进行精确调整，不使用setTimeout
          restoreScrollPosition(lastAnchorMessageId.value!);
        }
        
        // 恢复容器的交互性和样式
        container.style.pointerEvents = '';
        container.style.willChange = '';
        container.style.transform = '';
        container.style.minHeight = '';
      });
    }
  } catch (error: any) {
    console.error('加载更多消息失败:', error);
    // 发生错误时也要恢复容器状态
    container.style.pointerEvents = '';
    container.style.willChange = '';
    container.style.transform = '';
    container.style.minHeight = '';
  } finally {
    isLoadingMore.value = false;
    lastAnchorMessageId.value = null;
  }
};
// 处理滚动事件
const handleScroll = () => {
  if (!messagesContainer.value || !props.currentChatRoom || isLoadingMore.value) return;
  
  const { scrollTop } = messagesContainer.value;
  // 当滚动到距离顶部200px时开始加载更多消息
  if (scrollTop < 200) {
    // 添加防抖，避免频繁触发加载
    if (loadMoreDebounceTimer.value) {
      clearTimeout(loadMoreDebounceTimer.value);
    }
    
    loadMoreDebounceTimer.value = window.setTimeout(() => {
      // 检查是否已经在短时间内触发过加载
      const now = Date.now();
      if (!lastLoadMoreTime.value || (now - lastLoadMoreTime.value > 500)) {
        loadMoreMessages();  // 直接调用内部方法，不再emit
      }
    }, 300); // 300ms防抖延迟
  }
};

// 处理媒体预览
const handlePreviewMedia = (url: string, type: 'image' | 'video') => {
  emit('preview-media', url, type);
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    requestAnimationFrame(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });
  }
};

// 基于锚点消息恢复滚动位置 - 优化版本，防止闪烁
const restoreScrollPosition = async (anchorMessageId: number) => {
  if (!messagesContainer.value) return;
  
  await nextTick();
  
  const container = messagesContainer.value;
  const anchorElement = document.getElementById(`message-${anchorMessageId}`) as HTMLElement;
  
  if (!anchorElement) {
    console.warn('锚点元素未找到，使用备用方案');
    fallbackScrollRestore();
    return;
  }
  
  // 关键优化：直接设置滚动位置，不使用平滑滚动避免闪烁
  // 获取锚点元素相对于容器的位置
  const targetScrollTop = anchorElement.offsetTop;
  
  // 立即设置滚动位置，不使用动画
  container.scrollTop = targetScrollTop;
  
  // 强制重绘以确保位置正确
  container.style.transform = 'translateZ(0)';
  
  // 使用requestAnimationFrame确保滚动位置稳定
  requestAnimationFrame(() => {
    // 进行最终的微调，确保位置精确
    const finalScrollTop = anchorElement.offsetTop;
    if (Math.abs(container.scrollTop - finalScrollTop) > 3) {
      container.scrollTop = finalScrollTop;
    }
  });
};

// 备用滚动恢复方案
const fallbackScrollRestore = () => {
  if (!messagesContainer.value) return;
  
  const container = messagesContainer.value;
  const messages = container.querySelectorAll('.message-item');
  if (messages.length > 10) {
    const targetMessage = messages[10] as HTMLElement;
    if (targetMessage) {
      // 计算并设置滚动位置，确保目标消息保持在可视区域内
      const containerHeight = container.clientHeight;
      container.scrollTop = (targetMessage as HTMLElement).offsetTop - containerHeight * 0.3;
    }
  }
};

// 获取锚点消息ID - 优化版本，提高锚点准确性
const getAnchorMessageId = (): number | null => {
  if (!messagesContainer.value || !messages.value.length) return null;
  
  const container = messagesContainer.value;
  
  // 关键优化：直接获取第一个可见消息作为锚点，而不是基于ID估算
  // 这样可以确保锚点消息在DOM中确实可见
  const messageElements = document.querySelectorAll('.message-item');
  
  if (messageElements.length === 0) return messages.value[0].id;
  
  // 获取第一个可见区域的消息作为锚点
  for (const element of messageElements) {
    const rect = element.getBoundingClientRect();
    // 检查消息是否在容器的可见区域内
    if (rect.top >= 0 && rect.top <= container.clientHeight) {
      // 从元素ID中提取消息ID
      const idMatch = element.id.match(/^message-(\d+)$/);
      if (idMatch) {
        return Number(idMatch[1]);
      }
      break;
    }
  }
  
  // 回退方案：如果找不到可见消息，返回第一个消息ID
  return messages.value[0].id;
};

// 监听当前聊天房间变化
watch(
  () => messages.value.length, // 只监听长度变化
  (newLength, oldLength) => {
    if (props.currentChatRoom && !isLoadingMore.value && newLength > oldLength) {
      nextTick(() => {
        scrollToBottom();
      });
    }
  }
);

// 监听当前房间消息变化
watch(messages, (newMessages, oldMessages) => {
  if (props.currentChatRoom && !isLoadingMore.value) {
    // 只有当消息增加且不是在加载更多时才滚动到底部（处理新消息）
    if (oldMessages && newMessages && newMessages.length > oldMessages.length) {
      nextTick(() => {
        scrollToBottom();
      });
    }
  }
}, { deep: true });

// 生命周期
onMounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll);
  }
  
  // 当组件首次挂载时，如果已有选中的聊天房间，自动加载消息并滚动到底部
  if (props.currentChatRoom) {
    loadMessages(props.currentChatRoom.id);
  }
});

onUnmounted(() => {
    if (messagesContainer.value) {
      messagesContainer.value.removeEventListener('scroll', handleScroll);
    }
    
    // 清理定时器
    if (loadMoreDebounceTimer.value) {
      clearTimeout(loadMoreDebounceTimer.value);
    }
  });

// 暴露方法给父组件
defineExpose({
  scrollToBottom,
  restoreScrollPosition,
  getAnchorMessageId,
  fallbackScrollRestore
});
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding: 16px;
  background-color: #fafafa;
  -webkit-transform: translateZ(0); /* 硬件加速，改善移动设备渲染 */
  transform: translateZ(0);
  will-change: scroll-position; /* 告诉浏览器我们将改变滚动位置 */
  /* 添加滚动行为优化 */
  scroll-behavior: auto; /* 避免默认的平滑滚动导致的额外抖动 */
  contain: layout style; /* 提高渲染性能，减少布局抖动 */
}

/* 确保消息项在移动设备上正确渲染 */
.messages-list {
  min-height: 1px; /* 防止高度计算问题 */
  /* 优化消息列表的渲染性能 */
  contain: layout; /* 限制布局影响范围 */
}

/* 优化消息项的渲染性能 */
:deep(.message-item) {
  will-change: auto; /* 避免不必要的重绘 */
  contain: style; /* 限制样式影响范围 */
}

.loading-messages,
.empty-messages,
.no-chat-selected-content,
.loading-more,
.no-more-messages {
  text-align: center;
  color: #999;
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
  background-color: #f8f9fa;
}

.no-more-messages {
  background-color: #f0f0f0;
  color: #666;
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

/* 夜间模式样式 */
@media (prefers-color-scheme: dark) {
  .chat-messages {
    background-color: #1a1a1a;
  }
  
  .loading-messages,
  .empty-messages,
  .no-chat-selected-content,
  .loading-more,
  .no-more-messages {
    color: #aaa;
  }
  
  .loading-more {
    background-color: #2a2a2a;
  }
  
  .no-more-messages {
    background-color: #333;
    color: #aaa;
  }
}
</style>