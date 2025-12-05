"""
Price Grids Management Views for Admin Console
"""

import csv
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from vehicles.models import GrilleTarifaire

from ..decorators import admin_required
from ..mixins import AdminRequiredMixin, is_admin_user


class PriceGridListView(AdminRequiredMixin, ListView):
    """List view for price grids with pagination and filters"""

    model = GrilleTarifaire
    template_name = "administration/price_grids/list.html"
    context_object_name = "price_grids"
    paginate_by = 50

    def get_queryset(self):
        queryset = GrilleTarifaire.objects.all().order_by("-annee_fiscale", "puissance_min_cv", "source_energie")

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(source_energie__icontains=search) | Q(annee_fiscale__icontains=search))

        # Filter by fiscal year
        annee_fiscale = self.request.GET.get("annee_fiscale")
        if annee_fiscale:
            queryset = queryset.filter(annee_fiscale=annee_fiscale)

        # Filter by energy source
        source_energie = self.request.GET.get("source_energie")
        if source_energie:
            queryset = queryset.filter(source_energie=source_energie)

        # Filter by active status
        est_active = self.request.GET.get("est_active")
        if est_active == "true":
            queryset = queryset.filter(est_active=True)
        elif est_active == "false":
            queryset = queryset.filter(est_active=False)

        # Sorting
        sort = self.request.GET.get("sort", "-annee_fiscale")
        if sort:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get unique fiscal years for filter
        context["fiscal_years"] = (
            GrilleTarifaire.objects.values_list("annee_fiscale", flat=True).distinct().order_by("-annee_fiscale")
        )

        # Energy source choices
        context["energy_sources"] = GrilleTarifaire.SOURCE_ENERGIE_CHOICES

        # Current filter values
        context["search"] = self.request.GET.get("search", "")
        context["selected_year"] = self.request.GET.get("annee_fiscale", "")
        context["selected_energy"] = self.request.GET.get("source_energie", "")
        context["selected_active"] = self.request.GET.get("est_active", "")
        context["current_sort"] = self.request.GET.get("sort", "-annee_fiscale")

        # Statistics
        context["total_grids"] = GrilleTarifaire.objects.count()
        context["active_grids"] = GrilleTarifaire.objects.filter(est_active=True).count()

        return context


class PriceGridDetailView(AdminRequiredMixin, DetailView):
    """Detail view for a single price grid"""

    model = GrilleTarifaire
    template_name = "administration/price_grids/detail.html"
    context_object_name = "price_grid"


