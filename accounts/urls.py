from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signup_successful/', views.SignupSuccessful.as_view(), name='signup_successful')
]
