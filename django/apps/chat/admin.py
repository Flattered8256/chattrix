from django.contrib import admin
from .models import GroupChatRoom

@admin.register(GroupChatRoom)
class GroupChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','get_member_count', 'created_at')
    search_fields = ('name', 'admin__username')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('members','admin')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'avatar')
        }),
        ('管理信息', {
            'fields': ('admin', 'members')
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_member_count(self, obj):
        return obj.get_member_count()
    
    get_member_count.short_description = '成员数量'
