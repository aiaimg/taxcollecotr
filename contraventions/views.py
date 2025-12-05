import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from contraventions.forms import (
    ConfigurationSystemeForm,
    ContestationForm,
    ContraventionForm,
    DossierFourriereForm,
    TypeInfractionForm,
)
from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contestation,
    Contravention,
    DossierFourriere,
    TypeInfraction,
)
from contraventions.services import ContestationService, ContraventionService, FourriereService
from payments.models import PaiementTaxe


# Vues pour les agents contrôleurs
class AgentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un agent contrôleur"""

    def test_func(self):
        return (
            hasattr(self.request.user, "agent_controleur_profile")
            and self.request.user.agent_controleur_profile.est_actif
        )


class ContraventionCreateView(AgentRequiredMixin, CreateView):
    """Vue pour créer une nouvelle contravention"""

    model = Contravention
    form_class = ContraventionForm
    template_name = "contraventions/contravention_form.html"
    success_url = reverse_lazy("contraventions:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            contravention = form.save()
            messages.success(self.request, f"Contravention {contravention.numero_pv} créée avec succès.")
            return redirect("contraventions:detail", pk=contravention.pk)
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la création: {str(e)}")
            return self.form_invalid(form)


class ContraventionListView(AgentRequiredMixin, ListView):
    """Vue pour lister les contraventions de l'agent"""

    model = Contravention
    template_name = "contraventions/contravention_list.html"
    context_object_name = "contraventions"
    paginate_by = 50

    def get_queryset(self):
        queryset = Contravention.objects.filter(
            agent_controleur=self.request.user.agent_controleur_profile
        ).select_related("type_infraction", "conducteur", "vehicule")

        # Filtres
        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        date_from = self.request.GET.get("date_from")
        if date_from:
            queryset = queryset.filter(date_heure_infraction__date__gte=date_from)

        date_to = self.request.GET.get("date_to")
        if date_to:
            queryset = queryset.filter(date_heure_infraction__date__lte=date_to)

        type_infraction = self.request.GET.get("type_infraction")
        if type_infraction:
            queryset = queryset.filter(type_infraction__id=type_infraction)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuts"] = Contravention.STATUT_CHOICES
        context["types_infraction"] = TypeInfraction.objects.filter(est_actif=True)
        return context


class ContraventionDetailView(AgentRequiredMixin, DetailView):
    """Vue pour afficher les détails d'une contravention"""

    model = Contravention
    template_name = "contraventions/contravention_detail.html"
    context_object_name = "contravention"

    def get_queryset(self):
        return Contravention.objects.select_related(
            "agent_controleur", "type_infraction", "conducteur", "vehicule", "qr_code"
        ).prefetch_related("photos", "contestations", "audit_logs")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contravention = self.object

        # Vérifier si l'agent peut annuler
        peut_annuler = False
        if contravention.statut == "IMPAYEE":
            time_diff = timezone.now() - contravention.created_at
            config = ConfigurationSysteme.get_config()
            peut_annuler = time_diff.total_seconds() / 3600 <= config.delai_annulation_directe_heures

        context["peut_annuler"] = peut_annuler
        context["paiements"] = PaiementTaxe.objects.filter(contravention=contravention)
        return context


class ContraventionCancelView(AgentRequiredMixin, TemplateView):
    """Vue pour annuler une contravention"""

    template_name = "contraventions/contravention_cancel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contravention = get_object_or_404(
            Contravention, pk=kwargs["pk"], agent_controleur=self.request.user.agent_controleur_profile
        )
        context["contravention"] = contravention

        # Vérifier si l'agent peut annuler
        peut_annuler = False
        if contravention.statut == "IMPAYEE":
            time_diff = timezone.now() - contravention.created_at
            config = ConfigurationSysteme.get_config()
            peut_annuler = time_diff.total_seconds() / 3600 <= config.delai_annulation_directe_heures

        if not peut_annuler:
            messages.error(self.request, "Vous ne pouvez plus annuler cette contravention.")

        context["peut_annuler"] = peut_annuler
        return context

    def post(self, request, *args, **kwargs):
        contravention = get_object_or_404(
            Contravention, pk=kwargs["pk"], agent_controleur=request.user.agent_controleur_profile
        )

        motif = request.POST.get("motif", "")
        if not motif:
            messages.error(request, "Le motif d'annulation est obligatoire.")
            return redirect("contraventions:cancel", pk=contravention.pk)

        try:
            ContraventionService.annuler_contravention(contravention, request.user, motif)
            messages.success(request, f"Contravention {contravention.numero_pv} annulée avec succès.")
            return redirect("contraventions:list")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'annulation: {str(e)}")
            return redirect("contraventions:cancel", pk=contravention.pk)


