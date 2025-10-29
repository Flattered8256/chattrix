from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 你可以自定义显示字段
    list_display = ('id','username', 'email', 'user_status','user_avatar')
    list_filter = ('is_staff', 'user_status')
    search_fields = ('username', 'email')