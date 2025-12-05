from django.contrib import admin
from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from api.test_views import TestHealthView, TestVehicleCreateView, TestVehicleDetailView, TestThrottledView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", TestHealthView.as_view()),
    path("api/v1/vehicles/", TestVehicleCreateView.as_view()),
    path("api/v1/vehicles/<str:plaque>/", TestVehicleDetailView.as_view()),
    path("api/v1/throttled/", TestThrottledView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
