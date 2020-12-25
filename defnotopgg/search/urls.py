from django.urls import path
from .import views

urlpatterns = [
    path('', views.get_name, name = 'get_name'),
    path('<str:summonerName>', views.get_stats, name = 'get_stats')

]