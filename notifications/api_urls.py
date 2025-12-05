from django.urls import include, path

from rest_framework.routers import DefaultRouter

# from . import api_views

router = DefaultRouter()
# router.register(r'notifications', api_views.NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Additional API endpoints will be added here
]
