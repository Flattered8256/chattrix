from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets,permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate 
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.accounts.serializers import ChangePasswordSerializer, UserLoginSerializer, UserRegistrationSerializer, UserSearchSerializer, UserSerializer


# Create your views here.
class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer  
    permission_classes = [permissions.AllowAny]# 允许未登录用户注册
    http_method_names = ['post']

class LoginView(APIView):
 
    serializer_class = UserLoginSerializer  
    
    def post(self, request) -> Response:
     
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
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

class RefreshView(APIView):
   
    permission_classes = []  # 移除 IsAuthenticated 权限限制
    serializer_class = None  
    
    def post(self, request) -> Response:
        # 从请求数据中获取 refresh token
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                "code": 400,
                "message": "Refresh token is required",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证并刷新 token
            refresh = RefreshToken(refresh_token)
            return Response({
                "code": 200,
                "message": "Token refreshed successfully",
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            })
        except Exception as e:
            return Response({
                "code": 401,
                "message": "Invalid refresh token",
                "data": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


from rest_framework_simplejwt.views import TokenBlacklistView

class LogoutView(APIView):
    """实现登出功能"""
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request, *args, **kwargs):
        try:
            # 将令牌加入黑名单
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # 返回JSON响应而不是重定向
            return Response({
                "code": 200,
                "message": "Logout successful",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 500,
                "message": "Internal server error",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SearchUserView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserSearchSerializer  # 添加这一行
    
    def get(self, request) -> Response:

        serializer = UserSearchSerializer(data=request.GET)
        if serializer.is_valid():
            id = serializer.validated_data["id"]
            try:
                user = User.objects.get(id=id)
                return Response({
                    "code": 200,
                    "message": "User found",
                    "data": UserSerializer(user).data
                })
            except User.DoesNotExist:
                return Response({
                    "code": 404,
                    "message": "User not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "code": 400,
            "message": "Invalid UID",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
# 当前代码缺少关键配置

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer  
    
    def patch(self, request) -> Response:
   
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        return Response({
            "code": 400,
            "message": "Validation error",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class User_get_ProfileView(APIView):
    """获取用户个人资料"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get(self, request) -> Response:
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            "code": 200,
            "message": "Profile retrieved successfully",
            "data": serializer.data
        })


class ChangePasswordView(APIView):
    """
    密码更改视图
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "密码更改成功",
                "data": None
            })
        return Response({
            "code": 400,
            "message": "密码更改失败",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)