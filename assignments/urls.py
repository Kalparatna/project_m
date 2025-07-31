from django.urls import path
from . import views

app_name = "assignments" 

urlpatterns = [
    path('', views.generate_resource, name='generate_resource'),
    path('download_pdf/', views.download_pdf, name='download_pdf'), 
]