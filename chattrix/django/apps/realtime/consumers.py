import json
from abc import ABC, abstractmethod
from channels.generic.websocket import AsyncWebsocketConsumer


class BaseConsumer(AsyncWebsocketConsumer, ABC):
    """
    WebSocket消费者基类
    遵循SOLID原则中的单一职责原则和里氏替换原则
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.group_name = None
    
    async def connect(self):
        """
        处理WebSocket连接请求
        """
        self.user = self.scope['user']
        
        # 验证用户是否已认证
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
            
        # 设置组名
        self.group_name = await self.get_group_name()
        
        # 加入组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self,close_code):
        """
        处理WebSocket断开连接
        """
        # 离开组
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    async def receive(self, text_data):
        """
        接收客户端发送的消息，默认处理心跳机制
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # 处理心跳 ping 消息
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
                return
        except json.JSONDecodeError:
            pass
       
        # 如果不是心跳消息，则调用子类的处理方法
        await self.handle_receive(text_data)
    
    async def handle_receive(self, text_data):
        """
        子类重写此方法处理非心跳消息
        """
        pass
    
    @abstractmethod
    async def get_group_name(self):
        """
        抽象方法：获取组名
        遵循依赖倒置原则
        @abstractmethod 装饰器表明这是一个抽象方法，
        任何继承 BaseConsumer 的子类都必须实现这个方法
        """
        pass


class FriendNotificationConsumer(BaseConsumer):
    """
    好友通知WebSocket消费者
    处理好友请求、接受等相关通知
    遵循单一职责原则
    """
    
    async def get_group_name(self):
        """
        获取好友通知组名
        """
        return f'friends_{self.user.id}'
    
    async def friend_request(self, event):
        """
        处理好友请求通知事件
        """
        await self.send(text_data=json.dumps({
            'type': 'friend_request',
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message': event['message'],
        }))

    async def friend_accepted(self, event):
        """
        处理好友请求接受通知事件
        """
        await self.send(text_data=json.dumps({
            'type': 'friend_accepted',
            'friend_id': event['friend_id'],
            'friend_username': event['friend_username'],
        }))


class SystemNotificationConsumer(BaseConsumer):
    """
    系统通知WebSocket消费者
    处理系统级通知
    遵循单一职责原则
    """
    
    async def get_group_name(self):
        """
        获取系统通知组名
        """
        return f'notifications_{self.user.id}'
    
    async def system_notification(self, event):
        """
        处理系统通知事件
        """
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'user_id': event['user_id'],
            'title': event['title'],
            'message': event['message'],
            'level': event['level'],
        }))


class ChatConsumer(BaseConsumer):
    """
    聊天室WebSocket消费者
    处理聊天室中的实时消息
    遵循单一职责原则
    """
    
    async def get_group_name(self):
        """
        获取聊天室组名
        """
        room_id = self.scope['url_route']['kwargs']['room_id']
        return f'chat_{room_id}'
        
    async def chat_message(self, event):
        """
        处理聊天消息事件
        """
        # 准备基础响应数据

        await self.send(text_data=json.dumps(event))
        print(f"Sending message to user {self.user.id}")