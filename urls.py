from django.urls import path
from . import views

app_name = "payroll_accounting"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/<int:session_id>/",
         views.session_detail, name="session_detail"),
    path("members/", views.member_list, name="member_list"),
    path("roles/", views.role_list, name="role_list"),
    path("wallets/", views.wallet_list, name="wallet_list"),
    path("settings/", views.settings_view, name="settings"),
]
