from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.statistics, name='statistics'),
    path('detailed_statistics/', views.detailed_statistics, name='detailed_statistics'),
]