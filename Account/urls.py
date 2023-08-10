from django.urls import path, include
from Account import views

app_name = 'Account'

urlpatterns = [
    path('signup/', views.signup, name= 'signup'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name= 'logout'),
]
