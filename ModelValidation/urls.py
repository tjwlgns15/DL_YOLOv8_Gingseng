from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
]

# 정적 파일 서빙을 설정합니다.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)