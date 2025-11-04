from rest_framework import serializers
from .models import  Message
from apps.accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    """
    消息序列化器
    """
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
                'id', 'sender', 'timestamp', 
                'room_type', 'room_id','messages_type',
                'content', 'file', 'filename'
                ]
        read_only_fields = ['id', 'sender', 'timestamp']

    def validate(self, data):
        """验证消息类型与内容的匹配"""
        messages_type = data.get('messages_type', 'text')
        
        if messages_type == 'text' and not data.get('content'):
            raise serializers.ValidationError("文本消息必须提供内容")
        elif messages_type in ['image', 'video', 'file'] and not data.get('file'):
            raise serializers.ValidationError(f"{messages_type}消息必须提供文件")
        
        return data


