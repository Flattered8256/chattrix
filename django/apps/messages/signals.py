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


