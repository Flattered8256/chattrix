from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserListSerializer
from apps.accounts.serializers import UserLoginSerializer, UserSerializer
from .permissions import SuperAdminOnly

User = get_user_model()

class LoginView(APIView):
 
    serializer_class = UserLoginSerializer  
    
    def post(self, request) -> Response:
     
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                # 检查用户是否为超级管理员
                if not user.is_superuser:
                    return Response({
                        "code": 403,
                        "message": "权限不足，仅超级管理员可登录",
                        "data": None
                    }, status=status.HTTP_403_FORBIDDEN)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "code": 200,
                    "message": "Login successful",
                    "data": {
                        "user": UserSerializer(user).data,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                })
            elif user is None:
                return Response({
                    "code": 401,
                    "message": "用户不存在",
                    "data": None
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            "code": 400,
            "message": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data,partial=partial)
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
    