# Vues pour la fourrière
class DossierFourriereCreateView(AgentRequiredMixin, CreateView):
    """Vue pour créer un dossier de fourrière"""

    model = DossierFourriere
    form_class = DossierFourriereForm
    template_name = "contraventions/fourriere_form.html"

    def get_initial(self):
        initial = super().get_initial()
        contravention = get_object_or_404(
            Contravention,
            pk=self.kwargs["contravention_id"],
            agent_controleur=self.request.user.agent_controleur_profile,
        )
        initial["contravention"] = contravention
        return initial

    def form_valid(self, form):
        contravention = get_object_or_404(
            Contravention,
            pk=self.kwargs["contravention_id"],
            agent_controleur=self.request.user.agent_controleur_profile,
        )

        try:
            dossier = FourriereService.creer_dossier_fourriere(
                contravention=contravention,
                lieu_fourriere=form.cleaned_data["lieu_fourriere"],
                adresse_fourriere=form.cleaned_data["adresse_fourriere"],
                type_vehicule=form.cleaned_data["type_vehicule"],
                user=self.request.user,
            )
            messages.success(self.request, f"Dossier de fourrière {dossier.numero_dossier} créé avec succès.")
            return redirect("contraventions:fourriere_detail", pk=dossier.pk)
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la création: {str(e)}")
            return self.form_invalid(form)


class DossierFourriereDetailView(AgentRequiredMixin, DetailView):
    """Vue pour afficher les détails d'un dossier de fourrière"""

    model = DossierFourriere
    template_name = "contraventions/fourriere_detail.html"
    context_object_name = "dossier"

    def get_queryset(self):
        return DossierFourriere.objects.select_related("contravention")


class DossierFourriereListView(AgentRequiredMixin, ListView):
    """Vue pour lister les dossiers de fourrière"""

    model = DossierFourriere
    template_name = "contraventions/fourriere_list.html"
    context_object_name = "dossiers"
    paginate_by = 50

    def get_queryset(self):
        queryset = DossierFourriere.objects.select_related(
            "contravention", "contravention__type_infraction", "contravention__vehicule", "contravention__conducteur"
        ).order_by("-date_mise_fourriere")

        # Filtres
        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset


