from django.urls import path
from labelingpage import views

app_name = 'labelingpage'

urlpatterns = [

    path('data_labeling/', views.data_labeling, name='datalabeling'),

    path('save_coordinates/<str:title>/', views.save_coordinates, name='save_coordinates'),

    path('get_labeling_data/<str:image_id>/', views.get_labeling_data, name='get_labeling_data'),
]
