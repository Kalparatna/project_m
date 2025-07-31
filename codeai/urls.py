from django.urls import path
from . import views

app_name = 'codeai'

urlpatterns = [
    path('', views.index, name='index'),
     path('response/<int:idx>/', views.show_response, name='show_response'),  # Accepts idx as URL parameter
    path('download_response/<int:idx>/', views.download_response, name='download_response'),
]
