from django.urls import path
from . import views

app_name = 'uploadpage'

urlpatterns = [
    path('', views.Board_List.as_view(), name='index'),
    path('write_board/', views.write_board, name='write_board'),
    path('<int:board_id>/create_reply/', views.create_reply, name='create_reply'),
    path('increase_ginseng/', views.increase_ginseng, name = 'increase_ginseng'),
    path('create_generate_id/', views.create_generate_id, name='create_generate_id'),
]