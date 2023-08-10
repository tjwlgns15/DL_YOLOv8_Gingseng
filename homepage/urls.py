from django.urls import path,include
from homepage import views

app_name = 'homepage'

urlpatterns = [
    path('', views.HomeView.basepage),
    path('labelingpage/', include('labelingpage.urls')),
    path('adminpage/', include('adminpage.urls')),
    path('uploadpage/', include('uploadpage.urls')),
    path('', include('notice.urls')),
    path('account/', include('Account.urls')),
    path('', include('questionboard.urls')),
    path('my_page/', include('my_page.urls')),
    path('yolov8/', include('yolov8.urls')),
]