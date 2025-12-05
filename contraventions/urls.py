from django.urls import include, path

from . import views

app_name = "contraventions"

# URL patterns for agent views
agent_patterns = [
    path("", views.ContraventionListView.as_view(), name="list"),
    path("create/", views.ContraventionCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ContraventionDetailView.as_view(), name="detail"),
    path("<int:pk>/cancel/", views.ContraventionCancelView.as_view(), name="cancel"),
]

# URL patterns for fourriere
fourriere_patterns = [
    path("", views.DossierFourriereListView.as_view(), name="fourriere_list"),
    path("create/<int:contravention_id>/", views.DossierFourriereCreateView.as_view(), name="fourriere_create"),
    path("<int:pk>/", views.DossierFourriereDetailView.as_view(), name="fourriere_detail"),
]

# URL patterns for public views
public_patterns = [
    path("<str:numero_pv>/", views.ContraventionPublicDetailView.as_view(), name="public_detail"),
    path("<str:numero_pv>/contest/", views.ContestationPublicView.as_view(), name="contest"),
]

# URL patterns for admin views
admin_patterns = [
    path("infractions/", views.InfractionManagementView.as_view(), name="admin_infraction_list"),
    path("infractions/<uuid:pk>/activate/", views.infraction_activate, name="admin_infraction_activate"),
    path("infractions/<uuid:pk>/desactivate/", views.infraction_desactivate, name="admin_infraction_desactivate"),
    path("reports/", views.ContraventionReportView.as_view(), name="admin_report_dashboard"),
    path("contestations/", views.ContestationManagementView.as_view(), name="admin_contestation_list"),
    path("contestations/<int:pk>/", views.ContestationDetailView.as_view(), name="admin_contestation_detail"),
    path("configuration/", views.ConfigurationView.as_view(), name="admin_configuration"),
    path("maintenance-action/", views.admin_maintenance_action, name="admin_maintenance_action"),
]

# AJAX endpoints
ajax_patterns = [
    path("search-vehicle/", views.search_vehicle, name="ajax_search_vehicle"),
    path("search-conducteur/", views.search_conducteur, name="ajax_search_conducteur"),
    path("get-infraction-details/", views.get_infraction_details, name="ajax_get_infraction_details"),
    path("check-recidive/", views.check_recidive, name="ajax_check_recidive"),
]

# Main URL patterns
urlpatterns = [
    # Agent views
    path("", views.ContraventionListView.as_view(), name="list"),
    path("create/", views.ContraventionCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ContraventionDetailView.as_view(), name="detail"),
    path("<int:pk>/cancel/", views.ContraventionCancelView.as_view(), name="cancel"),
    # Fourriere
    path("fourriere/", include(fourriere_patterns)),
    # Public views
    path("public/", include(public_patterns)),
    # Admin views
    path("admin/", include(admin_patterns)),
    # AJAX endpoints
    path("ajax/", include(ajax_patterns)),
]
