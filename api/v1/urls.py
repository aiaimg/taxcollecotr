"""
API Version 1 URL Configuration
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

app_name = "api_v1"

# Create router for viewset-based endpoints
router = DefaultRouter()

# Authentication endpoints
router.register(r"auth", views.AuthViewSet, basename="auth")

# Vehicle endpoints
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"vehicle-types", views.VehicleTypeViewSet, basename="vehicle-type")
router.register(r"vehicle-documents", views.VehicleDocumentViewSet, basename="vehicle-document")

# Payment endpoints
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"price-grids", views.PriceGridViewSet, basename="price-grid")
router.register(r"qr-codes", views.QRCodeViewSet, basename="qr-code")

# User endpoints
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"profiles", views.UserProfileViewSet, basename="profile")

# Notification endpoints
router.register(r"notifications", views.NotificationViewSet, basename="notification")

# Tax calculation endpoints
router.register(r"tax-calculations", views.TaxCalculationViewSet, basename="tax-calculation")

# Dashboard/analytics endpoints
router.register(r"dashboard", views.DashboardViewSet, basename="dashboard")

# Agent endpoints
router.register(r"agent-partenaire", views.AgentPartenaireViewSet, basename="agent-partenaire")
router.register(r"agent-government", views.AgentGovernmentViewSet, basename="agent-government")

# API Key management endpoints
router.register(r"api-keys", views.APIKeyViewSet, basename="api-key")

# Webhook endpoints
router.register(r"webhook-subscriptions", views.WebhookSubscriptionViewSet, basename="webhook-subscription")
router.register(r"webhook-deliveries", views.WebhookDeliveryViewSet, basename="webhook-delivery")

urlpatterns = [
    # Router URLs
    path("", include(router.urls)),
    # Health check endpoint
    path("health/", views.HealthCheckView.as_view(), name="health-check"),
    # Utility endpoints
    path("convert-cylindree/", views.ConvertCylindreeView.as_view(), name="convert-cylindree"),
    path("audit/logs/", views.AuditLogView.as_view(), name="audit-logs"),
]
