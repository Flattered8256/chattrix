from django.db import models
from apps.accounts.models import User
# Create your models here.
class Message(models.Model):
    """
    遵循单一职责原则，仅负责消息的基本信息
    """
    MESSAGE_TYPES = (
        ('text', '文本'),
        ('image', '图片'), 
        ('video', '视频'),
        ('file', '文件'),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    room_type = models.CharField(max_length=20)  # "private", "group" 等
    room_id = models.BigIntegerField()  # 房间的ID

    messages_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    content = models.TextField(null=True, blank=True, verbose_name='内容')
    file = models.FileField(upload_to='chat/files/', null=True, blank=True, verbose_name='文件')
    filename = models.CharField(max_length=255, null=True, blank=True, verbose_name='文件名')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.messages_type} message from {self.sender.username}'
    
class IsRead(models.Model):
    """
    遵循单一职责原则，仅负责记录消息是否已读
    """
    room_id = models.BigIntegerField()  # 房间的ID
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='消息')
    receiver= models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='接受者')

    class Meta:
        
        unique_together = ['room_id', 'receiver']

    def __str__(self):
        return f'{self.receiver.username} read {self.message.id}'
