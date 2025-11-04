from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/friends/$', consumers.FriendNotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.SystemNotificationConsumer.as_asgi()),
]