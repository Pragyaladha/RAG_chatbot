from django.urls import path 
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('upload/',views.upload_data, name='upload_data'),
    path('api/chat/', views.chat_api, name='chat_api'),
    # path("reset/", views.reset_chat),
]
