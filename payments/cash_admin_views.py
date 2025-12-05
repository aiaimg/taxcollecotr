"""
Cash Payment Admin Views
Handles administrative functions for cash payment system
"""

import csv
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO, StringIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models, transaction
from django.db.models import Avg, Count, F, Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from core.models import User, UserProfile
from vehicles.models import VehicleType, Vehicule

from .forms import (
    AgentPartenaireForm,
    CashSystemConfigForm,
    ReconciliationForm,
    TransactionApprovalForm,
)
from .models import (
    AgentPartenaireProfile,
    CashAuditLog,
    CashReceipt,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    CommissionRecord,
    PaiementTaxe,
)
from .services.cash_audit_service import CashAuditService
from .services.cash_payment_service import CashPaymentService
from .services.cash_session_service import CashSessionService
from .services.commission_service import CommissionService
from .services.reconciliation_service import ReconciliationService

# ============================================================================
# MIXINS FOR PERMISSION CHECKING
# ============================================================================


class AdminStaffMixin(UserPassesTestMixin):
    """
    Mixin to ensure user is admin staff with proper permissions
    Checks:
    1. User is staff or superuser
    2. User is in "Admin Staff" group OR is superuser
    """

    def test_func(self):
        user = self.request.user

        # Superusers always have access
        if user.is_superuser:
            return True

        # Check if user is staff and in Admin Staff group
        is_staff = user.is_staff
        is_in_group = user.groups.filter(name="Admin Staff").exists()

        return is_staff and is_in_group

    def handle_no_permission(self):
        messages.error(self.request, _("Vous devez être un administrateur pour accéder à cette page."))
        return redirect("core:dashboard")


# ============================================================================
# TASK 5.1: COLLECTOR LIST VIEW
# ============================================================================


