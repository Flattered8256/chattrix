# apps/friends/serializers.py

from rest_framework import serializers
from .models import Friend, FriendRequest, FriendNickname, FriendGroup, FriendBlock, FriendGroupMembership
from django.conf import settings

class FriendSerializer(serializers.ModelSerializer):
    """
    好友序列化器
    """
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    friend_info = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = Friend
        fields = ['id', 'owner', 'friend', 'created_at', 'friend_info', 'nickname']

    def get_friend_info(self, obj):
        from apps.accounts.serializers import UserSerializer
        return UserSerializer(obj.friend).data

    def get_nickname(self, obj):
        try:
            return obj.nickname_obj.nickname
        except FriendNickname.DoesNotExist:
            return None


class FriendRequestSerializer(serializers.ModelSerializer):
    """
        好友请求序列化器
    """
    sender_info = serializers.SerializerMethodField()
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'updated_at','sender_info']
        read_only_fields = ('sender','sender_info')

    def get_sender_info(self, obj):
        from apps.accounts.serializers import UserSerializer
        return UserSerializer(obj.sender).data
    def validate(self, attrs):
        sender = self.context['request'].user
        receiver = attrs.get('receiver')
        
        if sender == receiver:
            raise serializers.ValidationError("不能向自己发送好友请求")
        # 检查接收者是否存在
        if not receiver:
            raise serializers.ValidationError("必须指定接收者")
            
        return attrs

class FriendGroupSerializer(serializers.ModelSerializer):
    """ 好友分组序列化器 """
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = FriendGroup
        fields = ['id', 'owner', 'name', 'created_at']
        
    def validate_name(self, value):
        # 确保名称不为空
        if not value.strip():
            raise serializers.ValidationError("分组名称不能为空")
        return value.strip()


class FriendGroupMembershipSerializer(serializers.ModelSerializer):
    """ 好友分组成员序列化器 """
    class Meta:
        model = FriendGroupMembership
        fields = ['id', 'group', 'friend']
        

    

class FriendNicknameSerializer(serializers.ModelSerializer):
    """ 好友昵称序列化器 """
    class Meta:
        model = FriendNickname
        fields = ['id', 'friend', 'nickname']
        
    def validate_nickname(self, value):
        if value and len(value) > 20:
            raise serializers.ValidationError("备注名不能超过20个字符")
        return value

class FriendBlockSerializer(serializers.ModelSerializer):
    """ 好友屏蔽序列化器 """
    class Meta:
        model = FriendBlock
        fields = ['id', 'friend', 'is_blocked']