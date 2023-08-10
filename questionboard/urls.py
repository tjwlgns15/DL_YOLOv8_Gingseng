from django.urls import path
from questionboard import views

app_name = 'questionboard'

urlpatterns = [
    path('questionboard/', views.index, name='index'),
    path('questionboard/new/', views.NewView, name='new'),
    path('questionboard/create/', views.Create, name='create'),
    path('questionboard/<int:pk>/', views.Detail, name='detail'),
    path('questionboard/<int:pk>/delete/', views.delete, name='delete'),
    path('questionboard/<int:pk>/edit/', views.edit, name='edit'),
    path('questionboard/<int:pk>/update/', views.update, name='update')
]