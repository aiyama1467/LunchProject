from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('my_page/', views.UserMyPage.as_view(), name='my_page'),
    path('delete/', views.UserDeleteView.as_view(), name='delete')
]
