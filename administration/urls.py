from django.urls import path
from . import views
from .views_modules import vehicle_types, price_grids, users, enhanced_vehicle_management, individual_vehicles, vehicle_type_management, payment_settings
from . import auth_views
from vehicles import views as vehicle_views

app_name = 'administration'

urlpatterns = [
    # Admin Authentication
    path('admin_login/', auth_views.AdminLoginView.as_view(), name='admin_login'),
    path('login/', auth_views.AdminLoginView.as_view(), name='admin_login_alt'),  # Alternative URL
    path('logout/', auth_views.AdminLogoutView.as_view(), name='admin_logout'),
    path('access-check/', auth_views.admin_required_view, name='admin_required'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Admin Vehicle Management - Direct vehicle operations for admins
    path('vehicules/', vehicle_views.AdminVehiculeListView.as_view(), name='admin_vehicle_list'),
    path('vehicules/add/', vehicle_views.AdminVehiculeCreateView.as_view(), name='admin_vehicle_create'),
    path('vehicules/<str:pk>/', vehicle_views.AdminVehiculeDetailView.as_view(), name='admin_vehicle_detail'),
    path('vehicules/<str:pk>/edit/', vehicle_views.AdminVehiculeUpdateView.as_view(), name='admin_vehicle_edit'),
    path('vehicules/<str:pk>/delete/', vehicle_views.AdminVehiculeDeleteView.as_view(), name='admin_vehicle_delete'),
    
    # Management views - Vehicles (legacy)
    path('vehicles/', views.VehicleManagementView.as_view(), name='vehicle_management'),
    
    # Enhanced Vehicle Management (Role-based)
    path('enhanced-vehicles/', enhanced_vehicle_management.EnhancedVehicleManagementView.as_view(), name='enhanced_vehicle_management'),
    path('api/enhanced-vehicles/', enhanced_vehicle_management.vehicle_management_api, name='enhanced_vehicle_management_api'),
    path('api/vehicle-owner-details/<int:user_id>/', enhanced_vehicle_management.vehicle_owner_details, name='vehicle_owner_details'),
    
    # Vehicle Types Management (Admin Console) - Managing VehicleType records
    path('vehicule_type/', vehicle_type_management.VehicleTypeManagementListView.as_view(), name='vehicle_type_list'),
    path('vehicule_type/create/', vehicle_type_management.VehicleTypeManagementCreateView.as_view(), name='vehicle_type_create'),
    path('vehicule_type/<int:pk>/', vehicle_type_management.VehicleTypeManagementDetailView.as_view(), name='vehicle_type_detail'),
    path('vehicule_type/<int:pk>/edit/', vehicle_type_management.VehicleTypeManagementUpdateView.as_view(), name='vehicle_type_update'),
    path('vehicule_type/<int:pk>/delete/', vehicle_type_management.VehicleTypeManagementDeleteView.as_view(), name='vehicle_type_delete'),
    path('vehicule_type/bulk-import/', vehicle_type_management.vehicle_type_bulk_import, name='vehicle_type_bulk_import'),
    
    # Vehicle Management (Admin Console) - Managing individual Vehicule records
    path('vehicule/', vehicle_types.VehicleTypeListView.as_view(), name='vehicle_list'),
    path('vehicule/create/', vehicle_types.VehicleTypeCreateView.as_view(), name='vehicle_create'),
    path('vehicule/bulk-import/', vehicle_types.vehicle_type_bulk_import, name='vehicle_bulk_import'),
    path('vehicule/<str:plaque>/', vehicle_types.VehicleTypeDetailView.as_view(), name='vehicle_detail'),
    path('vehicule/<str:plaque>/edit/', vehicle_types.VehicleTypeUpdateView.as_view(), name='vehicle_update'),
    path('vehicule/<str:plaque>/delete/', vehicle_types.VehicleTypeDeleteView.as_view(), name='vehicle_delete'),
    path('vehicule/export/', vehicle_types.vehicle_type_export, name='vehicle_export'),
    
    # Vehicle Management (Admin Console)
    path('individual-vehicles/', individual_vehicles.IndividualVehicleListView.as_view(), name='individual_vehicle_list'),
    path('individual-vehicles/create/', individual_vehicles.IndividualVehicleCreateView.as_view(), name='individual_vehicle_create'),
    path('individual-vehicles/search/', individual_vehicles.IndividualVehicleListView.as_view(), name='individual_vehicle_search'),

    path('individual-vehicles/bulk-operations/', individual_vehicles.individual_vehicle_bulk_operations, name='individual_vehicle_bulk_operations'),
    path('individual-vehicles/export/', individual_vehicles.individual_vehicle_export, name='individual_vehicle_export'),
    path('individual-vehicles/<str:plaque>/', individual_vehicles.IndividualVehicleDetailView.as_view(), name='individual_vehicle_detail'),
    path('individual-vehicles/<str:plaque>/edit/', individual_vehicles.IndividualVehicleUpdateView.as_view(), name='individual_vehicle_update'),
    path('individual-vehicles/<str:plaque>/delete/', individual_vehicles.IndividualVehicleDeleteView.as_view(), name='individual_vehicle_delete'),
    
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

    # Payment Settings - Stripe Configuration
    path('payment-settings/stripe/', payment_settings.StripeConfigManageView.as_view(), name='stripe_config_manage'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API endpoints
    path('api/stats/', views.dashboard_api_stats, name='api_stats'),
    path('api/vehicles/bulk-update/', vehicle_types.vehicle_type_bulk_update, name='vehicle_bulk_update'),
    path('api/price-grids/bulk-update/', price_grids.price_grid_bulk_update, name='price_grid_bulk_update'),
    path('api/users/bulk-operations/', users.user_bulk_operations, name='user_bulk_operations'),
    
    # Test components page
    path('test-components/', views.test_components_view, name='test_components'),
    
    # Placeholder URLs for base_admin.html navigation
    path('audit-logs/', views.dashboard_view, name='audit_log_list'),  # Placeholder
]