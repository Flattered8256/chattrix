from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Message, IsRead
from .serializers import MessageSerializer
from apps.chat.models import PrivateChatRoom, GroupChatRoom
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File as DjangoFile

class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, room_id) -> Response:
        data = dict(request.data.items())
        data['room_id'] = room_id
        
        # 支持分块上传（与前端约定字段：uploadId, chunkIndex, totalChunks, filename）
        upload_id = request.data.get('uploadId') or request.POST.get('uploadId')
        chunk_index = request.data.get('chunkIndex') or request.POST.get('chunkIndex')
        total_chunks = request.data.get('totalChunks') or request.POST.get('totalChunks')

        # 如果检测到 uploadId，我们按分块上传逻辑处理
        if upload_id is not None and chunk_index is not None and total_chunks is not None:
            try:
                chunk_index = int(chunk_index)
                total_chunks = int(total_chunks)
            except Exception:
                return Response({
                    "code": 400,
                    "message": "chunkIndex/totalChunks 必须为整数",
                }, status=status.HTTP_400_BAD_REQUEST)

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(upload_id))
            os.makedirs(upload_dir, exist_ok=True)

            # 文件字段名为 'file'
            chunk_file = request.FILES.get('file')
            if chunk_file is None:
                return Response({
                    "code": 400,
                    "message": "缺少文件块",
                }, status=status.HTTP_400_BAD_REQUEST)

            part_name = f'chunk_{chunk_index:06d}'
            part_path = os.path.join(upload_dir, part_name)

            # 如果已存在该分片，直接返回成功（支持重试）
            if default_storage.exists(part_path):
                return Response({"code": 200, "message": "chunk exists"}, status=status.HTTP_200_OK)

            # 保存该块到临时目录
            with default_storage.open(part_path, 'wb') as dest:
                for c in chunk_file.chunks():
                    dest.write(c)

            # 如果这是最后一个块，则合并并创建 Message
            if chunk_index == total_chunks - 1:
                # 合并所有块
                filename = request.data.get('filename') or chunk_file.name
                # 我们在 upload_dir 中合并分片为临时文件，随后交由 FileField.save 上传到 storage
                # 这样可以避免直接在 MEDIA_ROOT 写入已存在路径，防止 storage 在保存时因为文件已存在而生成第二份
                final_name = f'{upload_id}_{filename}'
                merged_temp_path = os.path.join(upload_dir, final_name)
                # 合并分片到临时合并文件（位于 upload_dir）
                with open(merged_temp_path, 'wb') as outfile:
                    for i in range(total_chunks):
                        part_i = os.path.join(upload_dir, f'chunk_{i:06d}')
                        with default_storage.open(part_i, 'rb') as infile:
                            outfile.write(infile.read())

                # 使用 Django 的文件对象保存到模型的 FileField（通过 storage 管理）
                # 这里传入的 name 只包含文件名，model 的 upload_to='chat/files/' 会负责目录
                with open(merged_temp_path, 'rb') as merged_f:
                    django_file = DjangoFile(merged_f, name=final_name)

                    # 自动确定room_type（复用上面逻辑）
                    room_type = None
                    if PrivateChatRoom.objects.filter(id=room_id).exists():
                        room_type = 'private'
                    elif GroupChatRoom.objects.filter(id=room_id).exists():
                        room_type = 'group'

                    messages_type = data.get('messages_type', 'file')

                    message = Message(
                        sender=request.user,
                        room_type=room_type or data.get('room_type', ''),
                        room_id=room_id,
                        messages_type=messages_type,
                        filename=filename,
                    )

                    message.file.save(final_name, django_file, save=False)
                    message.save()

                # 清理临时 chunk 和临时合并文件
                try:
                    # 删除分片
                    for i in range(total_chunks):
                        part_i = os.path.join(upload_dir, f'chunk_{i:06d}')
                        default_storage.delete(part_i)
                    # 删除临时合并文件
                    try:
                        os.remove(merged_temp_path)
                    except Exception:
                        pass
                    # 删除上传目录（若为空）
                    try:
                        os.rmdir(upload_dir)
                    except Exception:
                        pass
                except Exception:
                    # 忽略清理错误，但可记录日志
                    pass

                serializer = MessageSerializer(message, context={'request': request})
                return Response({
                    "code": 201,
                    "message": "消息发送成功",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            # 非最后块，仅返回已上传
            return Response({"code": 200, "message": "chunk uploaded"}, status=status.HTTP_200_OK)

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