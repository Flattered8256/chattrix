import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import type { Friend, FriendRequest, FriendGroup, FriendBlock, FriendGroupMembership, FriendNickname } from '../api/friends'
import {
  getFriends as apiGetFriends,
  getFriendRequests as apiGetFriendRequests,
  sendFriendRequest as apiSendFriendRequest,
  acceptFriendRequest as apiAcceptFriendRequest,
  rejectFriendRequest as apiRejectFriendRequest,
  removeFriend as apiRemoveFriend,
  getFriendGroups as apiGetFriendGroups,
  createFriendGroup as apiCreateFriendGroup,
  updateFriendGroup as apiUpdateFriendGroup,
  removeFriendGroup as apiRemoveFriendGroup,
  addFriendToGroup as apiAddFriendToGroup,
  removeFriendFromGroup as apiRemoveFriendFromGroup,
  setFriendNickname as apiSetFriendNickname,
  blockFriend as apiBlockFriend,
  unblockFriend as apiUnblockFriend,
  removeBlock as apiRemoveBlock,
  getBlockedFriends as apiGetBlockedFriends,
} from '../api/friends'
import { wsService, type WebSocketMessage } from '../api/webosckets'
import { useRoute } from 'vue-router'
import { useMessagesStore } from './messages'

export const useFriendsStore = defineStore('friends', () => {
  // 状态
  const friends = ref<Friend[]>([])  
  const friendRequests = ref<FriendRequest[]>([])  
  const friendGroups = ref<FriendGroup[]>([])  
  const blockedFriends = ref<FriendBlock[]>([])  
  const friendNicknames = ref<FriendNickname[]>([])  
  const groupMemberships = ref<FriendGroupMembership[]>([])  
  const isLoading = ref<boolean>(false)  
  const error = ref<string>('')  
   // 添加未读消息计数
  const unreadFriendMessagesCount = ref<number>(0)  
  const route = useRoute()
  const messagesStore = useMessagesStore()
  
  // 计算属性
  const pendingFriendRequests = computed(() => 
    friendRequests.value.filter(request => request.status === 'pending')
  )
  
  const acceptedFriendRequests = computed(() => 
    friendRequests.value.filter(request => request.status === 'accepted')
  )
  
  const rejectedFriendRequests = computed(() => 
    friendRequests.value.filter(request => request.status === 'rejected')
  )
  
   // 计算是否有未读好友相关消息
  const hasUnreadFriendMessages = computed(() => {
    return unreadFriendMessagesCount.value > 0
  })
  
  // 重置未读消息状态
  const resetUnreadFriendMessages = () => {
    unreadFriendMessagesCount.value = 0
  }
  
  // 增加未读消息计数
  const incrementUnreadFriendMessages = (count: number = 1) => {
    unreadFriendMessagesCount.value += count
  }

  const friendsWithGroups = computed(() => {
    const membershipMap = new Map<number, number[]>()
    groupMemberships.value.forEach(membership => {
      if (!membershipMap.has(membership.friend)) {
        membershipMap.set(membership.friend, [])
      }
      membershipMap.get(membership.friend)?.push(membership.group)
    })
    
    return friends.value.map(friend => ({
      ...friend,
      groups: membershipMap.get(friend.friend) || []
    }))
  })
  
// WebSocket消息处理函数
const handleFriendMessage = (message: WebSocketMessage) => {
  
  // 检查用户是否在好友页面
  const isOnContactsPage = route.path === '/contacts'
  
  switch (message.type) {
    case 'friend_accepted':
      // 只有当用户不在好友页面时才增加未读消息计数
      if (!isOnContactsPage) {
        incrementUnreadFriendMessages()
      }
      getFriends()
      messagesStore.RefreshNewChatRooms()
      break
    case 'friend_request':
      // 处理收到好友请求
      // 只有当用户不在好友页面时才增加未读消息计数
      if (!isOnContactsPage) {
        incrementUnreadFriendMessages()
      }
      getFriendRequests()
      break

    default:
      console.log('未知的好友WebSocket消息类型:', message.type)
    }
  }

  // 获取好友WebSocket连接
  const setupWebSocketConnection = () => {
    const friendsConnection = wsService.getFriendsConnection({
      onMessage: handleFriendMessage,
      onError: (wsError) => {
        console.error('好友WebSocket连接错误:', wsError)
        error.value = '好友实时更新连接失败'
      },

      onDisconnect: () => {
        console.log('好友WebSocket连接已断开')
      }
    })
    
    // 连接WebSocket
    friendsConnection.connect()
    
    return friendsConnection
  }

  // 存储WebSocket连接实例
  let friendsWebSocketConnection: any = null

  // 获取好友列表
  const getFriends = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetFriends()
      friends.value = response.data
      return { success: true, data: friends.value }
    } catch (err: any) {
      error.value = err.message || '获取好友列表失败'
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  

  
  // 获取好友请求列表
  const getFriendRequests = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetFriendRequests()
      friendRequests.value = response.data
      return { success: true, data: friendRequests.value }
    } catch (err: any) {
      error.value = err.message || '获取好友请求列表失败'
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  
  // 发送好友请求
  const sendFriendRequest = async (receiverId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiSendFriendRequest(receiverId)
      // 添加到本地好友请求列表
      friendRequests.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '发送好友请求失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 接受好友请求
  const acceptFriendRequest = async (requestId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiAcceptFriendRequest(requestId)
      // 更新本地状态
      const request = friendRequests.value.find(r => r.id === requestId)
      if (request) {
        request.status = 'accepted'
      }
      // 重新获取好友列表
      await getFriends()
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '接受好友请求失败'
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  
  // 拒绝好友请求
  const rejectFriendRequest = async (requestId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiRejectFriendRequest(requestId)
      // 更新本地状态
      const request = friendRequests.value.find(r => r.id === requestId)
      if (request) {
        request.status = 'rejected'
      }
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '拒绝好友请求失败'
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除好友
  const removeFriend = async (friendId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiRemoveFriend(friendId)
      // 从本地列表中移除
      await getFriends()
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除好友失败'
      await getFriends()
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取好友分组列表
  const getFriendGroups = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetFriendGroups()
      friendGroups.value = response.data
      return { success: true, data: friendGroups.value }
    } catch (err: any) {
      error.value = err.message || '获取好友分组列表失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建好友分组
  const createFriendGroup = async (name: string) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiCreateFriendGroup(name)
      friendGroups.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '创建好友分组失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 更新好友分组
  const updateFriendGroup = async (groupId: number, name: string) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiUpdateFriendGroup(groupId, name)
      // 更新本地状态
      const group = friendGroups.value.find(g => g.id === groupId)
      if (group) {
        group.name = name
      }
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '更新好友分组失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除好友分组
  const removeFriendGroup = async (groupId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiRemoveFriendGroup(groupId)
      // 从本地列表中移除
      friendGroups.value = friendGroups.value.filter(group => group.id !== groupId)
      // 同时移除该分组的所有成员关系
      groupMemberships.value = groupMemberships.value.filter(membership => membership.group !== groupId)
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除好友分组失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 添加好友到分组
  const addFriendToGroup = async (groupId: number, friendId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiAddFriendToGroup(groupId, friendId)
      groupMemberships.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '添加好友到分组失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 从分组中移除好友
  const removeFriendFromGroup = async (membershipId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiRemoveFriendFromGroup(membershipId)
      // 从本地列表中移除
      groupMemberships.value = groupMemberships.value.filter(membership => membership.id !== membershipId)
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '从分组中移除好友失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 设置好友备注
  const setFriendNickname = async (friendId: number, nickname: string) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiSetFriendNickname(friendId, nickname)
      friendNicknames.value.push(response.data)
      await getFriends()  
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '设置好友备注失败'
      throw new Error(error.value) 
    } finally {
      isLoading.value = false
    }
  }
  

  
  // 屏蔽好友
  const blockFriend = async (friendId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiBlockFriend(friendId)
      blockedFriends.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '屏蔽好友失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 解除好友屏蔽
  const unblockFriend = async (blockId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiUnblockFriend(blockId)
      // 更新本地状态
      const blockIndex = blockedFriends.value.findIndex(b => b.id === blockId)
      if (blockIndex !== -1) {
        blockedFriends.value[blockIndex] = response.data
      }
      return { success: true, data: response.data }
    } catch (err: any) {
      error.value = err.message || '解除好友屏蔽失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除屏蔽记录
  const removeBlock = async (blockId: number) => {
    isLoading.value = true
    error.value = ''
    
    try {
      await apiRemoveBlock(blockId)
      // 从本地列表中移除
      blockedFriends.value = blockedFriends.value.filter(block => block.id !== blockId)
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除屏蔽记录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取屏蔽列表
  const getBlockedFriends = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await apiGetBlockedFriends()
      blockedFriends.value = response.data
      return { success: true, data: blockedFriends.value }
    } catch (err: any) {
      error.value = err.message || '获取屏蔽列表失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  

  
  // 初始化好友数据
  const initializeFriends = async () => {
    try {
      await Promise.all([
        getFriends(),
        getFriendRequests(),
        getFriendGroups(),
        getBlockedFriends()
      ])
      if (!friendsWebSocketConnection) {
        friendsWebSocketConnection = setupWebSocketConnection()
      }
      return { success: true }
    } catch (err) {
      return { success: false }
    }
  }
  
  // 清除错误信息
  const clearError = () => {
    error.value = ''
  }

  onUnmounted(() => {
    if (friendsWebSocketConnection) {
      friendsWebSocketConnection.disconnect()
      friendsWebSocketConnection = null
    }
  })
  
  return {
    // 状态
    friends,
    friendRequests,
    friendGroups,
    blockedFriends,
    friendNicknames,
    groupMemberships,
    isLoading,
    error,
    unreadFriendMessagesCount,
    
    // 计算属性
    pendingFriendRequests,
    acceptedFriendRequests,
    rejectedFriendRequests,
    friendsWithGroups,
    hasUnreadFriendMessages,
    
    // 方法
    getFriends,
    getFriendRequests,
    sendFriendRequest,
    acceptFriendRequest,
    rejectFriendRequest,
    removeFriend,
    getFriendGroups,
    createFriendGroup,
    updateFriendGroup,
    removeFriendGroup,
    addFriendToGroup,
    removeFriendFromGroup,
    setFriendNickname,
    blockFriend,
    unblockFriend,
    removeBlock,
    getBlockedFriends,
    initializeFriends,
    clearError,
    resetUnreadFriendMessages,
    incrementUnreadFriendMessages
  }
})