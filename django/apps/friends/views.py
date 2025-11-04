from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Friend, FriendRequest, FriendGroup, FriendGroupMembership, FriendNickname, FriendBlock
from .serializers import (
    FriendSerializer, 
    FriendRequestSerializer, 
    FriendGroupSerializer, 
    FriendGroupMembershipSerializer,
    FriendNicknameSerializer,
    FriendBlockSerializer
)
from asgiref.sync import async_to_sync
from apps.realtime.services import RealtimeService

class FriendCleanupService:
    """
    好友关系清理服务，处理好友删除时的级联操作
    """
    @staticmethod
    def cleanup_friend_relations(friend_instance):
        """
        清理好友相关的附属数据（备注、屏蔽等）
        """
        # 删除相关备注
        try:
            friend_instance.nickname_obj.delete()
        except FriendNickname.DoesNotExist:
            pass
            
        # 删除相关屏蔽记录
        try:
            friend_instance.block_obj.delete()
        except FriendBlock.DoesNotExist:
            pass
        FriendRequest.objects.filter(
            (Q(sender=friend_instance.owner) & Q(receiver=friend_instance.friend)) |
            (Q(sender=friend_instance.friend) & Q(receiver=friend_instance.owner))
        ).delete()
        Friend.objects.filter(
            owner=friend_instance.friend,
            friend=friend_instance.owner
        ).delete()


