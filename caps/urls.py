from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('team/<str:abbreviation>/', views.team_overview, name='team_overview'),
    path('team/<str:abbreviation>/<str:season>/', views.team_detail, name='team_detail_season'),
    
]