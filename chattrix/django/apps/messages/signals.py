from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.realtime.services import RealtimeService
from asgiref.sync import async_to_sync
from ..chat.models import PrivateChatRoom
from .models import Message
from django.core.exceptions import ObjectDoesNotExist
from channels.layers import get_channel_layer
from .serializers import MessageSerializer
# 获取channel layer用于发送实时消息
channel_layer = get_channel_layer()

@receiver(post_save, sender=Message)

def handle_message_saved(instance, created,**kwargs):
    """
    处理消息保存后的逻辑
    当新消息被创建时，通过WebSocket发送实时通知
    """
    if created:  # 仅在创建新消息时触发
        # 根据room_type和room_id获取房间信息
        try:            
            serializer = MessageSerializer(instance)
            event = {
                'type': 'chat_message',
                **serializer.data
            }
            # 发送到聊天室组
            async_to_sync(channel_layer.group_send)(
                            f'chat_{instance.room_id}',
                            event
                        )
        except ObjectDoesNotExist:
            # 用户不存在，忽略消息
            pass


@receiver(post_save, sender=PrivateChatRoom)
def handle_private_chat_room_created(sender, instance, created, **kwargs):
    """
    处理私聊房间创建后的逻辑
    当新的私聊房间被创建时，通过WebSocket发送实时通知给两个用户
    """
    if created:  # 仅在创建新房间时触发
        # 向用户1发送通知
        async_to_sync(RealtimeService.send_system_notification)(
            user_id=instance.user1.id,
            title="新私聊房间",
            message=f"与 {instance.user2.username} 的私聊房间已创建",
            level="info"
        )
        
        # 向用户2发送通知
        async_to_sync(RealtimeService.send_system_notification)(
            user_id=instance.user2.id,
            title="新私聊房间",
            message=f"与 {instance.user1.username} 的私聊房间已创建",
            level="info"
        )