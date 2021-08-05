from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path('test/', views.test, name='test'),
    # path('start', views.start, name='start'),
]
