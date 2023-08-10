from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'yolov8'

urlpatterns = [
    path('yolov8/', views.yolov8_main, name='yolov8_main'),
    path('yolov8_model/', views.yolov8_model, name='yolov8_model'),
]