from django.urls import path, include
from . import views

app_name = 'vehicles'

urlpatterns = [
    # Vehicle management URLs
    path('', views.VehiculeListView.as_view(), name='vehicle_list'),
    path('add/', views.VehiculeCreateView.as_view(), name='vehicle_create'),
    path('<str:pk>/', views.VehiculeDetailView.as_view(), name='vehicle_detail'),
    path('<str:pk>/documents/upload/', views.upload_vehicle_document, name='vehicle_document_upload'),
    path('<str:pk>/edit/', views.VehiculeUpdateView.as_view(), name='vehicle_edit'),
    path('<str:pk>/delete/', views.VehiculeDeleteView.as_view(), name='vehicle_delete'),
    
    # AJAX endpoints
    path('ajax/calculate-tax/', views.calculate_tax_ajax, name='calculate_tax_ajax'),
    
    # API endpoints
    path('api/', include('vehicles.api_urls', namespace='api')),
]