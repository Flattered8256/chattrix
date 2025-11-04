from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import  PrivateChatRoom,GroupChatRoom
from .serializers import  PrivateChatRoomSerializer,GroupChatRoomSerializer
from apps.accounts.models import User

class PrivateChatRoomView(APIView):
    """
    处理私聊房间的创建和访问
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PrivateChatRoomSerializer
    
    def post(self, request) -> Response:
        """
        创建私聊房间
        """
        user2_id = request.data.get('user2_id')
        
        if not user2_id:
            return Response({
                "code": 400,
                "message": "缺少用户ID参数",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user2 = User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response({
                "code": 404,
                "message": "用户不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否尝试与自己聊天
        if request.user == user2:
            return Response({
                "code": 400,
                "message": "不能与自己创建聊天",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已经存在聊天房间
        try:
            chat_room = PrivateChatRoom.objects.get(
                user1=request.user,
                user2=user2
            )
        except PrivateChatRoom.DoesNotExist:
            try:
                chat_room = PrivateChatRoom.objects.get(
                    user1=user2,
                    user2=request.user
                )
            except PrivateChatRoom.DoesNotExist:
                # 创建新的聊天房间
                chat_room = PrivateChatRoom.objects.create(
                    user1=request.user,
                    user2=user2
                )
        
        serializer = PrivateChatRoomSerializer(chat_room)
        return Response({
            "code": 200,
            "message": "聊天房间创建成功",
            "data": serializer.data
        })
    
    def get(self, request) -> Response:
        """
        获取当前用户的所有私聊房间
        """
        # 获取用户作为user1或user2的所有聊天房间
        chat_rooms = PrivateChatRoom.objects.filter(
            user1=request.user
        ) | PrivateChatRoom.objects.filter(
            user2=request.user
        )

        serializer = PrivateChatRoomSerializer(chat_rooms, many=True, context={'request': request})
        return Response({
            "code": 200,
            "message": "获取聊天房间列表成功",
            "data": serializer.data
        })
    
class GroupChatRoomView(APIView):
    """
    处理群聊房间的创建和访问
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GroupChatRoomSerializer
    
    def post(self, request) -> Response:
        """
        创建群聊房间
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            group_chat = serializer.save()
            group_chat.add_member(request.user)  # 在视图中添加成员
            group_chat.add_admin(request.user)  # 在视图中添加管理员
            
            return Response({
                "code": 200,
                "message": "群聊房间创建成功",
                "data": self.serializer_class(group_chat).data
            })
        return Response({
            "code": 400,
            "message": "群聊房间创建失败",
            "data": serializer.errors
        })

    def get(self, request) -> Response:
        """
        获取当前用户的所有群聊房间
        """
        # 获取用户作为member的所有群聊房间
        group_rooms = GroupChatRoom.objects.filter(
            members=request.user
        )

        serializer = GroupChatRoomSerializer(group_rooms, many=True, context={'request': request})
        return Response({
            "code": 200,
            "message": "获取群聊房间列表成功",
            "data": serializer.data
        })