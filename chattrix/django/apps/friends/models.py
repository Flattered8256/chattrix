from django.db import models
from ..accounts.models import User 
# Create your models here.

class Friend(models.Model):
    """
    只负责“谁是谁的好友”这一事实。
    一条记录 = 单向好友关系。
    """
    owner  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('owner', 'friend'), name='unique_friend'),
            models.CheckConstraint(check=~models.Q(owner=models.F('friend')),
                                   name='no_self_friend')
        ]
        verbose_name = '好友关系'
        verbose_name_plural = '好友关系'

    def __str__(self):
        return f'{self.owner} -> {self.friend}'

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        constraints = [
            models.CheckConstraint(check=~models.Q(sender=models.F('receiver')),
                                   name='no_self_request')
        ]
        verbose_name = '好友申请'
        verbose_name_plural = '好友申请'

    def __str__(self):
        return f'{self.sender} -> {self.receiver} [{self.status}]'

class FriendNickname(models.Model):
    """
    只负责“某个好友在某人视角下的备注名”。
    """
    friend = models.OneToOneField(
        Friend,
        on_delete=models.CASCADE,
        related_name='nickname_obj'
    )
    nickname = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = '好友备注'
        verbose_name_plural = '好友备注'

    def __str__(self):
        return self.nickname or '- no nickname -'


class FriendGroup(models.Model):
    """
    好友分组，用于对好友进行分类管理。
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_groups'
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'name')
        verbose_name = '好友分组'
        verbose_name_plural = '好友分组'

    def __str__(self):
        return self.name


class FriendBlock(models.Model):
    """
    只负责“某个好友在某人视角下是否被屏蔽”。
    """
    friend = models.OneToOneField(
        Friend,
        on_delete=models.CASCADE,
        related_name='block_obj'
    )
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = '好友屏蔽'
        verbose_name_plural = '好友屏蔽'

    def __str__(self):
        return 'blocked' if self.is_blocked else 'not blocked'
    
class FriendGroupMembership(models.Model):
    group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE)
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'friend')