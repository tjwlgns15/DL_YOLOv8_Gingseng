from django.urls import path,include
from my_page import views


app_name = 'my_page'

urlpatterns = [
    path('my_page/', views.MysiteView.my_page, name = 'my_page_a'),
    path('wonsi_data_detail/<int:pk>/', views.wonsi_data_detail_my_page, name='wonsi_data_detail_my_page'),
    path('data_labeling/<int:pk>/', views.data_labeling_detail_my_page, name='data_labeling_detail_my_page'),
    path("add_payment/", views.add_payment, name="add_payment"),
]