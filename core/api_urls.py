from django.urls import include, path

from rest_framework.routers import DefaultRouter

# API URL patterns
urlpatterns = [
    path("vehicles/", include("vehicles.api_urls")),
    path("payments/", include("payments.api_urls")),
    path("notifications/", include("notifications.api_urls")),
    path("administration/", include("administration.api_urls")),
]