# Vues publiques pour les conducteurs
class ContraventionPublicDetailView(DetailView):
    """Vue publique pour consulter une contravention via QR code ou numéro PV"""

    model = Contravention
    template_name = "contraventions/contravention_public_detail.html"
    context_object_name = "contravention"
    slug_field = "numero_pv"
    slug_url_kwarg = "numero_pv"

    def get_queryset(self):
        return Contravention.objects.select_related(
            "type_infraction", "conducteur", "vehicule", "qr_code"
        ).prefetch_related("photos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contravention = self.object

        # Vérifier si le conducteur peut contester
        peut_contester = False
        if contravention.statut in ["IMPAYEE", "CONTESTEE"]:
            config = ConfigurationSysteme.get_config()
            time_diff = timezone.now() - contravention.created_at
            peut_contester = time_diff.days <= config.delai_contestation_jours

        context["peut_contester"] = peut_contester
        context["paiements"] = PaiementTaxe.objects.filter(contravention=contravention)
        return context


class ContraventionPaymentView(DetailView):
    """Vue pour sélectionner la méthode de paiement"""

    model = Contravention
    template_name = "contraventions/payment_select.html"
    context_object_name = "contravention"
    slug_field = "numero_pv"
    slug_url_kwarg = "numero_pv"

    def get_queryset(self):
        return Contravention.objects.select_related("type_infraction")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contravention = self.object
        context["montant_total"] = contravention.get_montant_total()
        return context


class ContestationPublicView(CreateView):
    """Vue publique pour soumettre une contestation"""

    model = Contestation
    form_class = ContestationForm
    template_name = "contraventions/contestation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        contravention = get_object_or_404(Contravention, numero_pv=self.kwargs["numero_pv"])
        initial["contravention"] = contravention
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contravention = get_object_or_404(Contravention, numero_pv=self.kwargs["numero_pv"])
        context["contravention"] = contravention
        return context

    def form_valid(self, form):
        contravention = get_object_or_404(Contravention, numero_pv=self.kwargs["numero_pv"])

        try:
            contestation = ContestationService.soumettre_contestation(
                contravention=contravention,
                demandeur_data={
                    "nom_demandeur": form.cleaned_data["nom_demandeur"],
                    "email_demandeur": form.cleaned_data["email_demandeur"],
                    "telephone_demandeur": form.cleaned_data["telephone_demandeur"],
                },
                motif=form.cleaned_data["motif"],
                documents=self.request.FILES.getlist("documents"),
                user=self.request.user if self.request.user.is_authenticated else None,
            )
            messages.success(self.request, "Votre contestation a été soumise avec succès.")
            return redirect("contraventions:public-detail", numero_pv=contravention.numero_pv)
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la soumission: {str(e)}")
            return self.form_invalid(form)


# Vues d'administration
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est administrateur"""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class InfractionManagementView(AdminRequiredMixin, ListView):
    """Vue pour gérer les types d'infractions"""

    model = TypeInfraction
    template_name = "contraventions/admin/infraction_list.html"
    context_object_name = "infractions"
    paginate_by = 50

    def get_queryset(self):
        return TypeInfraction.objects.all().order_by("categorie", "nom")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = TypeInfraction.CATEGORIE_CHOICES
        return context


class ContraventionReportView(AdminRequiredMixin, TemplateView):
    """Vue pour les rapports et statistiques"""

    template_name = "contraventions/admin/report_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistiques générales
        total_contraventions = Contravention.objects.count()
        contraventions_payees = Contravention.objects.filter(statut="PAYEE").count()
        taux_paiement = (contraventions_payees / total_contraventions * 100) if total_contraventions > 0 else 0

        # Montants
        montant_total = Contravention.objects.aggregate(total=Sum("montant_amende_ariary"))["total"] or 0

        # Contraventions impayées en retard
        contraventions_retard = Contravention.objects.filter(
            statut="IMPAYEE", date_limite_paiement__lt=timezone.now().date()
        ).count()

        # Par catégorie
        stats_par_categorie = (
            Contravention.objects.values("type_infraction__categorie")
            .annotate(count=Count("id"), total_montant=Sum("montant_amende_ariary"))
            .order_by("-count")
        )

        # Par agent
        stats_par_agent = (
            Contravention.objects.values("agent_controleur__nom_complet")
            .annotate(count=Count("id"), total_montant=Sum("montant_amende_ariary"))
            .order_by("-count")[:10]
        )

        context.update(
            {
                "total_contraventions": total_contraventions,
                "contraventions_payees": contraventions_payees,
                "taux_paiement": taux_paiement,
                "montant_total": montant_total,
                "contraventions_retard": contraventions_retard,
                "stats_par_categorie": stats_par_categorie,
                "stats_par_agent": stats_par_agent,
            }
        )

        return context


class ContestationManagementView(AdminRequiredMixin, ListView):
    """Vue pour gérer les contestations"""

    model = Contestation
    template_name = "contraventions/admin/contestation_list.html"
    context_object_name = "contestations"
    paginate_by = 50

    def get_queryset(self):
        return Contestation.objects.select_related("contravention").order_by("-date_soumission")


class ContestationDetailView(AdminRequiredMixin, DetailView):
    """Vue pour examiner une contestation en détail"""

    model = Contestation
    template_name = "contraventions/admin/contestation_detail.html"
    context_object_name = "contestation"

    def get_queryset(self):
        return Contestation.objects.select_related(
            "contravention",
            "contravention__type_infraction",
            "contravention__agent_controleur",
            "contravention__vehicule",
            "contravention__conducteur",
        )


class ConfigurationView(AdminRequiredMixin, UpdateView):
    """Vue pour configurer le système"""

    model = ConfigurationSysteme
    form_class = ConfigurationSystemeForm
    template_name = "contraventions/admin/configuration.html"
    success_url = reverse_lazy("contraventions:admin_configuration")

    def get_object(self, queryset=None):
        return ConfigurationSysteme.get_config()

    def form_valid(self, form):
        messages.success(self.request, "Configuration mise à jour avec succès.")
        return super().form_valid(form)


@login_required
def admin_maintenance_action(request):
    """Handle maintenance actions from admin configuration page"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé. Réservé aux administrateurs.")
        return redirect("administration:admin_login")

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "reset_cache":
                from django.core.cache import cache

                cache.clear()
                messages.success(request, "Cache système réinitialisé avec succès.")
            elif action == "cleanup":
                messages.success(request, "Nettoyage des fichiers temporaires lancé.")
            elif action == "backup":
                messages.success(request, "Sauvegarde de la base de données initiée.")
            else:
                messages.warning(request, "Action inconnue.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'exécution de l'action: {str(e)}")

    return redirect("contraventions:admin_configuration")


@login_required
def infraction_activate(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé.")
        return redirect("administration:admin_login")
    try:
        t = TypeInfraction.objects.get(pk=pk)
        t.est_actif = True
        t.save(update_fields=["est_actif"])
        messages.success(request, "Infraction activée.")
    except TypeInfraction.DoesNotExist:
        messages.error(request, "Infraction introuvable.")
    return redirect("contraventions:admin_infraction_list")


@login_required
def infraction_desactivate(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé.")
        return redirect("administration:admin_login")
    try:
        t = TypeInfraction.objects.get(pk=pk)
        t.est_actif = False
        t.save(update_fields=["est_actif"])
        messages.success(request, "Infraction désactivée.")
    except TypeInfraction.DoesNotExist:
        messages.error(request, "Infraction introuvable.")
    return redirect("contraventions:admin_infraction_list")


# Vues AJAX pour les recherches
@login_required
def search_vehicle(request):
    if request.method == "GET":
        from vehicles.models import Vehicule

        vid = request.GET.get("id")
        if vid:
            vehicule = Vehicule.objects.filter(id=vid).first()
            if vehicule:
                data = {
                    "success": True,
                    "vehicle": {
                        "id": vehicule.id,
                        "numero_plaque": vehicule.plaque_immatriculation,
                        "marque": vehicule.marque,
                        "modele": vehicule.modele,
                        "numero_chassis": getattr(vehicule, "numero_chassis", ""),
                        "proprietaire_nom": (
                            vehicule.proprietaire.nom_complet if getattr(vehicule, "proprietaire", None) else ""
                        ),
                    },
                }
            else:
                data = {"success": False, "message": "Véhicule non trouvé"}
            return JsonResponse(data)
        q = request.GET.get("q", "").upper().replace(" ", "")
        results = []
        if q:
            qs = Vehicule.objects.filter(plaque_immatriculation__icontains=q)[:10]
            for v in qs:
                results.append(
                    {
                        "id": v.id,
                        "numero_plaque": v.plaque_immatriculation,
                        "marque": v.marque,
                        "modele": v.modele,
                        "numero_chassis": getattr(v, "numero_chassis", ""),
                        "proprietaire_nom": v.proprietaire.nom_complet if getattr(v, "proprietaire", None) else "",
                    }
                )
        return JsonResponse({"success": True, "vehicles": results})


@login_required
def search_conducteur(request):
    if request.method == "GET":
        cid = request.GET.get("id")
        if cid:
            c = Conducteur.objects.filter(id=cid).first()
            if c:
                return JsonResponse(
                    {
                        "success": True,
                        "conducteur": {
                            "id": c.id,
                            "nom": c.nom_complet,
                            "prenom": "",
                            "numero_permis": c.numero_permis or "",
                            "telephone": c.telephone or "",
                            "adresse": c.adresse or "",
                        },
                    }
                )
            return JsonResponse({"success": False, "message": "Conducteur non trouvé"})
        q = request.GET.get("q", "")
        conducteurs = []
        if q:
            qs = Conducteur.objects.filter(
                Q(cin__icontains=q) | Q(nom_complet__icontains=q) | Q(numero_permis__icontains=q)
            )[:10]
            for c in qs:
                conducteurs.append(
                    {
                        "id": c.id,
                        "nom": c.nom_complet,
                        "prenom": "",
                        "numero_permis": c.numero_permis or "",
                        "telephone": c.telephone or "",
                        "adresse": c.adresse or "",
                    }
                )
        return JsonResponse({"success": True, "conducteurs": conducteurs})


@login_required
def get_infraction_details(request):
    if request.method == "GET":
        type_id = request.GET.get("type_id")
        if not type_id:
            return JsonResponse({"success": False, "error": "ID du type d'infraction requis"}, status=400)
        try:
            type_infraction = TypeInfraction.objects.get(id=type_id)
            data = {
                "success": True,
                "montant": float(type_infraction.montant_min_ariary),
                "montant_base": float(type_infraction.montant_min_ariary),
                "montant_variable": type_infraction.montant_variable,
                "fourriere_obligatoire": type_infraction.fourriere_obligatoire,
                "sanctions_administratives": type_infraction.sanctions_administratives,
            }
            return JsonResponse(data)
        except TypeInfraction.DoesNotExist:
            return JsonResponse({"success": False, "error": "Type d'infraction non trouvé"}, status=404)


@login_required
def check_recidive(request):
    if request.method == "GET":
        conducteur_id = request.GET.get("conducteur_id")
        type_infraction_id = request.GET.get("type_infraction_id")
        data = {"success": True, "has_recidive": False}
        if conducteur_id and type_infraction_id:
            try:
                conducteur = Conducteur.objects.get(id=conducteur_id)
                type_infraction = TypeInfraction.objects.get(id=type_infraction_id)
                est_recidive = ContraventionService.detecter_recidive(
                    conducteur=conducteur, type_infraction=type_infraction, periode_mois=12
                )
                if est_recidive:
                    recidives = Contravention.objects.filter(
                        conducteur=conducteur,
                        type_infraction=type_infraction,
                        date_heure_infraction__gte=timezone.now() - timedelta(days=365),
                    ).order_by("-date_heure_infraction")[:5]
                    data = {
                        "success": True,
                        "has_recidive": True,
                        "message": "Récidive détectée",
                        "recidive_count": len(recidives),
                        "majoration": 0,
                    }
            except (Conducteur.DoesNotExist, TypeInfraction.DoesNotExist):
                data = {"success": False, "message": "Conducteur ou infraction non trouvée"}
        return JsonResponse(data)
