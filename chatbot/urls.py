from django.urls import path
from . import views


urlpatterns = [

    # Customer Chat API
    path('chat/', views.chat_message, name='chat'),

    # Customer Chat History API
    path('chat/history/', views.chat_history, name='chat_history'),

]