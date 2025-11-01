from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'api'

router = DefaultRouter()
# router.register(r'vehicles', api_views.VehicleViewSet)
# router.register(r'tax-grid', api_views.GrilleTarifaireViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # API endpoint pour la conversion cylindrée → CV
    path('convert-cylindree/', api_views.ConvertCylindreeView.as_view(), name='convert-cylindree'),
    path('convert-cylindree-simple/', api_views.convert_cylindree_simple, name='convert-cylindree-simple'),
]