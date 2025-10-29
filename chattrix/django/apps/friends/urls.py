from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FriendViewSet, 
    FriendRequestViewSet, 
    FriendGroupViewSet, 
    FriendGroupMembershipViewSet,
    FriendNicknameViewSet,
    FriendBlockViewSet
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'friends', FriendViewSet, basename='friend')
router.register(r'requests', FriendRequestViewSet, basename='friendrequest')
router.register(r'groups', FriendGroupViewSet, basename='friendgroup')
router.register(r'group-memberships', FriendGroupMembershipViewSet, basename='friendgroupmembership')
router.register(r'nicknames', FriendNicknameViewSet, basename='friendnickname')
router.register(r'blocks', FriendBlockViewSet, basename='friendblock')

urlpatterns = [
    path('', include(router.urls)),
]