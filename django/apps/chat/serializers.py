from rest_framework import serializers
from .models import PrivateChatRoom,GroupChatRoom
from apps.accounts.serializers import UserSerializer

class PrivateChatRoomSerializer(serializers.ModelSerializer):
    """
    私聊房间序列化器
    遵循单一职责原则，专门处理私聊房间的序列化
    """
    user1 = UserSerializer()
    user2 = UserSerializer()
    other_user_info = serializers.SerializerMethodField()
    class Meta:
        model = PrivateChatRoom
        fields = ['id', 'created_at', 'updated_at', 'user1', 'user2', 'other_user_info']
        read_only_fields = ['id', 'created_at', 'updated_at', 'other_user_info']
        
    def get_other_user_info(self, obj):
        """
        获取当前用户的对方用户信息
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user
            return obj.get_chat_display_info(current_user)
        return None

class GroupChatRoomSerializer(serializers.ModelSerializer):
    """
    群聊房间序列化器
    遵循单一职责原则，专门处理群聊房间的序列化
    """
    admin = UserSerializer(many=True)
    members = UserSerializer(many=True)
    class Meta:
        model = GroupChatRoom
        fields = ['id','name','avatar','description', 'admin', 'members', 'created_at']
        read_only_fields = ['id', 'created_at' ]