class CollectorListView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    List all Agent Partenaire profiles with search and filters
    Requirements: 15
    """

    model = AgentPartenaireProfile
    template_name = "payments/cash/admin/collector_list.html"
    context_object_name = "collectors"
    paginate_by = 20

    def get_queryset(self):
        queryset = AgentPartenaireProfile.objects.select_related("user", "created_by").all()

        # Search filter
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(agent_id__icontains=search_query)
                | Q(full_name__icontains=search_query)
                | Q(phone_number__icontains=search_query)
                | Q(collection_location__icontains=search_query)
            )

        # Status filter
        status = self.request.GET.get("status", "")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        # Location filter
        location = self.request.GET.get("location", "").strip()
        if location:
            queryset = queryset.filter(collection_location__icontains=location)

        # Order by
        order_by = self.request.GET.get("order_by", "-created_at")
        queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values for form persistence
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["location_filter"] = self.request.GET.get("location", "")
        context["order_by"] = self.request.GET.get("order_by", "-created_at")

        # Get statistics
        context["total_collectors"] = AgentPartenaireProfile.objects.count()
        context["active_collectors"] = AgentPartenaireProfile.objects.filter(is_active=True).count()
        context["inactive_collectors"] = AgentPartenaireProfile.objects.filter(is_active=False).count()

        # Get unique locations for filter dropdown
        context["locations"] = (
            AgentPartenaireProfile.objects.values_list("collection_location", flat=True)
            .distinct()
            .order_by("collection_location")
        )

        return context


# ============================================================================
# TASK 5.2: COLLECTOR CREATE VIEW
# ============================================================================


class CollectorCreateView(LoginRequiredMixin, AdminStaffMixin, CreateView):
    """
    Create new Agent Partenaire
    Requirements: 6, 14, 15
    """

    model = AgentPartenaireProfile
    form_class = AgentPartenaireForm
    template_name = "payments/cash/admin/collector_form.html"
    success_url = reverse_lazy("payments:admin_collector_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "create"
        context["title"] = _("Créer un Agent Partenaire")

        # Get default commission rate from config
        config = CashSystemConfig.get_config()
        context["default_commission_rate"] = config.default_commission_rate

        return context

    def form_valid(self, form):
        # Set created_by to current user
        form.instance.created_by = self.request.user

        response = super().form_valid(form)

        messages.success(self.request, _(f"Agent Partenaire {form.instance.full_name} créé avec succès."))

        # Log action
        CashAuditService.log_action(
            action_type="agent_created",
            user=self.request.user,
            data={
                "agent_id": form.instance.agent_id,
                "full_name": form.instance.full_name,
                "collection_location": form.instance.collection_location,
            },
            request=self.request,
        )

        return response


# ============================================================================
# TASK 5.3: COLLECTOR UPDATE VIEW
# ============================================================================


class CollectorUpdateView(LoginRequiredMixin, AdminStaffMixin, UpdateView):
    """
    Edit Agent Partenaire details, update commission rate, activate/deactivate
    Requirements: 6, 14, 15
    """

    model = AgentPartenaireProfile
    form_class = AgentPartenaireForm
    template_name = "payments/cash/admin/collector_form.html"

    def get_success_url(self):
        return reverse("payments:admin_collector_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "update"
        context["title"] = _(f"Modifier {self.object.full_name}")

        # Get default commission rate from config
        config = CashSystemConfig.get_config()
        context["default_commission_rate"] = config.default_commission_rate

        return context

    def form_valid(self, form):
        # Track changes for audit log
        changes = {}
        for field in form.changed_data:
            old_value = getattr(self.object, field)
            new_value = form.cleaned_data[field]
            changes[field] = {"old": str(old_value), "new": str(new_value)}

        response = super().form_valid(form)

        messages.success(self.request, _(f"Agent Partenaire {form.instance.full_name} mis à jour avec succès."))

        # Log action
        if changes:
            CashAuditService.log_action(
                action_type="agent_updated",
                user=self.request.user,
                data={
                    "agent_id": form.instance.agent_id,
                    "changes": changes,
                },
                request=self.request,
            )

        return response


# ============================================================================
# TASK 5.4: COLLECTOR DETAIL VIEW
# ============================================================================


class CollectorDetailView(LoginRequiredMixin, AdminStaffMixin, DetailView):
    """
    Show agent details, session history, commission totals, performance metrics
    Requirements: 6, 11, 15
    """

    model = AgentPartenaireProfile
    template_name = "payments/cash/admin/collector_detail.html"
    context_object_name = "collector"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collector = self.get_object()

        # Get date range from query params (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

        context["date_from"] = start_date
        context["date_to"] = end_date

        # Get session history
        sessions = CashSession.objects.filter(
            collector=collector, opening_time__date__gte=start_date, opening_time__date__lte=end_date
        ).order_by("-opening_time")
        context["sessions"] = sessions

        # Get commission totals
        commission_data = CommissionService.get_collector_commission_report(
            collector=collector, start_date=start_date, end_date=end_date
        )
        context["commission_data"] = commission_data

        # Get performance metrics
        transactions = CashTransaction.objects.filter(
            collector=collector,
            is_voided=False,
            transaction_time__date__gte=start_date,
            transaction_time__date__lte=end_date,
        )

        metrics = transactions.aggregate(
            total_transactions=Count("id"),
            total_tax_collected=Sum("tax_amount"),
            total_commission=Sum("commission_amount"),
            avg_transaction_amount=Avg("tax_amount"),
        )
        context["metrics"] = metrics

        # Get recent transactions
        recent_transactions = transactions.order_by("-transaction_time")[:10]
        context["recent_transactions"] = recent_transactions

        # Get session statistics
        session_stats = sessions.aggregate(
            total_sessions=Count("id"),
            open_sessions=Count("id", filter=Q(status="open")),
            closed_sessions=Count("id", filter=Q(status="closed")),
            reconciled_sessions=Count("id", filter=Q(status="reconciled")),
            total_discrepancies=Sum("discrepancy_amount"),
        )
        context["session_stats"] = session_stats

        return context


# ============================================================================
# TASK 5.5: TRANSACTION APPROVAL LIST VIEW
# ============================================================================


class TransactionApprovalListView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    List pending approvals with filters
    Requirements: 8
    """

    model = CashTransaction
    template_name = "payments/cash/admin/approval_list.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            CashTransaction.objects.filter(requires_approval=True, approved_by__isnull=True, is_voided=False)
            .select_related("collector", "session", "payment")
            .order_by("-transaction_time")
        )

        # Amount filter
        min_amount = self.request.GET.get("min_amount")
        max_amount = self.request.GET.get("max_amount")

        if min_amount:
            queryset = queryset.filter(tax_amount__gte=Decimal(min_amount))
        if max_amount:
            queryset = queryset.filter(tax_amount__lte=Decimal(max_amount))

        # Date filter
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(transaction_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_time__date__lte=date_to)

        # Agent filter
        agent_id = self.request.GET.get("agent")
        if agent_id:
            queryset = queryset.filter(collector_id=agent_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values
        context["min_amount"] = self.request.GET.get("min_amount", "")
        context["max_amount"] = self.request.GET.get("max_amount", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["selected_agent"] = self.request.GET.get("agent", "")

        # Get agents for filter dropdown
        context["agents"] = AgentPartenaireProfile.objects.filter(is_active=True).order_by("full_name")

        # Get statistics
        pending_count = CashTransaction.objects.filter(
            requires_approval=True, approved_by__isnull=True, is_voided=False
        ).count()

        pending_total = CashTransaction.objects.filter(
            requires_approval=True, approved_by__isnull=True, is_voided=False
        ).aggregate(total=Sum("tax_amount"))["total"] or Decimal("0")

        context["pending_count"] = pending_count
        context["pending_total"] = pending_total

        # Get dual verification threshold
        config = CashSystemConfig.get_config()
        context["dual_verification_threshold"] = config.dual_verification_threshold

        return context


# ============================================================================
# TASK 5.6: TRANSACTION APPROVE VIEW
# ============================================================================


class TransactionApproveView(LoginRequiredMixin, AdminStaffMixin, View):
    """
    Approve or reject transaction with notes and notification
    Requirements: 8
    """

    template_name = "payments/cash/admin/transaction_approve.html"

    def get(self, request, pk):
        transaction_obj = get_object_or_404(
            CashTransaction, pk=pk, requires_approval=True, approved_by__isnull=True, is_voided=False
        )

        form = TransactionApprovalForm()

        context = {
            "transaction": transaction_obj,
            "form": form,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        transaction_obj = get_object_or_404(
            CashTransaction, pk=pk, requires_approval=True, approved_by__isnull=True, is_voided=False
        )

        form = TransactionApprovalForm(request.POST)

        if not form.is_valid():
            context = {
                "transaction": transaction_obj,
                "form": form,
            }
            return render(request, self.template_name, context)

        action = form.cleaned_data["action"]
        approval_notes = form.cleaned_data.get("approval_notes", "")

        if action == "approve":
            # Approve transaction
            success, error = CashPaymentService.approve_transaction(
                transaction=transaction_obj, admin_user=request.user, notes=approval_notes, request=request
            )

            if error:
                messages.error(request, error)
            else:
                messages.success(request, _(f"Transaction {transaction_obj.transaction_number} approuvée avec succès."))

                # Send notification to agent (if notification system is available)
                try:
                    from notifications.services import NotificationService

                    NotificationService.create_notification(
                        user=transaction_obj.collector.user,
                        notification_type="transaction_approved",
                        title=_("Transaction approuvée"),
                        message=_(f"Votre transaction {transaction_obj.transaction_number} a été approuvée."),
                        related_object=transaction_obj,
                    )
                except ImportError:
                    pass

        elif action == "reject":
            # Reject transaction (void it)
            success, error = CashPaymentService.void_transaction(
                transaction=transaction_obj,
                admin_user=request.user,
                reason=f"Rejeté par admin: {approval_notes}",
                request=request,
            )

            if error:
                messages.error(request, error)
            else:
                messages.warning(request, _(f"Transaction {transaction_obj.transaction_number} rejetée et annulée."))

                # Send notification to agent
                try:
                    from notifications.services import NotificationService

                    NotificationService.create_notification(
                        user=transaction_obj.collector.user,
                        notification_type="transaction_rejected",
                        title=_("Transaction rejetée"),
                        message=_(
                            f"Votre transaction {transaction_obj.transaction_number} a été rejetée. Raison: {approval_notes}"
                        ),
                        related_object=transaction_obj,
                    )
                except ImportError:
                    pass

        return redirect("payments:admin_approval_list")


# ============================================================================
# TASK 5.7: DAILY RECONCILIATION VIEW
# ============================================================================


class DailyReconciliationView(LoginRequiredMixin, AdminStaffMixin, TemplateView):
    """
    Show all sessions for selected date, calculate totals, enter physical count
    Requirements: 10
    """

    template_name = "payments/cash/admin/reconciliation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date from query params (default to today)
        reconciliation_date_str = self.request.GET.get("date", timezone.now().date().isoformat())
        reconciliation_date = datetime.strptime(reconciliation_date_str, "%Y-%m-%d").date()

        context["reconciliation_date"] = reconciliation_date

        # Get all sessions for the date
        sessions = (
            CashSession.objects.filter(opening_time__date=reconciliation_date)
            .select_related("collector")
            .order_by("opening_time")
        )

        context["sessions"] = sessions

        # Calculate expected totals
        report_data = ReconciliationService.generate_daily_report(reconciliation_date)
        context["report_data"] = report_data

        # Get config for tolerance
        config = CashSystemConfig.get_config()
        context["reconciliation_tolerance"] = config.reconciliation_tolerance

        # Check if already reconciled
        context["is_reconciled"] = all(session.status == "reconciled" for session in sessions)

        return context

    def post(self, request):
        form = ReconciliationForm(request.POST)

        if not form.is_valid():
            messages.error(request, _("Formulaire invalide."))
            return redirect("payments:admin_reconciliation")

        reconciliation_date = form.cleaned_data["reconciliation_date"]
        physical_cash_count = form.cleaned_data["physical_cash_count"]
        reconciliation_notes = form.cleaned_data.get("reconciliation_notes", "")

        # Perform reconciliation
        success, error = ReconciliationService.reconcile_day(
            date=reconciliation_date,
            admin_user=request.user,
            physical_count=physical_cash_count,
            notes=reconciliation_notes,
            request=request,
        )

        if error:
            messages.error(request, error)
        else:
            messages.success(request, _(f"Réconciliation du {reconciliation_date} effectuée avec succès."))

        return redirect(f"{reverse('payments:admin_reconciliation')}?date={reconciliation_date}")


# ============================================================================
# TASK 5.8: RECONCILIATION REPORT VIEW
# ============================================================================


class ReconciliationReportView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    Show reconciliation history with filters and export
    Requirements: 10, 11
    """

    model = CashSession
    template_name = "payments/cash/admin/reconciliation_history.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            CashSession.objects.filter(status__in=["closed", "reconciled"])
            .select_related("collector", "approved_by")
            .order_by("-closing_time")
        )

        # Date filter
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(closing_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(closing_time__date__lte=date_to)

        # Agent filter
        agent_id = self.request.GET.get("agent")
        if agent_id:
            queryset = queryset.filter(collector_id=agent_id)

        # Status filter
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Discrepancy filter
        has_discrepancy = self.request.GET.get("has_discrepancy")
        if has_discrepancy == "yes":
            queryset = queryset.exclude(discrepancy_amount=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["selected_agent"] = self.request.GET.get("agent", "")
        context["selected_status"] = self.request.GET.get("status", "")
        context["has_discrepancy"] = self.request.GET.get("has_discrepancy", "")

        # Get agents for filter
        context["agents"] = AgentPartenaireProfile.objects.filter(is_active=True).order_by("full_name")

        # Calculate statistics
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_sessions=Count("id"),
            total_discrepancies=Sum("discrepancy_amount"),
            avg_discrepancy=Avg("discrepancy_amount"),
        )
        context["stats"] = stats

        return context

    def render_to_response(self, context, **response_kwargs):
        # Check if export is requested
        export_format = self.request.GET.get("export")

        if export_format == "csv":
            return self._export_csv()
        elif export_format == "pdf":
            return self._export_pdf()

        return super().render_to_response(context, **response_kwargs)

    def _export_csv(self):
        """Export reconciliation history to CSV"""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="reconciliation_history_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Session Number",
                "Agent",
                "Opening Time",
                "Closing Time",
                "Opening Balance",
                "Expected Balance",
                "Closing Balance",
                "Discrepancy",
                "Status",
                "Notes",
            ]
        )

        for session in self.get_queryset():
            writer.writerow(
                [
                    session.session_number,
                    session.collector.full_name,
                    session.opening_time.strftime("%Y-%m-%d %H:%M"),
                    session.closing_time.strftime("%Y-%m-%d %H:%M") if session.closing_time else "",
                    session.opening_balance,
                    session.expected_balance or "",
                    session.closing_balance or "",
                    session.discrepancy_amount,
                    session.status,
                    session.discrepancy_notes or "",
                ]
            )

        return response

    def _export_pdf(self):
        """Export reconciliation history to PDF"""
        # This would use ReportLab to generate PDF
        # For now, return a simple message
        messages.info(self.request, _("Export PDF en cours de développement."))
        return redirect("payments:admin_reconciliation_history")


# ============================================================================
# TASK 5.9: CASH COLLECTION REPORT VIEW
# ============================================================================


class CashCollectionReportView(LoginRequiredMixin, AdminStaffMixin, TemplateView):
    """
    Generate collection reports with filters and export
    Requirements: 11
    """

    template_name = "payments/cash/admin/collection_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

        context["date_from"] = start_date
        context["date_to"] = end_date

        # Get filters
        agent_id = self.request.GET.get("agent")
        vehicle_type_id = self.request.GET.get("vehicle_type")

        # Build query
        transactions = CashTransaction.objects.filter(
            is_voided=False, transaction_time__date__gte=start_date, transaction_time__date__lte=end_date
        ).select_related("collector", "payment", "payment__vehicule_plaque__type_vehicule")

        if agent_id:
            transactions = transactions.filter(collector_id=agent_id)

        if vehicle_type_id:
            transactions = transactions.filter(payment__vehicule_plaque__type_vehicule_id=vehicle_type_id)

        # Calculate summary statistics
        summary = transactions.aggregate(
            total_transactions=Count("id"),
            total_tax_collected=Sum("tax_amount"),
            total_cash_tendered=Sum("amount_tendered"),
            total_change_given=Sum("change_given"),
            total_commission=Sum("commission_amount"),
            avg_transaction_amount=Avg("tax_amount"),
        )
        context["summary"] = summary

        # Group by agent
        by_agent = (
            transactions.values("collector__agent_id", "collector__full_name")
            .annotate(
                transaction_count=Count("id"),
                total_collected=Sum("tax_amount"),
                total_commission=Sum("commission_amount"),
            )
            .order_by("-total_collected")
        )
        context["by_agent"] = by_agent

        # Group by vehicle type
        by_vehicle_type = (
            transactions.values("payment__vehicule_plaque__type_vehicule__nom")
            .annotate(
                transaction_count=Count("id"),
                total_collected=Sum("tax_amount"),
            )
            .order_by("-total_collected")
        )
        context["by_vehicle_type"] = by_vehicle_type

        # Group by date
        by_date = (
            transactions.extra(select={"date": "DATE(transaction_time)"})
            .values("date")
            .annotate(
                transaction_count=Count("id"),
                total_collected=Sum("tax_amount"),
            )
            .order_by("date")
        )
        context["by_date"] = by_date

        # Add filter options
        context["agents"] = AgentPartenaireProfile.objects.filter(is_active=True).order_by("full_name")
        context["vehicle_types"] = VehicleType.objects.filter(est_actif=True).order_by("nom")
        context["selected_agent"] = agent_id or ""
        context["selected_vehicle_type"] = vehicle_type_id or ""

        return context

    def render_to_response(self, context, **response_kwargs):
        # Check if export is requested
        export_format = self.request.GET.get("export")

        if export_format == "csv":
            return self._export_csv(context)
        elif export_format == "pdf":
            return self._export_pdf(context)

        return super().render_to_response(context, **response_kwargs)

    def _export_csv(self, context):
        """Export collection report to CSV"""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="collection_report_{timezone.now().date()}.csv"'

        writer = csv.writer(response)

        # Summary section
        writer.writerow(["Collection Report"])
        writer.writerow(["Period", f"{context['date_from']} to {context['date_to']}"])
        writer.writerow([])

        # Summary statistics
        writer.writerow(["Summary Statistics"])
        summary = context["summary"]
        writer.writerow(["Total Transactions", summary["total_transactions"]])
        writer.writerow(["Total Tax Collected", summary["total_tax_collected"]])
        writer.writerow(["Total Cash Tendered", summary["total_cash_tendered"]])
        writer.writerow(["Total Change Given", summary["total_change_given"]])
        writer.writerow(["Total Commission", summary["total_commission"]])
        writer.writerow(["Average Transaction", summary["avg_transaction_amount"]])
        writer.writerow([])

        # By agent
        writer.writerow(["By Agent"])
        writer.writerow(["Agent ID", "Agent Name", "Transactions", "Total Collected", "Commission"])
        for row in context["by_agent"]:
            writer.writerow(
                [
                    row["collector__agent_id"],
                    row["collector__full_name"],
                    row["transaction_count"],
                    row["total_collected"],
                    row["total_commission"],
                ]
            )

        return response

    def _export_pdf(self, context):
        """Export collection report to PDF"""
        messages.info(self.request, _("Export PDF en cours de développement."))
        return redirect("payments:admin_collection_report")


# ============================================================================
# TASK 5.10: DISCREPANCY REPORT VIEW
# ============================================================================


class DiscrepancyReportView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    Show all discrepancies with filters
    Requirements: 11
    """

    model = CashSession
    template_name = "payments/cash/admin/discrepancy_report.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        # Only sessions with discrepancies
        queryset = (
            CashSession.objects.exclude(discrepancy_amount=0)
            .select_related("collector", "approved_by")
            .order_by("-closing_time")
        )

        # Date filter
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(closing_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(closing_time__date__lte=date_to)

        # Agent filter
        agent_id = self.request.GET.get("agent")
        if agent_id:
            queryset = queryset.filter(collector_id=agent_id)

        # Resolution status filter
        resolution_status = self.request.GET.get("resolution_status")
        if resolution_status == "resolved":
            queryset = queryset.filter(status="reconciled")
        elif resolution_status == "pending":
            queryset = queryset.filter(status="closed")

        # Discrepancy amount filter
        min_discrepancy = self.request.GET.get("min_discrepancy")
        if min_discrepancy:
            queryset = queryset.filter(
                Q(discrepancy_amount__gte=Decimal(min_discrepancy))
                | Q(discrepancy_amount__lte=-Decimal(min_discrepancy))
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["selected_agent"] = self.request.GET.get("agent", "")
        context["resolution_status"] = self.request.GET.get("resolution_status", "")
        context["min_discrepancy"] = self.request.GET.get("min_discrepancy", "")

        # Get agents for filter
        context["agents"] = AgentPartenaireProfile.objects.filter(is_active=True).order_by("full_name")

        # Calculate statistics
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_discrepancies=Count("id"),
            total_amount=Sum("discrepancy_amount"),
            avg_discrepancy=Avg("discrepancy_amount"),
            max_discrepancy=models.Max("discrepancy_amount"),
            min_discrepancy=models.Min("discrepancy_amount"),
        )
        context["stats"] = stats

        # Get config for tolerance
        config = CashSystemConfig.get_config()
        context["reconciliation_tolerance"] = config.reconciliation_tolerance

        # Count by resolution status
        context["resolved_count"] = (
            CashSession.objects.exclude(discrepancy_amount=0).filter(status="reconciled").count()
        )

        context["pending_count"] = CashSession.objects.exclude(discrepancy_amount=0).filter(status="closed").count()

        return context


# ============================================================================
# TASK 5.11: COMMISSION REPORT VIEW
# ============================================================================


class CommissionReportView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    Show commission by agent with filters and export
    Requirements: 6, 11
    """

    model = CommissionRecord
    template_name = "payments/cash/admin/commission_report.html"
    context_object_name = "commission_records"
    paginate_by = 20

    def get_queryset(self):
        queryset = CommissionRecord.objects.select_related("collector", "session", "transaction").order_by(
            "-created_at"
        )

        # Date filter
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # Agent filter
        agent_id = self.request.GET.get("agent")
        if agent_id:
            queryset = queryset.filter(collector_id=agent_id)

        # Payment status filter
        payment_status = self.request.GET.get("payment_status")
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["selected_agent"] = self.request.GET.get("agent", "")
        context["payment_status"] = self.request.GET.get("payment_status", "")

        # Get agents for filter
        context["agents"] = AgentPartenaireProfile.objects.filter(is_active=True).order_by("full_name")

        # Calculate statistics
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_records=Count("id"),
            total_commission=Sum("commission_amount"),
            total_tax_amount=Sum("tax_amount"),
            avg_commission=Avg("commission_amount"),
        )
        context["stats"] = stats

        # Group by agent
        by_agent = (
            queryset.values("collector__agent_id", "collector__full_name")
            .annotate(
                total_commission=Sum("commission_amount"),
                transaction_count=Count("id"),
                pending_commission=Sum("commission_amount", filter=Q(payment_status="pending")),
                paid_commission=Sum("commission_amount", filter=Q(payment_status="paid")),
            )
            .order_by("-total_commission")
        )
        context["by_agent"] = by_agent

        # Count by payment status
        context["pending_count"] = queryset.filter(payment_status="pending").count()
        context["paid_count"] = queryset.filter(payment_status="paid").count()
        context["cancelled_count"] = queryset.filter(payment_status="cancelled").count()

        return context

    def render_to_response(self, context, **response_kwargs):
        # Check if export is requested
        export_format = self.request.GET.get("export")

        if export_format == "csv":
            return self._export_csv(context)
        elif export_format == "pdf":
            return self._export_pdf(context)

        return super().render_to_response(context, **response_kwargs)

    def _export_csv(self, context):
        """Export commission report to CSV"""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="commission_report_{timezone.now().date()}.csv"'

        writer = csv.writer(response)

        # Header
        writer.writerow(["Commission Report"])
        writer.writerow(["Period", f"{context['date_from']} to {context['date_to']}"])
        writer.writerow([])

        # Summary
        writer.writerow(["Summary"])
        stats = context["stats"]
        writer.writerow(["Total Records", stats["total_records"]])
        writer.writerow(["Total Commission", stats["total_commission"]])
        writer.writerow(["Total Tax Amount", stats["total_tax_amount"]])
        writer.writerow(["Average Commission", stats["avg_commission"]])
        writer.writerow([])

        # By agent
        writer.writerow(["By Agent"])
        writer.writerow(["Agent ID", "Agent Name", "Transactions", "Total Commission", "Pending", "Paid"])
        for row in context["by_agent"]:
            writer.writerow(
                [
                    row["collector__agent_id"],
                    row["collector__full_name"],
                    row["transaction_count"],
                    row["total_commission"],
                    row["pending_commission"] or 0,
                    row["paid_commission"] or 0,
                ]
            )

        return response

    def _export_pdf(self, context):
        """Export commission report to PDF"""
        messages.info(self.request, _("Export PDF en cours de développement."))
        return redirect("payments:admin_commission_report")


# ============================================================================
# TASK 5.12: AUDIT TRAIL VIEW
# ============================================================================


class AuditTrailView(LoginRequiredMixin, AdminStaffMixin, ListView):
    """
    Display audit log entries with filters and hash chain verification
    Requirements: 9, 12
    """

    model = CashAuditLog
    template_name = "payments/cash/admin/audit_trail.html"
    context_object_name = "audit_logs"
    paginate_by = 50

    def get_queryset(self):
        queryset = CashAuditLog.objects.select_related("user", "session", "transaction").order_by("-timestamp")

        # Action type filter
        action_type = self.request.GET.get("action_type")
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        # User filter
        user_id = self.request.GET.get("user")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Date filter
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values
        context["action_type"] = self.request.GET.get("action_type", "")
        context["selected_user"] = self.request.GET.get("user", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")

        # Get action types for filter
        context["action_types"] = (
            CashAuditLog.objects.values_list("action_type", flat=True).distinct().order_by("action_type")
        )

        # Get users for filter
        context["users"] = User.objects.filter(
            id__in=CashAuditLog.objects.values_list("user_id", flat=True).distinct()
        ).order_by("username")

        # Verify hash chain integrity
        is_valid, tampered_entries = CashAuditService.verify_audit_trail()
        context["hash_chain_valid"] = is_valid
        context["tampered_entries"] = tampered_entries

        # Statistics
        context["total_logs"] = CashAuditLog.objects.count()
        context["logs_today"] = CashAuditLog.objects.filter(timestamp__date=timezone.now().date()).count()

        return context

    def render_to_response(self, context, **response_kwargs):
        # Check if export is requested
        export_format = self.request.GET.get("export")

        if export_format == "csv":
            return self._export_csv()

        return super().render_to_response(context, **response_kwargs)

    def _export_csv(self):
        """Export audit trail to CSV"""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="audit_trail_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Timestamp", "Action Type", "User", "Session", "Transaction", "IP Address", "Hash Valid"])

        for log in self.get_queryset():
            writer.writerow(
                [
                    log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    log.action_type,
                    log.user.username if log.user else "",
                    log.session.session_number if log.session else "",
                    log.transaction.transaction_number if log.transaction else "",
                    log.ip_address or "",
                    "Yes" if log.current_hash else "No",
                ]
            )

        return response


# ============================================================================
# TASK 5.13: CASH SYSTEM CONFIG VIEW
# ============================================================================


class CashSystemConfigView(LoginRequiredMixin, AdminStaffMixin, UpdateView):
    """
    Edit system configuration
    Requirements: 6, 8, 10, 14
    """

    model = CashSystemConfig
    form_class = CashSystemConfigForm
    template_name = "payments/cash/admin/system_config.html"
    success_url = reverse_lazy("payments:admin_system_config")

    def get_object(self, queryset=None):
        # Get or create singleton config
        return CashSystemConfig.get_config()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Configuration du système de paiement en espèces")

        # Get usage statistics
        context["total_agents"] = AgentPartenaireProfile.objects.filter(is_active=True).count()
        context["open_sessions"] = CashSession.objects.filter(status="open").count()
        context["total_transactions"] = CashTransaction.objects.filter(is_voided=False).count()

        return context

    def form_valid(self, form):
        # Track changes for audit log
        changes = {}
        for field in form.changed_data:
            old_value = getattr(self.object, field)
            new_value = form.cleaned_data[field]
            changes[field] = {"old": str(old_value), "new": str(new_value)}

        response = super().form_valid(form)

        messages.success(self.request, _("Configuration mise à jour avec succès."))

        # Log configuration changes
        if changes:
            CashAuditService.log_action(
                action_type="config_updated", user=self.request.user, data={"changes": changes}, request=self.request
            )

        return response
