from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Friend
from apps.chat.models import PrivateChatRoom

@receiver(post_save, sender=Friend)
def create_private_chatroom(sender, instance, created, **kwargs):
    """
    当好友关系创建时，自动创建私聊房间
    """
    if created:
        # 确保双向好友关系都存在时才创建聊天室
        if Friend.objects.filter(owner=instance.friend, friend=instance.owner).exists():
            # 创建私聊房间，确保不会重复创建
            try:
                PrivateChatRoom.objects.get_or_create(
                    user1=instance.owner,
                    user2=instance.friend
                )
            except Exception:
                # 如果创建失败，可能是唯一约束冲突，忽略错误
                pass

@receiver(post_delete, sender=Friend)
def delete_private_chatroom(sender, instance, **kwargs):
    """
    当好友关系删除时，自动删除私聊房间
    """
    try:
        # 查找并删除对应的私聊房间
        chat_room = PrivateChatRoom.objects.filter(
            user1__in=[instance.owner, instance.friend],
            user2__in=[instance.owner, instance.friend]
        ).first()
        
        if chat_room:
            chat_room.delete()
    except PrivateChatRoom.DoesNotExist:
        pass