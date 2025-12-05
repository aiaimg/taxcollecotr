from django.urls import include, path

from . import views

app_name = "vehicles"

urlpatterns = [
    # Vehicle management URLs
    path("", views.VehiculeListView.as_view(), name="vehicle_list"),
    path("drafts/", views.DraftVehicleListView.as_view(), name="draft_vehicle_list"),
    path("history/", views.DeclarationHistoryView.as_view(), name="declaration_history"),
    path("history/export/", views.DeclarationHistoryExportView.as_view(), name="declaration_history_export"),
    path("category-selection/", views.VehicleCategorySelectionView.as_view(), name="category_selection"),
    path("add/", views.VehiculeCreateView.as_view(), name="vehicle_create"),
    path("add/terrestrial/", views.VehiculeCreateView.as_view(), name="vehicle_create_terrestrial"),
    path("add/aerial/", views.VehiculeAerienCreateView.as_view(), name="vehicle_create_aerial"),
    path("add/maritime/", views.VehiculeMaritimeCreateView.as_view(), name="vehicle_create_maritime"),
    path("<str:pk>/", views.VehiculeDetailView.as_view(), name="vehicle_detail"),
    path("<str:pk>/documents/upload/", views.upload_vehicle_document, name="vehicle_document_upload"),
    path("<str:pk>/edit/", views.VehiculeUpdateView.as_view(), name="vehicle_edit"),
    path("<str:pk>/delete/", views.VehiculeDeleteView.as_view(), name="vehicle_delete"),
    # AJAX endpoints
    path("ajax/calculate-tax/", views.calculate_tax_ajax, name="calculate_tax_ajax"),
    path("ajax/classify-maritime/", views.classify_maritime_ajax, name="classify_maritime_ajax"),
    path("ajax/convert-power/", views.convert_power_ajax, name="convert_power_ajax"),
    path("ajax/ocr/carte-grise/", views.process_carte_grise_ocr, name="process_carte_grise_ocr"),
    # Document management AJAX endpoints
    path("<str:pk>/documents/", views.get_vehicle_documents, name="vehicle_documents_list"),
    path("<str:pk>/documents/upload-ajax/", views.upload_vehicle_document_ajax, name="vehicle_document_upload_ajax"),
    path("<str:pk>/documents/<uuid:document_id>/", views.update_vehicle_document, name="vehicle_document_update"),
    path(
        "<str:pk>/documents/<uuid:document_id>/delete/", views.delete_vehicle_document, name="vehicle_document_delete"
    ),
    # API endpoints
    path("api/", include("vehicles.api_urls", namespace="api")),
]
