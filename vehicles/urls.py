from django.urls import path, include
from . import views

app_name = 'vehicles'

urlpatterns = [
    # Vehicle management URLs
    path('', views.VehiculeListView.as_view(), name='list'),
    path('add/', views.VehiculeCreateView.as_view(), name='add'),
    path('<str:pk>/', views.VehiculeDetailView.as_view(), name='detail'),
    path('<str:pk>/edit/', views.VehiculeUpdateView.as_view(), name='edit'),
    path('<str:pk>/delete/', views.VehiculeDeleteView.as_view(), name='delete'),
    
    # AJAX endpoints
    path('ajax/calculate-tax/', views.calculate_tax_ajax, name='calculate_tax_ajax'),
    
    # API endpoints
    path('api/', include('vehicles.api_urls', namespace='api')),
]