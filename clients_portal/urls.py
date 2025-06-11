from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('account/', views.user_account, name='account'),
]