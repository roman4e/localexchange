from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/shared_text/$', consumers.SharedTextConsumer.as_asgi()),
]