class FriendViewSet(viewsets.ModelViewSet):
    """
    好友关系视图集
    """
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Friend.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def perform_destroy(self, instance):
        # 使用服务层处理级联清理
        FriendCleanupService.cleanup_friend_relations(instance)
        instance.delete()
    
    def list(self, request, *args, **kwargs):
        """获取好友列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友关系"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "好友添加成功",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友信息获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "好友信息更新成功",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除好友关系"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友关系删除成功",
            "data": None
        }, status=status.HTTP_200_OK)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """
    好友请求视图集
    """
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户可以看到接收到的好友请求
        return FriendRequest.objects.filter(
            Q(receiver=self.request.user)
        )
    
    def perform_create(self, serializer):
        # 在创建前检查是否已经存在反向好友关系
        sender = self.request.user
        receiver = serializer.validated_data['receiver']
        
        if sender == receiver:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("不能给自己发送好友请求")
        
        existing_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
        if existing_request:
            if existing_request.status == 'pending':
                from rest_framework.exceptions import ValidationError
                raise ValidationError("已存在待处理的好友请求")
            

        if Friend.objects.filter(owner=sender, friend=receiver).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("该好友关系已存在")

        # 发送好友请求通知
     
        async_to_sync(RealtimeService.send_friend_request_notification)(
            sender_id=sender.id, 
            receiver_id=receiver.id, 
            message="我想添加你为好友"
        )

        serializer.save(sender=sender)
    
    def list(self, request, *args, **kwargs):
        """获取好友请求列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友请求列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友请求"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "code": 201,
                "message": "好友请求发送成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友请求详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友请求详情获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友请求"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "好友请求更新成功",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除好友请求"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友请求删除成功",
            "data": None
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受好友请求"""
        friend_request = self.get_object()
        if friend_request.receiver != request.user:
            return Response({
                "code": 403,
                "message": "您没有权限执行此操作",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if friend_request.status != 'pending':
            return Response({
                "code": 400,
                "message": "该请求已处理",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新请求状态
        friend_request.status = 'accepted'
        friend_request.save()
        
        # 检查是否已经存在反向好友关系
        if not Friend.objects.filter(
            owner=friend_request.receiver, 
            friend=friend_request.sender
        ).exists():
            # 创建反向好友关系
            Friend.objects.create(
                owner=friend_request.receiver, 
                friend=friend_request.sender
            )
            
        # 检查是否已经存在正向好友关系
        if not Friend.objects.filter(
            owner=friend_request.sender, 
            friend=friend_request.receiver
        ).exists():
            # 创建正向好友关系
            Friend.objects.create(
                owner=friend_request.sender, 
                friend=friend_request.receiver
            )
        
        # 发送好友成功请求通知
        # 通知请求发送方，他的好友请求被接受了
        async_to_sync(RealtimeService.send_friend_accepted_notification)(
            friend_id=friend_request.receiver.id, 
            user_id=friend_request.sender.id
        )
        
        # 通知请求接收方，他已成功添加好友
        async_to_sync(RealtimeService.send_friend_accepted_notification)(
            friend_id=friend_request.sender.id, 
            user_id=friend_request.receiver.id
        )
        return Response({
            "code": 200,
            "message": "好友请求已接受",
            "data": None
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝好友请求"""
        friend_request = self.get_object()
        if friend_request.receiver != request.user:
            return Response({
                "code": 403,
                "message": "您没有权限执行此操作",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if friend_request.status != 'pending':
            return Response({
                "code": 400,
                "message": "该请求已处理",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.delete()
        
        return Response({
            "code": 200,
            "message": "好友请求已拒绝",
            "data": None
        })


class FriendGroupViewSet(viewsets.ModelViewSet):
    """
    好友分组视图集
    """
    serializer_class = FriendGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FriendGroup.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """获取好友分组列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友分组列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友分组"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "好友分组创建成功",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友分组详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友分组详情获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友分组"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "好友分组更新成功",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除好友分组"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友分组删除成功",
            "data": None
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取分组中的好友关系"""
        group = self.get_object()
        # 确保用户只能访问自己的分组
        if group.owner != request.user:
            return Response({
                "code": 403,
                "message": "您没有权限执行此操作",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
            
        memberships = FriendGroupMembership.objects.filter(group=group)
        # 返回分组关系而不是好友列表
        serializer = FriendGroupMembershipSerializer(memberships, many=True)
        return Response({
            "code": 200,
            "message": "分组成员获取成功",
            "data": serializer.data
        })


class FriendGroupMembershipViewSet(viewsets.ModelViewSet):
    """
    好友分组成员视图集
    """
    serializer_class = FriendGroupMembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 只能操作自己创建的分组中的成员关系
        return FriendGroupMembership.objects.filter(group__owner=self.request.user)
        
    def perform_create(self, serializer):
        group = serializer.validated_data['group']
        # 确保用户只能向自己的分组添加成员
        if group.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限向此分组添加成员")
            
        friend = serializer.validated_data['friend']
        # 确保只能添加自己的好友
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能将自己好友添加到分组中")
        
        # 检查是否已经存在该分组成员关系
        if FriendGroupMembership.objects.filter(group=group, friend=friend).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("该好友已在分组中")
            
        serializer.save()
        
    def perform_update(self, serializer):
        group = serializer.validated_data.get('group', serializer.instance.group)
        friend = serializer.validated_data.get('friend', serializer.instance.friend)
        
        # 确保用户只能操作自己的分组
        if group.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限操作此分组")
            
        # 确保只能操作自己的好友
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能操作自己的好友")
            
        serializer.save()
        
    def perform_destroy(self, instance):
        # 确保用户只能删除自己分组中的成员关系
        if instance.group.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限删除此分组成员关系")
            
        instance.delete()
    
    def list(self, request, *args, **kwargs):
        """获取好友分组成员列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友分组成员列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友分组成员关系"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "code": 201,
                "message": "好友分组成员关系创建成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友分组成员关系详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友分组成员关系详情获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友分组成员关系"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "code": 200,
                "message": "好友分组成员关系更新成功",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """删除好友分组成员关系"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友分组成员关系删除成功",
            "data": None
        }, status=status.HTTP_200_OK)


class FriendNicknameViewSet(viewsets.ModelViewSet):
    """
    好友备注视图集
    """
    serializer_class = FriendNicknameSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FriendNickname.objects.filter(friend__owner=self.request.user)
        
    def perform_create(self, serializer):
        friend = serializer.validated_data['friend']
        # 确保只能为自己的好友添加备注
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能为自己的好友设置备注")
            
        serializer.save()
        
    def perform_update(self, serializer):
        friend = serializer.validated_data.get('friend', serializer.instance.friend)
        # 确保只能为自己的好友修改备注
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能为自己的好友设置备注")
            
        serializer.save()
        
    def perform_destroy(self, instance):
        # 确保只能删除自己好友的备注
        if instance.friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能删除自己好友的备注")
            
        instance.delete()
    
    def list(self, request, *args, **kwargs):
        """获取好友备注列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友备注列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友备注"""
        # 先检查是否已存在对应friend的备注
        friend_id = request.data.get('friend')
        if friend_id:
            try:
                # 尝试查找已存在的备注
                existing_nickname = FriendNickname.objects.get(friend_id=friend_id)
                # 如果存在，则转为更新操作
                return self.update(request, *args, **kwargs)
            except FriendNickname.DoesNotExist:
                # 如果不存在，则继续创建流程
                pass
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "code": 201,
                "message": "好友备注创建成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友备注详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友备注详情获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友备注"""
        # 对于更新操作，先尝试获取实例，如果通过create调用则kwargs中没有pk
        try:
            instance = self.get_object()
        except:
            # 通过friend字段查找实例
            friend_id = request.data.get('friend')
            if friend_id:
                try:
                    instance = FriendNickname.objects.get(friend_id=friend_id)
                except FriendNickname.DoesNotExist:
                    return Response({
                        "code": 400,
                        "message": "未找到对应的备注记录",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "code": 400,
                    "message": "缺少friend参数",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "code": 200,
                "message": "好友备注更新成功",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """删除好友备注"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友备注删除成功",
            "data": None
        }, status=status.HTTP_200_OK)


class FriendBlockViewSet(viewsets.ModelViewSet):
    """
    好友屏蔽视图集
    """
    serializer_class = FriendBlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FriendBlock.objects.filter(friend__owner=self.request.user)
        
    def perform_create(self, serializer):
        friend = serializer.validated_data['friend']
        # 确保只能屏蔽自己的好友
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能屏蔽自己的好友")
            
        serializer.save()
        
    def perform_update(self, serializer):
        friend = serializer.validated_data.get('friend', serializer.instance.friend)
        # 确保只能操作自己好友的屏蔽状态
        if friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能操作自己好友的屏蔽状态")
            
        serializer.save()
        
    def perform_destroy(self, instance):
        # 确保只能删除自己好友的屏蔽记录
        if instance.friend.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能删除自己好友的屏蔽记录")
            
        instance.delete()
    
    def list(self, request, *args, **kwargs):
        """获取好友屏蔽列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "好友屏蔽列表获取成功",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建好友屏蔽记录"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "code": 201,
                "message": "好友屏蔽记录创建成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个好友屏蔽记录详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "好友屏蔽记录详情获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新好友屏蔽记录"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "code": 200,
                "message": "好友屏蔽记录更新成功",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 400,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """删除好友屏蔽记录"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "好友屏蔽记录删除成功",
            "data": None
        }, status=status.HTTP_200_OK)