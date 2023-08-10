from django.urls import path, include
from adminpage import views

app_name = 'adminpage'

urlpatterns = [
    path('', views.Admin_Home.as_view(), name='admin_home'),
    path('get_grade_data/', views.Admin_Home.as_view(), name='get_grade_data'),

    path('adminpage/user_manage/', views.User_Manage.as_view(), name='user_index'),
    path('update_user_authority/', views.update_user_authority, name='update_user_authority'),

    # 원시
    path('adminpage/wonsi_verification/', views.Wonsi_Verification.as_view(), name='wonsi_verification_index'),
    path('update_wonsi_verification/', views.update_wonsi_verification, name='update_wonsi_verification'),
    path('adminpage/wonsi_verification/<int:pk>/', views.wonsi_data_detail, name='wonsi_data_detail'),

    # 라벨링
    path('adminpage/data_labeling_verification/', views.Data_labeling_Verification.as_view(), name='data_labeling_verification_index'),
    path('update_data_labeling_verification/', views.update_data_labeling_verification, name='update_data_labeling_verification'),
    path('adminpage/data_labeling_verification/<int:pk>/', views.labeling_data_detail, name='labeling_detail'),
    path('adminpage/assignment/', views.assignment_view, name='assignment_view'),
    path('adminpage/assign_data/', views.assign_data, name='assign_data'),

    # adminnotice
    path('adminpage/adminnotice/', views.notice_index, name='notice_index'),
    path('adminpage/adminnotice/new/', views.notice_NewView, name='notice_new'),
    path('adminpage/adminnotice/create/', views.notice_Create, name='notice_create'),
    path('adminpage/adminnotice/<int:pk>/', views.notice_Detail, name='notice_detail'),
    path('adminpage/adminnotice/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
    path('adminpage/adminnotice/<int:pk>/edit/', views.notice_edit, name='notice_edit'),
    path('adminpage/adminnotice/<int:pk>/update/', views.notice_update, name='notice_update'),

    # questionboardadmin
    path('adminpage/questionboardadmin/', views.questionboard_index, name='questionboard_index'),
    path('adminpage/questionboardadmin/<int:pk>/', views.questionboard_Detail, name='questionboard_detail'),
    path('adminpage/questionboardadmin/<int:pk>/delete/', views.questionboard_delete, name='questionboard_delete'),

    # 포인트

    path('point_d_list/', views.show_point_d_list, name='point_d_list'),
    path('adminpage/point_change/', views.point_change_form, name='point_change'),
    path('point_change/', views.point_change_form, name='point_change_form'),
    path('adminpage/Point_settlement_list/', views.Point_settlement_index, name='Point_settlement_list'),
    path('update_data_Point_settlement/', views.update_data_Point_settlement, name='update_data_Point_settlement'),
]
