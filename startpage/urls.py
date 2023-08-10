from startpage import views
from django.urls import path, include

urlpatterns = [
    path('', views.MainView.as_view()),
    path('home/', include('homepage.urls')),
    path('home_model/', include('ModelValidation.urls')),
]