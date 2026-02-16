from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器 - 用于展示用户列表基本信息
    """
    class Meta:
        model = User
        fields = ["id", "username", "user_avatar", "date_joined"]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {
            'user_avatar': {'required': False}
        }


