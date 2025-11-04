from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('<int:room_id>/', views.MessageView.as_view(), name='room_messages'),
    path('<int:room_id>/<int:message_id>/is_read/', views.MessageReadView.as_view(), name='read_message'),
    path('<int:room_id>/unread_count/', views.UnreadMessageCountView.as_view(), name='unread_count')
]