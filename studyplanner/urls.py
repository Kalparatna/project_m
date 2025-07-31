from django.urls import path
from . import views

app_name = 'studyplanner'


urlpatterns = [
    # Add your other URLs here
    path('', views.index, name='index'), 
    path('generate_plan/', views.generate_plan, name='generate_plan'),
 
    
   
]