from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Message, IsRead
from .serializers import MessageSerializer
from apps.chat.models import PrivateChatRoom, GroupChatRoom

class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, room_id) -> Response:
        data = dict(request.data.items())
        data['room_id'] = room_id
        
        # 自动确定room_type
        room_type = None
        # 首先检查是否是私聊房间
        if PrivateChatRoom.objects.filter(id=room_id).exists():
            room_type = 'private'
        # 然后检查是否是群聊房间
        elif GroupChatRoom.objects.filter(id=room_id).exists():
            room_type = 'group'
        
        # 如果找到了房间类型，设置room_type
        if room_type:
            data['room_type'] = room_type
        
        serializer = MessageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response({
                "code": 201,
                "message": "消息发送成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "code": 400,
                "message": "消息数据无效",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, room_id) -> Response:
        messages = Message.objects.filter(
            room_id=room_id
        ).order_by('-timestamp')
        
        # 使用DRF分页器
        paginator = PageNumberPagination()
        paginator.page_size = 20  # 可以调整每页大小
        page = paginator.paginate_queryset(messages, request, view=self)

        page = list(page)
        page.reverse()  # 反转当前页，让最早的消息在前
        
        serializer = MessageSerializer(page, many=True)
        
        return Response({
            "code": 200,
            "message": "获取消息列表成功",
            "data": serializer.data,
            "pagination-next": paginator.get_next_link(),
        })

class MessageReadView(APIView):
    """
    消息已读状态视图
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, room_id, message_id) -> Response:
        """
        标记消息为已读
        """
        
        receiver = request.user
        message = Message.objects.get(id=message_id)
        
        # 使用update_or_create确保每个用户在每个房间只有一条已读记录，且始终指向最后标记为已读的消息
        # update_or_create返回元组(object, created)，我们只需要第一个元素
        is_read_record, created = IsRead.objects.update_or_create(
            room_id=room_id,
            receiver=receiver,
            defaults={'message': message}
        )
        
        # 直接构造返回数据
        data = {
            "message": is_read_record.message.id,
            "receiver": is_read_record.receiver.id,
        }
                
        return Response({
            "code": 201,
            "message": "消息已读标记创建成功",
            "data": data
        }, status=status.HTTP_201_CREATED)


class UnreadMessageCountView(APIView):
    """
    获取聊天室未读消息计数
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, room_id) -> Response:
        """
        获取指定聊天室的未读消息数量
        """
        user = request.user
        
        # 1. 获取该用户在该聊天室中已读的最后一次消息
        try:
            last_read_message = IsRead.objects.get(
                room_id=room_id,
                receiver=user
            )
            last_read_id = last_read_message.message.id
        except IsRead.DoesNotExist:
            # 如果用户在该聊天室还没有任何已读记录，设置last_read_id为0
            last_read_id = 0
        
        # 2. 统计比该ID大的消息数量，且发送者不是当前用户
        unread_count = Message.objects.filter(
            room_id=room_id,
            id__gt=last_read_id
        ).exclude(
            sender=user  # 排除自己发送的消息
        ).count()
        
        return Response({
            "code": 200,
            "message": "获取未读消息数成功",
            "data": {
                "unread_count": unread_count
            }
        })