from django.urls import path
from . import views


app_name = 'trust'
urlpatterns = [
    path('', views.index),
]