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

    async def connect(self):
        await super().connect()
        
        # 连接成功后立即同步未读消息
        await self.sync_unread_messages()
    
    async def sync_unread_messages(self):
            """同步未读消息"""
            from asgiref.sync import sync_to_async
            
            room_id = self.scope['url_route']['kwargs']['room_id']
            user = self.user
            
            # 异步执行数据库查询
            unread_messages = await sync_to_async(self.get_unread_messages)(room_id, user)
            
            if unread_messages:
                # 发送未读消息给客户端，使用与信号文件相同的格式
                for message_data in unread_messages:
                    # 构造与信号文件完全相同的消息格式
                    event = {
                        'type': 'chat_message',
                        **message_data
                    }
                    await self.send(text_data=json.dumps(event))
    
    def get_unread_messages(self, room_id, user):
        """获取未读消息（同步方法）"""
        from apps.messages.models import Message, IsRead
        try:
            # 获取最后已读消息ID
            last_read = IsRead.objects.filter(
                room_id=room_id, 
                receiver=user
            ).first()
            
            last_read_id = last_read.message.id if last_read else 0
            
            # 获取未读消息（排除自己发送的）
            unread_messages = Message.objects.filter(
                room_id=room_id,
                id__gt=last_read_id
            ).exclude(sender=user).order_by('timestamp')
            
            # 使用序列化器
            from apps.messages.serializers import MessageSerializer
            serializer = MessageSerializer(unread_messages, many=True)
            return serializer.data
            
        except Exception as e:
            print(f"Error fetching unread messages: {e}")
            return []