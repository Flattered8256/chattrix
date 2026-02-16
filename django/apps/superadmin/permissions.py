from rest_framework import permissions

class SuperAdminOnly(permissions.BasePermission):
    """
    仅超级管理员可访问
    """
    message = "需要超级管理员权限"
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser