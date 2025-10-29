import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PrivateChatRoom, CreatePrivateChatRoomRequest } from '../api/chat'
import {
  createPrivateChatRoom as apiCreatePrivateChatRoom,
  getPrivateChatRooms as apiGetPrivateChatRooms,
} from '../api/chat'
import { useAuthStore } from './auth'




export const useChatStore = defineStore('chat', () => {
  // 状态
  const privateChatRooms = ref<PrivateChatRoom[]>([])
  const currentChatRoomId = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')


  const authStore = useAuthStore()
  
  // 计算属性
  const currentChatRoom = computed(() => {
    if (!currentChatRoomId.value) return null
    return privateChatRooms.value.find(room => room.id === currentChatRoomId.value)
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
  // 初始化store
  const initStore = async () => {
    if (authStore.isAuthenticated) {
      await getPrivateChatRooms()
    }
  }

  // 登出时清理资源
  const cleanupOnLogout = () => {
    privateChatRooms.value = []
    currentChatRoomId.value = null
    
  }

  return {
    // 状态
    privateChatRooms,
    currentChatRoomId,
    isLoading,
    error,
    // 计算属性
    currentChatRoom,
    // 方法
    createPrivateChatRoom,
    getPrivateChatRooms,
    getPrivateChatRoomWithUser,
    cleanupOnLogout,
    initStore
  }
})