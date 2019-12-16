from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('my_page/', views.UserMyPage.as_view(), name='my_page'),
    path('delete/', views.UserDeleteView.as_view(), name='delete'),
    path('my_page/password_modify/', views.PasswordModifyView.as_view(), name='password_modify'),
    path('my_page/password_modify/done/', views.PasswordModifyDoneView.as_view(), name='password_modify_done'),
    path('my_page/modify_user_info/', views.ModifyUserInfoView.as_view(), name='modify_user_info'),
    path('my_page/modify_eatlog/<date>', views.ModifyEatLogView.as_view(), name='modifyeatlog'),
    path('my_page/add_eatlog/', views.AddEatLogView.as_view(), name='addeatlog'),
    path('my_page/delete_eatlog/<date>',
         views.DeleteEatLogView.as_view(), name='deleatlog'),

]
