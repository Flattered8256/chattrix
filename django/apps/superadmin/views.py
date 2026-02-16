from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserListSerializer
from .permissions import SuperAdminOnly

User = get_user_model()


class UserViewSet(ModelViewSet):
    """
    用户管理视图集 - 仅超级管理员可访问
    提供用户列表、创建、更新、删除等操作
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [SuperAdminOnly]
    http_method_names = ['get', 'put', 'patch', 'delete']
    
    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "用户列表获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "用户信息更新成功",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "用户删除成功",
            "data": None
        })
    

