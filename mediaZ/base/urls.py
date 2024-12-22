from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('room_page/<str:pk>/', views.room, name="room"),
    path('create-room/', views.createRoom, name='create-room'),
    path('edit-room/<str:pk>/', views.updateRoom, name='edit-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room')

]
