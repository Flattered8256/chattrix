from django.db import models
from django.conf import settings
from apps.accounts.models import User
from apps.friends.models import Friend
import random

class ChatRoom(models.Model):
    """
    聊天房间基类
    遵循单一职责原则，仅负责聊天房间的基本信息
    """
    id = models.BigIntegerField(primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        """生成10位数的ID"""
        if not self.id:
            while True:
                new_id = random.randint(1000000000, 9999999999)
                if not self.__class__.objects.filter(id=new_id).exists():
                    self.id = new_id
                    break
        super().save(*args, **kwargs)

class PrivateChatRoom(ChatRoom):
    """
    私聊房间
    遵循单一职责原则，专门处理私聊功能
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_rooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_rooms_as_user2')

    class Meta:
        verbose_name = '私聊房间'
        verbose_name_plural = '私聊房间'
        unique_together = ('user1', 'user2')
        constraints = [
            models.CheckConstraint(check=~models.Q(user1=models.F('user2')),
                                  name='no_self_private_chat')
        ]

    def __str__(self):
        return f'Private Chat: {self.user1.username} <-> {self.user2.username}'
        
    def get_other_user(self, current_user):
        """
        获取私聊中的另一方用户
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            User: 聊天对象用户
        """
        if current_user == self.user1:
            return self.user2
        elif current_user == self.user2:
            return self.user1
        else:
            # 用户不在这个聊天房间中
            return None

    def get_chat_display_info(self, current_user):
        """
        获取聊天展示信息（对方的名字和头像）
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            dict: 包含对方名字和头像的字典
        """
        other_user = self.get_other_user(current_user)
        if other_user:
            # 检查是否有好友备注
            try:
                from apps.friends.models import FriendNickname
                friend_relationship = Friend.objects.get(owner=current_user, friend=other_user)
                nickname_obj = FriendNickname.objects.get(friend=friend_relationship)
                display_name = nickname_obj.nickname if nickname_obj.nickname else other_user.username
            except (Friend.DoesNotExist, FriendNickname.DoesNotExist):
                display_name = other_user.username
                
            return {
                'id': other_user.id,
                'name': display_name,
                'avatar': other_user.user_avatar.url if other_user.user_avatar else None,
            }
        return None
    
class GroupChatRoom(ChatRoom):
    """
    群聊房间
    遵循单一职责原则，专门处理群聊功能
    """ 
    name = models.CharField(max_length=255, verbose_name='群聊名称')
    avatar = models.ImageField(upload_to='group_avatars/', verbose_name='群聊头像', blank=True, null=True)
    description = models.TextField(verbose_name='群聊描述', blank=True, null=True)
    admin = models.ManyToManyField(User, related_name='admin_groups', verbose_name='群聊管理员')
    members = models.ManyToManyField(User, related_name='group_rooms', verbose_name='群聊成员')



    class Meta:
        verbose_name = '群聊房间'
        verbose_name_plural = '群聊房间'

    def is_member(self, user):
        """检查用户是否是群成员"""
        return self.members.filter(id=user.id).exists()
    
    def is_admin(self, user):
        """检查用户是否是群管理员"""
        return self.admin.filter(id=user.id).exists()

    def get_member_count(self):
        """获取群成员数量"""
        return self.members.count()
    
    def add_member(self, user):
        """添加成员到群聊"""
        if not self.is_member(user):
            self.members.add(user)
            return True
        return False
    
    def remove_member(self, user):
        """从群聊移除成员"""
        if self.is_member(user):
            # 移除成员时同时移除其管理员权限
            if self.is_admin(user):
                self.admin.remove(user)
            self.members.remove(user)
            return True
        return False
    def add_admin(self, user):
        """添加管理员到群聊"""
        if self.is_member(user):
            self.admin.add(user)
            self.save()
            return True
        return False

    
