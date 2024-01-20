from django.urls import path
from mango import views

app_name = 'mango'

urlpatterns = [
    path('', views.index, name='index'),
]