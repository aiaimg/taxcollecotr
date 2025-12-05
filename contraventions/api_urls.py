from django.urls import include, path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api_views

app_name = "contraventions_api"

urlpatterns = [
    # Authentication
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Contravention endpoints
    path("contraventions/", api_views.APIContraventionListView.as_view(), name="api_contraventions_list"),
    path(
        "contraventions/<str:numero_pv>/",
        api_views.APIContraventionDetailView.as_view(),
        name="api_contravention_detail",
    ),
    path("contraventions/create/", api_views.APIContraventionCreateView.as_view(), name="api_contravention_create"),
    path(
        "contraventions/<str:numero_pv>/payment/",
        api_views.APIContraventionPaymentView.as_view(),
        name="api_contravention_payment",
    ),
    # Payment verification
    path("payments/verify/", api_views.APIPaymentVerificationView.as_view(), name="api_payment_verify"),
    # QR Code verification
    path("qr/verify/", api_views.APIQRVerificationView.as_view(), name="api_qr_verify"),
    # Contestation endpoints
    path("contestations/", api_views.APIContestationCreateView.as_view(), name="api_contestation_create"),
    path(
        "contestations/<str:numero_pv>/",
        api_views.APIContestationCreateView.as_view(),
        name="api_contestation_create_for_contravention",
    ),
    # Statistics
    path("stats/agent/", api_views.APIAgentStatsView.as_view(), name="api_agent_stats"),
    # Search endpoints
    path("search/vehicles/", api_views.APIVehicleSearchView.as_view(), name="api_vehicle_search"),
    path("search/conducteurs/", api_views.APIConducteurSearchView.as_view(), name="api_conducteur_search"),
    # Utility endpoints
    path("utils/check-recidive/", api_views.check_recidive, name="api_check_recidive"),
    path("utils/infraction-details/", api_views.get_infraction_details, name="api_infraction_details"),
]
