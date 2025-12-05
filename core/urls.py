from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Dashboard and authenticated user features
    path("", views.VelzonDashboardView.as_view(), name="home"),  # Default authenticated user home
    path("dashboard/", views.VelzonDashboardView.as_view(), name="velzon_dashboard"),
    path("qr-verification/", views.QRVerificationView.as_view(), name="qr_verification"),
    # Authentication URLs
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("registration-complete/", views.RegistrationCompleteView.as_view(), name="registration_complete"),
    path("verify-email/<uidb64>/<token>/", views.EmailVerificationView.as_view(), name="verify_email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend_verification"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("social-accounts/", views.SocialAccountManageView.as_view(), name="social_accounts"),
    path("social-accounts/unlink/<int:pk>/", views.SocialAccountUnlinkView.as_view(), name="social_account_unlink"),
    # Password reset URLs
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Fleet Manager URLs
    path("fleet/", views.FleetDashboardView.as_view(), name="fleet_dashboard"),
    path("fleet/vehicles/", views.FleetVehicleListView.as_view(), name="fleet_vehicles"),
    path("fleet/batch-payment/", views.FleetBatchPaymentView.as_view(), name="fleet_batch_payment"),
    path("fleet/export/", views.FleetExportView.as_view(), name="fleet_export"),
    path("fleet/export/csv/", views.FleetExportCSVView.as_view(), name="fleet_export_csv"),
    path("fleet/export/excel/", views.FleetExportExcelView.as_view(), name="fleet_export_excel"),
    path("fleet/export/pdf/", views.FleetExportPDFView.as_view(), name="fleet_export_pdf"),
    path("fleet/import/", views.FleetImportView.as_view(), name="fleet_import"),
    path("fleet/import/process/", views.FleetImportProcessView.as_view(), name="fleet_import_process"),
    path("fleet/import/history/", views.FleetImportHistoryView.as_view(), name="fleet_import_history"),
    path("fleet/import/<int:batch_id>/", views.FleetImportDetailView.as_view(), name="fleet_import_detail"),
    path(
        "fleet/import/<int:batch_id>/rollback/", views.FleetImportRollbackView.as_view(), name="fleet_import_rollback"
    ),
    path("fleet/bulk-edit/", views.FleetBulkEditView.as_view(), name="fleet_bulk_edit"),
    path("fleet/bulk-edit/history/", views.FleetBulkEditHistoryView.as_view(), name="fleet_bulk_edit_history"),
    path(
        "fleet/bulk-edit/<int:op_id>/rollback/",
        views.FleetBulkEditRollbackView.as_view(),
        name="fleet_bulk_edit_rollback",
    ),
    # Velzon Payment URLs
    path("payments/", views.PaymentListVelzonView.as_view(), name="payment_list_velzon"),
    # Notification Demo (for testing/development)
    path("notifications/demo/", views.NotificationDemoView.as_view(), name="notification_demo"),
]
