from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('private-rooms/', views.PrivateChatRoomView.as_view(), name='private_chat_rooms'),
    path('group-rooms/', views.GroupChatRoomView.as_view(), name='group_chat_rooms'),
]