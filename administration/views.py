from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from payments.models import PaiementTaxe, QRCode
from vehicles.models import GrilleTarifaire, Vehicule

from .decorators import admin_required
from .mixins import AdminRequiredMixin, is_admin_user
from .models import AgentVerification, ConfigurationSysteme, StatistiquesPlateforme, VerificationQR


@login_required
@admin_required
def dashboard_view(request):
    """Main administration dashboard"""

    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Import cash models
    from payments.models import AgentPartenaireProfile, CashSession, CashTransaction

    # Basic statistics
    stats = {
        "total_users": User.objects.filter(is_active=True).count(),
        "total_vehicles": Vehicule.objects.count(),
        "total_payments": PaiementTaxe.objects.count(),
        "total_revenue": PaiementTaxe.objects.filter(statut="complete").aggregate(Sum("montant_paye_ariary"))[
            "montant_paye_ariary__sum"
        ]
        or 0,
        # Today's statistics
        "today_payments": PaiementTaxe.objects.filter(created_at__date=today).count(),
        "today_revenue": PaiementTaxe.objects.filter(created_at__date=today, statut="complete").aggregate(
            Sum("montant_paye_ariary")
        )["montant_paye_ariary__sum"]
        or 0,
        # This week
        "week_payments": PaiementTaxe.objects.filter(created_at__date__gte=week_ago).count(),
        "week_revenue": PaiementTaxe.objects.filter(created_at__date__gte=week_ago, statut="complete").aggregate(
            Sum("montant_paye_ariary")
        )["montant_paye_ariary__sum"]
        or 0,
        # QR Codes
        "total_qr_codes": QRCode.objects.count(),
        "active_qr_codes": QRCode.objects.filter(date_expiration__gt=timezone.now()).count(),
    }

    # Cash collection statistics
    cash_stats = {
        "total_agents": AgentPartenaireProfile.objects.filter(is_active=True).count(),
        "active_sessions": CashSession.objects.filter(status="open").count(),
        "today_cash_transactions": CashTransaction.objects.filter(
            transaction_time__date=today, is_voided=False
        ).count(),
        "today_cash_revenue": CashTransaction.objects.filter(transaction_time__date=today, is_voided=False).aggregate(
            Sum("tax_amount")
        )["tax_amount__sum"]
        or 0,
        "today_cash_commission": CashTransaction.objects.filter(
            transaction_time__date=today, is_voided=False
        ).aggregate(Sum("commission_amount"))["commission_amount__sum"]
        or 0,
        "week_cash_transactions": CashTransaction.objects.filter(
            transaction_time__date__gte=week_ago, is_voided=False
        ).count(),
        "week_cash_revenue": CashTransaction.objects.filter(
            transaction_time__date__gte=week_ago, is_voided=False
        ).aggregate(Sum("tax_amount"))["tax_amount__sum"]
        or 0,
        "pending_approvals": CashTransaction.objects.filter(
            requires_approval=True, approved_by__isnull=True, is_voided=False
        ).count(),
    }

    # Contraventions statistics
    try:
        from contraventions.models import Contestation, Contravention

        total_contraventions = Contravention.objects.count()
        monthly_contraventions = Contravention.objects.filter(date_heure_infraction__gte=month_ago).count()

        # Calculate monthly growth
        previous_month_start = month_ago - timedelta(days=30)
        previous_month_contraventions = Contravention.objects.filter(
            date_heure_infraction__gte=previous_month_start, date_heure_infraction__lt=month_ago
        ).count()

        if previous_month_contraventions > 0:
            monthly_growth = (
                (monthly_contraventions - previous_month_contraventions) / previous_month_contraventions
            ) * 100
        else:
            monthly_growth = 100 if monthly_contraventions > 0 else 0

        # Revenue from contraventions
        monthly_contravention_revenue = (
            Contravention.objects.filter(date_heure_infraction__gte=month_ago, statut="PAYEE").aggregate(
                Sum("montant_amende_ariary")
            )["montant_amende_ariary__sum"]
            or 0
        )

        # Payment rate
        paid_contraventions = Contravention.objects.filter(statut="PAYEE").count()
        payment_rate = (paid_contraventions / total_contraventions * 100) if total_contraventions > 0 else 0

        # Pending contestations
        pending_contestations = Contestation.objects.filter(statut="EN_ATTENTE").count()

        # Recent contraventions
        recent_contraventions = Contravention.objects.select_related(
            "type_infraction", "vehicule", "conducteur", "agent_controleur"
        ).order_by("-date_heure_infraction")[:5]

        contravention_stats = {
            "monthly_count": monthly_contraventions,
            "monthly_growth": monthly_growth,
            "monthly_revenue": monthly_contravention_revenue,
            "payment_rate": round(payment_rate, 2),
            "pending_contestations": pending_contestations,
        }
    except:
        # If contraventions app is not available
        contravention_stats = {
            "monthly_count": 0,
            "monthly_growth": 0,
            "monthly_revenue": 0,
            "payment_rate": 0,
            "pending_contestations": 0,
        }
        recent_contraventions = []

    # Top performing agents (by revenue this week)
    top_agents = (
        CashTransaction.objects.filter(transaction_time__date__gte=week_ago, is_voided=False)
        .values("collector__full_name", "collector__agent_id")
        .annotate(
            total_revenue=Sum("tax_amount"), total_transactions=Count("id"), total_commission=Sum("commission_amount")
        )
        .order_by("-total_revenue")[:5]
    )

    # Payment method breakdown
    payment_methods = (
        PaiementTaxe.objects.values("methode_paiement")
        .annotate(count=Count("*"), total=Sum("montant_paye_ariary"))
        .order_by("-count")
    )

    # Recent payments
    recent_payments = PaiementTaxe.objects.select_related("vehicule_plaque").order_by("-created_at")[:10]

    # Vehicle type breakdown
    vehicle_types = (
        Vehicule.objects.values("type_vehicule").annotate(count=Count("plaque_immatriculation")).order_by("-count")[:5]
    )

    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        revenue = (
            PaiementTaxe.objects.filter(created_at__date__range=[month_start, month_end], statut="complete").aggregate(
                Sum("montant_paye_ariary")
            )["montant_paye_ariary__sum"]
            or 0
        )

        monthly_revenue.append({"month": month_start.strftime("%B %Y"), "revenue": float(revenue)})

    monthly_revenue.reverse()

    # Payment status statistics (for all vehicles)
    current_year = timezone.now().year
    payment_status_stats = {
        "total_vehicles": 0,
        "exempt_vehicles": 0,
        "paid_valid": 0,
        "expiring_soon": 0,
        "expired": 0,
        "unpaid": 0,
    }

    all_vehicles = Vehicule.objects.filter(est_actif=True)
    for vehicle in all_vehicles:
        payment_status_stats["total_vehicles"] += 1

        status_info = vehicle.get_current_payment_status()
        status = status_info["status"]

        if status == "exempt":
            payment_status_stats["exempt_vehicles"] += 1
        elif status == "valid":
            payment_status_stats["paid_valid"] += 1
        elif status == "expiring_soon":
            payment_status_stats["expiring_soon"] += 1
        elif status == "expired":
            payment_status_stats["expired"] += 1
        elif status == "unpaid":
            payment_status_stats["unpaid"] += 1

    context = {
        "stats": stats,
        "cash_stats": cash_stats,
        "contravention_stats": contravention_stats,
        "recent_contraventions": recent_contraventions,
        "top_agents": top_agents,
        "payment_methods": payment_methods,
        "recent_payments": recent_payments,
        "vehicle_types": vehicle_types,
        "monthly_revenue": monthly_revenue,
        "payment_status_stats": payment_status_stats,
        "current_year": current_year,
    }

    return render(request, "administration/dashboard.html", context)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin access"""

    def test_func(self):
        return is_admin_user(self.request.user)


class VehicleManagementView(AdminRequiredMixin, ListView):
    """Vehicle fleet management"""

    model = Vehicule
    template_name = "administration/vehicle_management.html"
    context_object_name = "vehicles"
    paginate_by = 20

    def get_queryset(self):
        queryset = Vehicule.objects.select_related("proprietaire").order_by("-created_at")

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search)
                | Q(proprietaire__first_name__icontains=search)
                | Q(proprietaire__last_name__icontains=search)
                | Q(proprietaire__email__icontains=search)
            )

        # Filter by vehicle type
        vehicle_type = self.request.GET.get("type")
        if vehicle_type:
            try:
                # Convert to integer if it's an ID
                vehicle_type_id = int(vehicle_type)
                queryset = queryset.filter(type_vehicule_id=vehicle_type_id)
            except (ValueError, TypeError):
                # If it's not a valid ID, try to filter by name
                queryset = queryset.filter(type_vehicule__nom__icontains=vehicle_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicles.models import VehicleType

        # Get active vehicle types as choices (id, nom)
        context["vehicle_types"] = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]
        context["search"] = self.request.GET.get("search", "")

        # Get selected type and convert to integer if possible for comparison
        selected_type = self.request.GET.get("type", "")
        try:
            context["selected_type"] = int(selected_type) if selected_type else ""
        except (ValueError, TypeError):
            context["selected_type"] = selected_type

        return context


class UserManagementView(AdminRequiredMixin, ListView):
    """User management"""

    model = User
    template_name = "administration/user_management.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.order_by("-date_joined")

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        elif status == "staff":
            queryset = queryset.filter(is_staff=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class PaymentManagementView(AdminRequiredMixin, ListView):
    """Payment management"""

    model = PaiementTaxe
    template_name = "administration/payment_management.html"
    context_object_name = "payments"
    paginate_by = 20

    def get_queryset(self):
        queryset = PaiementTaxe.objects.select_related("vehicule_plaque", "vehicule_plaque__proprietaire").order_by(
            "-created_at"
        )

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(vehicule_plaque__plaque_immatriculation__icontains=search)
                | Q(vehicule_plaque__proprietaire__username__icontains=search)
                | Q(transaction_id__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(statut=status)

        # Filter by payment method
        method = self.request.GET.get("method")
        if method:
            queryset = queryset.filter(methode_paiement=method)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statut_choices"] = PaiementTaxe.STATUT_CHOICES
        context["method_choices"] = PaiementTaxe.METHODE_PAIEMENT_CHOICES
        context["search"] = self.request.GET.get("search", "")
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_method"] = self.request.GET.get("method", "")
        return context


@login_required
@admin_required
def analytics_view(request):
    """Analytics and reporting"""

    # Get date range from request
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

    # Payment analytics
    payments_in_range = PaiementTaxe.objects.filter(created_at__date__range=[start_date, end_date])

    analytics = {
        "total_payments": payments_in_range.count(),
        "successful_payments": payments_in_range.filter(statut="complete").count(),
        "pending_payments": payments_in_range.filter(statut="en_attente").count(),
        "failed_payments": payments_in_range.filter(statut="echec").count(),
        "total_revenue": payments_in_range.filter(statut="complete").aggregate(Sum("montant_paye_ariary"))[
            "montant_paye_ariary__sum"
        ]
        or 0,
        "average_payment": payments_in_range.filter(statut="complete").aggregate(Avg("montant_paye_ariary"))[
            "montant_paye_ariary__avg"
        ]
        or 0,
    }

    # Daily breakdown
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        day_payments = payments_in_range.filter(created_at__date=current_date)
        daily_stats.append(
            {
                "date": current_date.strftime("%Y-%m-%d"),
                "payments": day_payments.count(),
                "revenue": day_payments.filter(statut="complete").aggregate(Sum("montant_paye_ariary"))[
                    "montant_paye_ariary__sum"
                ]
                or 0,
            }
        )
        current_date += timedelta(days=1)

    context = {
        "analytics": analytics,
        "daily_stats": daily_stats,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    return render(request, "administration/analytics.html", context)


@login_required
@admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        was_active = user.is_active
        user.is_active = not user.is_active
        user.save()

        # Create notification for user
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(user, "profile"):
            langue = user.profile.langue_preferee

        if user.is_active:
            NotificationService.create_account_reactivated_notification(user=user, langue=langue)
        else:
            NotificationService.create_account_deactivated_notification(user=user, langue=langue)

        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"L'utilisateur {user.username} a été {status}.")

    return redirect("administration:user_management")


@login_required
@admin_required
def dashboard_api_stats(request):
    """API endpoint for dashboard statistics"""

    today = timezone.now().date()

    # Real-time stats
    stats = {
        "total_users": User.objects.filter(is_active=True).count(),
        "total_vehicles": Vehicule.objects.count(),
        "today_payments": PaiementTaxe.objects.filter(created_at__date=today).count(),
        "today_revenue": float(
            PaiementTaxe.objects.filter(created_at__date=today, statut="complete").aggregate(
                Sum("montant_paye_ariary")
            )["montant_paye_ariary__sum"]
            or 0
        ),
        "pending_payments": PaiementTaxe.objects.filter(statut="en_attente").count(),
    }

    return JsonResponse(stats)


@login_required
@admin_required
def test_components_view(request):
    """Test page for Material Design components"""
    return render(request, "admin_console/test_components.html")


@login_required
@admin_required
def payment_gateways_view(request):
    """Payment Gateway Management Dashboard"""
    from django.conf import settings

    from payments.models import MvolaConfiguration

    # Get MVola configurations
    mvola_configs = MvolaConfiguration.objects.all().order_by("-is_active", "-created_at")
    mvola_active = MvolaConfiguration.get_active_config()

    # Get Stripe configuration from settings
    stripe_enabled = bool(getattr(settings, "STRIPE_PUBLIC_KEY", None) and getattr(settings, "STRIPE_SECRET_KEY", None))
    stripe_config = {
        "name": "Stripe",
        "is_active": stripe_enabled,
        "is_configured": stripe_enabled,
        "environment": "production" if not getattr(settings, "STRIPE_TEST_MODE", True) else "test",
        "public_key": getattr(settings, "STRIPE_PUBLIC_KEY", "")[:20] + "..." if stripe_enabled else "Non configuré",
    }

    # Placeholder for future payment gateways
    orange_money_config = {
        "name": "Orange Money",
        "is_active": False,
        "is_configured": False,
        "status": "coming_soon",
        "description": "Bientôt disponible",
    }

    airtel_money_config = {
        "name": "Airtel Money",
        "is_active": False,
        "is_configured": False,
        "status": "coming_soon",
        "description": "Bientôt disponible",
    }

    # Get payment statistics
    from payments.models import PaiementTaxe

    # MVola statistics
    mvola_stats = {
        "total": PaiementTaxe.objects.filter(methode_paiement="mvola").count(),
        "successful": PaiementTaxe.objects.filter(methode_paiement="mvola", statut="PAYE").count(),
        "pending": PaiementTaxe.objects.filter(methode_paiement="mvola", statut="EN_ATTENTE").count(),
        "failed": PaiementTaxe.objects.filter(methode_paiement="mvola", statut__in=["ANNULE", "ECHEC"]).count(),
        "total_amount": PaiementTaxe.objects.filter(methode_paiement="mvola", statut="PAYE").aggregate(
            Sum("montant_paye_ariary")
        )["montant_paye_ariary__sum"]
        or 0,
    }

    # Stripe statistics
    stripe_stats = {
        "total": PaiementTaxe.objects.filter(methode_paiement="stripe").count(),
        "successful": PaiementTaxe.objects.filter(methode_paiement="stripe", statut="PAYE").count(),
        "pending": PaiementTaxe.objects.filter(methode_paiement="stripe", statut="EN_ATTENTE").count(),
        "failed": PaiementTaxe.objects.filter(methode_paiement="stripe", statut__in=["ANNULE", "ECHEC"]).count(),
        "total_amount": PaiementTaxe.objects.filter(methode_paiement="stripe", statut="PAYE").aggregate(
            Sum("montant_paye_ariary")
        )["montant_paye_ariary__sum"]
        or 0,
    }

    # Calculate success rates
    if mvola_stats["total"] > 0:
        mvola_stats["success_rate"] = round((mvola_stats["successful"] / mvola_stats["total"]) * 100, 1)
    else:
        mvola_stats["success_rate"] = 0

    if stripe_stats["total"] > 0:
        stripe_stats["success_rate"] = round((stripe_stats["successful"] / stripe_stats["total"]) * 100, 1)
    else:
        stripe_stats["success_rate"] = 0

    context = {
        "mvola_configs": mvola_configs,
        "mvola_active": mvola_active,
        "mvola_stats": mvola_stats,
        "stripe_config": stripe_config,
        "stripe_stats": stripe_stats,
        "orange_money_config": orange_money_config,
        "airtel_money_config": airtel_money_config,
        "total_gateways": 4,
        "active_gateways": sum(
            [
                1 if mvola_active and mvola_active.is_enabled else 0,
                1 if stripe_enabled else 0,
            ]
        ),
    }

    return render(request, "administration/payment_gateways.html", context)


@login_required
@admin_required
def mvola_config_detail_view(request, config_id):
    """MVola Configuration Detail View"""
    from payments.models import MvolaConfiguration

    config = get_object_or_404(MvolaConfiguration, pk=config_id)

    # Get transaction statistics for this config
    from payments.models import PaiementTaxe

    if config.is_active:
        transactions = PaiementTaxe.objects.filter(methode_paiement="mvola").order_by("-created_at")[:10]
    else:
        transactions = []

    context = {
        "config": config,
        "transactions": transactions,
    }

    return render(request, "administration/mvola_config_detail.html", context)


@login_required
@admin_required
def mvola_config_test_view(request, config_id):
    """Test MVola Configuration"""
    from payments.models import MvolaConfiguration

    config = get_object_or_404(MvolaConfiguration, pk=config_id)

    if request.method == "POST":
        success, message = config.test_connection()

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("administration:mvola_config_detail", config_id=config_id)

    return redirect("administration:payment_gateways")


@login_required
@admin_required
def mvola_config_toggle_view(request, config_id):
    """Toggle MVola Configuration Active Status"""
    from payments.models import MvolaConfiguration

    config = get_object_or_404(MvolaConfiguration, pk=config_id)

    if request.method == "POST":
        if config.is_active:
            # Deactivate
            config.is_active = False
            config.save()
            messages.success(request, f"Configuration '{config.name}' désactivée")
        else:
            # Deactivate all other configs
            MvolaConfiguration.objects.filter(is_active=True).update(is_active=False)

            # Activate this config
            config.is_active = True
            config.save()

            # Apply to settings
            config.apply_to_settings()

            messages.success(request, f"Configuration '{config.name}' activée")

    return redirect("administration:payment_gateways")


@login_required
@admin_required
def admin_declaration_validation_queue(request):
    """
    Declaration validation queue for administrators.
    Lists all vehicles pending validation, grouped by category.
    """
    from payments.models import PaiementTaxe
    from vehicles.models import Vehicule

    # Get filter parameters
    vehicle_category = request.GET.get("vehicle_category", "")
    search = request.GET.get("search", "")

    # Get all vehicles that need validation (unpaid or pending payment)
    # For now, we consider vehicles without completed payments as "pending"
    queryset = (
        Vehicule.objects.filter(est_actif=True).select_related("proprietaire", "type_vehicule").order_by("-created_at")
    )

    # Filter by category
    if vehicle_category:
        queryset = queryset.filter(vehicle_category=vehicle_category)

    # Search functionality
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

    # Annotate with payment status
    vehicles_with_status = []
    for vehicle in queryset[:100]:  # Limit to 100 for performance
        payment_status = vehicle.get_current_payment_status()
        vehicles_with_status.append(
            {
                "vehicle": vehicle,
                "payment_status": payment_status,
                "needs_validation": payment_status["status"] in ["unpaid", "expired"],
            }
        )

    # Filter to only show vehicles needing validation
    pending_vehicles = [v for v in vehicles_with_status if v["needs_validation"]]

    # Statistics by category
    all_pending = Vehicule.objects.filter(est_actif=True)
    stats_by_category = {
        "TERRESTRE": {
            "count": all_pending.filter(vehicle_category="TERRESTRE").count(),
            "icon": "ri-car-line",
            "name": "Terrestres",
            "color": "primary",
        },
        "AERIEN": {
            "count": all_pending.filter(vehicle_category="AERIEN").count(),
            "icon": "ri-plane-line",
            "name": "Aériens",
            "color": "info",
        },
        "MARITIME": {
            "count": all_pending.filter(vehicle_category="MARITIME").count(),
            "icon": "ri-ship-line",
            "name": "Maritimes",
            "color": "success",
        },
    }

    context = {
        "pending_vehicles": pending_vehicles,
        "vehicle_category_filter": vehicle_category,
        "search_query": search,
        "stats_by_category": stats_by_category,
        "total_pending": len(pending_vehicles),
    }

    return render(request, "administration/declarations/validation_queue.html", context)


@login_required
@admin_required
def validate_vehicle_declaration(request, vehicle_pk):
    """Validate a vehicle declaration"""
    if request.method == "POST":
        vehicle = get_object_or_404(Vehicule, pk=vehicle_pk)

        # Create notification for validation
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(vehicle.proprietaire, "profile"):
            langue = vehicle.proprietaire.profile.langue_preferee

        # For now, validation means the vehicle is approved
        # In the future, this would update statut_declaration field
        messages.success(
            request,
            f"Déclaration du véhicule {vehicle.plaque_immatriculation or vehicle.immatriculation_aerienne or vehicle.numero_francisation} validée.",
        )

        # Send notification to owner
        NotificationService.create_vehicle_added_notification(user=vehicle.proprietaire, vehicle=vehicle, langue=langue)

    return redirect("administration:admin_declaration_validation_queue")


@login_required
@admin_required
def reject_vehicle_declaration(request, vehicle_pk):
    """Reject a vehicle declaration"""
    if request.method == "POST":
        vehicle = get_object_or_404(Vehicule, pk=vehicle_pk)
        rejection_reason = request.POST.get("rejection_reason", "")

        if not rejection_reason:
            messages.error(request, "Veuillez fournir une raison de rejet.")
            return redirect("administration:admin_declaration_validation_queue")

        # For now, we just send a notification
        # In the future, this would update statut_declaration field
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(vehicle.proprietaire, "profile"):
            langue = vehicle.proprietaire.profile.langue_preferee

        messages.warning(
            request,
            f"Déclaration du véhicule {vehicle.plaque_immatriculation or vehicle.immatriculation_aerienne or vehicle.numero_francisation} rejetée.",
        )

        # TODO: Send rejection notification with reason
        # NotificationService.create_vehicle_rejected_notification(...)

    return redirect("administration:admin_declaration_validation_queue")


@login_required
@admin_required
def multi_vehicle_statistics_dashboard(request):
    """
    Statistics dashboard for multi-category vehicles.
    Shows distribution, revenue, and trends by vehicle category.
    """
    from datetime import timedelta

    from django.db.models.functions import TruncMonth

    from payments.models import PaiementTaxe
    from vehicles.models import VehicleType, Vehicule

    # Get date range
    today = timezone.now().date()
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            start_date = today - timedelta(days=365)
            end_date = today
    else:
        start_date = today - timedelta(days=365)
        end_date = today

    # Vehicle distribution by category
    vehicle_distribution = {
        "TERRESTRE": Vehicule.objects.filter(vehicle_category="TERRESTRE", est_actif=True).count(),
        "AERIEN": Vehicule.objects.filter(vehicle_category="AERIEN", est_actif=True).count(),
        "MARITIME": Vehicule.objects.filter(vehicle_category="MARITIME", est_actif=True).count(),
    }
    total_vehicles = sum(vehicle_distribution.values())

    # Calculate percentages
    vehicle_distribution_percent = {}
    for category, count in vehicle_distribution.items():
        vehicle_distribution_percent[category] = {
            "count": count,
            "percent": round((count / total_vehicles * 100) if total_vehicles > 0 else 0, 1),
        }

    # Revenue by category
    revenue_by_category = {}
    for category in ["TERRESTRE", "AERIEN", "MARITIME"]:
        vehicles = Vehicule.objects.filter(vehicle_category=category, est_actif=True)
        vehicle_ids = [v.plaque_immatriculation for v in vehicles]

        revenue = (
            PaiementTaxe.objects.filter(
                vehicule_plaque__in=vehicle_ids, statut="complete", created_at__date__range=[start_date, end_date]
            ).aggregate(Sum("montant_paye_ariary"))["montant_paye_ariary__sum"]
            or 0
        )

        revenue_by_category[category] = float(revenue)

    total_revenue = sum(revenue_by_category.values())

    # Monthly evolution by category (last 6 months)
    monthly_evolution = {}
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_label = month_start.strftime("%b %Y")

        monthly_evolution[month_label] = {}

        for category in ["TERRESTRE", "AERIEN", "MARITIME"]:
            # Count new vehicles in this month
            count = Vehicule.objects.filter(
                vehicle_category=category, created_at__date__range=[month_start, month_end]
            ).count()
            monthly_evolution[month_label][category] = count

    # Reverse to show oldest first
    monthly_evolution = dict(reversed(list(monthly_evolution.items())))

    # Top 10 vehicle types
    top_vehicle_types = VehicleType.objects.annotate(vehicle_count=Count("vehicule")).order_by("-vehicle_count")[:10]

    # Payment rate by category
    payment_rates = {}
    for category in ["TERRESTRE", "AERIEN", "MARITIME"]:
        vehicles = Vehicule.objects.filter(vehicle_category=category, est_actif=True)
        total = vehicles.count()

        if total > 0:
            paid_count = 0
            for vehicle in vehicles:
                payment_status = vehicle.get_current_payment_status()
                if payment_status["status"] == "valid":
                    paid_count += 1

            payment_rates[category] = {"total": total, "paid": paid_count, "rate": round((paid_count / total * 100), 1)}
        else:
            payment_rates[category] = {"total": 0, "paid": 0, "rate": 0}

    # Recent activity (last 10 vehicles added)
    recent_vehicles = Vehicule.objects.select_related("proprietaire", "type_vehicule").order_by("-created_at")[:10]

    context = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "vehicle_distribution": vehicle_distribution_percent,
        "total_vehicles": total_vehicles,
        "revenue_by_category": revenue_by_category,
        "total_revenue": total_revenue,
        "monthly_evolution": monthly_evolution,
        "top_vehicle_types": top_vehicle_types,
        "payment_rates": payment_rates,
        "recent_vehicles": recent_vehicles,
    }

    return render(request, "administration/statistics/multi_vehicle_dashboard.html", context)
