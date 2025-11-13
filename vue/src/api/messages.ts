import { get, post,uploadFile, type ApiResponse } from './https';
import { handleApiError } from './error';
import type { User } from './auth';


export interface Message {
  id: number;
  sender?: User;
  timestamp: string;
  is_read?: boolean; // 可选的是否已读状态，默认值为false
  room_type: string; // 更新为与后端一致
  room_id: number; // 更新为与后端一致
  content?: string; // 可选的内容属性，确保所有消息类型都能访问
  messages_type: 'text' | 'image' | 'video' | 'file';
  filename?: string; // 可选的文件名，用于文件消息
}



// 发送消息请求参数接口
export interface SendMessageRequest {
  messages_type: 'text' | 'image' | 'video' | 'file';
  content?: string; // 文本消息内容
  file?: File; // 用于文件上传的字段
  room_type?: string; // 房间类型，默认私聊
}

export interface PaginatedApiResponse<T = any> extends ApiResponse<T> {
  'pagination-next'?: string;
}

// 发送消息，只需要传入type、room_type、room_id  以及可选的content或file
export async function sendMessage(
  roomId: number,
  request: SendMessageRequest
): Promise<ApiResponse<Message>> {
  try {
    // 根据消息类型构建请求数据
    const formData = new FormData();
    formData.append('messages_type', request.messages_type);
    // 从请求参数中获取room_type，而不是硬编码
    formData.append('room_type', request.room_type || 'private'); // 添加默认值作为后备
    formData.append('room_id', roomId.toString()); // 添加room_id
    
    if (request.content) {
      formData.append('content', request.content);
    }
    
    if (request.file) {
      // 统一使用'file'字段，与后端MessageSerializer的验证逻辑保持一致
      formData.append('file', request.file);
      // 添加filename字段
      formData.append('filename', request.file.name);
      return await uploadFile<Message>(`api/messages/${roomId}/`, formData);
    }
    
    return await post(`api/messages/${roomId}/`, formData);
  } catch (error) {
    throw handleApiError(error);
  }
}

// 获取房间消息

export async function getRoomMessages(
  roomId: number
): Promise<PaginatedApiResponse<Message[]>> {
  try {
    return await get(`api/messages/${roomId}/`);
  } catch (error) {
    throw handleApiError(error);
  }
}

// 标记消息为已读
export async function markMessageAsRead(
  roomId: number,
  messageId: number
): Promise<ApiResponse<any>> {
  try {
    return await post(`api/messages/${roomId}/${messageId}/is_read/`);
  } catch (error) {
    throw handleApiError(error);
  }
}

// 获取未读消息计数
export async function getUnreadMessageCount(
  roomId: number
): Promise<ApiResponse<{ unread_count: number }>> {
  try {
    return await get(`api/messages/${roomId}/unread_count/`);
  } catch (error) {
    throw handleApiError(error);
  }
}