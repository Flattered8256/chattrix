import json
from typing import Any, Dict
from channels.layers import get_channel_layer
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

# 获取channel layer用于发送实时消息
channel_layer = get_channel_layer()


class RealtimeService:
    """
    实时服务类，用于处理应用间解耦的实时消息发送
    遵循低耦合原则，避免直接依赖chat和friends应用的具体实现
    """

    @staticmethod
    async def send_friend_request_notification(sender_id: int, receiver_id: int, message: str = ""):
        """
        发送好友请求通知
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID
            message: 附加消息
        """
        try:
            # 使用Django的apps.get_model动态获取模型，避免直接导入
            User = apps.get_model('accounts', 'User')
            sender = await User.objects.aget(id=sender_id)
            
            # 构造通知事件
            event = {
                'type': 'friend.request',
                'sender_id': sender_id,
                'sender_username': sender.username,
                'message': message,
            }
            
            # 发送到好友通知组
            await channel_layer.group_send(
                f'friends_{receiver_id}',
                event
            )
        except ObjectDoesNotExist:
            # 用户不存在，忽略通知
            pass

    @staticmethod
    async def send_friend_accepted_notification(friend_id: int, user_id: int):
        """
        发送好友请求被接受的通知
        
        Args:
            friend_id: 好友ID
            user_id: 用户ID
        """
        try:
            # 使用Django的apps.get_model动态获取模型，避免直接导入
            User = apps.get_model('accounts', 'User')
            friend = await User.objects.aget(id=friend_id)
            
            # 构造通知事件
            event = {
                'type': 'friend.accepted',
                'friend_id': friend_id,
                'friend_username': friend.username,
            }
            
            # 发送到好友通知组
            await channel_layer.group_send(
                f'friends_{user_id}',
                event
            )
        except ObjectDoesNotExist:
            # 用户不存在，忽略通知
            pass

    @staticmethod
    async def send_system_notification(user_id: int, title: str, message: str, level: str = "info"):
        """
        发送系统通知
        
        Args:
            user_id: 接收通知的用户ID
            title: 通知标题
            message: 通知内容
            level: 通知级别 (info, warning, error)
        """
        event = {
            'type': 'system.notification',
            'user_id': user_id,
            'title': title,
            'message': message,
            'level': level,
        }
        
        # 发送到系统通知组
        await channel_layer.group_send(
            f'notifications_{user_id}',
            event
        )

    @staticmethod
    async def send_chat_message(room_id: int, message: str, sender_id: int, message_type: str = "text", extra_data: dict = None):
        """
        发送聊天室消息
        
        Args:
            room_id: 聊天室ID
            message: 消息内容
            sender_id: 发送者ID
            message_type: 消息类型 (text, image, video, file)
            extra_data: 额外数据，用于传递不同类型消息的特定信息
        """
        try:
            # 使用Django的apps.get_model动态获取模型，避免直接导入
            User = apps.get_model('accounts', 'User')
            sender = await User.objects.aget(id=sender_id)
            
            # 构造消息事件
            event = {
                'type': 'chat.message',
                'message': message,
                'sender': sender.username,
                'sender_id': sender_id,
                'message_type': message_type,
            }
            
            # 如果有额外数据，则添加到事件中
            if extra_data:
                event.update(extra_data)
            
            # 发送到聊天室组
            await channel_layer.group_send(
                f'chat_{room_id}',
                event
            )
        except ObjectDoesNotExist:
            # 用户不存在，忽略消息
            pass

    @staticmethod
    async def send_chat_room_notification(room_id: int, title: str, message: str):
        """
        发送聊天室系统通知
        
        Args:
            room_id: 聊天室ID
            title: 通知标题
            message: 通知内容
        """
        event = {
            'type': 'chat.notification',
            'title': title,
            'message': message,
        }
        
        # 发送到聊天室组
        await channel_layer.group_send(
            f'chat_{room_id}',
            event
        )