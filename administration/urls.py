from django.urls import path
from . import views
from .views_modules import vehicle_types, price_grids, users

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Management views - Vehicles (legacy)
    path('vehicles/', views.VehicleManagementView.as_view(), name='vehicle_management'),
    
    # Vehicle Types Management (Admin Console)
    path('vehicle-types/', vehicle_types.VehicleTypeListView.as_view(), name='vehicle_type_list'),
    path('vehicle-types/create/', vehicle_types.VehicleTypeCreateView.as_view(), name='vehicle_type_create'),
    path('vehicle-types/<str:plaque>/', vehicle_types.VehicleTypeDetailView.as_view(), name='vehicle_type_detail'),
    path('vehicle-types/<str:plaque>/edit/', vehicle_types.VehicleTypeUpdateView.as_view(), name='vehicle_type_update'),
    path('vehicle-types/<str:plaque>/delete/', vehicle_types.VehicleTypeDeleteView.as_view(), name='vehicle_type_delete'),
    path('vehicle-types-export/', vehicle_types.vehicle_type_export, name='vehicle_type_export'),
    
    # Price Grids Management (Admin Console)
    path('price-grids/', price_grids.PriceGridListView.as_view(), name='price_grid_list'),
    path('price-grids/create/', price_grids.PriceGridCreateView.as_view(), name='price_grid_create'),
    path('price-grids/<int:pk>/', price_grids.PriceGridDetailView.as_view(), name='price_grid_detail'),
    path('price-grids/<int:pk>/edit/', price_grids.PriceGridUpdateView.as_view(), name='price_grid_update'),
    path('price-grids/<int:pk>/delete/', price_grids.PriceGridDeleteView.as_view(), name='price_grid_delete'),
    path('price-grids-export/', price_grids.price_grid_export, name='price_grid_export'),
    path('price-grids-import/', price_grids.price_grid_import, name='price_grid_import'),
    path('price-grids-report/', price_grids.price_grid_report, name='price_grid_report'),
    
    # Users Management (Admin Console)
    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', users.user_detail_view, name='user_detail'),
    path('users/<int:user_id>/edit/', users.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:user_id>/toggle-status/', users.toggle_user_status, name='user_toggle_status'),
    path('users/<int:user_id>/activity-stats/', users.user_activity_stats, name='user_activity_stats'),
    path('users/<int:user_id>/reset-password/', users.reset_user_password, name='user_reset_password'),
    path('users/<int:user_id>/permissions/', users.user_permissions_view, name='user_permissions'),
    path('users/export/', users.user_export, name='user_export'),
    
    # Legacy user management view
    path('user-management/', views.UserManagementView.as_view(), name='user_management'),
    path('user-management/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Management views - Payments
    path('payments/', views.PaymentManagementView.as_view(), name='payment_management'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API endpoints
    path('api/stats/', views.dashboard_api_stats, name='api_stats'),
    path('api/vehicle-types/bulk-update/', vehicle_types.vehicle_type_bulk_update, name='vehicle_type_bulk_update'),
    path('api/price-grids/bulk-update/', price_grids.price_grid_bulk_update, name='price_grid_bulk_update'),
    path('api/users/bulk-operations/', users.user_bulk_operations, name='user_bulk_operations'),
    
    # Test components page
    path('test-components/', views.test_components_view, name='test_components'),
    
    # Placeholder URLs for base_admin.html navigation
    path('audit-logs/', views.dashboard_view, name='audit_log_list'),  # Placeholder
]