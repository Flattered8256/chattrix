import { ref, onUnmounted, type Ref } from 'vue';
import { getStoredToken } from './https';

// WebSocket消息类型定义
export interface WebSocketMessage {
  type: string;
  id: number;
  timestamp: string;
  room_type: string;
  room_id: number;
  messages_type: 'text' | 'image' | 'video' | 'file';
  [key: string]: any;
}

// WebSocket连接状态类型
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// WebSocket事件处理函数类型
export interface WebSocketHandlers {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
}

// WebSocket管理器基类
class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: WebSocketHandlers;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private reconnectTimer: number | null = null;
  private isManualDisconnect = false;
  private pingInterval: number | null = null;
  private pingTimeout: number | null = null;
  private readonly pingIntervalTime = 30000; // 30秒
  private readonly pingTimeoutTime = 10000; // 10秒

  // 连接状态
  public status: Ref<ConnectionStatus> = ref('disconnected');

  constructor(url: string, handlers: WebSocketHandlers = {}) {
    this.url = url;
    this.handlers = handlers;
  }

  // 连接WebSocket
  public connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    this.isManualDisconnect = false;
    this.status.value = 'connecting';

    try {
      const token = getStoredToken();
      // 在WebSocket URL中添加token参数进行认证
      const wsUrl = this.url + (this.url.includes('?') ? '&' : '?') + `token=${token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => this.handleOpen();
      this.ws.onclose = (event) => this.handleClose(event);
      this.ws.onerror = (error) => this.handleError(error);
      this.ws.onmessage = (event) => this.handleMessage(event);
    } catch (error) {
      console.error('WebSocket连接错误:', error);
      this.status.value = 'error';
    }
  }

  // 断开WebSocket连接
  public disconnect(): void {
    this.isManualDisconnect = true;
    this.cleanup();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.status.value = 'disconnected';
    if (this.handlers.onDisconnect) {
      this.handlers.onDisconnect();
    }
  }

  // 发送消息
  public send(data: any): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送消息');
      return false;
    }

    try {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('WebSocket发送消息失败:', error);
      return false;
    }
  }

  // 处理连接打开
  private handleOpen(): void {
    this.status.value = 'connected';
    this.reconnectAttempts = 0;
    
    // 启动心跳机制
    this.startHeartbeat();
    
    if (this.handlers.onConnect) {
      this.handlers.onConnect();
    }
  }

  // 处理连接关闭
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket连接已关闭:', this.url, 'code:', event.code, 'reason:', event.reason);
    
    // 清理心跳定时器
    this.cleanup();
    
    this.ws = null;
    this.status.value = 'disconnected';
    
    // 如果不是手动断开连接，则尝试重连
    if (!this.isManualDisconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnect();
    } else if (this.isManualDisconnect && this.handlers.onDisconnect) {
      this.handlers.onDisconnect();
    }
  }

  // 处理错误
  private handleError(error: Event): void {
    console.error('WebSocket错误:', this.url, error);
    this.status.value = 'error';
    if (this.handlers.onError) {
      this.handlers.onError(error);
    }
  }

  // 处理消息
 private handleMessage(event: MessageEvent): void {
    try {
      // 处理其他JSON格式的消息
      const data = JSON.parse(event.data);
      
      // 如果是JSON格式的pong消息
      if (data.type === 'pong') {
        // 清除心跳超时定时器
        if (this.pingTimeout) {
          clearTimeout(this.pingTimeout);
          this.pingTimeout = null;
        }
        return;
      }
      
      // 非心跳消息，传递给用户定义的处理函数
      if (this.handlers.onMessage) {
        this.handlers.onMessage(data);
      }
    } catch (error) {
      console.error('WebSocket消息解析错误:', error);
    }
  }

  // 重连机制
  private reconnect(): void {
    this.reconnectAttempts++;
    console.log(`WebSocket重连尝试 #${this.reconnectAttempts}...`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  // 心跳机制
 private startHeartbeat(): void {
    // 清除可能存在的定时器
    this.cleanup();
    
    // 定时发送ping消息
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // 发送JSON格式的ping消息
        this.send({type: "ping"});
        
        // 设置超时检查
        this.pingTimeout = setTimeout(() => {
          console.error('WebSocket心跳超时，关闭连接');
          if (this.ws) {
            this.ws.close();
          }
        }, this.pingTimeoutTime);
      }
    }, this.pingIntervalTime);
  }

  // 清理定时器
  private cleanup(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    if (this.pingTimeout) {
      clearTimeout(this.pingTimeout);
      this.pingTimeout = null;
    }
  }

  // 销毁资源
  public destroy(): void {
    this.disconnect();
  }
}

