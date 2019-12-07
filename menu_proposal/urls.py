from django.urls import path

from . import views

app_name = 'menu_proposal'

urlpatterns = [
    path('', views.Home.home, name="home"),
    path('add/', views.MenuCreateView.as_view(), name="add"),
    path('edit/', views.MenuEditView.as_view(), name="edit"),
    path('edit/', views.MenuEditView.as_view(), name="edit_page"),
    path('list/', views.MenuListView.as_view(), name="list"),
    path('list/', views.MenuListView.as_view(), name="list_page"),
    path('list/<pk>', views.MenuDetailView.as_view(), name="detail"),
    path('update/<pk>', views.MenuUpdateView.as_view(), name="update"),
    path('delete/<pk>', views.MenuDeleteView.as_view(), name="delete"),
    path('proposal/', views.MenuProposalView.as_view(), name='proposal'),
]
