import { get, post, put, remove, type ApiResponse, createCancelToken } from './https';
import type { User } from './auth';
import { handleApiError } from './error'; // 从error.ts导入

// 定义好友相关的类型
export interface Friend {
  id: number;
  owner: number;
  friend: number;
  created_at: string;
  friend_info: User;
  nickname: string;
}

export interface FriendRequest {
  id: number;
  sender: number;
  receiver: number;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  updated_at: string;
  sender_info: User;
}

export interface FriendGroup {
  id: number;
  owner: number;
  name: string;
  created_at: string;
}

export interface FriendGroupMembership {
  id: number;
  group: number;
  friend: number;
}

export interface FriendNickname {
  id: number;
  friend: number;
  nickname: string;
}

export interface FriendBlock {
  id: number;
  friend: number;
  is_blocked: boolean;
}

// 获取好友列表
export async function getFriends(): Promise<ApiResponse<Friend[]>> {
  try {
    return await get('api/friends/friends/');
  } catch (error) {
    console.error('获取好友列表失败:', error);
    throw handleApiError(error);
  }
}

// 获取单个好友详情
export async function getFriendDetail(friendId: number): Promise<ApiResponse<Friend>> {
  try {
    return await get(`api/friends/friends/${friendId}/`);
  } catch (error) {
    console.error(`获取好友 ${friendId} 详情失败:`, error);
    throw handleApiError(error);
  }
}




// 删除好友
export async function removeFriend(friendId: number): Promise<ApiResponse<null>> {
  try {
    return await remove(`api/friends/friends/${friendId}/`);
  } catch (error) {
    console.error(`删除好友 ${friendId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 获取好友请求列表
export async function getFriendRequests(): Promise<ApiResponse<FriendRequest[]>> {
  try {
    return await get('api/friends/requests/');
  } catch (error) {
    console.error('获取好友请求列表失败:', error);
    throw handleApiError(error);
  }
}

// 发送好友请求
export async function sendFriendRequest(receiverId: number): Promise<ApiResponse<FriendRequest>> {
  try {
    return await post('api/friends/requests/', { receiver: receiverId });
  } catch (error) {
    console.error(`发送好友请求给用户 ${receiverId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 接受好友请求
export async function acceptFriendRequest(requestId: number): Promise<ApiResponse<null>> {
  try {
    return await post(`api/friends/requests/${requestId}/accept/`);
  } catch (error) {
    console.error(`接受好友请求 ${requestId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 拒绝好友请求
export async function rejectFriendRequest(requestId: number): Promise<ApiResponse<null>> {
  try {
    return await post(`api/friends/requests/${requestId}/reject/`);
  } catch (error) {
    console.error(`拒绝好友请求 ${requestId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 获取好友分组列表
export async function getFriendGroups(): Promise<ApiResponse<FriendGroup[]>> {
  try {
    return await get('api/friends/groups/');
  } catch (error) {
    console.error('获取好友分组列表失败:', error);
    throw handleApiError(error);
  }
}

// 创建好友分组
export async function createFriendGroup(name: string): Promise<ApiResponse<FriendGroup>> {
  try {
    return await post('api/friends/groups/', { name });
  } catch (error) {
    console.error(`创建好友分组 "${name}" 失败:`, error);
    throw handleApiError(error);
  }
}

// 更新好友分组
export async function updateFriendGroup(groupId: number, name: string): Promise<ApiResponse<FriendGroup>> {
  try {
    return await put(`api/friends/groups/${groupId}/`, { name });
  } catch (error) {
    console.error(`更新好友分组 ${groupId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 删除好友分组
export async function removeFriendGroup(groupId: number): Promise<ApiResponse<null>> {
  try {
    return await remove(`api/friends/groups/${groupId}/`);
  } catch (error) {
    console.error(`删除好友分组 ${groupId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 获取分组中的成员
export async function getGroupMembers(groupId: number): Promise<ApiResponse<FriendGroupMembership[]>> {
  try {
    return await get(`api/friends/groups/${groupId}/members/`);
  } catch (error) {
    console.error(`获取分组 ${groupId} 成员失败:`, error);
    throw handleApiError(error);
  }
}

// 添加好友到分组
export async function addFriendToGroup(groupId: number, friendId: number): Promise<ApiResponse<FriendGroupMembership>> {
  try {
    return await post('api/friends/group-memberships/', { group: groupId, friend: friendId });
  } catch (error) {
    console.error(`添加好友 ${friendId} 到分组 ${groupId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 从分组中移除好友
export async function removeFriendFromGroup(membershipId: number): Promise<ApiResponse<null>> {
  try {
    return await remove(`api/friends/group-memberships/${membershipId}/`);
  } catch (error) {
    console.error(`从分组中移除好友关系 ${membershipId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 设置好友备注
export async function setFriendNickname(friendId: number, nickname: string): Promise<ApiResponse<FriendNickname>> {
  try {
    return await post('api/friends/nicknames/', { friend: friendId, nickname });
  } catch (error) {
    console.error(`设置好友 ${friendId} 备注失败:`, error);
    throw handleApiError(error);
  }
}


// 屏蔽好友
export async function blockFriend(friendId: number): Promise<ApiResponse<FriendBlock>> {
  try {
    return await post('api/friends/blocks/', { friend: friendId, is_blocked: true });
  } catch (error) {
    console.error(`屏蔽好友 ${friendId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 解除好友屏蔽
export async function unblockFriend(blockId: number): Promise<ApiResponse<FriendBlock>> {
  try {
    return await put(`api/friends/blocks/${blockId}/`, { is_blocked: false });
  } catch (error) {
    console.error(`解除好友屏蔽 ${blockId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 删除屏蔽记录
export async function removeBlock(blockId: number): Promise<ApiResponse<null>> {
  try {
    return await remove(`api/friends/blocks/${blockId}/`);
  } catch (error) {
    console.error(`删除屏蔽记录 ${blockId} 失败:`, error);
    throw handleApiError(error);
  }
}

// 新增功能：获取屏蔽列表
export async function getBlockedFriends(): Promise<ApiResponse<FriendBlock[]>> {
  try {
    return await get('api/friends/blocks/');
  } catch (error) {
    console.error('获取屏蔽列表失败:', error);
    throw handleApiError(error);
  }
}


// 导出取消请求的工具函数
export { createCancelToken };
