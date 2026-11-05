from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    # Home URL - Redirect to Dashboard
    path(
        '',
        RedirectView.as_view(url='/dashboard/', permanent=False),
        name='home'
    ),

    # Admin URL
    path('admin/', admin.site.urls),

    # Accounts API URLs
    path('api/', include('accounts.urls')),

    # Chatbot API URLs
    path('api/', include('chatbot.urls')),

    # Customer Support Dashboard URLs
    path('', include('support.urls')),
]