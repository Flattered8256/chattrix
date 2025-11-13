from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from apps.chat.models import GroupChatRoom
from apps.friends.models import Friend



@receiver(post_save, sender=User)
def add_user_to_groups(sender, instance, created, **kwargs):
    """
    当新用户创建时，将用户添加到指定的群聊中。
    
    Args:
        sender: 发送信号的模型类
        instance: 创建的用户实例
        created: 是否是新创建的用户
        **kwargs: 其他参数
    """
    if created:
        # 这里使用空列表表示不需要添加到任何群聊
        # 如果需要指定群聊，可以在groups_to_add中添加群聊ID
        groups_to_add = [] #自动拉新用户进入指定群聊
        users_to_add = [] #自动拉新用户成为好友
        # 如果有指定的群聊，则将用户添加进去
        for group_id in groups_to_add:
            try:
                group = GroupChatRoom.objects.get(id=group_id)
                group.add_member(instance)
            except GroupChatRoom.DoesNotExist:
                # 群聊不存在时静默忽略
                pass
                
        for user_id in users_to_add:
            try:
                user = User.objects.get(id=user_id)
                # 创建双向好友关系
                Friend.objects.create(owner=user, friend=instance)
                Friend.objects.create(owner=instance, friend=user)
            except User.DoesNotExist:
                # 用户不存在时静默忽略
                pass