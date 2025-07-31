 # App/urls.py
from django.urls import path
from .views import index, modules
from . import views



urlpatterns = [
    path('', views.home, name='home'),  # New home page as default
    path('services/', views.services, name='services1'),
    path('search/', views.index, name='index'),  # Moved index (topic search) to /search/
    path('modules/<str:topic>/', modules, name='modules'),
    path('get_gemini_response/', views.character_selection, name='get_gemini_response'),
    path('level_selection/<str:character>/', views.level_selection, name='level_selection'),  # This line should be present
    path('chat/<str:character>/<str:level>/', views.chat_with_tutor, name='chat_with_tutor'),


    

   
]



