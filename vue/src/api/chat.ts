import { get, post, type ApiResponse } from './https';
import { handleApiError } from './error';
import type { User } from './auth';

// 聊天房间类型定义
export interface ChatRoom {
  id: number;
  created_at: string;
  updated_at: string;
}

// 私聊房间类型定义
export interface PrivateChatRoom extends ChatRoom {
  user1: User;
  user2: User;
  other_user_info: ChatUserInfo;
}

// 聊天用户信息类型
export interface ChatUserInfo {
  id: number;
  name: string;
  avatar: string;
}
// 创建私聊房间请求参数类型
export interface CreatePrivateChatRoomRequest {
  user2_id: number;
}


// 群聊房间类型定义
export interface GroupChatRoom extends ChatRoom {
  name: string;
  avatar: string | null;
  description: string | null;
  admin: User[];
  members: User[];
}

// 创建群聊房间请求参数类型
export interface CreateGroupChatRoomRequest {
  name: string;
  description?: string;
  member_ids: number[];
}

// 创建私聊房间
export async function createPrivateChatRoom(
  request: CreatePrivateChatRoomRequest
): Promise<ApiResponse<PrivateChatRoom>> {
  try {
    return await post('api/chat/private-rooms/', request);
  } catch (error) {
    throw handleApiError(error);
  }
}

// 获取当前用户的所有私聊房间
export async function getPrivateChatRooms():
  Promise<ApiResponse<PrivateChatRoom[]>> {
  try {
    return await get('api/chat/private-rooms/');
  } catch (error) {
    throw handleApiError(error);
  }
}

// 创建群聊房间
export async function createGroupChatRoom(
  request: CreateGroupChatRoomRequest
): Promise<ApiResponse<GroupChatRoom>> {
  try {
    return await post('api/chat/group-rooms/', request);
  } catch (error) {
    throw handleApiError(error);
  }
}

// 获取当前用户的所有群聊房间
export async function getGroupChatRooms():
  Promise<ApiResponse<GroupChatRoom[]>> {
  try {
    return await get('api/chat/group-rooms/');
  } catch (error) {
    throw handleApiError(error);
  }
}



