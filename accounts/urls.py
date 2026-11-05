from django.urls import path
from . import views


urlpatterns = [
    # User Registration API
    path('register/', views.register_user, name='register'),

    # User Login API
    path('login/', views.login_user, name='login'),
]