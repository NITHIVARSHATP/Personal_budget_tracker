from django.contrib.auth import views as auth_views
from django.urls import path
from tracker_app import views
from .views import register_view
from .views import dashboard_view
from .views import profile_view
from .views import settings_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('add/', views.add_transaction_view, name='add_transaction'),
    path('transactions/', views.transactions_list_view, name='transactions_list'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('settings/', settings_view, name='settings'),
]
