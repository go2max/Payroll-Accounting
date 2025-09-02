from django.urls import path
from . import views

app_name = "payroll_accounting"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("roles/", views.roles, name="roles"),
    path("settings/", views.settings_view, name="settings"),
]
