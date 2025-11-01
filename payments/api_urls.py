from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from . import api_views

router = DefaultRouter()
# router.register(r'payments', api_views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Additional API endpoints will be added here
]