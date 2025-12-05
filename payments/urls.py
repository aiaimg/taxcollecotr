from django.urls import include, path

from . import views
from .mvola_views import MvolaCallbackView, MvolaInitiatePaymentView, MvolaStatusCheckView

app_name = "payments"

urlpatterns = [
    path("", views.PaymentListView.as_view(), name="list"),
    path("<uuid:pk>/", views.PaymentDetailView.as_view(), name="detail"),
    path("create/<str:plaque>/", views.PaymentCreateView.as_view(), name="create"),
    path("<uuid:pk>/status/", views.PaymentStatusCheckView.as_view(), name="check_status"),
    path("<uuid:pk>/qr/", views.QRCodeGenerateView.as_view(), name="qr_generate"),
    path("<uuid:pk>/qr/download/", views.DownloadQRCodeView.as_view(), name="download_qr"),
    path("<uuid:pk>/receipt/", views.DownloadReceiptView.as_view(), name="download_receipt"),
    # Stripe routes
    path("stripe/init/<str:plaque>/", views.StripePaymentInitView.as_view(), name="stripe_payment_init"),
    path("stripe/success/", views.PaymentSuccessView.as_view(), name="stripe_success"),
    path("stripe/cancel/", views.PaymentCancelView.as_view(), name="stripe_cancel"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    # MVola routes
    path("mvola/initiate/", MvolaInitiatePaymentView.as_view(), name="mvola-initiate"),
    path("mvola/callback/", MvolaCallbackView.as_view(), name="mvola-callback"),
    path("mvola/status/<str:server_correlation_id>/", MvolaStatusCheckView.as_view(), name="mvola-status"),
    path("mvola/<uuid:pk>/status/", views.MvolaStatusView.as_view(), name="mvola-status-page"),
    # QR Code verification routes
    path("qr/verify/<str:code>/", views.QRCodeVerifyView.as_view(), name="qr_verify"),
    path("qr/image/<str:code>/", views.QRCodeImageView.as_view(), name="qr_image"),
    path("qr/api/<str:code>/", views.QRCodeVerifyAPIView.as_view(), name="qr_api"),
    path("qr/verification/dashboard/", views.QRVerificationDashboardView.as_view(), name="qr_verification_dashboard"),
    # Cash payment system routes
    path("", include("payments.cash_urls")),
]
