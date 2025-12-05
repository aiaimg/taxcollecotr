"""
Advanced Vehicle Search Module
Vue globale des véhicules avec filtres avancés, pagination, et vues liste/grille
"""

import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.views.generic import ListView

from vehicles.models import Vehicule

from ..decorators import admin_required
from ..mixins import AdminRequiredMixin


class AdvancedVehicleSearchView(AdminRequiredMixin, ListView):
    """
    Vue de recherche avancée des véhicules avec:
    - Filtres multiples (type, catégorie, statut, propriétaire, etc.)
    - Pagination
    - Vue liste et grille
    - Export
    """

    model = Vehicule
    template_name = "administration/advanced_vehicle_search/list.html"
    context_object_name = "vehicles"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Vehicule.objects.select_related("proprietaire", "proprietaire__profile")
            .prefetch_related("paiements")
            .order_by("-created_at")
        )

        # Filtre par recherche générale
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search)
                | Q(proprietaire__username__icontains=search)
                | Q(proprietaire__email__icontains=search)
                | Q(proprietaire__first_name__icontains=search)
                | Q(proprietaire__last_name__icontains=search)
                | Q(marque__icontains=search)
                | Q(modele__icontains=search)
            )

        # Filtre par type de véhicule
        vehicle_type = self.request.GET.get("type", "")
        if vehicle_type:
            queryset = queryset.filter(type_vehicule=vehicle_type)

        # Filtre par catégorie
        category = self.request.GET.get("category", "")
        if category:
            queryset = queryset.filter(categorie_vehicule=category)

        # Filtre par statut
        status = self.request.GET.get("status", "")
        if status == "active":
            queryset = queryset.filter(est_actif=True)
        elif status == "inactive":
            queryset = queryset.filter(est_actif=False)

        # Filtre par propriétaire
        owner = self.request.GET.get("owner", "")
        if owner:
            queryset = queryset.filter(
                Q(proprietaire__username__icontains=owner) | Q(proprietaire__email__icontains=owner)
            )

        # Filtre par année
        year_from = self.request.GET.get("year_from", "")
        year_to = self.request.GET.get("year_to", "")
        if year_from:
            queryset = queryset.filter(annee_fabrication__gte=year_from)
        if year_to:
            queryset = queryset.filter(annee_fabrication__lte=year_to)

        # Filtre par marque
        brand = self.request.GET.get("brand", "")
        if brand:
            queryset = queryset.filter(marque__icontains=brand)

        # Filtre par modèle
        model = self.request.GET.get("model", "")
        if model:
            queryset = queryset.filter(modele__icontains=model)

        # Filtre par statut de paiement
        payment_status = self.request.GET.get("payment_status", "")
        if payment_status == "paid":
            queryset = queryset.filter(paiements__statut="PAID").distinct()
        elif payment_status == "unpaid":
            queryset = queryset.exclude(paiements__statut="PAID").distinct()

        # Tri
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sorts = [
            "plaque_immatriculation",
            "-plaque_immatriculation",
            "created_at",
            "-created_at",
            "annee_fabrication",
            "-annee_fabrication",
            "marque",
            "-marque",
            "proprietaire__username",
            "-proprietaire__username",
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Mode d'affichage (liste ou grille)
        context["view_mode"] = self.request.GET.get("view", "list")

        # Paramètres de recherche pour les conserver dans la pagination
        context["search_params"] = self.request.GET.copy()
        if "page" in context["search_params"]:
            del context["search_params"]["page"]

        # Statistiques
        queryset = self.get_queryset()
        context["total_vehicles"] = queryset.count()
        context["active_vehicles"] = queryset.filter(est_actif=True).count()
        context["inactive_vehicles"] = queryset.filter(est_actif=False).count()

        # Choix pour les filtres
        from vehicles.models import VehicleType

        context["vehicle_types"] = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]
        context["vehicle_categories"] = Vehicule.CATEGORIE_CHOICES

        # Valeurs actuelles des filtres
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "type": self.request.GET.get("type", ""),
            "category": self.request.GET.get("category", ""),
            "status": self.request.GET.get("status", ""),
            "owner": self.request.GET.get("owner", ""),
            "year_from": self.request.GET.get("year_from", ""),
            "year_to": self.request.GET.get("year_to", ""),
            "brand": self.request.GET.get("brand", ""),
            "model": self.request.GET.get("model", ""),
            "payment_status": self.request.GET.get("payment_status", ""),
            "sort": self.request.GET.get("sort", "-created_at"),
        }

        # Nombre de filtres actifs
        active_filters = sum(1 for v in context["current_filters"].values() if v)
        context["active_filters_count"] = active_filters

        return context


@login_required
@admin_required
def advanced_vehicle_search_export(request):
    """Export des résultats de recherche en CSV/Excel"""
    # TODO: Implémenter l'export
    return JsonResponse({"status": "not_implemented"})


@login_required
@admin_required
def advanced_vehicle_search_stats(request):
    """Statistiques AJAX pour la recherche avancée"""
    queryset = Vehicule.objects.all()

    # Appliquer les mêmes filtres que la vue principale
    search = request.GET.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(plaque_immatriculation__icontains=search) | Q(proprietaire__username__icontains=search)
        )

    stats = {
        "total": queryset.count(),
        "active": queryset.filter(est_actif=True).count(),
        "inactive": queryset.filter(est_actif=False).count(),
        "by_type": {},
        "by_category": {},
    }

    # Stats par type
    from vehicles.models import VehicleType

    for vehicle_type in VehicleType.get_active_types():
        count = queryset.filter(type_vehicule=vehicle_type).count()
        if count > 0:
            stats["by_type"][vehicle_type.nom] = count

    # Stats par catégorie
    for cat_code, cat_name in Vehicule.CATEGORIE_CHOICES:
        count = queryset.filter(categorie_vehicule=cat_code).count()
        if count > 0:
            stats["by_category"][cat_name] = count

    return JsonResponse(stats)
