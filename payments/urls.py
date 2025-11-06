from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='list'),
    path('<uuid:pk>/', views.PaymentDetailView.as_view(), name='detail'),
    path('create/<str:plaque>/', views.PaymentCreateView.as_view(), name='create'),
    path('<uuid:pk>/status/', views.PaymentStatusCheckView.as_view(), name='check_status'),
    path('<uuid:pk>/qr/', views.QRCodeGenerateView.as_view(), name='qr_generate'),
    path('<uuid:pk>/receipt/', views.DownloadReceiptView.as_view(), name='download_receipt'),
    # Stripe routes
    path('stripe/init/<str:plaque>/', views.StripePaymentInitView.as_view(), name='stripe_payment_init'),
    path('stripe/success/', views.PaymentSuccessView.as_view(), name='stripe_success'),
    path('stripe/cancel/', views.PaymentCancelView.as_view(), name='stripe_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]