from django.urls import path
from . import views
from .views import login_view, register_view, logout_view, DashboardView

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("news/", views.FetchNewsView.as_view(), name="news"),
    path("set-payout/", views.SetPayoutView.as_view(), name="set-payout"),
    path("export-pdf/", views.export_pdf, name="export-pdf"),
    path("export-csv/", views.export_csv, name="export-csv"),
    path(
        "export-google-sheets/", views.export_google_sheets, name="export-google-sheets"
    ),
]
