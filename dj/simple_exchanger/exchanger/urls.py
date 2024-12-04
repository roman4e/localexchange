# exchange/urls.py
from django.urls import path
from .views import index, upload, delete_file, get_text_history

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload, name='upload'),
    path('delete_file/', delete_file, name='delete_file'),
    path('get_text_history/', get_text_history, name='get_text_history'),
]
