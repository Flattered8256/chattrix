import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PrivateChatRoom, CreatePrivateChatRoomRequest, GroupChatRoom, CreateGroupChatRoomRequest } from '../api/chat'
import {
  createPrivateChatRoom as apiCreatePrivateChatRoom,
  getPrivateChatRooms as apiGetPrivateChatRooms,
  createGroupChatRoom as apiCreateGroupChatRoom,
  getGroupChatRooms as apiGetGroupChatRooms,
} from '../api/chat'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const privateChatRooms = ref<PrivateChatRoom[]>([])
  const groupChatRooms = ref<GroupChatRoom[]>([])
  const currentChatRoomId = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')


  const authStore = useAuthStore()
  
  // 计算属性
  const currentChatRoom = computed<PrivateChatRoom | GroupChatRoom | null>(() => {
    if (!currentChatRoomId.value) return null
    // 先在私聊房间中查找
    let room: PrivateChatRoom | GroupChatRoom | undefined = privateChatRooms.value.find(room => room.id === currentChatRoomId.value)
    // 如果找不到，在群聊房间中查找
    if (!room) {
      room = groupChatRooms.value.find(room => room.id === currentChatRoomId.value)
    }
    return room || null
  })

  // 获取所有聊天房间（私聊和群聊）
  const allChatRooms = computed(() => {
    return [...privateChatRooms.value, ...groupChatRooms.value]
  })

  // 创建私聊房间
  const createPrivateChatRoom = async (request: CreatePrivateChatRoomRequest) => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await apiCreatePrivateChatRoom(request)
      const newRoom = response.data
      
      // 检查是否已存在该房间，如果不存在则添加
      if (!privateChatRooms.value.find(room => room.id === newRoom.id)) {
        privateChatRooms.value.push(newRoom)
      }
      
      return { success: true, data: newRoom }
    } catch (err: any) {
      error.value = err.message || '创建私聊房间失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 获取所有私聊房间
  const getPrivateChatRooms = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await apiGetPrivateChatRooms()
      privateChatRooms.value = response.data
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '获取私聊房间失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 获取指定用户的聊天房间
  const getPrivateChatRoomWithUser = (userId: number) => {
    return privateChatRooms.value.find(room => 
      room.user1.id === userId || room.user2.id === userId
    )
  }
  // 创建群聊房间
  const createGroupChatRoom = async (request: CreateGroupChatRoomRequest) => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await apiCreateGroupChatRoom(request)
      const newRoom = response.data
      
      // 检查是否已存在该房间，如果不存在则添加
      if (!groupChatRooms.value.find(room => room.id === newRoom.id)) {
        groupChatRooms.value.push(newRoom)
      }
      
      return { success: true, data: newRoom }
    } catch (err: any) {
      error.value = err.message || '创建群聊房间失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 获取所有群聊房间
  const getGroupChatRooms = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await apiGetGroupChatRooms()
      groupChatRooms.value = response.data
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '获取群聊房间失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
// 获取聊天房间的显示信息（名称和头像）
const getChatRoomDisplayInfo = (room: PrivateChatRoom | GroupChatRoom) => {
  if ('other_user_info' in room) {
    // 私聊房间
    return {
      name: room.other_user_info.name,
      avatar: room.other_user_info.avatar,
      id: room.other_user_info.id
    };
  } else {
    // 群聊房间
    return {
      name: room.name,
      avatar: room.avatar || '',
      id: room.id
    };
  }
};

  // 初始化store
  const initStore = async () => {
    if (authStore.isAuthenticated) {
      await Promise.all([
        getPrivateChatRooms(),
        getGroupChatRooms()
      ])
    }
  }

  // 登出时清理资源
  const cleanupOnLogout = () => {
    privateChatRooms.value = []
    groupChatRooms.value = []
    currentChatRoomId.value = null
    
  }

  return {
    // 状态
    privateChatRooms,
    groupChatRooms,
    currentChatRoomId,
    isLoading,
    error,
    // 计算属性
    currentChatRoom,
    allChatRooms,
    // 方法
    createPrivateChatRoom,
    getPrivateChatRooms,
    getPrivateChatRoomWithUser,
    createGroupChatRoom,
    getGroupChatRooms,
    cleanupOnLogout,
    initStore,
    getChatRoomDisplayInfo
  }
})