// WebSocket服务类，管理所有WebSocket连接
export class WebSocketService {
  private static instance: WebSocketService;
  private chatConnections: Map<number, WebSocketManager> = new Map();
  private friendsConnection: WebSocketManager | null = null;
  private notificationsConnection: WebSocketManager | null = null;
 

 
  // 单例模式获取实例
  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  // 获取WebSocket URL
  private getWsUrl(endpoint: string): string {
    // 将HTTP URL转换为WebSocket URL
    return endpoint;
  }

  // 创建或获取聊天室WebSocket连接
  public getChatConnection(roomId: number, handlers: WebSocketHandlers = {}): WebSocketManager {
    if (!this.chatConnections.has(roomId)) {
      const url = this.getWsUrl(`ws/chat/${roomId}/`);
      const connection = new WebSocketManager(url, handlers);
      this.chatConnections.set(roomId, connection);
    }
    return this.chatConnections.get(roomId)!;
  }

  // 创建或获取好友通知WebSocket连接
  public getFriendsConnection(handlers: WebSocketHandlers = {}): WebSocketManager {
    if (!this.friendsConnection) {
      const url = this.getWsUrl('ws/friends/');
      this.friendsConnection = new WebSocketManager(url, handlers);
    }
    return this.friendsConnection;
  }

  // 创建或获取系统通知WebSocket连接
  public getNotificationsConnection(handlers: WebSocketHandlers = {}): WebSocketManager {
    if (!this.notificationsConnection) {
      const url = this.getWsUrl('ws/notifications/');
      this.notificationsConnection = new WebSocketManager(url, handlers);
    }
    return this.notificationsConnection;
  }

  // 关闭并移除聊天室连接
  public closeChatConnection(roomId: number): void {
    const connection = this.chatConnections.get(roomId);
    if (connection) {
      connection.destroy();
      this.chatConnections.delete(roomId);
    }
  }

  // 关闭好友通知连接
  public closeFriendsConnection(): void {
    if (this.friendsConnection) {
      this.friendsConnection.destroy();
      this.friendsConnection = null;
    }
  }

  // 关闭系统通知连接
  public closeNotificationsConnection(): void {
    if (this.notificationsConnection) {
      this.notificationsConnection.destroy();
      this.notificationsConnection = null;
    }
  }

  // 关闭所有连接
  public closeAllConnections(): void {
    // 关闭所有聊天室连接
    this.chatConnections.forEach((connection) => {
      connection.destroy();
    });
    this.chatConnections.clear();

    // 关闭好友通知连接
    this.closeFriendsConnection();

    // 关闭系统通知连接
    this.closeNotificationsConnection();
  }

  // 重新连接所有连接
  public reconnectAllConnections(): void {
    // 重新连接所有聊天室连接
    this.chatConnections.forEach((connection) => {
      connection.connect();
    });

    // 重新连接好友通知连接
    if (this.friendsConnection) {
      this.friendsConnection.connect();
    }

    // 重新连接系统通知连接
    if (this.notificationsConnection) {
      this.notificationsConnection.connect();
    }
  }
}

// 导出单例实例
export const wsService = WebSocketService.getInstance();

// 提供Vue组件中使用的组合式函数
export function useWebSocket() {
  // 在组件卸载时关闭所有连接
  onUnmounted(() => {
    // 注意：通常不应该在组件卸载时关闭所有连接，而是在应用退出登录时
    // 这里可以根据实际需求调整
  });

  return {
    wsService,
    WebSocketManager
  };
}