class PriceGridCreateView(AdminRequiredMixin, CreateView):
    """Create view for price grids"""

    model = GrilleTarifaire
    template_name = "administration/price_grids/form.html"
    success_url = reverse_lazy("administration:price_grid_list")

    def get_form_class(self):
        from administration.forms.price_grids import PriceGridForm

        return PriceGridForm

    def form_valid(self, form):
        messages.success(self.request, "Price grid created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PriceGridUpdateView(AdminRequiredMixin, UpdateView):
    """Update view for price grids"""

    model = GrilleTarifaire
    template_name = "administration/price_grids/form.html"
    success_url = reverse_lazy("administration:price_grid_list")

    def get_form_class(self):
        from administration.forms.price_grids import PriceGridForm

        return PriceGridForm

    def form_valid(self, form):
        messages.success(self.request, "Price grid updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PriceGridDeleteView(AdminRequiredMixin, DeleteView):
    """Delete view for price grids"""

    model = GrilleTarifaire
    template_name = "administration/price_grids/delete_confirm.html"
    success_url = reverse_lazy("administration:price_grid_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Price grid deleted successfully.")
        return super().delete(request, *args, **kwargs)


@login_required
@admin_required
def price_grid_bulk_update(request):
    """AJAX endpoint for bulk operations on price grids"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        action = data.get("action")
        item_ids = data.get("items", [])

        if not action or not item_ids:
            return JsonResponse({"success": False, "message": "Missing action or items"}, status=400)

        # Get the price grids
        price_grids = GrilleTarifaire.objects.filter(id__in=item_ids)
        count = price_grids.count()

        if count == 0:
            return JsonResponse({"success": False, "message": "No price grids found"}, status=404)

        # Perform the action
        if action == "activate":
            price_grids.update(est_active=True)
            message = f"Successfully activated {count} price grid(s)"
        elif action == "deactivate":
            price_grids.update(est_active=False)
            message = f"Successfully deactivated {count} price grid(s)"
        elif action == "delete":
            price_grids.delete()
            message = f"Successfully deleted {count} price grid(s)"
        else:
            return JsonResponse({"success": False, "message": f"Unknown action: {action}"}, status=400)

        return JsonResponse({"success": True, "message": message, "count": count})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)


@login_required
@admin_required
def price_grid_import(request):
    """Import price grids from CSV or JSON file"""
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return render(request, "administration/price_grids/import.html")

        # Determine file type
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension not in ["csv", "json"]:
            messages.error(request, "Invalid file format. Please upload a CSV or JSON file.")
            return render(request, "administration/price_grids/import.html")

        try:
            if file_extension == "csv":
                result = _import_csv(uploaded_file, request)
            else:
                result = _import_json(uploaded_file, request)

            if result["success"]:
                messages.success(
                    request,
                    f"Successfully imported {result['created']} price grid(s). "
                    f"{result['skipped']} skipped due to errors.",
                )
                return redirect("administration:price_grid_list")
            else:
                messages.error(request, f"Import failed: {result['message']}")
                return render(request, "administration/price_grids/import.html", {"errors": result.get("errors", [])})

        except Exception as e:
            messages.error(request, f"Error during import: {str(e)}")
            return render(request, "administration/price_grids/import.html")

    return render(request, "administration/price_grids/import.html")


def _import_csv(uploaded_file, request):
    """Import price grids from CSV file"""
    from administration.forms.price_grids import PriceGridForm

    errors = []
    created = 0
    skipped = 0

    try:
        # Read CSV file
        decoded_file = uploaded_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Prepare data
                data = {
                    "puissance_min_cv": row.get("puissance_min_cv"),
                    "puissance_max_cv": row.get("puissance_max_cv") or None,
                    "source_energie": row.get("source_energie"),
                    "age_min_annees": row.get("age_min_annees", 0),
                    "age_max_annees": row.get("age_max_annees") or None,
                    "montant_ariary": row.get("montant_ariary"),
                    "annee_fiscale": row.get("annee_fiscale"),
                    "est_active": row.get("est_active", "true").lower() in ["true", "1", "yes"],
                }

                # Validate with form
                form = PriceGridForm(data)
                if form.is_valid():
                    form.save()
                    created += 1
                else:
                    skipped += 1
                    error_messages = []
                    for field, field_errors in form.errors.items():
                        error_messages.append(f"{field}: {', '.join(field_errors)}")
                    errors.append(f"Row {row_num}: {'; '.join(error_messages)}")

            except Exception as e:
                skipped += 1
                errors.append(f"Row {row_num}: {str(e)}")

        return {"success": True, "created": created, "skipped": skipped, "errors": errors}

    except Exception as e:
        return {"success": False, "message": str(e), "created": created, "skipped": skipped, "errors": errors}


def _import_json(uploaded_file, request):
    """Import price grids from JSON file"""
    from administration.forms.price_grids import PriceGridForm

    errors = []
    created = 0
    skipped = 0

    try:
        # Read JSON file
        data = json.loads(uploaded_file.read().decode("utf-8"))

        if not isinstance(data, list):
            return {
                "success": False,
                "message": "JSON file must contain an array of price grids",
                "created": 0,
                "skipped": 0,
            }

        for index, item in enumerate(data, start=1):
            try:
                # Validate with form
                form = PriceGridForm(item)
                if form.is_valid():
                    form.save()
                    created += 1
                else:
                    skipped += 1
                    error_messages = []
                    for field, field_errors in form.errors.items():
                        error_messages.append(f"{field}: {', '.join(field_errors)}")
                    errors.append(f"Item {index}: {'; '.join(error_messages)}")

            except Exception as e:
                skipped += 1
                errors.append(f"Item {index}: {str(e)}")

        return {"success": True, "created": created, "skipped": skipped, "errors": errors}

    except json.JSONDecodeError as e:
        return {"success": False, "message": f"Invalid JSON format: {str(e)}", "created": 0, "skipped": 0}
    except Exception as e:
        return {"success": False, "message": str(e), "created": created, "skipped": skipped, "errors": errors}


@login_required
@admin_required
def price_grid_export(request):
    """Export price grids to CSV or JSON"""
    export_format = request.GET.get("format", "csv")

    # Get filtered queryset based on request parameters
    queryset = GrilleTarifaire.objects.all().order_by("-annee_fiscale", "puissance_min_cv", "source_energie")

    # Apply filters from request
    annee_fiscale = request.GET.get("annee_fiscale")
    if annee_fiscale:
        queryset = queryset.filter(annee_fiscale=annee_fiscale)

    source_energie = request.GET.get("source_energie")
    if source_energie:
        queryset = queryset.filter(source_energie=source_energie)

    est_active = request.GET.get("est_active")
    if est_active == "true":
        queryset = queryset.filter(est_active=True)
    elif est_active == "false":
        queryset = queryset.filter(est_active=False)

    # Limit to 10,000 records
    queryset = queryset[:10000]

    if export_format == "json":
        return _export_json(queryset)
    else:
        return _export_csv(queryset)


def _export_csv(queryset):
    """Export price grids to CSV format"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="price_grids_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )

    writer = csv.writer(response)

    # Write header
    writer.writerow(
        [
            "ID",
            "Fiscal Year",
            "Min Power (CV)",
            "Max Power (CV)",
            "Energy Source",
            "Min Age (Years)",
            "Max Age (Years)",
            "Amount (Ariary)",
            "Active",
            "Created At",
        ]
    )

    # Write data
    for grid in queryset:
        writer.writerow(
            [
                grid.id,
                grid.annee_fiscale,
                grid.puissance_min_cv,
                grid.puissance_max_cv or "",
                grid.source_energie,
                grid.age_min_annees,
                grid.age_max_annees or "",
                float(grid.montant_ariary),
                grid.est_active,
                grid.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    return response


def _export_json(queryset):
    """Export price grids to JSON format"""
    data = []

    for grid in queryset:
        data.append(
            {
                "id": grid.id,
                "annee_fiscale": grid.annee_fiscale,
                "puissance_min_cv": grid.puissance_min_cv,
                "puissance_max_cv": grid.puissance_max_cv,
                "source_energie": grid.source_energie,
                "age_min_annees": grid.age_min_annees,
                "age_max_annees": grid.age_max_annees,
                "montant_ariary": float(grid.montant_ariary),
                "est_active": grid.est_active,
                "created_at": grid.created_at.isoformat(),
            }
        )

    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = (
        f'attachment; filename="price_grids_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    )

    return response


@login_required
@admin_required
def price_grid_report(request):
    """Generate custom reports for price grids"""
    # Get report parameters
    report_type = request.GET.get("type", "distribution")
    annee_fiscale = request.GET.get("annee_fiscale")

    if report_type == "distribution":
        # Price distribution report
        queryset = GrilleTarifaire.objects.all()

        if annee_fiscale:
            queryset = queryset.filter(annee_fiscale=annee_fiscale)

        # Group by energy source
        by_energy = (
            queryset.values("source_energie")
            .annotate(
                count=Count("id"),
                avg_amount=Avg("montant_ariary"),
                min_amount=models.Min("montant_ariary"),
                max_amount=models.Max("montant_ariary"),
            )
            .order_by("source_energie")
        )

        # Group by fiscal year
        by_year = (
            queryset.values("annee_fiscale")
            .annotate(count=Count("id"), avg_amount=Avg("montant_ariary"))
            .order_by("-annee_fiscale")
        )

        context = {
            "report_type": "distribution",
            "by_energy": by_energy,
            "by_year": by_year,
            "selected_year": annee_fiscale,
            "fiscal_years": GrilleTarifaire.objects.values_list("annee_fiscale", flat=True)
            .distinct()
            .order_by("-annee_fiscale"),
        }

        return render(request, "administration/price_grids/report.html", context)

    return redirect("administration:price_grid_list")


@login_required
@admin_required
def admin_tariff_grid_management(request):
    """
    Unified tariff grid management view for all vehicle categories.
    Displays 3 sections: Progressive (Terrestre), Forfaitaire Aérien, Forfaitaire Maritime
    """
    from administration.forms.price_grids import AerialTariffForm, MaritimeTariffForm

    # Get current fiscal year
    current_year = timezone.now().year
    selected_year = request.GET.get("year", current_year)
    try:
        selected_year = int(selected_year)
    except (ValueError, TypeError):
        selected_year = current_year

    # Handle form submissions
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "aerial":
            form = AerialTariffForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Grille tarifaire aérienne créée avec succès.")
                return redirect("administration:admin_tariff_grid_management")
            else:
                messages.error(request, "Erreur lors de la création de la grille aérienne.")

        elif form_type == "maritime":
            form = MaritimeTariffForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Grille tarifaire maritime créée avec succès.")
                return redirect("administration:admin_tariff_grid_management")
            else:
                messages.error(request, "Erreur lors de la création de la grille maritime.")

    # Get terrestrial grids (progressive)
    terrestrial_grids = GrilleTarifaire.objects.filter(grid_type="PROGRESSIVE", annee_fiscale=selected_year).order_by(
        "source_energie", "puissance_min_cv", "age_min_annees"
    )

    # Get aerial grids (flat rate)
    aerial_grids = GrilleTarifaire.objects.filter(grid_type="FLAT_AERIAL", annee_fiscale=selected_year).order_by(
        "aerial_type"
    )

    # Get maritime grids (flat rate by category)
    maritime_grids = GrilleTarifaire.objects.filter(grid_type="FLAT_MARITIME", annee_fiscale=selected_year).order_by(
        "maritime_category"
    )

    # Statistics
    stats = {
        "terrestrial": {
            "total": terrestrial_grids.count(),
            "active": terrestrial_grids.filter(est_active=True).count(),
        },
        "aerial": {
            "total": aerial_grids.count(),
            "active": aerial_grids.filter(est_active=True).count(),
        },
        "maritime": {
            "total": maritime_grids.count(),
            "active": maritime_grids.filter(est_active=True).count(),
        },
    }

    # Get available fiscal years
    fiscal_years = GrilleTarifaire.objects.values_list("annee_fiscale", flat=True).distinct().order_by("-annee_fiscale")

    # Initialize forms for creation
    aerial_form = AerialTariffForm(initial={"annee_fiscale": selected_year})
    maritime_form_navire = MaritimeTariffForm(
        initial={
            "annee_fiscale": selected_year,
            "maritime_category": "NAVIRE_PLAISANCE",
            "longueur_min_metres": 7.00,
            "puissance_min_cv_maritime": 22.00,
            "puissance_min_kw_maritime": 90.00,
            "montant_ariary": 200000.00,
        }
    )
    maritime_form_jetski = MaritimeTariffForm(
        initial={
            "annee_fiscale": selected_year,
            "maritime_category": "JETSKI",
            "puissance_min_kw_maritime": 90.00,
            "montant_ariary": 200000.00,
        }
    )
    maritime_form_autres = MaritimeTariffForm(
        initial={"annee_fiscale": selected_year, "maritime_category": "AUTRES_ENGINS", "montant_ariary": 1000000.00}
    )

    context = {
        "selected_year": selected_year,
        "fiscal_years": fiscal_years,
        "terrestrial_grids": terrestrial_grids,
        "aerial_grids": aerial_grids,
        "maritime_grids": maritime_grids,
        "stats": stats,
        "aerial_form": aerial_form,
        "maritime_form_navire": maritime_form_navire,
        "maritime_form_jetski": maritime_form_jetski,
        "maritime_form_autres": maritime_form_autres,
        "current_year": current_year,
    }

    return render(request, "administration/tariff_grids/management.html", context)


@login_required
@admin_required
def toggle_tariff_grid_status(request, grid_id):
    """Toggle the active status of a tariff grid"""
    if request.method == "POST":
        grid = get_object_or_404(GrilleTarifaire, id=grid_id)
        grid.est_active = not grid.est_active
        grid.save()

        status = "activée" if grid.est_active else "désactivée"
        messages.success(request, f"Grille tarifaire {status} avec succès.")

    return redirect("administration:admin_tariff_grid_management")


@login_required
@admin_required
def delete_tariff_grid(request, grid_id):
    """Delete a tariff grid"""
    if request.method == "POST":
        grid = get_object_or_404(GrilleTarifaire, id=grid_id)
        grid.delete()
        messages.success(request, "Grille tarifaire supprimée avec succès.")

    return redirect("administration:admin_tariff_grid_management")
