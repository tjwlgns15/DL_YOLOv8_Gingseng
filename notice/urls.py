from django.urls import path
from notice import views

app_name = 'notice'

urlpatterns = [
    path('notice/', views.index, name='index'),
    path('notice/new/', views.NewView, name='new'),
    path('notice/create/', views.Create, name='create'),
    path('notice/<int:pk>/', views.Detail, name='detail'),
    path('notice/<int:pk>/delete/', views.delete, name='delete'),
    path('notice/<int:pk>/edit/', views.edit, name='edit'),
    path('notice/<int:pk>/update/', views.update, name='update')
]