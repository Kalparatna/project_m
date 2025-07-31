from django.urls import path
from . import views
app_name = 'summaries'
urlpatterns = [
    path("", views.index, name="index"),
    path("generate_summaries/", views.generate_summary, name="generate_summary"),
]