from django.urls import path

from . import views

app_name = 'menu_proposal'

urlpatterns = [
    path('form/', views.MenuProposalView.as_view(), name='proposal'),

]
