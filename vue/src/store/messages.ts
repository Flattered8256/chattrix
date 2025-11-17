import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {Message, SendMessageRequest, PaginatedApiResponse } from '../api/messages'
import {
  getRoomMessages as apiGetRoomMessages,
  sendMessage as apiSendMessage
} from '../api/messages'
import { type WebSocketMessage } from '../api/webosckets'
import { useChatStore } from './chat'
import { useAuthStore } from './auth'
import { wsService } from '../api/webosckets'
import {get} from '../api/https'
import { markMessageAsRead, getUnreadMessageCount } from '../api/messages'



interface MessagesState {
  [roomId: number]: Message[]
}

interface PaginationState {
  [roomId: number]: {
    hasMore: boolean;
    nextUrl: string | null; 
    isLoadingMore: boolean;
  }
}

interface MessageSendingState {
  [roomId: number]: {
    [messageId: string]: 'sending' | 'sent' | 'failed'
  }
}
export const useMessagesStore = defineStore('messages', () => {
  // 状态
  const messages = ref<MessagesState>({})
  const messageSendingStates = ref<MessageSendingState>({})
  const isMessagesLoading = ref<Map<number, boolean>>(new Map())
  const messagesError = ref<Map<number, string>>(new Map())
  const unreadMessagesCount = ref<Map<number, number>>(new Map())
  const navigation_UnreadMessagesCount = ref<Map<number, number>>(new Map())
  const paginationState = ref<PaginationState>({})
  // 新增状态：跟踪用户是否当前正在聊天页面查看消息
  const isUserViewingChat = ref(false)
  // 新增状态：缓存WebSocket消息，用于处理离线后重新上线时的批量消息
  const cachedWebSocketMessages = ref<Map<number, Message[]>>(new Map())
  // 新增状态：标记是否正在处理缓存的消息
  const isProcessingCachedMessages = ref<Map<number, boolean>>(new Map())
  //计算属性
  const currentRoomMessages = computed(() => {
  if (!chatStore.currentChatRoomId) return []
  return messages.value[chatStore.currentChatRoomId] || []                    
  })
  const hasUnreadMessages = computed(() => {
    return Array.from(unreadMessagesCount.value.values()).some(count => count > 0)
  })
  const totalUnreadMessagesCount = computed(() => {
    return Array.from(navigation_UnreadMessagesCount.value.values()).reduce((total, count) => total + count, 0)
  })

  const chatStore = useChatStore()
  const authStore = useAuthStore()

  // 添加辅助函数将绝对URL转换为相对路径
const convertToRelativeUrl = (absoluteUrl: string): string => {
  try {
    const url = new URL(absoluteUrl);
    // 只保留路径和查询参数部分
    return url.pathname + url.search;
  } catch {
    // 如果已经是相对路径，直接返回
    return absoluteUrl;
  }
};
  const getRoomMessages = async (roomId: number, isLoadMore: boolean = false) => {
  // 如果是加载更多且已经没有更多消息，则直接返回
  if (isLoadMore && paginationState.value[roomId] && !paginationState.value[roomId].hasMore) {
    return { success: true, hasMore: false }
  }

  // 设置加载状态
  if (isLoadMore) {
    if (!paginationState.value[roomId]) {
      paginationState.value[roomId] = { 
        hasMore: true, 
        nextUrl: null,
        isLoadingMore: false 
      }
    }
    paginationState.value[roomId].isLoadingMore = true
  } else {
    isMessagesLoading.value.set(roomId, true)
  }
  messagesError.value.set(roomId, '')

  try {
    let response: PaginatedApiResponse<Message[]>;
    
    if (isLoadMore && paginationState.value[roomId]?.nextUrl) {
      // 直接使用存储的相对路径URL获取下一页数据
      response = await get(paginationState.value[roomId].nextUrl!);
    } else {
      // 第一次加载，使用常规API
      response = await apiGetRoomMessages(roomId)
    }
    

    // 处理消息，确保文件名正确显示
    const processedMessages = response.data.map((msg: Message) => {
      if ('file' in msg && msg.filename && !msg.content) {
        return {
          ...msg,
          content: msg.filename
        }
      }
      return msg
    })
    
    // 初始化分页状态
    if (!paginationState.value[roomId]) {
      paginationState.value[roomId] = {
        hasMore: true,
        nextUrl: null,
        isLoadingMore: false
      }
    }
    
    // 更新分页信息 - 将绝对URL转换为相对路径
    const hasMore = response['pagination-next'] !== null && response['pagination-next'] !== undefined;
    let nextUrl = response['pagination-next'] || null;
    
    // 如果是绝对URL，转换为相对路径
    if (nextUrl && nextUrl.startsWith('http')) {
      nextUrl = convertToRelativeUrl(nextUrl);
    }
    
    paginationState.value[roomId].hasMore = hasMore;
    paginationState.value[roomId].nextUrl = nextUrl;
    
    // 更新消息列表

    if (isLoadMore) {
      if (!messages.value[roomId]) {
        messages.value[roomId] = [];
      }
      // 去重处理
      const existingIds = new Set(messages.value[roomId].map(msg => msg.id));
      const newMessages = processedMessages.filter(msg => msg.id && !existingIds.has(msg.id));
      // 修复：将历史消息添加到开头
      messages.value[roomId] = [...newMessages, ...messages.value[roomId]];
    } else {
      messages.value[roomId] = processedMessages;
    }
    
    return { 
      success: true, 
      data: processedMessages,
      hasMore: paginationState.value[roomId].hasMore
    }
  } catch (err: any) {
    const errorMessage = err.message || '获取房间消息失败'
    messagesError.value.set(roomId, errorMessage)
    return { success: false, error: errorMessage }
  } finally {
    // 重置加载状态
    if (isLoadMore) {
      if (paginationState.value[roomId]) {
        paginationState.value[roomId].isLoadingMore = false;
      }
    } else {
      isMessagesLoading.value.set(roomId, false)
    }
  }
}
    // 发送消息
  const sendMessage = async (roomId: number, request: SendMessageRequest) => {
    // 生成临时消息ID用于状态跟踪
    const tempMessageId = `temp_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`
    
    // 初始化消息发送状态
    if (!messageSendingStates.value[roomId]) {
      messageSendingStates.value[roomId] = {}
    }
    messageSendingStates.value[roomId][tempMessageId] = 'sending'

    try {
      // 直接调用API发送消息，不添加临时消息到前端
      const response = await apiSendMessage(roomId, request)
      const newMessage = response.data
      
      // 更新消息发送状态
      messageSendingStates.value[roomId][tempMessageId] = 'sent'
      
      // 确保消息列表存在
      if (!messages.value[roomId]) {
        messages.value[roomId] = []
      }      
      return { success: true, data: newMessage }
    } catch (err: any) {
      const errorMessage = err.message || '发送消息失败'
      messageSendingStates.value[roomId][tempMessageId] = 'failed'
      
      return { success: false, error: errorMessage, tempMessageId }
    } finally {
      // 清理消息发送状态
      setTimeout(() => {
        if (messageSendingStates.value[roomId]) {
          delete messageSendingStates.value[roomId][tempMessageId];
        }
      }, 3000);
    }
  }
  // 设置当前聊天房间
  const setCurrentChatRoom = async (roomId: number) => {
    chatStore.currentChatRoomId = roomId
    // 清除当前房间的未读消息计数
    if (unreadMessagesCount.value.has(roomId)) {
      unreadMessagesCount.value.set(roomId, 0)
    }
    // 如果当前房间还没有消息，则获取消息
    if (!messages.value[roomId] || messages.value[roomId].length === 0) {
      await getRoomMessages(roomId)
    }
    // 标记最后一条消息为已读
    if (messages.value[roomId] && messages.value[roomId].length > 0) {
      // 获取最后一条消息（假设消息是按时间正序排列的）
      const lastMessage = messages.value[roomId][messages.value[roomId].length - 1];
      // 检查是否有消息ID且不是当前用户发送的（避免标记自己的消息为已读）
      if (lastMessage.id && lastMessage.sender && lastMessage.sender.id !== authStore.user?.id) {
        try {
          await markMessageAsRead(roomId, lastMessage.id);
        } catch (error) {
          console.error('标记消息为已读失败:', error);
        }
      }
    }
  }

const fetchRoomUnreadCount = async (roomId: number) => {
  try {
    const response = await getUnreadMessageCount(roomId)
    if (response.data.unread_count > 0) {
      unreadMessagesCount.value.set(roomId, response.data.unread_count)
      navigation_UnreadMessagesCount.value.set(roomId, response.data.unread_count)
    }
  } catch (err) {
    console.error(`获取房间 ${roomId} 的未读消息数失败:`, err)
  }
}
const initializeUnreadCounts = async () => {
  if (!authStore.isAuthenticated) return
  
  // 遍历所有私有聊天房间并获取未读消息数
  for (const room of chatStore.privateChatRooms) {
    await fetchRoomUnreadCount(room.id)
  }
  
  // 遍历所有群聊房间并获取未读消息数
  for (const room of chatStore.groupChatRooms) {
    await fetchRoomUnreadCount(room.id)
  }
}
   // 增加未读消息计数
  const incrementUnreadMessages = (roomId: number) => {
    const currentCount = unreadMessagesCount.value.get(roomId) || 0
    unreadMessagesCount.value.set(roomId, currentCount + 1)
  }


  // 新增：加载所有房间的历史消息
  const loadAllRoomsMessages = async () => {
    const promises: Promise<any>[] = [];
    
    // 遍历所有私有聊天房间
    chatStore.privateChatRooms?.forEach(room => {
      // 检查是否需要加载消息（如果该房间还没有消息数据）
      if (!messages.value[room.id] || messages.value[room.id].length === 0) {
        promises.push(getRoomMessages(room.id))
      }
    })
    
    // 遍历所有群聊房间
    chatStore.groupChatRooms?.forEach(room => {
      // 检查是否需要加载消息（如果该房间还没有消息数据）
      if (!messages.value[room.id] || messages.value[room.id].length === 0) {
        promises.push(getRoomMessages(room.id))
      }
    })
    
    // 等待所有消息加载完成
    await Promise.all(promises);
  }
    // 连接到聊天室WebSocket
  const connectToChatRoomWebSocket = (roomId: number) => {
    const wsHandler = wsService.getChatConnection(roomId, {
      onMessage: (message) => handleChatMessage(message) // 传递roomId给处理函数
    })
      // 只有在连接未打开且未连接中时才发起连接
    if (wsHandler.status.value !== 'connected' && wsHandler.status.value !== 'connecting') {
      wsHandler.connect()
    }
  }
      // 连接所有聊天房间的WebSocket
  const connectAllChatRooms = () => {
    // 遍历所有私有聊天房间并建立连接
    chatStore.privateChatRooms?.forEach(room => {
      connectToChatRoomWebSocket(room.id)
    })
    
    // 遍历所有群聊房间并建立连接
    chatStore.groupChatRooms?.forEach(room => {
      connectToChatRoomWebSocket(room.id)
    })
  }

  
  // 1. handleChatMessage 函数
const handleChatMessage = (message: WebSocketMessage) => {
  switch (message.type) {
    case 'chat_message':
      // 处理新消息，添加防御性检查
      if (message) {
        // 对于chat_message类型，我们需要特殊处理，先缓存再统一处理
        const roomId = message.room_id;
        
        // 如果是当前查看的房间，并且用户正在聊天页面，先缓存消息
        if (roomId === chatStore.currentChatRoomId && isUserViewingChat.value) {
          // 初始化该房间的缓存数组
          if (!cachedWebSocketMessages.value.has(roomId)) {
            cachedWebSocketMessages.value.set(roomId, []);
          }
          
          // 将消息添加到缓存中
          cachedWebSocketMessages.value.get(roomId)!.push(message);
          
          // 如果还没有开始处理这个房间的缓存消息，则启动处理
          if (!isProcessingCachedMessages.value.get(roomId)) {
            processCachedMessages(roomId);
          }
        } else {
          // 对于非当前查看的房间，直接处理
          handleNewMessage(message);
        }
      } else {
        console.warn('收到无效的chat_message: 消息数据不存在')
      }
      break
    case 'chat_room_created':
      // 处理聊天房间创建
      chatStore.getPrivateChatRooms()
      break
    // 可以根据需要添加更多消息类型处理
  }
}


    // 重新发送失败的消息
  const resendFailedMessage = async (roomId: number, tempMessageId: string, request: SendMessageRequest) => {
    if (messageSendingStates.value[roomId]?.[tempMessageId] === 'failed') {
      return sendMessage(roomId, request)
    }
    return { success: false, error: '该消息不需要重新发送' }
  }

  // 2. handleNewMessage 函数
const handleNewMessage = (messageData: Message) => {
  const roomId = messageData.room_id; // 使用room_id代替room
  
  // 确保房间消息数组存在
  if (!messages.value[roomId]) {
    messages.value[roomId] = []
  }
  
  // 防止重复消息：检查消息ID是否已存在
  const messageExists = messages.value[roomId].some(msg => msg.id && msg.id === messageData.id);
  if (!messageExists) {
    // 只有当消息不存在时才添加
    messages.value[roomId].push(messageData);
    // 处理消息已读状态
    // 正确比较发送者ID与当前用户ID，只有他人发送的消息才需要处理已读状态
    if (messageData.sender?.id !== authStore.user?.id) {
      // 只有当用户真正在聊天页面查看该房间时，才标记消息为已读
      // 注意：这里不再直接标记已读，已读标记由processCachedMessages处理
      if (!(roomId === chatStore.currentChatRoomId && isUserViewingChat.value)) {
        // 如果不在该房间或用户不在聊天页面，增加未读计数
        incrementUnreadMessages(roomId);
      }
    }
  }
}

  // 新增：处理缓存的WebSocket消息
const processCachedMessages = async (roomId: number) => {
  // 标记该房间正在处理缓存消息
  isProcessingCachedMessages.value.set(roomId, true);
  
  try {
    // 等待一小段时间，收集可能同时到达的多条消息
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const cachedMessages = cachedWebSocketMessages.value.get(roomId);
    if (!cachedMessages || cachedMessages.length === 0) {
      return;
    }
    
    // 过滤出非自己发送的消息，并按ID排序
    const nonSelfMessages = cachedMessages.filter(msg => 
      msg.sender?.id !== authStore.user?.id && msg.id
    ).sort((a, b) => (a.id || 0) - (b.id || 0));
      
    // 处理所有缓存的消息，添加到消息列表
    cachedMessages.forEach(messageData => {
      handleNewMessage(messageData);
    });
    
    // 只标记最后一条非自己发送的消息为已读
    if (nonSelfMessages.length > 0) {
      const lastMessage = nonSelfMessages[nonSelfMessages.length - 1];
      if (lastMessage.id) {
        try {
          await markMessageAsRead(roomId, lastMessage.id);
          // 清除该房间的未读消息计数
          if (unreadMessagesCount.value.has(roomId)) {
            unreadMessagesCount.value.set(roomId, 0);
          }
        } catch (error) {
          console.error('标记缓存消息最后一条为已读失败:', error);
        }
      }
    }
  } finally {
    // 清除缓存并重置处理状态
    cachedWebSocketMessages.value.delete(roomId);
    isProcessingCachedMessages.value.delete(roomId);
  }
}

  const initStore = async () => {
    if (authStore.isAuthenticated) {
      await loadAllRoomsMessages()
      initializeUnreadCounts()
      connectAllChatRooms()
    }
  }

    // 清理当前房间的WebSocket连接
  const cleanupCurrentRoomConnection = () => {
    if (chatStore.currentChatRoomId) {
      wsService.closeChatConnection(chatStore.currentChatRoomId)
    }
  }

  // 登出时清理资源
  const cleanupOnLogout = () => {
    messages.value = {}
    unreadMessagesCount.value.clear()
    messageSendingStates.value = {}
    isMessagesLoading.value.clear()
    messagesError.value.clear()
    cachedWebSocketMessages.value.clear() // 清除缓存的消息
    isProcessingCachedMessages.value.clear() // 清除处理状态
    wsService.closeAllConnections()
  }

  // 检测并处理新的聊天房间
  const RefreshNewChatRooms = async () => {
    try {
      // 保存当前的房间列表ID
      const currentPrivateRoomIds = new Set(chatStore.privateChatRooms?.map(room => room.id) || []);
      const currentGroupRoomIds = new Set(chatStore.groupChatRooms?.map(room => room.id) || []);
      
      // 重新刷新房间列表
      await Promise.all([
        chatStore.getPrivateChatRooms(),
        chatStore.getGroupChatRooms()
      ]);
      
      // 获取最新的房间列表
      const updatedPrivateRooms = chatStore.privateChatRooms || [];
      const updatedGroupRooms = chatStore.groupChatRooms || [];
      
      // 找出新的私聊房间
      const newPrivateRooms = updatedPrivateRooms.filter(room => !currentPrivateRoomIds.has(room.id));
      // 找出新的群聊房间
      const newGroupRooms = updatedGroupRooms.filter(room => !currentGroupRoomIds.has(room.id));
      
      // 合并所有新房间
      const allNewRooms = [...newPrivateRooms, ...newGroupRooms];
      
      // 为新房间添加未读计数并连接WebSocket
      for (const room of allNewRooms) {
        // 为新房间初始化未读消息计数
        incrementUnreadMessages(room.id);
        // 为新房间建立WebSocket连接
        connectToChatRoomWebSocket(room.id);
      }
      
      return { success: true, newRooms: allNewRooms };
    } catch (error) {
      console.error('检测和处理新聊天房间失败:', error);
      return { success: false, error };
    }
  }

  return {
    // 状态
    messages,
    messageSendingStates,
    isMessagesLoading,
    messagesError,
    unreadMessagesCount,
    paginationState,
    isUserViewingChat, // 导出新状态
    
    //计算属性
    currentRoomMessages,
    hasUnreadMessages,
    totalUnreadMessagesCount, 

    //方法
    cleanupOnLogout,
    setCurrentChatRoom,
    incrementUnreadMessages,
    getRoomMessages,
    sendMessage,
    resendFailedMessage,
    handleChatMessage,
    initStore,
    cleanupCurrentRoomConnection,
    RefreshNewChatRooms,
    processCachedMessages, // 导出新方法
  }


})
