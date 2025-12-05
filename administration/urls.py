from django.urls import path
from django.views.generic import RedirectView

from vehicles import views as vehicle_views

from . import auth_views, views
from .views_modules import (
    advanced_vehicle_search,
    payment_settings,
    price_grids,
    users,
    vehicle_documents,
    vehicle_type_management,
)

app_name = "administration"

urlpatterns = [
    # Admin Authentication
    path("admin_login/", auth_views.AdminLoginView.as_view(), name="admin_login"),
    path("login/", auth_views.AdminLoginView.as_view(), name="admin_login_alt"),  # Alternative URL
    path("logout/", auth_views.AdminLogoutView.as_view(), name="admin_logout"),
    path("access-check/", auth_views.admin_required_view, name="admin_required"),
    # Agent Authentication
    path("agent-partenaire/login/", auth_views.AgentPartenaireLoginView.as_view(), name="agent_partenaire_login"),
    path("agent-government/login/", auth_views.AgentGovernmentLoginView.as_view(), name="agent_government_login"),
    # Dashboard
    path("", views.dashboard_view, name="dashboard"),
    # Admin Vehicle Management - Direct vehicle operations for admins
    path("vehicules/", vehicle_views.AdminVehiculeListView.as_view(), name="admin_vehicle_list"),
    path("vehicules/add/", vehicle_views.AdminVehiculeCreateView.as_view(), name="admin_vehicle_create"),
    path("vehicules/<str:pk>/", vehicle_views.AdminVehiculeDetailView.as_view(), name="admin_vehicle_detail"),
    path("vehicules/<str:pk>/edit/", vehicle_views.AdminVehiculeUpdateView.as_view(), name="admin_vehicle_edit"),
    path("vehicules/<str:pk>/delete/", vehicle_views.AdminVehiculeDeleteView.as_view(), name="admin_vehicle_delete"),
    # Advanced Vehicle Search - Vue globale avec filtres avancés
    path(
        "vehicules/search/advanced/",
        advanced_vehicle_search.AdvancedVehicleSearchView.as_view(),
        name="advanced_vehicle_search",
    ),
    path(
        "vehicules/search/stats/",
        advanced_vehicle_search.advanced_vehicle_search_stats,
        name="advanced_vehicle_search_stats",
    ),
    path(
        "vehicules/search/export/",
        advanced_vehicle_search.advanced_vehicle_search_export,
        name="advanced_vehicle_search_export",
    ),
    # Management views - Vehicles (legacy)
    path("vehicles/", views.VehicleManagementView.as_view(), name="vehicle_management"),
    # Removed: Enhanced/Advanced Vehicle Management routes (deprecated)
    # Vehicle Types Management (Admin Console) - Managing VehicleType records
    path("vehicule_type/", vehicle_type_management.VehicleTypeManagementListView.as_view(), name="vehicle_type_list"),
    path(
        "vehicule_type/create/",
        vehicle_type_management.VehicleTypeManagementCreateView.as_view(),
        name="vehicle_type_create",
    ),
    path(
        "vehicule_type/<int:pk>/",
        vehicle_type_management.VehicleTypeManagementDetailView.as_view(),
        name="vehicle_type_detail",
    ),
    path(
        "vehicule_type/<int:pk>/edit/",
        vehicle_type_management.VehicleTypeManagementUpdateView.as_view(),
        name="vehicle_type_update",
    ),
    path(
        "vehicule_type/<int:pk>/delete/",
        vehicle_type_management.VehicleTypeManagementDeleteView.as_view(),
        name="vehicle_type_delete",
    ),
    path(
        "vehicule_type/bulk-import/", vehicle_type_management.vehicle_type_bulk_import, name="vehicle_type_bulk_import"
    ),
    # DEPRECATED: Redirects to main vehicle management
    # Old vehicle management routes - redirect to vehicules/
    path("vehicule/", RedirectView.as_view(pattern_name="administration:admin_vehicle_list", permanent=True)),
    path("vehicule/create/", RedirectView.as_view(pattern_name="administration:admin_vehicle_create", permanent=True)),
    path(
        "vehicule/<str:plaque>/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_detail", permanent=True),
    ),
    path(
        "vehicule/<str:plaque>/edit/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_edit", permanent=True),
    ),
    path(
        "vehicule/<str:plaque>/delete/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_delete", permanent=True),
    ),
    # Old individual-vehicles routes - redirect to vehicules/
    path(
        "individual-vehicles/", RedirectView.as_view(pattern_name="administration:admin_vehicle_list", permanent=True)
    ),
    path(
        "individual-vehicles/create/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_create", permanent=True),
    ),
    path(
        "individual-vehicles/<str:plaque>/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_detail", permanent=True),
    ),
    path(
        "individual-vehicles/<str:plaque>/edit/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_edit", permanent=True),
    ),
    path(
        "individual-vehicles/<str:plaque>/delete/",
        RedirectView.as_view(pattern_name="administration:admin_vehicle_delete", permanent=True),
    ),
    # Vehicle Documents Management (Admin Console)
    path("vehicle-documents/", vehicle_documents.VehicleDocumentListView.as_view(), name="vehicle_document_list"),
    # Price Grids Management (Admin Console)
    path("price-grids/", price_grids.PriceGridListView.as_view(), name="price_grid_list"),
    path("price-grids/create/", price_grids.PriceGridCreateView.as_view(), name="price_grid_create"),
    path("price-grids/<int:pk>/", price_grids.PriceGridDetailView.as_view(), name="price_grid_detail"),
    path("price-grids/<int:pk>/edit/", price_grids.PriceGridUpdateView.as_view(), name="price_grid_update"),
    path("price-grids/<int:pk>/delete/", price_grids.PriceGridDeleteView.as_view(), name="price_grid_delete"),
    path("price-grids-export/", price_grids.price_grid_export, name="price_grid_export"),
    path("price-grids-import/", price_grids.price_grid_import, name="price_grid_import"),
    path("price-grids-report/", price_grids.price_grid_report, name="price_grid_report"),
    # Unified Tariff Grid Management (Multi-Vehicle)
    path("tariff-grids/", price_grids.admin_tariff_grid_management, name="admin_tariff_grid_management"),
    path("tariff-grids/<int:grid_id>/toggle/", price_grids.toggle_tariff_grid_status, name="toggle_tariff_grid_status"),
    path("tariff-grids/<int:grid_id>/delete/", price_grids.delete_tariff_grid, name="delete_tariff_grid"),
    # Declaration Validation Queue
    path(
        "declarations/validation/", views.admin_declaration_validation_queue, name="admin_declaration_validation_queue"
    ),
    path(
        "declarations/<str:vehicle_pk>/validate/",
        views.validate_vehicle_declaration,
        name="validate_vehicle_declaration",
    ),
    path("declarations/<str:vehicle_pk>/reject/", views.reject_vehicle_declaration, name="reject_vehicle_declaration"),
    # Multi-Vehicle Statistics Dashboard
    path(
        "statistics/multi-vehicle/", views.multi_vehicle_statistics_dashboard, name="multi_vehicle_statistics_dashboard"
    ),
    # Users Management (Admin Console)
    path("users/", users.UserListView.as_view(), name="user_list"),
    path("users/<int:user_id>/", users.user_detail_view, name="user_detail"),
    path("users/<int:user_id>/edit/", users.UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:user_id>/toggle-status/", users.toggle_user_status, name="user_toggle_status"),
    path("users/<int:user_id>/activity-stats/", users.user_activity_stats, name="user_activity_stats"),
    path("users/<int:user_id>/reset-password/", users.reset_user_password, name="user_reset_password"),
    path("users/<int:user_id>/permissions/", users.user_permissions_view, name="user_permissions"),
    path("users/export/", users.user_export, name="user_export"),
    # Legacy user management view
    path("user-management/", views.UserManagementView.as_view(), name="user_management"),
    path("user-management/<int:user_id>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),
    # Management views - Payments
    path("payments/", views.PaymentManagementView.as_view(), name="payment_management"),
    # Payment Settings - Stripe Configuration
    path("payment-settings/stripe/", payment_settings.StripeConfigManageView.as_view(), name="stripe_config_manage"),
    # Payment Gateways Management
    path("payment-gateways/", views.payment_gateways_view, name="payment_gateways"),
    path("payment-gateways/mvola/<int:config_id>/", views.mvola_config_detail_view, name="mvola_config_detail"),
    path("payment-gateways/mvola/<int:config_id>/test/", views.mvola_config_test_view, name="mvola_config_test"),
    path("payment-gateways/mvola/<int:config_id>/toggle/", views.mvola_config_toggle_view, name="mvola_config_toggle"),
    # Analytics
    path("analytics/", views.analytics_view, name="analytics"),
    # API endpoints
    path("api/stats/", views.dashboard_api_stats, name="api_stats"),
    path("api/vehicles/bulk-update/", vehicle_type_management.vehicle_type_bulk_import, name="vehicle_bulk_update"),
    path("api/price-grids/bulk-update/", price_grids.price_grid_bulk_update, name="price_grid_bulk_update"),
    path("api/users/bulk-operations/", users.user_bulk_operations, name="user_bulk_operations"),
    # Test components page
    path("test-components/", views.test_components_view, name="test_components"),
    # Removed duplicate/placeholder: audit-logs now unified with dashboard
]
