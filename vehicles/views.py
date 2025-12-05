from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from .forms import (
    VehicleDocumentUpdateForm,
    VehicleDocumentUploadForm,
    VehiculeAerienForm,
    VehiculeForm,
    VehiculeMaritimeForm,
    VehiculeSearchForm,
)
from .models import EXEMPT_VEHICLE_CATEGORIES, DocumentVehicule, GrilleTarifaire, Vehicule


class VehicleCategorySelectionView(LoginRequiredMixin, TemplateView):
    """Vue pour sélectionner la catégorie de véhicule à déclarer"""

    template_name = "vehicles/category_selection.html"
    login_url = reverse_lazy("core:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Count vehicles by category for the current user
        user_vehicles = Vehicule.objects.filter(proprietaire=self.request.user, est_actif=True)

        terrestrial_count = user_vehicles.filter(vehicle_category="TERRESTRE").count()
        aerial_count = user_vehicles.filter(vehicle_category="AERIEN").count()
        maritime_count = user_vehicles.filter(vehicle_category="MARITIME").count()

        context["categories"] = [
            {
                "code": "TERRESTRE",
                "name": _("Véhicule Terrestre"),
                "description": _("Voiture, moto, camion, bus, etc."),
                "icon": "ri-car-line",
                "url": reverse("vehicles:vehicle_create_terrestrial"),
                "count": terrestrial_count,
            },
            {
                "code": "AERIEN",
                "name": _("Véhicule Aérien"),
                "description": _("Avion, hélicoptère, drone, ULM, etc."),
                "icon": "ri-plane-line",
                "url": reverse("vehicles:vehicle_create_aerial"),
                "count": aerial_count,
            },
            {
                "code": "MARITIME",
                "name": _("Véhicule Maritime"),
                "description": _("Bateau, navire, yacht, jet-ski, etc."),
                "icon": "ri-ship-line",
                "url": reverse("vehicles:vehicle_create_maritime"),
                "count": maritime_count,
            },
        ]
        context["page_title"] = _("Déclarer un Véhicule")
        return context


class VehiculeListView(LoginRequiredMixin, ListView):
    """List user's vehicles with search functionality"""

    model = Vehicule
    template_name = "vehicles/vehicule_list.html"
    context_object_name = "vehicules"
    paginate_by = 10
    login_url = reverse_lazy("core:login")

    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user

        if is_admin_user(self.request.user):
            return ["administration/vehicles/vehicule_list.html"]
        # Regular users (including company users) should use regular templates
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle list"""
        from administration.mixins import is_admin_user

        if is_admin_user(request.user):
            return redirect("administration:admin_vehicle_list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Filter vehicles by current user and search criteria"""
        # All users (including company users) should only see their own vehicles
        queryset = Vehicule.objects.filter(proprietaire=self.request.user, est_actif=True).order_by("-created_at")

        # Apply search filters
        form = VehiculeSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get("search")
            if search:
                queryset = queryset.filter(
                    Q(plaque_immatriculation__icontains=search)
                    | Q(immatriculation_aerienne__icontains=search)
                    | Q(numero_francisation__icontains=search)
                    | Q(nom_navire__icontains=search)
                    | Q(marque__icontains=search)
                    | Q(nom_proprietaire__icontains=search)
                )

            marque = form.cleaned_data.get("marque")
            if marque:
                queryset = queryset.filter(marque__icontains=marque)

            source_energie = form.cleaned_data.get("source_energie")
            if source_energie:
                queryset = queryset.filter(source_energie=source_energie)

            categorie_vehicule = form.cleaned_data.get("categorie_vehicule")
            if categorie_vehicule:
                queryset = queryset.filter(categorie_vehicule=categorie_vehicule)

            type_vehicule = form.cleaned_data.get("type_vehicule")
            if type_vehicule:
                queryset = queryset.filter(type_vehicule=type_vehicule)

            # Filter by vehicle category (TERRESTRE/AERIEN/MARITIME)
            vehicle_category = self.request.GET.get("vehicle_category")
            if vehicle_category:
                queryset = queryset.filter(vehicle_category=vehicle_category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = VehiculeSearchForm(self.request.GET)
        context["page_title"] = _("Mes Véhicules")
        context["vehicle_category_filter"] = self.request.GET.get("vehicle_category", "")

        # Count vehicles by category for filter display
        user_vehicles = Vehicule.objects.filter(proprietaire=self.request.user, est_actif=True)
        context["terrestrial_count"] = user_vehicles.filter(vehicle_category="TERRESTRE").count()
        context["aerial_count"] = user_vehicles.filter(vehicle_category="AERIEN").count()
        context["maritime_count"] = user_vehicles.filter(vehicle_category="MARITIME").count()

        return context


class DraftVehicleListView(LoginRequiredMixin, ListView):
    """List user's draft vehicles"""

    model = Vehicule
    template_name = "vehicles/draft_vehicle_list.html"
    context_object_name = "draft_vehicles"
    paginate_by = 20
    login_url = reverse_lazy("core:login")

    def get_queryset(self):
        """Filter vehicles by current user and draft status"""
        from datetime import timedelta

        queryset = Vehicule.objects.filter(
            proprietaire=self.request.user, statut_declaration="BROUILLON", est_actif=True
        ).order_by("-updated_at")

        # Annotate with age warning (drafts older than 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        for vehicle in queryset:
            vehicle.is_old_draft = vehicle.updated_at < thirty_days_ago

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Mes Brouillons")

        # Count drafts by category
        draft_vehicles = Vehicule.objects.filter(
            proprietaire=self.request.user, statut_declaration="BROUILLON", est_actif=True
        )
        context["terrestrial_draft_count"] = draft_vehicles.filter(vehicle_category="TERRESTRE").count()
        context["aerial_draft_count"] = draft_vehicles.filter(vehicle_category="AERIEN").count()
        context["maritime_draft_count"] = draft_vehicles.filter(vehicle_category="MARITIME").count()
        context["total_draft_count"] = draft_vehicles.count()

        return context


class VehiculeDetailView(LoginRequiredMixin, DetailView):
    """Vehicle detail view with tax calculation"""

    model = Vehicule
    template_name = "vehicles/vehicule_detail.html"
    context_object_name = "vehicule"
    login_url = reverse_lazy("core:login")

    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user

        if is_admin_user(self.request.user):
            return ["administration/vehicles/vehicule_detail.html"]
        # Regular users (including company users) should use regular templates
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle detail"""
        from administration.mixins import is_admin_user

        if is_admin_user(request.user):
            return redirect("administration:admin_vehicle_detail", pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Only show user's own vehicles"""
        return Vehicule.objects.filter(proprietaire=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = self.get_object()

        # Calculate current year tax
        current_year = timezone.now().year
        tax_amount = self.calculate_tax(vehicule, current_year)

        # Get payment status
        payment_status = vehicule.get_current_payment_status()
        current_payment = vehicule.current_payment

        # Get recent payments for this vehicle
        from payments.models import PaiementTaxe

        payments = PaiementTaxe.objects.filter(vehicule_plaque=vehicule).order_by("-created_at")[:5]

        # Get vehicle identifier based on category
        vehicle_identifier = vehicule.plaque_immatriculation
        if vehicule.vehicle_category == "AERIEN":
            vehicle_identifier = vehicule.immatriculation_aerienne or vehicule.plaque_immatriculation
        elif vehicule.vehicle_category == "MARITIME":
            vehicle_identifier = vehicule.nom_navire or vehicule.numero_francisation or vehicule.plaque_immatriculation

        # Get maritime classification if applicable
        maritime_classification = None
        if vehicule.vehicle_category == "MARITIME" and vehicule.specifications_techniques:
            maritime_classification = vehicule.specifications_techniques.get("maritime_classification")

        # Get required documents and validation status
        is_valid, missing_docs = vehicule.validate_required_documents()
        required_doc_types = vehicule.get_required_documents_by_category()

        # Get uploaded documents
        uploaded_documents = DocumentVehicule.objects.filter(vehicule=vehicule).order_by("-created_at")
        uploaded_doc_types = set(uploaded_documents.values_list("document_type", flat=True))

        # Build required documents list with status
        from vehicles.models import DocumentVehicule as DocModel

        doc_choices_dict = dict(DocModel.DOCUMENT_TYPE_CHOICES)
        required_documents = []

        for doc_type in required_doc_types:
            doc_info = {
                "code": doc_type,
                "name": doc_choices_dict.get(doc_type, doc_type),
                "uploaded": doc_type in uploaded_doc_types,
                "is_expired": False,
            }

            # Check if document is expired (for certificates)
            if doc_type in uploaded_doc_types:
                doc = uploaded_documents.filter(document_type=doc_type).first()
                if doc and doc.expiration_date:
                    from datetime import date

                    today = date.today()
                    if doc.expiration_date < today:
                        doc_info["is_expired"] = True

            required_documents.append(doc_info)

        context.update(
            {
                "page_title": f'{_("Véhicule")} {vehicle_identifier}',
                "current_year": current_year,
                "tax_amount": tax_amount,
                "is_exempt": vehicule.est_exonere(),
                "documents": uploaded_documents,
                "document_form": VehicleDocumentUploadForm(),
                "payment_status": payment_status,
                "current_payment": current_payment,
                "payments": payments,
                "vehicle_category": vehicule.vehicle_category,
                "maritime_classification": maritime_classification,
                "required_documents": required_documents,
                "missing_documents": missing_docs,
                "documents_valid": is_valid,
            }
        )

        return context

    def calculate_tax(self, vehicule, year):
        """Calculate tax amount for a vehicle based on category"""
        if vehicule.est_exonere():
            return Decimal("0.00")

        try:
            # Use TaxCalculationService for proper calculation
            from vehicles.services import TaxCalculationService

            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicule, year)

            if tax_info and "amount" in tax_info:
                return tax_info["amount"]

            # Fallback to old method for terrestrial vehicles
            if vehicule.vehicle_category == "TERRESTRE":
                tax_grid = GrilleTarifaire.objects.filter(annee_fiscale=year, est_active=True)

                for rate in tax_grid:
                    if rate.est_applicable(vehicule):
                        return rate.montant_ariary

            # No applicable rate found
            return None

        except Exception:
            return None


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
@require_POST
def upload_vehicle_document(request, pk):
    """Upload a document for a specific vehicle (owner or admin)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)

    # Permissions: owner or admin users
    from administration.mixins import is_admin_user

    if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
        messages.error(request, _("Permission refusée pour télécharger un document pour ce véhicule."))
        return redirect("vehicles:vehicle_detail", pk=pk)

    form = VehicleDocumentUploadForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.vehicule = vehicule
        doc.uploaded_by = request.user
        doc.save()

        # Send notification to owner
        try:
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(vehicule.proprietaire, "profile"):
                langue = vehicule.proprietaire.profile.langue_preferee
            NotificationService.create_notification(
                user=vehicule.proprietaire,
                type_notification="document_uploaded",
                titre=_("Nouveau document pour votre véhicule"),
                contenu=_("Le document %(doc)s a été ajouté pour le véhicule %(plaque)s.")
                % {"doc": doc.get_document_type_display(), "plaque": vehicule.plaque_immatriculation},
                langue=langue,
                metadata={"vehicule": vehicule.plaque_immatriculation, "document_id": str(doc.id)},
            )
        except Exception:
            # Do not block on notification errors
            pass

        messages.success(request, _("Document téléchargé avec succès."))
    else:
        messages.error(request, _("Échec du téléchargement du document. Veuillez vérifier les informations."))

    return redirect("vehicles:vehicle_detail", pk=pk)


class VehiculeCreateView(LoginRequiredMixin, CreateView):
    """Create new vehicle"""

    model = Vehicule
    form_class = VehiculeForm
    template_name = "vehicles/vehicule_form.html"
    login_url = reverse_lazy("core:login")

    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user

        if is_admin_user(self.request.user):
            return ["administration/vehicles/vehicule_form.html"]
        # Regular users (including company users) should use regular templates
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle creation"""
        from administration.mixins import is_admin_user

        if is_admin_user(request.user):
            return redirect("administration:admin_vehicle_create")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set the owner based on user permissions"""
        from administration.mixins import is_admin_user

        # Check if saving as draft
        is_draft = "save_draft" in self.request.POST

        if is_admin_user(self.request.user):
            # Admin can assign vehicle to selected owner
            if form.cleaned_data.get("proprietaire"):
                form.instance.proprietaire = form.cleaned_data["proprietaire"]
            else:
                # If no owner selected, assign to admin (fallback)
                form.instance.proprietaire = self.request.user
        else:
            # Non-admin users can only create vehicles for themselves
            form.instance.proprietaire = self.request.user

        # Set status based on whether it's a draft or submission
        if is_draft:
            form.instance.statut_declaration = "BROUILLON"
        else:
            form.instance.statut_declaration = "SOUMISE"

        response = super().form_valid(form)

        # Only create notification for submitted declarations, not drafts
        if not is_draft:
            # Create notification for vehicle added
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(self.request.user, "profile"):
                langue = self.request.user.profile.langue_preferee

            NotificationService.create_vehicle_added_notification(
                user=form.instance.proprietaire,  # Send notification to the actual owner
                vehicle=form.instance,
                langue=langue,
            )

        # Success message varies based on draft or submission
        if is_draft:
            messages.success(self.request, _("Brouillon sauvegardé avec succès! Vous pouvez le reprendre plus tard."))
        else:
            # Success message varies based on who added the vehicle
            if is_admin_user(self.request.user) and form.instance.proprietaire != self.request.user:
                messages.success(
                    self.request,
                    _("Véhicule %(plaque)s ajouté avec succès pour %(owner)s!")
                    % {
                        "plaque": form.instance.plaque_immatriculation,
                        "owner": form.instance.proprietaire.get_full_name() or form.instance.proprietaire.username,
                    },
                )
            else:
                messages.success(
                    self.request,
                    _("Véhicule %(plaque)s ajouté avec succès!") % {"plaque": form.instance.plaque_immatriculation},
                )
        return response

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Ajouter un Véhicule")
        context["form_action"] = _("Ajouter")
        context["current_year"] = timezone.now().year
        return context


class VehiculeAerienCreateView(LoginRequiredMixin, CreateView):
    """Création de véhicule aérien"""

    model = Vehicule
    form_class = VehiculeAerienForm
    template_name = "vehicles/vehicule_aerien_form.html"
    login_url = reverse_lazy("core:login")

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set vehicle category and owner"""
        form.instance.vehicle_category = "AERIEN"
        form.instance.proprietaire = self.request.user

        # Check if saving as draft
        is_draft = "save_draft" in self.request.POST

        # Set status based on whether it's a draft or submission
        if is_draft:
            form.instance.statut_declaration = "BROUILLON"
        else:
            form.instance.statut_declaration = "SOUMISE"

        response = super().form_valid(form)

        # Only create notification for submitted declarations, not drafts
        if not is_draft:
            # Create notification for vehicle added
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(self.request.user, "profile"):
                langue = self.request.user.profile.langue_preferee

            NotificationService.create_vehicle_added_notification(
                user=self.request.user, vehicle=form.instance, langue=langue
            )

        # Success message varies based on draft or submission
        if is_draft:
            messages.success(self.request, _("Brouillon sauvegardé avec succès! Vous pouvez le reprendre plus tard."))
        else:
            messages.success(
                self.request,
                _("Aéronef %(immat)s ajouté avec succès!") % {"immat": form.instance.immatriculation_aerienne},
            )
        return response

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Déclarer un Véhicule Aérien")
        context["form_action"] = _("Déclarer")
        context["current_year"] = timezone.now().year
        context["vehicle_category"] = "AERIEN"
        return context


class VehiculeMaritimeCreateView(LoginRequiredMixin, CreateView):
    """Création de véhicule maritime"""

    model = Vehicule
    form_class = VehiculeMaritimeForm
    template_name = "vehicles/vehicule_maritime_form.html"
    login_url = reverse_lazy("core:login")

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set vehicle category, owner, and classification"""
        form.instance.vehicle_category = "MARITIME"
        form.instance.proprietaire = self.request.user

        # Check if saving as draft
        is_draft = "save_draft" in self.request.POST

        # Get maritime classification
        classification = form.get_maritime_classification()
        if not form.instance.specifications_techniques:
            form.instance.specifications_techniques = {}
        form.instance.specifications_techniques["maritime_classification"] = classification

        # Set status based on whether it's a draft or submission
        if is_draft:
            form.instance.statut_declaration = "BROUILLON"
        else:
            form.instance.statut_declaration = "SOUMISE"

        response = super().form_valid(form)

        # Only create notifications for submitted declarations, not drafts
        if not is_draft:
            # Create notifications for vehicle added and maritime classification
            from notifications.services import NotificationService
            from vehicles.services import TaxCalculationService

            langue = "fr"
            if hasattr(self.request.user, "profile"):
                langue = self.request.user.profile.langue_preferee

            # General vehicle added notification
            NotificationService.create_vehicle_added_notification(
                user=self.request.user, vehicle=form.instance, langue=langue
            )

            # Calculate tax to get the amount for the classification notification
            tax_service = TaxCalculationService()
            tax_info = tax_service.calculate_maritime_tax(form.instance)
            tax_amount = tax_info.get("amount", 0)

            # Maritime classification notification with tax amount and contestation option
            NotificationService.create_maritime_classification_notification(
                user=self.request.user,
                vehicle=form.instance,
                classification=classification,
                tax_amount=tax_amount,
                langue=langue,
            )

        # Success message varies based on draft or submission
        if is_draft:
            messages.success(self.request, _("Brouillon sauvegardé avec succès! Vous pouvez le reprendre plus tard."))
        else:
            # Display classification in success message
            classification_display = {
                "NAVIRE_PLAISANCE": _("Navire de plaisance"),
                "JETSKI": _("Jet-ski"),
                "AUTRES_ENGINS": _("Autres engins maritimes"),
            }.get(classification, classification)

            messages.success(
                self.request,
                _("Navire %(nom)s ajouté avec succès! Classification: %(classification)s")
                % {
                    "nom": form.instance.nom_navire or form.instance.numero_francisation,
                    "classification": classification_display,
                },
            )
        return response

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Déclarer un Véhicule Maritime")
        context["form_action"] = _("Déclarer")
        context["current_year"] = timezone.now().year
        context["vehicle_category"] = "MARITIME"
        return context


class VehiculeUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing vehicle"""

    model = Vehicule
    form_class = VehiculeForm
    template_name = "vehicles/vehicule_form.html"
    login_url = reverse_lazy("core:login")

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_template_names(self):
        """Use Velzon template for fleet managers (non-individual users)"""
        if hasattr(self.request.user, "profile") and self.request.user.profile.user_type != "individual":
            return ["administration/vehicles/vehicule_form.html"]
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle edit"""
        from administration.mixins import is_admin_user

        if is_admin_user(request.user):
            return redirect("administration:admin_vehicle_edit", pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Only allow editing user's own vehicles, or all vehicles for fleet managers"""
        # For fleet management: users with non-individual profiles can edit any vehicle
        if hasattr(self.request.user, "profile") and self.request.user.profile.user_type != "individual":
            return Vehicule.objects.all()
        else:
            # Individual users can only edit their own vehicles
            return Vehicule.objects.filter(proprietaire=self.request.user)

    def form_valid(self, form):
        # Check if saving as draft or submitting
        is_draft = "save_draft" in self.request.POST
        was_draft = form.instance.statut_declaration == "BROUILLON"

        # If submitting (not saving as draft), validate required documents
        if not is_draft:
            is_valid, missing_documents = form.instance.validate_required_documents()
            if not is_valid:
                # Build error message with missing documents
                missing_doc_names = [doc["name"] for doc in missing_documents]
                error_message = _(
                    "Documents requis manquants: %(docs)s. Veuillez télécharger tous les documents requis avant de soumettre."
                ) % {"docs": ", ".join(missing_doc_names)}
                messages.error(self.request, error_message)
                # Return to form with error
                return self.form_invalid(form)

        # Update status based on action
        if is_draft:
            form.instance.statut_declaration = "BROUILLON"
        elif was_draft:
            # If it was a draft and now being submitted, change to SOUMISE
            form.instance.statut_declaration = "SOUMISE"

        response = super().form_valid(form)

        # Create notification only if submitting (not saving as draft)
        if not is_draft:
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(self.request.user, "profile"):
                langue = self.request.user.profile.langue_preferee

            # If it was a draft being submitted for the first time, send vehicle added notification
            if was_draft:
                NotificationService.create_vehicle_added_notification(
                    user=self.request.user, vehicle=form.instance, langue=langue
                )
            else:
                # Otherwise send vehicle updated notification
                NotificationService.create_vehicle_updated_notification(
                    user=self.request.user, vehicle=form.instance, langue=langue
                )

        # Success message varies based on action
        if is_draft:
            messages.success(self.request, _("Brouillon sauvegardé avec succès! Vous pouvez le reprendre plus tard."))
        elif was_draft:
            messages.success(
                self.request,
                _("Déclaration soumise avec succès! Votre véhicule %(plaque)s est en attente de validation.")
                % {"plaque": form.instance.plaque_immatriculation},
            )
        else:
            messages.success(
                self.request,
                _("Véhicule %(plaque)s modifié avec succès!") % {"plaque": form.instance.plaque_immatriculation},
            )
        return response

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = self.get_object()

        # Load documents for this vehicle
        context["documents"] = DocumentVehicule.objects.filter(vehicule=vehicule).order_by("-created_at")
        context["document_form"] = VehicleDocumentUploadForm()

        # Check if editing a draft
        is_draft = vehicule.statut_declaration == "BROUILLON"
        context["is_draft"] = is_draft

        if is_draft:
            context["page_title"] = _("Reprendre le Brouillon")
            context["form_action"] = _("Soumettre la déclaration")
        else:
            context["page_title"] = _("Modifier le Véhicule")
            context["form_action"] = _("Modifier")

        return context


class VehiculeDeleteView(LoginRequiredMixin, DeleteView):
    """Soft delete vehicle (set est_actif=False)"""

    model = Vehicule
    template_name = "vehicles/vehicule_confirm_delete.html"
    success_url = reverse_lazy("vehicles:vehicle_list")
    login_url = reverse_lazy("core:login")

    def get_template_names(self):
        """Use Velzon template for fleet managers (non-individual users)"""
        if hasattr(self.request.user, "profile") and self.request.user.profile.user_type != "individual":
            return ["administration/vehicles/vehicule_confirm_delete.html"]
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle delete"""
        from administration.mixins import is_admin_user

        if is_admin_user(request.user):
            return redirect("administration:admin_vehicle_delete", pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Only allow deleting user's own vehicles, or all vehicles for fleet managers"""
        # For fleet management: users with non-individual profiles can delete any vehicle
        if hasattr(self.request.user, "profile") and self.request.user.profile.user_type != "individual":
            return Vehicule.objects.all()
        else:
            # Individual users can only delete their own vehicles
            return Vehicule.objects.filter(proprietaire=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Soft delete - set est_actif=False instead of actual deletion"""
        self.object = self.get_object()
        vehicle_plaque = self.object.plaque_immatriculation
        self.object.est_actif = False
        self.object.save()

        # Create notification for vehicle deleted
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(request.user, "profile"):
            langue = request.user.profile.langue_preferee

        NotificationService.create_vehicle_deleted_notification(
            user=request.user, vehicle_plaque=vehicle_plaque, langue=langue
        )

        messages.success(
            request, _("Véhicule %(plaque)s supprimé avec succès!") % {"plaque": self.object.plaque_immatriculation}
        )

        return redirect(self.success_url)


def calculate_tax_ajax(request):
    """
    AJAX endpoint for real-time tax calculation for all vehicle categories

    Accepts POST with vehicle data (category, characteristics)
    Creates temporary Vehicule instance (not saved)
    Calls TaxCalculationService.calculate_tax()
    Returns JSON with amount, applicable grid, calculation method

    Requirements: 5.7, 7.3
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            from datetime import datetime

            from vehicles.models import VehicleType
            from vehicles.services import TaxCalculationService

            # Get vehicle category
            vehicle_category = request.POST.get("vehicle_category", "TERRESTRE")
            categorie_vehicule = request.POST.get("categorie_vehicule", "Personnel")

            # Check if exempt (using constant from models)
            if categorie_vehicule in EXEMPT_VEHICLE_CATEGORIES:
                return JsonResponse(
                    {
                        "success": True,
                        "tax_amount": "0.00",
                        "is_exempt": True,
                        "message": _("Véhicule exonéré de taxe"),
                        "calculation_method": "Exonération",
                    }
                )

            # Create temporary vehicle instance (not saved to database)
            temp_vehicle = Vehicule()
            temp_vehicle.vehicle_category = vehicle_category
            temp_vehicle.categorie_vehicule = categorie_vehicule

            # Parse common fields
            date_premiere_circulation = request.POST.get("date_premiere_circulation", "")
            if date_premiere_circulation:
                try:
                    temp_vehicle.date_premiere_circulation = datetime.strptime(
                        date_premiere_circulation, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return JsonResponse({"success": False, "message": _("Format de date invalide")})

            # Get vehicle type if provided
            type_vehicule_id = request.POST.get("type_vehicule")
            if type_vehicule_id:
                try:
                    temp_vehicle.type_vehicule = VehicleType.objects.get(id=type_vehicule_id)
                except VehicleType.DoesNotExist:
                    pass

            # Parse category-specific fields
            if vehicle_category == "TERRESTRE":
                # Terrestrial vehicle fields
                puissance_fiscale_cv = request.POST.get("puissance_fiscale_cv", 0)
                source_energie = request.POST.get("source_energie", "")

                if not all([puissance_fiscale_cv, source_energie, date_premiere_circulation]):
                    return JsonResponse({"success": False, "message": _("Données incomplètes pour véhicule terrestre")})

                temp_vehicle.puissance_fiscale_cv = int(puissance_fiscale_cv)
                temp_vehicle.source_energie = source_energie

            elif vehicle_category == "AERIEN":
                # Aerial vehicle fields
                masse_maximale_decollage_kg = request.POST.get("masse_maximale_decollage_kg", 0)
                puissance_moteur_kw = request.POST.get("puissance_moteur_kw", 0)

                if masse_maximale_decollage_kg:
                    temp_vehicle.masse_maximale_decollage_kg = int(masse_maximale_decollage_kg)
                if puissance_moteur_kw:
                    temp_vehicle.puissance_moteur_kw = Decimal(puissance_moteur_kw)

            elif vehicle_category == "MARITIME":
                # Maritime vehicle fields
                longueur_metres = request.POST.get("longueur_metres", 0)
                puissance_fiscale_cv = request.POST.get("puissance_fiscale_cv", 0)
                puissance_moteur_kw = request.POST.get("puissance_moteur_kw", 0)

                if longueur_metres:
                    temp_vehicle.longueur_metres = Decimal(longueur_metres)
                if puissance_fiscale_cv:
                    temp_vehicle.puissance_fiscale_cv = int(puissance_fiscale_cv)
                if puissance_moteur_kw:
                    temp_vehicle.puissance_moteur_kw = Decimal(puissance_moteur_kw)

            # Calculate tax using service
            service = TaxCalculationService()
            tax_info = service.calculate_tax(temp_vehicle)

            if tax_info.get("error"):
                return JsonResponse({"success": False, "message": tax_info["error"]})

            # Prepare response
            response_data = {
                "success": True,
                "tax_amount": str(tax_info["amount"]) if tax_info["amount"] else "0.00",
                "is_exempt": tax_info.get("is_exempt", False),
                "calculation_method": tax_info.get("calculation_method", ""),
                "message": _("Taxe calculée avec succès"),
            }

            # Add grid information if available
            if tax_info.get("grid"):
                grid = tax_info["grid"]
                response_data["grid_info"] = {
                    "id": grid.id,
                    "montant": str(grid.montant_ariary),
                    "annee_fiscale": grid.annee_fiscale,
                    "grid_type": grid.grid_type,
                }

            # Add maritime classification if applicable
            if vehicle_category == "MARITIME" and tax_info.get("maritime_category"):
                response_data["maritime_category"] = tax_info["maritime_category"]
                category_display = {
                    "NAVIRE_PLAISANCE": _("Navire de plaisance"),
                    "JETSKI": _("Jet-ski"),
                    "AUTRES_ENGINS": _("Autres engins maritimes"),
                }.get(tax_info["maritime_category"], tax_info["maritime_category"])
                response_data["maritime_category_display"] = category_display

            return JsonResponse(response_data)

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in calculate_tax_ajax: {str(e)}")
            return JsonResponse({"success": False, "message": _("Erreur lors du calcul de la taxe")})

    return JsonResponse({"success": False, "message": _("Méthode non autorisée")})


def classify_maritime_ajax(request):
    """
    AJAX endpoint for real-time maritime vehicle classification

    Accepts POST with length, power (CV), power (kW), vehicle type
    Calls _classify_maritime_vehicle()
    Returns JSON with category, tax amount, confidence level
    Allows manual override if confidence is medium

    Requirements: 10.6, 10.7
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            from vehicles.models import VehicleType
            from vehicles.services import TaxCalculationService

            # Get maritime vehicle characteristics
            longueur_metres = request.POST.get("longueur_metres", 0)
            puissance_fiscale_cv = request.POST.get("puissance_fiscale_cv", 0)
            puissance_moteur_kw = request.POST.get("puissance_moteur_kw", 0)
            type_vehicule_id = request.POST.get("type_vehicule")

            # Create temporary vehicle for classification
            temp_vehicle = Vehicule()
            temp_vehicle.vehicle_category = "MARITIME"

            if longueur_metres:
                temp_vehicle.longueur_metres = Decimal(longueur_metres)
            if puissance_fiscale_cv:
                temp_vehicle.puissance_fiscale_cv = int(puissance_fiscale_cv)
            if puissance_moteur_kw:
                temp_vehicle.puissance_moteur_kw = Decimal(puissance_moteur_kw)

            # Get vehicle type if provided
            if type_vehicule_id:
                try:
                    temp_vehicle.type_vehicule = VehicleType.objects.get(id=type_vehicule_id)
                except VehicleType.DoesNotExist:
                    pass

            # Classify the vehicle
            service = TaxCalculationService()
            classification = service._classify_maritime_vehicle(temp_vehicle)

            # Determine confidence level
            confidence = "HIGH"
            allow_override = False

            # Medium confidence cases (at threshold boundaries)
            longueur_val = float(longueur_metres) if longueur_metres else 0
            puissance_cv_val = float(puissance_fiscale_cv) if puissance_fiscale_cv else 0
            puissance_kw_val = float(puissance_moteur_kw) if puissance_moteur_kw else 0

            # Check if values are exactly at thresholds (±0.5 tolerance)
            if abs(longueur_val - 7.0) < 0.5:
                confidence = "MEDIUM"
                allow_override = True
            if abs(puissance_cv_val - 22.0) < 1.0:
                confidence = "MEDIUM"
                allow_override = True
            if abs(puissance_kw_val - 90.0) < 2.0:
                confidence = "MEDIUM"
                allow_override = True

            # Get tax amount for this classification
            tax_info = service.calculate_maritime_tax(temp_vehicle)
            tax_amount = str(tax_info["amount"]) if tax_info.get("amount") else None

            # Prepare category display names
            category_display = {
                "NAVIRE_PLAISANCE": _("Navire de plaisance (≥7m ou ≥22CV/90kW)"),
                "JETSKI": _("Jet-ski/moto nautique (≥90kW)"),
                "AUTRES_ENGINS": _("Autres engins maritimes motorisés"),
            }.get(classification, classification)

            # Prepare explanation
            explanation_parts = []
            if longueur_val >= 7:
                explanation_parts.append(_("Longueur ≥ 7m"))
            if puissance_cv_val >= 22:
                explanation_parts.append(_("Puissance ≥ 22 CV"))
            if puissance_kw_val >= 90:
                explanation_parts.append(_("Puissance ≥ 90 kW"))

            if classification == "JETSKI":
                explanation = _("Détecté comme jet-ski/moto nautique avec puissance ≥ 90 kW")
            elif classification == "NAVIRE_PLAISANCE":
                if explanation_parts:
                    explanation = _("Classé comme navire de plaisance: ") + ", ".join(explanation_parts)
                else:
                    explanation = _("Classé comme navire de plaisance")
            else:
                explanation = _("Ne répond pas aux critères de navire de plaisance ou jet-ski")

            return JsonResponse(
                {
                    "success": True,
                    "classification": classification,
                    "classification_display": category_display,
                    "tax_amount": tax_amount,
                    "confidence": confidence,
                    "allow_override": allow_override,
                    "explanation": explanation,
                    "message": _("Classification effectuée avec succès"),
                }
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in classify_maritime_ajax: {str(e)}")
            return JsonResponse({"success": False, "message": _("Erreur lors de la classification")})

    return JsonResponse({"success": False, "message": _("Méthode non autorisée")})


def convert_power_ajax(request):
    """
    AJAX endpoint for power unit conversion (CV ↔ kW)

    Accepts POST with value and source unit (CV or kW)
    Calls convert_cv_to_kw() or convert_kw_to_cv()
    Returns JSON with converted value

    Requirements: 10.4, 10.5
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            from vehicles.services import convert_cv_to_kw, convert_kw_to_cv, validate_power_conversion

            # Get input parameters
            value = request.POST.get("value", "")
            source_unit = request.POST.get("source_unit", "CV")  # CV or kW

            if not value:
                return JsonResponse({"success": False, "message": _("Valeur de puissance requise")})

            try:
                value_decimal = Decimal(value)
            except (ValueError, TypeError):
                return JsonResponse({"success": False, "message": _("Valeur de puissance invalide")})

            # Perform conversion
            if source_unit == "CV":
                # Convert CV to kW
                converted_value = convert_cv_to_kw(value_decimal)
                target_unit = "kW"
                formula = "kW = CV × 0.735"
            elif source_unit == "kW":
                # Convert kW to CV
                converted_value = convert_kw_to_cv(value_decimal)
                target_unit = "CV"
                formula = "CV = kW × 1.36"
            else:
                return JsonResponse({"success": False, "message": _("Unité source invalide. Utilisez CV ou kW.")})

            # Validate round-trip conversion (optional check)
            if source_unit == "CV":
                is_valid, validation_message = validate_power_conversion(value_decimal, converted_value)
            else:
                is_valid, validation_message = validate_power_conversion(converted_value, value_decimal)

            return JsonResponse(
                {
                    "success": True,
                    "original_value": str(value_decimal),
                    "original_unit": source_unit,
                    "converted_value": str(converted_value),
                    "converted_unit": target_unit,
                    "formula": formula,
                    "is_valid": is_valid,
                    "validation_message": validation_message,
                    "message": _("Conversion effectuée avec succès"),
                }
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in convert_power_ajax: {str(e)}")
            return JsonResponse({"success": False, "message": _("Erreur lors de la conversion")})

    return JsonResponse({"success": False, "message": _("Méthode non autorisée")})


# Admin-specific vehicle views
from administration.mixins import AdminRequiredMixin


class AdminVehiculeListView(AdminRequiredMixin, ListView):
    """Admin view for listing all vehicles"""

    model = Vehicule
    template_name = "administration/vehicles/vehicule_list.html"
    context_object_name = "vehicules"
    paginate_by = 20

    def get_queryset(self):
        """Get all vehicles for admin view with category filtering"""
        queryset = Vehicule.objects.select_related("proprietaire", "type_vehicule").order_by("-created_at")

        # Filter by vehicle category (TERRESTRE/AERIEN/MARITIME)
        vehicle_category = self.request.GET.get("vehicle_category")
        if vehicle_category and vehicle_category in ["TERRESTRE", "AERIEN", "MARITIME"]:
            queryset = queryset.filter(vehicle_category=vehicle_category)

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search)
                | Q(immatriculation_aerienne__icontains=search)
                | Q(numero_francisation__icontains=search)
                | Q(nom_navire__icontains=search)
                | Q(proprietaire__username__icontains=search)
                | Q(proprietaire__first_name__icontains=search)
                | Q(proprietaire__last_name__icontains=search)
                | Q(proprietaire__email__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Gestion des Véhicules - Administration")
        context["is_admin_view"] = True

        # Add category filter information
        context["vehicle_category_filter"] = self.request.GET.get("vehicle_category", "")
        context["search_query"] = self.request.GET.get("search", "")

        # Statistics by category
        all_vehicles = Vehicule.objects.filter(est_actif=True)
        context["stats_by_category"] = {
            "TERRESTRE": {
                "count": all_vehicles.filter(vehicle_category="TERRESTRE").count(),
                "icon": "ri-car-line",
                "name": _("Terrestres"),
                "color": "primary",
            },
            "AERIEN": {
                "count": all_vehicles.filter(vehicle_category="AERIEN").count(),
                "icon": "ri-plane-line",
                "name": _("Aériens"),
                "color": "info",
            },
            "MARITIME": {
                "count": all_vehicles.filter(vehicle_category="MARITIME").count(),
                "icon": "ri-ship-line",
                "name": _("Maritimes"),
                "color": "success",
            },
        }
        context["total_vehicles"] = all_vehicles.count()

        return context


class AdminVehiculeCreateView(AdminRequiredMixin, CreateView):
    """Admin view for creating vehicles"""

    model = Vehicule
    form_class = VehiculeForm
    template_name = "administration/vehicles/vehicule_form.html"

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set the owner based on admin selection"""
        from administration.mixins import is_admin_user

        if is_admin_user(self.request.user):
            # Admin can assign vehicle to selected owner
            if form.cleaned_data.get("proprietaire"):
                form.instance.proprietaire = form.cleaned_data["proprietaire"]
            else:
                # If no owner selected, assign to admin (fallback)
                form.instance.proprietaire = self.request.user
        else:
            # This shouldn't happen due to dispatch check, but safety fallback
            form.instance.proprietaire = self.request.user

        response = super().form_valid(form)

        # Create notification for vehicle added
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(form.instance.proprietaire, "profile"):
            langue = form.instance.proprietaire.profile.langue_preferee

        NotificationService.create_vehicle_added_notification(
            user=form.instance.proprietaire,  # Send notification to the actual owner
            vehicle=form.instance,
            langue=langue,
        )

        # Success message for admin
        messages.success(
            self.request,
            _("Véhicule %(plaque)s ajouté avec succès pour %(owner)s!")
            % {
                "plaque": form.instance.plaque_immatriculation,
                "owner": form.instance.proprietaire.get_full_name() or form.instance.proprietaire.username,
            },
        )
        return response

    def get_success_url(self):
        return reverse_lazy("administration:admin_vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Ajouter un Véhicule - Administration")
        context["form_action"] = _("Ajouter")
        context["is_admin_view"] = True
        return context


class AdminVehiculeDetailView(AdminRequiredMixin, DetailView):
    """Admin view for vehicle details"""

    model = Vehicule
    template_name = "administration/vehicles/vehicule_detail.html"
    context_object_name = "vehicule"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Détails du Véhicule - Administration")
        context["is_admin_view"] = True

        # Calculate tax for display
        vehicule = self.get_object()
        context["calculated_tax"] = self._calculate_tax(vehicule)

        return context

    def _calculate_tax(self, vehicule):
        """Calculate tax for the vehicle"""
        try:
            from django.utils import timezone

            from payments.models import GrilleTarifaire

            # Get current year
            current_year = timezone.now().year

            # Check if exempt (using method from model)
            if vehicule.est_exonere():
                return 0

            # Calculate age
            age = current_year - vehicule.date_premiere_circulation.year

            # Find applicable tax rate
            tax_grid = (
                GrilleTarifaire.objects.filter(
                    annee_fiscale=current_year,
                    est_active=True,
                    source_energie=vehicule.source_energie,
                    puissance_min_cv__lte=vehicule.puissance_fiscale_cv,
                    age_min_annees__lte=age,
                )
                .filter(
                    models.Q(puissance_max_cv__gte=vehicule.puissance_fiscale_cv)
                    | models.Q(puissance_max_cv__isnull=True)
                )
                .filter(models.Q(age_max_annees__gte=age) | models.Q(age_max_annees__isnull=True))
                .order_by("-puissance_min_cv", "-age_min_annees")
            )

            for rate in tax_grid:
                if rate.est_applicable(vehicule):
                    return rate.montant_ariary

            # No applicable rate found
            return None

        except Exception:
            return None


class AdminVehiculeUpdateView(AdminRequiredMixin, UpdateView):
    """Admin view for updating vehicles"""

    model = Vehicule
    form_class = VehiculeForm
    template_name = "administration/vehicles/vehicule_form.html"

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Handle admin vehicle update"""
        # Admin can change vehicle owner
        if form.cleaned_data.get("proprietaire"):
            form.instance.proprietaire = form.cleaned_data["proprietaire"]

        response = super().form_valid(form)

        messages.success(
            self.request,
            _("Véhicule %(plaque)s modifié avec succès!") % {"plaque": form.instance.plaque_immatriculation},
        )
        return response

    def get_success_url(self):
        return reverse_lazy("administration:admin_vehicle_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Modifier le Véhicule - Administration")
        context["form_action"] = _("Modifier")
        context["is_admin_view"] = True
        return context


class AdminVehiculeDeleteView(AdminRequiredMixin, DeleteView):
    """Admin view for deleting vehicles"""

    model = Vehicule
    template_name = "administration/vehicles/vehicule_confirm_delete.html"
    success_url = reverse_lazy("administration:admin_vehicle_list")

    def delete(self, request, *args, **kwargs):
        """Handle vehicle deletion with success message"""
        vehicule = self.get_object()
        plaque = vehicule.plaque_immatriculation

        response = super().delete(request, *args, **kwargs)

        messages.success(self.request, _("Véhicule %(plaque)s supprimé avec succès!") % {"plaque": plaque})

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Supprimer le Véhicule - Administration")
        context["is_admin_view"] = True
        return context


import json
import logging
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

# OCR Views for Carte Grise Biométrique
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def log_document_audit(action, document, user, request, data_before=None, data_after=None):
    """Helper function to log document operations for audit purposes"""
    try:
        from django.utils import timezone

        from core.models import AuditLog

        # Prepare audit data
        audit_data = {
            "action": action,
            "table_concernee": "DocumentVehicule",
            "objet_id": str(document.id),
            "user": user,
            "adresse_ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "session_id": request.session.session_key or "",
            "donnees_avant": data_before or {},
            "donnees_apres": data_after or {},
        }

        AuditLog.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Error logging document audit: {str(e)}")


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@require_http_methods(["POST"])
@csrf_exempt  # We'll handle CSRF in the form
def process_carte_grise_ocr(request):
    """
    Process uploaded carte grise biométrique images (recto + verso) and extract vehicle information

    This endpoint is specifically for Madagascar carte grise biométrique only.
    Not for carte rose (temporary) or facture (motorcycle invoices).
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": _("Vous devez être connecté pour utiliser cette fonctionnalité")}, status=401
        )

    # Check for recto (required)
    if "carte_grise_recto" not in request.FILES:
        return JsonResponse(
            {"success": False, "error": _("Veuillez télécharger au moins le recto de la carte grise")}, status=400
        )

    recto_file = request.FILES["carte_grise_recto"]
    verso_file = request.FILES.get("carte_grise_verso")  # Optional

    # Validate file types and sizes
    allowed_extensions = [".jpg", ".jpeg", ".png"]

    for uploaded_file in [recto_file, verso_file]:
        if uploaded_file is None:
            continue

        file_ext = os.path.splitext(uploaded_file.name)[1].lower()

        if file_ext not in allowed_extensions:
            return JsonResponse({"success": False, "error": _("Format non supporté. Utilisez JPG ou PNG.")}, status=400)

        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({"success": False, "error": _("Fichier trop volumineux. Max 10MB.")}, status=400)

    temp_paths = []

    try:
        from .ocr_utils import CarteGriseOCR

        # Save recto temporarily
        recto_temp_path = default_storage.save(
            f"temp/carte_grise_recto_{request.user.id}_{recto_file.name}", ContentFile(recto_file.read())
        )
        temp_paths.append(recto_temp_path)
        recto_full_path = default_storage.path(recto_temp_path)

        # Process recto
        result = CarteGriseOCR.process_carte_grise(recto_full_path)

        # If verso is provided, process it too and merge results
        if verso_file:
            verso_temp_path = default_storage.save(
                f"temp/carte_grise_verso_{request.user.id}_{verso_file.name}", ContentFile(verso_file.read())
            )
            temp_paths.append(verso_temp_path)
            verso_full_path = default_storage.path(verso_temp_path)

            verso_result = CarteGriseOCR.process_carte_grise(verso_full_path)

            # Merge results (verso data supplements recto data)
            if verso_result["success"]:
                for key, value in verso_result["data"].items():
                    if value and not result["data"].get(key):
                        result["data"][key] = value

                # Update confidence
                result["confidence"] = (result["confidence"] + verso_result["confidence"]) / 2

        # Clean up temp files
        for temp_path in temp_paths:
            default_storage.delete(temp_path)

        if result["success"]:
            return JsonResponse(
                {
                    "success": True,
                    "confidence": result["confidence"],
                    "data": result["data"],
                    "message": _("Informations extraites avec succès"),
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": result.get("error", _("Erreur lors de l'extraction des informations"))},
                status=500,
            )

    except Exception as e:
        logger.error(f"Error processing carte grise OCR: {str(e)}")
        return JsonResponse(
            {"success": False, "error": _("Erreur lors du traitement de l'image. Veuillez réessayer.")}, status=500
        )


# AJAX endpoints for vehicle document management
@login_required
def get_vehicle_documents(request, pk):
    """Get all documents for a vehicle (AJAX)"""
    try:
        vehicule = get_object_or_404(Vehicule, pk=pk)

        # Check permissions
        from administration.mixins import is_admin_user

        if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
            return JsonResponse({"success": False, "error": _("Permission refusée")}, status=403)

        documents = DocumentVehicule.objects.filter(vehicule=vehicule).order_by("-created_at")

        documents_data = []
        for doc in documents:
            documents_data.append(
                {
                    "id": str(doc.id),
                    "document_type": doc.document_type,
                    "document_type_display": doc.get_document_type_display(),
                    "file_url": doc.fichier.url if doc.fichier else "",
                    "file_name": doc.fichier.name.split("/")[-1] if doc.fichier else "",
                    "note": doc.note or "",
                    "expiration_date": doc.expiration_date.isoformat() if doc.expiration_date else None,
                    "verification_status": doc.verification_status,
                    "verification_status_display": doc.get_verification_status_display(),
                    "verification_comment": doc.verification_comment or "",
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                    "uploaded_by": doc.uploaded_by.get_full_name() or doc.uploaded_by.username,
                }
            )

        return JsonResponse({"success": True, "documents": documents_data})

    except Exception as e:
        logger.error(f"Error getting vehicle documents: {str(e)}")
        return JsonResponse({"success": False, "error": _("Erreur lors de la récupération des documents")}, status=500)


@login_required
@require_http_methods(["POST"])
def upload_vehicle_document_ajax(request, pk):
    """Upload a document for a vehicle (AJAX)"""
    try:
        vehicule = get_object_or_404(Vehicule, pk=pk)

        # Check permissions
        from administration.mixins import is_admin_user

        if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
            return JsonResponse({"success": False, "error": _("Permission refusée")}, status=403)

        form = VehicleDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.vehicule = vehicule
            doc.uploaded_by = request.user
            doc.save()

            # Log audit
            log_document_audit(
                action="CREATE",
                document=doc,
                user=request.user,
                request=request,
                data_after={
                    "document_type": doc.document_type,
                    "file_name": doc.fichier.name if doc.fichier else "",
                    "note": doc.note or "",
                    "expiration_date": str(doc.expiration_date) if doc.expiration_date else None,
                },
            )

            # Send notification to owner
            try:
                from notifications.services import NotificationService

                langue = "fr"
                if hasattr(vehicule.proprietaire, "profile"):
                    langue = vehicule.proprietaire.profile.langue_preferee
                NotificationService.create_notification(
                    user=vehicule.proprietaire,
                    type_notification="document_uploaded",
                    titre=_("Nouveau document pour votre véhicule"),
                    contenu=_("Le document %(doc)s a été ajouté pour le véhicule %(plaque)s.")
                    % {"doc": doc.get_document_type_display(), "plaque": vehicule.plaque_immatriculation},
                    langue=langue,
                    metadata={"vehicule": vehicule.plaque_immatriculation, "document_id": str(doc.id)},
                )
            except Exception:
                pass

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Document téléchargé avec succès"),
                    "document": {
                        "id": str(doc.id),
                        "document_type": doc.document_type,
                        "document_type_display": doc.get_document_type_display(),
                        "file_url": doc.fichier.url if doc.fichier else "",
                        "file_name": doc.fichier.name.split("/")[-1] if doc.fichier else "",
                        "note": doc.note or "",
                        "expiration_date": doc.expiration_date.isoformat() if doc.expiration_date else None,
                        "verification_status": doc.verification_status,
                        "verification_status_display": doc.get_verification_status_display(),
                        "created_at": doc.created_at.isoformat(),
                        "uploaded_by": doc.uploaded_by.get_full_name() or doc.uploaded_by.username,
                    },
                }
            )
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0] if error_list else ""

            return JsonResponse({"success": False, "error": _("Erreur de validation"), "errors": errors}, status=400)

    except Exception as e:
        logger.error(f"Error uploading vehicle document: {str(e)}")
        return JsonResponse({"success": False, "error": _("Erreur lors du téléchargement du document")}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_vehicle_document(request, pk, document_id):
    """Delete a vehicle document (AJAX)"""
    try:
        vehicule = get_object_or_404(Vehicule, pk=pk)
        document = get_object_or_404(DocumentVehicule, id=document_id, vehicule=vehicule)

        # Check permissions
        from administration.mixins import is_admin_user

        if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
            return JsonResponse({"success": False, "error": _("Permission refusée")}, status=403)

        # Store data before deletion for audit
        data_before = {
            "document_type": document.document_type,
            "file_name": document.fichier.name if document.fichier else "",
            "note": document.note or "",
            "expiration_date": str(document.expiration_date) if document.expiration_date else None,
            "verification_status": document.verification_status,
            "verification_comment": document.verification_comment or "",
        }
        document_id_str = str(document.id)

        # Log audit before deletion
        try:
            from core.models import AuditLog

            AuditLog.objects.create(
                action="DELETE",
                table_concernee="DocumentVehicule",
                objet_id=document_id_str,
                user=request.user,
                adresse_ip=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                session_id=request.session.session_key or "",
                donnees_avant=data_before,
            )
        except Exception as audit_error:
            logger.error(f"Error logging document deletion audit: {str(audit_error)}")

        # Delete the file if it exists
        if document.fichier:
            try:
                document.fichier.delete()
            except Exception as file_error:
                logger.error(f"Error deleting document file: {str(file_error)}")

        # Delete the document
        document.delete()

        return JsonResponse(
            {"success": True, "message": _("Document supprimé avec succès"), "document_id": document_id_str}
        )

    except Exception as e:
        logger.error(f"Error deleting vehicle document: {str(e)}")
        return JsonResponse({"success": False, "error": _("Erreur lors de la suppression du document")}, status=500)


@login_required
@require_http_methods(["POST", "PUT", "PATCH"])
def update_vehicle_document(request, pk, document_id):
    """Update a vehicle document metadata or replace file (AJAX)"""
    try:
        vehicule = get_object_or_404(Vehicule, pk=pk)
        document = get_object_or_404(DocumentVehicule, id=document_id, vehicule=vehicule)

        # Check permissions
        from administration.mixins import is_admin_user

        if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
            return JsonResponse({"success": False, "error": _("Permission refusée")}, status=403)

        # Store data before update for audit
        data_before = {
            "document_type": document.document_type,
            "file_name": document.fichier.name if document.fichier else "",
            "note": document.note or "",
            "expiration_date": str(document.expiration_date) if document.expiration_date else None,
            "verification_status": document.verification_status,
            "verification_comment": document.verification_comment or "",
        }

        # Check if this is a file replacement
        if "fichier" in request.FILES:
            new_file = request.FILES["fichier"]

            # Validate file type and size (match upload constraints)
            try:
                import os

                allowed_exts = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
                ext = os.path.splitext(new_file.name)[1].lower()
                if ext not in allowed_exts:
                    return JsonResponse(
                        {"success": False, "error": _("Formats autorisés: PDF, JPG, JPEG, PNG, WEBP.")}, status=400
                    )

                max_size_bytes = 10 * 1024 * 1024
                if getattr(new_file, "size", 0) > max_size_bytes:
                    return JsonResponse(
                        {"success": False, "error": _("La taille du fichier dépasse 10MB.")}, status=400
                    )
            except Exception:
                return JsonResponse({"success": False, "error": _("Fichier invalide")}, status=400)

            # Replace the file
            old_file = document.fichier
            document.fichier = new_file

            # Delete old file
            if old_file:
                try:
                    old_file.delete()
                except Exception:
                    pass

        # Update metadata
        form_data = request.POST.copy()
        if "document_type" in form_data:
            document.document_type = form_data["document_type"]
        if "note" in form_data:
            document.note = form_data["note"]
        if "expiration_date" in form_data:
            if form_data["expiration_date"]:
                from datetime import datetime

                document.expiration_date = datetime.strptime(form_data["expiration_date"], "%Y-%m-%d").date()
            else:
                document.expiration_date = None
        if "verification_status" in form_data:
            document.verification_status = form_data["verification_status"]
        if "verification_comment" in form_data:
            document.verification_comment = form_data["verification_comment"]

        document.save()

        # Store data after update for audit
        data_after = {
            "document_type": document.document_type,
            "file_name": document.fichier.name if document.fichier else "",
            "note": document.note or "",
            "expiration_date": str(document.expiration_date) if document.expiration_date else None,
            "verification_status": document.verification_status,
            "verification_comment": document.verification_comment or "",
        }

        # Log audit
        log_document_audit(
            action="UPDATE",
            document=document,
            user=request.user,
            request=request,
            data_before=data_before,
            data_after=data_after,
        )

        return JsonResponse(
            {
                "success": True,
                "message": _("Document modifié avec succès"),
                "document": {
                    "id": str(document.id),
                    "document_type": document.document_type,
                    "document_type_display": document.get_document_type_display(),
                    "file_url": document.fichier.url if document.fichier else "",
                    "file_name": document.fichier.name.split("/")[-1] if document.fichier else "",
                    "note": document.note or "",
                    "expiration_date": document.expiration_date.isoformat() if document.expiration_date else None,
                    "verification_status": document.verification_status,
                    "verification_status_display": document.get_verification_status_display(),
                    "verification_comment": document.verification_comment or "",
                    "updated_at": document.updated_at.isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error updating vehicle document: {str(e)}")
        return JsonResponse({"success": False, "error": _("Erreur lors de la modification du document")}, status=500)


# ============================================================================
# Declaration History Views
# ============================================================================


class DeclarationHistoryView(LoginRequiredMixin, ListView):
    """
    View to display declaration history for the current user.
    Lists all vehicles grouped by fiscal year and category.
    Requirements: 17.1, 17.2
    """

    model = Vehicule
    template_name = "vehicles/declaration_history.html"
    context_object_name = "vehicules"
    paginate_by = 20
    login_url = reverse_lazy("core:login")

    def get_queryset(self):
        """
        Get all vehicles for the current user with filters applied.
        Requirements: 17.3, 17.4, 17.5
        """
        queryset = (
            Vehicule.objects.filter(proprietaire=self.request.user, est_actif=True)
            .select_related("type_vehicule", "proprietaire")
            .prefetch_related("paiements", "documents")
            .order_by("-created_at")
        )

        # Apply filters from GET parameters
        category = self.request.GET.get("category")
        if category and category in ["TERRESTRE", "AERIEN", "MARITIME"]:
            queryset = queryset.filter(vehicle_category=category)

        status = self.request.GET.get("status")
        if status and status in ["BROUILLON", "SOUMISE", "VALIDEE", "REJETEE"]:
            queryset = queryset.filter(statut_declaration=status)

        fiscal_year = self.request.GET.get("fiscal_year")
        if fiscal_year:
            try:
                year = int(fiscal_year)
                # Filter by vehicles that have payments for this fiscal year
                # or were created in this fiscal year
                queryset = queryset.filter(Q(paiements__annee_fiscale=year) | Q(created_at__year=year)).distinct()
            except ValueError:
                pass

        # Search by identifier (plaque, immat aérienne, francisation)
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search_query)
                | Q(immatriculation_aerienne__icontains=search_query)
                | Q(numero_francisation__icontains=search_query)
                | Q(nom_navire__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)

        # Get all vehicles for grouping
        all_vehicles = self.get_queryset()

        # Group vehicles by fiscal year and category
        from collections import defaultdict

        from payments.models import PaiementTaxe

        grouped_vehicles = defaultdict(lambda: defaultdict(list))

        for vehicule in all_vehicles:
            # Get the most recent payment to determine fiscal year
            latest_payment = vehicule.paiements.order_by("-annee_fiscale").first()
            fiscal_year = latest_payment.annee_fiscale if latest_payment else timezone.now().year

            # Get vehicle details
            vehicle_data = {
                "vehicule": vehicule,
                "identifier": self._get_vehicle_identifier(vehicule),
                "submission_date": vehicule.created_at,
                "validation_date": vehicule.updated_at if vehicule.statut_declaration == "VALIDEE" else None,
                "payment_status": vehicule.get_current_payment_status(),
                "tax_amount": self._get_tax_amount(vehicule, fiscal_year),
                "has_qr_code": self._has_qr_code(vehicule),
                "has_receipt": self._has_receipt(vehicule),
            }

            grouped_vehicles[fiscal_year][vehicule.vehicle_category].append(vehicle_data)

        # Convert to regular dict and sort by year (descending)
        grouped_vehicles = dict(sorted(grouped_vehicles.items(), key=lambda x: x[0], reverse=True))

        # Get available fiscal years for filter
        fiscal_years = sorted(
            set(
                [timezone.now().year]
                + list(
                    PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=self.request.user)
                    .values_list("annee_fiscale", flat=True)
                    .distinct()
                )
            ),
            reverse=True,
        )

        # Get filter values
        current_filters = {
            "category": self.request.GET.get("category", ""),
            "status": self.request.GET.get("status", ""),
            "fiscal_year": self.request.GET.get("fiscal_year", ""),
            "search": self.request.GET.get("search", ""),
        }

        context.update(
            {
                "page_title": _("Historique des Déclarations"),
                "grouped_vehicles": grouped_vehicles,
                "fiscal_years": fiscal_years,
                "current_filters": current_filters,
                "category_choices": [
                    ("TERRESTRE", _("Terrestre")),
                    ("AERIEN", _("Aérien")),
                    ("MARITIME", _("Maritime")),
                ],
                "status_choices": [
                    ("BROUILLON", _("Brouillon")),
                    ("SOUMISE", _("Soumise")),
                    ("VALIDEE", _("Validée")),
                    ("REJETEE", _("Rejetée")),
                ],
            }
        )

        return context

    def _get_vehicle_identifier(self, vehicule):
        """Get the appropriate identifier based on vehicle category"""
        if vehicule.vehicle_category == "AERIEN":
            return vehicule.immatriculation_aerienne or vehicule.plaque_immatriculation
        elif vehicule.vehicle_category == "MARITIME":
            return vehicule.nom_navire or vehicule.numero_francisation or vehicule.plaque_immatriculation
        return vehicule.plaque_immatriculation

    def _get_tax_amount(self, vehicule, fiscal_year):
        """Get the tax amount for a vehicle for a given fiscal year"""
        from payments.models import PaiementTaxe

        payment = PaiementTaxe.objects.filter(
            vehicule_plaque=vehicule, annee_fiscale=fiscal_year, type_paiement="TAXE_VEHICULE"
        ).first()

        if payment:
            return payment.montant_du_ariary

        # Calculate tax if no payment exists
        from vehicles.services import TaxCalculationService

        service = TaxCalculationService()
        tax_info = service.calculate_tax(vehicule, fiscal_year)
        return tax_info.get("amount", Decimal("0"))

    def _has_qr_code(self, vehicule):
        """Check if vehicle has a valid QR code"""
        try:
            from payments.models import QRCode

            return QRCode.objects.filter(vehicule_plaque=vehicule, type_code="TAXE_VEHICULE").exists()
        except:
            return False

    def _has_receipt(self, vehicule):
        """Check if vehicle has a paid receipt"""
        from payments.models import PaiementTaxe

        return PaiementTaxe.objects.filter(
            vehicule_plaque=vehicule, statut="PAYE", type_paiement="TAXE_VEHICULE"
        ).exists()


class DeclarationHistoryExportView(LoginRequiredMixin, View):
    """
    Export declaration history to CSV or PDF format.
    Requirements: 17.6
    """

    login_url = reverse_lazy("core:login")

    def get(self, request, *args, **kwargs):
        """Handle export request"""
        export_format = request.GET.get("export", "csv")

        # Get filtered queryset (reuse logic from DeclarationHistoryView)
        queryset = self._get_filtered_queryset(request)

        if export_format == "csv":
            return self._export_csv(queryset)
        elif export_format == "pdf":
            return self._export_pdf(queryset, request)
        else:
            messages.error(request, _("Format d'export non supporté"))
            return redirect("vehicles:declaration_history")

    def _get_filtered_queryset(self, request):
        """Get filtered queryset based on request parameters"""
        queryset = (
            Vehicule.objects.filter(proprietaire=request.user, est_actif=True)
            .select_related("type_vehicule", "proprietaire")
            .prefetch_related("paiements", "documents")
            .order_by("-created_at")
        )

        # Apply filters
        category = request.GET.get("category")
        if category and category in ["TERRESTRE", "AERIEN", "MARITIME"]:
            queryset = queryset.filter(vehicle_category=category)

        status = request.GET.get("status")
        if status and status in ["BROUILLON", "SOUMISE", "VALIDEE", "REJETEE"]:
            queryset = queryset.filter(statut_declaration=status)

        fiscal_year = request.GET.get("fiscal_year")
        if fiscal_year:
            try:
                year = int(fiscal_year)
                queryset = queryset.filter(Q(paiements__annee_fiscale=year) | Q(created_at__year=year)).distinct()
            except ValueError:
                pass

        search_query = request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search_query)
                | Q(immatriculation_aerienne__icontains=search_query)
                | Q(numero_francisation__icontains=search_query)
                | Q(nom_navire__icontains=search_query)
            )

        return queryset

    def _export_csv(self, queryset):
        """Export to CSV format"""
        import csv

        from django.http import HttpResponse

        from payments.models import PaiementTaxe

        # Create response
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="historique_declarations_{timezone.now().strftime("%Y%m%d")}.csv"'
        )

        # Add BOM for Excel UTF-8 support
        response.write("\ufeff")

        writer = csv.writer(response)

        # Write header
        writer.writerow(
            [
                _("Identifiant"),
                _("Catégorie"),
                _("Type"),
                _("Marque"),
                _("Modèle"),
                _("Date Soumission"),
                _("Date Validation"),
                _("Statut Déclaration"),
                _("Année Fiscale"),
                _("Montant Taxe (Ar)"),
                _("Statut Paiement"),
                _("Date Paiement"),
            ]
        )

        # Write data
        for vehicule in queryset:
            # Get identifier
            if vehicule.vehicle_category == "AERIEN":
                identifier = vehicule.immatriculation_aerienne or vehicule.plaque_immatriculation
            elif vehicule.vehicle_category == "MARITIME":
                identifier = vehicule.nom_navire or vehicule.numero_francisation or vehicule.plaque_immatriculation
            else:
                identifier = vehicule.plaque_immatriculation

            # Get latest payment
            latest_payment = vehicule.paiements.order_by("-annee_fiscale").first()
            fiscal_year = latest_payment.annee_fiscale if latest_payment else timezone.now().year

            # Get tax amount
            from vehicles.services import TaxCalculationService

            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicule, fiscal_year)
            tax_amount = tax_info.get("amount", Decimal("0"))

            # Get payment status
            payment_status = vehicule.get_current_payment_status()
            payment_date = latest_payment.date_paiement if latest_payment and latest_payment.date_paiement else ""

            # Get validation date
            validation_date = vehicule.updated_at if vehicule.statut_declaration == "VALIDEE" else ""

            writer.writerow(
                [
                    identifier,
                    vehicule.get_vehicle_category_display(),
                    vehicule.type_vehicule.nom if vehicule.type_vehicule else "",
                    vehicule.marque or "",
                    vehicule.modele or "",
                    vehicule.created_at.strftime("%d/%m/%Y %H:%M") if vehicule.created_at else "",
                    validation_date.strftime("%d/%m/%Y %H:%M") if validation_date else "",
                    vehicule.get_statut_declaration_display(),
                    fiscal_year,
                    f"{tax_amount:.2f}",
                    payment_status,
                    payment_date.strftime("%d/%m/%Y %H:%M") if payment_date else "",
                ]
            )

        return response

    def _export_pdf(self, queryset, request):
        """Export to PDF format"""
        from django.http import HttpResponse
        from django.template.loader import render_to_string

        from payments.models import PaiementTaxe

        try:
            from weasyprint import CSS, HTML
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            messages.error(request, _("Export PDF non disponible. Veuillez installer WeasyPrint."))
            return redirect("vehicles:declaration_history")

        # Prepare data
        vehicles_data = []
        for vehicule in queryset:
            # Get identifier
            if vehicule.vehicle_category == "AERIEN":
                identifier = vehicule.immatriculation_aerienne or vehicule.plaque_immatriculation
            elif vehicule.vehicle_category == "MARITIME":
                identifier = vehicule.nom_navire or vehicule.numero_francisation or vehicule.plaque_immatriculation
            else:
                identifier = vehicule.plaque_immatriculation

            # Get latest payment
            latest_payment = vehicule.paiements.order_by("-annee_fiscale").first()
            fiscal_year = latest_payment.annee_fiscale if latest_payment else timezone.now().year

            # Get tax amount
            from vehicles.services import TaxCalculationService

            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicule, fiscal_year)
            tax_amount = tax_info.get("amount", Decimal("0"))

            vehicles_data.append(
                {
                    "identifier": identifier,
                    "category": vehicule.get_vehicle_category_display(),
                    "type": vehicule.type_vehicule.nom if vehicule.type_vehicule else "",
                    "marque": vehicule.marque or "",
                    "modele": vehicule.modele or "",
                    "submission_date": vehicule.created_at,
                    "validation_date": vehicule.updated_at if vehicule.statut_declaration == "VALIDEE" else None,
                    "declaration_status": vehicule.get_statut_declaration_display(),
                    "fiscal_year": fiscal_year,
                    "tax_amount": tax_amount,
                    "payment_status": vehicule.get_current_payment_status(),
                    "payment_date": (
                        latest_payment.date_paiement if latest_payment and latest_payment.date_paiement else None
                    ),
                }
            )

        # Render HTML
        html_string = render_to_string(
            "vehicles/declaration_history_pdf.html",
            {
                "vehicles": vehicles_data,
                "user": request.user,
                "export_date": timezone.now(),
                "filters": {
                    "category": request.GET.get("category", ""),
                    "status": request.GET.get("status", ""),
                    "fiscal_year": request.GET.get("fiscal_year", ""),
                    "search": request.GET.get("search", ""),
                },
            },
        )

        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url=request.build_absolute_uri())

        # Create response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="historique_declarations_{timezone.now().strftime("%Y%m%d")}.pdf"'
        )

        # Write PDF
        html.write_pdf(response, font_config=font_config)

        return response
