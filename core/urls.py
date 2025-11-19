from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard/', views.index, name='dashboard'),
    path('welcome/', views.dashboard_view, name='welcome'),
    path('', views.landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name="auth/auth-login.html"), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Use custom logout view
    path('change-password/', views.change_password, name='change_password'),
]