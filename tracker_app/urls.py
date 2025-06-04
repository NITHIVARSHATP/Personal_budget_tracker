from django.contrib.auth import views as auth_views
from django.urls import path
from tracker_app import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register_view,
    dashboard_view,
    profile_view,
    settings_view,
    reports_view,
    export_report_csv,     
    export_report_pdf,
    set_goal_view  
)
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
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
        name='password_change_done'
    ),
    path('reports/', reports_view, name='reports'),
    path('export/csv/', export_report_csv, name='export_report_csv'),
    path('export/pdf/', export_report_pdf, name='export_report_pdf'),
    path('set-goal/', set_goal_view, name='set_goal'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
