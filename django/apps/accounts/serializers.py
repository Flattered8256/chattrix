from __future__ import annotations
from jsonschema import ValidationError
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=False,
        required=False,
        validators=[]
    )
    user_status = serializers.CharField(   # 根据实际类型调整
        read_only=False,
        required=False,
        validators=[]
    )

    class Meta:
        model = User
        fields = ["id", "username", "user_avatar", "user_status"]

    def validate_id(self, value):
        if value is not None:
            raise serializers.ValidationError("id 不可修改。")
        return value

    def validate_user_status(self, value):
        # 只要客户端尝试传 user_status，就抛 400
        if value is not None:
            raise serializers.ValidationError("user_status 不可修改。")
        return value
           

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):

        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    """登录序列化器"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSearchSerializer(serializers.Serializer):
    """搜索用户序列化器"""
    
    id = serializers.IntegerField()
    
    def validate_id(self, value):
      
        if len(str(value)) != 10:
            raise serializers.ValidationError("UID must be a 10-digit number.")
        return value
    
class ChangePasswordSerializer(serializers.Serializer):
    """
    密码更改序列化器
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("新密码和确认密码不匹配")
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError("新密码不能与旧密码相同")
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user