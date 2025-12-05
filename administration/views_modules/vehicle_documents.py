from datetime import timedelta

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView

from administration.mixins import AdminRequiredMixin
from vehicles.models import DocumentVehicule, VehicleType


class VehicleDocumentListView(AdminRequiredMixin, ListView):
    """Admin list view for vehicle documents with filters and pagination."""

    model = DocumentVehicule
    template_name = "administration/vehicle_documents/list.html"
    context_object_name = "documents"
    paginate_by = 25

    def get_paginate_by(self, queryset):
        try:
            page_size = int(self.request.GET.get("page_size", self.paginate_by))
        except (TypeError, ValueError):
            page_size = self.paginate_by
        return page_size if page_size in (25, 50, 100) else self.paginate_by

    def get_queryset(self):
        qs = DocumentVehicule.objects.select_related("vehicule", "uploaded_by", "vehicule__type_vehicule").order_by(
            "-created_at"
        )

        params = self.request.GET
        document_type = params.get("document_type")
        verification_status = params.get("verification_status")
        vehicle_type = params.get("vehicle_type")
        expiration = params.get("expiration")  # 'expired', 'expiring_soon', or None
        search = params.get("q")

        if document_type:
            qs = qs.filter(document_type=document_type)

        if verification_status:
            qs = qs.filter(verification_status=verification_status)

        if vehicle_type:
            qs = qs.filter(vehicule__type_vehicule_id=vehicle_type)

        if expiration == "expired":
            qs = qs.filter(expiration_date__isnull=False, expiration_date__lt=timezone.now().date())
        elif expiration == "expiring_soon":
            soon = timezone.now().date() + timedelta(days=30)
            qs = qs.filter(
                expiration_date__isnull=False, expiration_date__lte=soon, expiration_date__gte=timezone.now().date()
            )

        if search:
            qs = qs.filter(
                Q(vehicule__plaque_immatriculation__icontains=search)
                | Q(uploaded_by__username__icontains=search)
                | Q(note__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Choices for filters
        context["document_type_choices"] = DocumentVehicule.DOCUMENT_TYPE_CHOICES
        context["verification_status_choices"] = DocumentVehicule.VERIFICATION_STATUS_CHOICES
        context["vehicle_types"] = VehicleType.objects.filter(est_actif=True).order_by("ordre_affichage", "nom")
        context["today"] = timezone.now().date()
        context["page_size_choices"] = [25, 50, 100]

        # Current filter values
        params = self.request.GET
        context["current_filters"] = {
            "document_type": params.get("document_type", ""),
            "verification_status": params.get("verification_status", ""),
            "vehicle_type": params.get("vehicle_type", ""),
            "expiration": params.get("expiration", ""),
            "q": params.get("q", ""),
            "page_size": params.get("page_size", str(self.get_paginate_by(self.get_queryset()))),
        }

        # Page title and breadcrumbs
        context["page_title"] = "Documents des Véhicules"
        context["page_subtitle"] = "Vérification, conformité et pièces jointes"

        return context
