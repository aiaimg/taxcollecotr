"""
URL configuration for taxcollector_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django_prometheus.exports import ExportToDjangoView
from api.changelog_views import APIChangelogView
from api.admin_metrics_views import (
    metrics_dashboard_view,
    metrics_usage_data,
    metrics_error_data,
    metrics_performance_data,
    metrics_timeseries_data,
    metrics_top_endpoints_data,
    metrics_rate_limit_data,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("core.allauth_urls")),
    # Root path now points to CMS for frontend content
    path("", include("cms.urls", namespace="cms")),
    # Core URLs for authenticated user features (dashboard, profile, etc.)
    path("app/", include("core.urls", namespace="core")),
    path("vehicles/", include("vehicles.urls", namespace="vehicles")),
    path("payments/", include("payments.urls", namespace="payments")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("administration/", include("administration.urls", namespace="administration")),
    path("contraventions/", include("contraventions.urls", namespace="contraventions")),
    # Pages app - Velzon template demos only (not CMS-managed, for reference only)
    # Comment out if not needed in production
    path("pages/", include("pages.urls")),
    # Legacy API URLs (kept for backward compatibility)
    path("api/", include("core.api_urls")),
    path("api/contraventions/", include("contraventions.api_urls")),
    # New versioned API
    path("api/v1/", include("api.v1.urls")),
    # Prometheus metrics endpoint
    path("api/metrics/", ExportToDjangoView, name="prometheus-metrics"),
    # OpenAPI/Swagger documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API changelog
    path("api/changelog", APIChangelogView.as_view(), name="api-changelog"),
    # i18n URLs for language switching
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/metrics/", admin.site.admin_view(metrics_dashboard_view), name="admin-metrics"),
    path("admin/metrics/data/usage", admin.site.admin_view(metrics_usage_data), name="admin-metrics-usage"),
    path("admin/metrics/data/errors", admin.site.admin_view(metrics_error_data), name="admin-metrics-errors"),
    path("admin/metrics/data/performance", admin.site.admin_view(metrics_performance_data), name="admin-metrics-performance"),
    path("admin/metrics/data/timeseries", admin.site.admin_view(metrics_timeseries_data), name="admin-metrics-timeseries"),
    path("admin/metrics/data/top-endpoints", admin.site.admin_view(metrics_top_endpoints_data), name="admin-metrics-top"),
    path("admin/metrics/data/rate-limit", admin.site.admin_view(metrics_rate_limit_data), name="admin-metrics-rate-limit"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
