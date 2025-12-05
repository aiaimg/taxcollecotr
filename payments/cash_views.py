"""
Cash Payment Views for Agent Partenaire
Handles cash payment processing, session management, and receipt generation
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from core.models import User, UserProfile
from vehicles.models import VehicleType, Vehicule
from vehicles.services import TaxCalculationService

from .forms import (
    CashPaymentForm,
    CashSessionCloseForm,
    CashSessionOpenForm,
)
from .models import (
    AgentPartenaireProfile,
    CashReceipt,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    CommissionRecord,
    PaiementTaxe,
)
from .services.cash_payment_service import CashPaymentService
from .services.cash_receipt_service import CashReceiptService
from .services.cash_session_service import CashSessionService
from .services.commission_service import CommissionService

# ============================================================================
# MIXINS FOR PERMISSION CHECKING
# ============================================================================


class AgentPartenaireMixin(UserPassesTestMixin):
    """
    Mixin to ensure user is an Agent Partenaire with proper permissions
    Checks:
    1. User has an active AgentPartenaireProfile
    2. User is in "Agent Partenaire" group OR is staff/superuser
    """

    def test_func(self):
        user = self.request.user

        # Check if user has agent partenaire profile and is active
        has_profile = hasattr(user, "agent_partenaire_profile") and user.agent_partenaire_profile.is_active

        # Check if user is in Agent Partenaire group or is staff/superuser
        is_in_group = user.groups.filter(name="Agent Partenaire").exists()
        is_admin = user.is_staff or user.is_superuser

        return has_profile and (is_in_group or is_admin)

    def handle_no_permission(self):
        messages.error(self.request, _("Vous devez être un Agent Partenaire actif pour accéder à cette page."))
        return redirect("core:dashboard")

    def get_agent_profile(self):
        """Get the agent partenaire profile for the current user"""
        return self.request.user.agent_partenaire_profile


# ============================================================================
# TASK 4.1: CASH SESSION OPEN VIEW
# ============================================================================


class CashSessionOpenView(LoginRequiredMixin, AgentPartenaireMixin, CreateView):
    """
    Open a new cash collection session
    Requirements: 7
    """

    model = CashSession
    form_class = CashSessionOpenForm
    template_name = "payments/cash/session_open.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.get_agent_profile()

        # Check for existing open session
        active_session = CashSessionService.get_active_session(agent)
        context["has_active_session"] = active_session is not None
        context["active_session"] = active_session
        context["agent"] = agent

        return context

    def form_valid(self, form):
        agent = self.get_agent_profile()
        opening_balance = form.cleaned_data["opening_balance"]

        # Open session using service
        session, error = CashSessionService.open_session(
            collector=agent, opening_balance=opening_balance, request=self.request
        )

        if error:
            messages.error(self.request, error)
            return self.form_invalid(form)

        messages.success(
            self.request,
            _(f"Session {session.session_number} ouverte avec succès. Solde d'ouverture: {opening_balance} Ar"),
        )
        return redirect("payments:cash_session_detail", pk=session.pk)


# ============================================================================
# TASK 4.2: CASH SESSION CLOSE VIEW
# ============================================================================


class CashSessionCloseView(LoginRequiredMixin, AgentPartenaireMixin, UpdateView):
    """
    Close a cash collection session
    Requirements: 7
    """

    model = CashSession
    form_class = CashSessionCloseForm
    template_name = "payments/cash/session_close.html"

    def get_queryset(self):
        agent = self.get_agent_profile()
        return CashSession.objects.filter(collector=agent, status="open")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()

        # Calculate session totals
        totals = CashSessionService.calculate_session_totals(session)
        context.update(totals)
        context["session"] = session
        context["agent"] = self.get_agent_profile()

        # Get config for tolerance display
        config = CashSystemConfig.get_config()
        context["reconciliation_tolerance"] = config.reconciliation_tolerance

        return context

    def form_valid(self, form):
        session = self.get_object()
        closing_balance = form.cleaned_data["closing_balance"]
        discrepancy_notes = form.cleaned_data.get("discrepancy_notes", "")

        # Close session using service
        closed_session, discrepancy = CashSessionService.close_session(
            session=session,
            closing_balance=closing_balance,
            counted_by=self.request.user,
            discrepancy_notes=discrepancy_notes,
            request=self.request,
        )

        if not closed_session:
            messages.error(self.request, _("Erreur lors de la fermeture de la session."))
            return self.form_invalid(form)

        # Check if requires admin approval
        config = CashSystemConfig.get_config()
        if abs(discrepancy) > config.reconciliation_tolerance:
            messages.warning(
                self.request,
                _(f"Session fermée avec un écart de {discrepancy} Ar. " f"Approbation administrative requise."),
            )
        else:
            messages.success(self.request, _(f"Session fermée avec succès. Écart: {discrepancy} Ar"))

        return redirect("payments:cash_session_detail", pk=closed_session.pk)


# ============================================================================
# TASK 4.3: CASH SESSION DETAIL VIEW
# ============================================================================


class CashSessionDetailView(LoginRequiredMixin, AgentPartenaireMixin, DetailView):
    """
    Display session information with transactions and commission
    Requirements: 6, 7
    """

    model = CashSession
    template_name = "payments/cash/session_detail.html"
    context_object_name = "session"

    def get_queryset(self):
        agent = self.get_agent_profile()
        return CashSession.objects.filter(collector=agent)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()

        # Get session summary
        summary = CashSessionService.get_session_summary(session)
        context.update(summary)

        # Get all transactions (non-voided)
        transactions = session.transactions.filter(is_voided=False).order_by("-transaction_time")
        context["transactions"] = transactions

        # Get pending approvals
        pending_approvals = transactions.filter(requires_approval=True, approved_by__isnull=True)
        context["pending_approvals"] = pending_approvals

        context["agent"] = self.get_agent_profile()

        return context


# ============================================================================
# TASK 4.4: CASH PAYMENT CREATE VIEW
# ============================================================================


class CashPaymentCreateView(LoginRequiredMixin, AgentPartenaireMixin, CreateView):
    """
    Create cash payment for new or existing customers
    Requirements: 1, 2, 3, 4, 5, 6, 8
    """

    model = CashTransaction
    form_class = CashPaymentForm
    template_name = "payments/cash/payment_create.html"

    def get_form(self, form_class=None):
        """Override to not pass instance since CashPaymentForm is a regular Form, not ModelForm"""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Get form kwargs without instance since we're using a regular Form"""
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.get_agent_profile()

        # Check for active session
        active_session = CashSessionService.get_active_session(agent)
        context["active_session"] = active_session
        context["agent"] = agent

        # Get vehicle types for dropdown
        context["vehicle_types"] = VehicleType.objects.filter(est_actif=True)

        # Get current year
        context["current_year"] = timezone.now().year

        # Get config for dual verification threshold
        config = CashSystemConfig.get_config()
        context["dual_verification_threshold"] = config.dual_verification_threshold

        return context

    def form_valid(self, form):
        agent = self.get_agent_profile()

        # Check for active session
        active_session = CashSessionService.get_active_session(agent)
        if not active_session:
            messages.error(self.request, _("Vous devez ouvrir une session avant de traiter des paiements."))
            return redirect("payments:cash_session_open")

        # Get form data
        is_new_customer = form.cleaned_data.get("is_new_customer", False)
        amount_tendered = form.cleaned_data["amount_tendered"]

        # Process payment based on customer type
        if is_new_customer:
            # Create new customer and vehicle
            transaction_obj, error = self._process_new_customer_payment(form, agent)
        else:
            # Process existing customer payment
            vehicle_plate = form.cleaned_data.get("vehicle_plate")
            transaction_obj, error = CashPaymentService.process_existing_customer_payment(
                collector=agent, vehicle_plate=vehicle_plate, amount_tendered=amount_tendered, request=self.request
            )

        if error:
            messages.error(self.request, error)
            return self.form_invalid(form)

        # Generate receipt
        receipt, receipt_error = CashReceiptService.generate_cash_receipt(
            cash_transaction=transaction_obj, request=self.request
        )

        if receipt_error:
            messages.warning(self.request, _(f"Paiement enregistré mais erreur de génération du reçu: {receipt_error}"))

        # Check if requires approval
        if transaction_obj.requires_approval:
            messages.warning(
                self.request, _(f"Paiement enregistré. Montant élevé - approbation administrative requise.")
            )
        else:
            messages.success(
                self.request, _(f"Paiement enregistré avec succès. Transaction: {transaction_obj.transaction_number}")
            )

        return redirect("payments:cash_payment_success", pk=transaction_obj.pk)

    def _process_new_customer_payment(self, form, agent):
        """Process payment for new customer with vehicle registration"""
        # Extract customer data
        customer_data = {
            "name": form.cleaned_data["customer_name"],
            "phone": form.cleaned_data.get("customer_phone", ""),
            "email": form.cleaned_data.get("customer_email", ""),
            "id_number": form.cleaned_data.get("customer_id_number", ""),
            "owner_name": form.cleaned_data["owner_name"],
        }

        # Create or get user account
        user = self._get_or_create_user(customer_data)

        # Create vehicle
        vehicle = self._create_vehicle(form, user)

        if not vehicle:
            return None, "Erreur lors de la création du véhicule."

        # Process payment
        return CashPaymentService.create_cash_payment(
            collector=agent,
            vehicle=vehicle,
            customer_data=customer_data,
            amount_tendered=form.cleaned_data["amount_tendered"],
            request=self.request,
        )

    def _get_or_create_user(self, customer_data):
        """Get or create user account for customer"""
        # Try to find existing user by email or phone
        email = customer_data.get("email")
        phone = customer_data.get("phone")

        user = None
        if email:
            user = User.objects.filter(email=email).first()

        if not user and phone:
            user = UserProfile.objects.filter(phone_number=phone).first()
            if user:
                user = user.user

        # Create new user if not found
        if not user:
            username = f"customer_{timezone.now().timestamp()}"
            user = User.objects.create_user(
                username=username,
                email=email or "",
                first_name=customer_data.get("name", "").split()[0] if customer_data.get("name") else "",
                last_name=" ".join(customer_data.get("name", "").split()[1:]) if customer_data.get("name") else "",
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=phone or "",
            )

        return user

    def _create_vehicle(self, form, user):
        """Create vehicle from form data"""
        try:
            vehicle_data = {
                "proprietaire": user,
                "plaque_immatriculation": (
                    form.cleaned_data.get("vehicle_plate") if form.cleaned_data.get("has_plate") else None
                ),
                "numero_identification_temporaire": (
                    None if form.cleaned_data.get("has_plate") else f"TEMP-{timezone.now().timestamp()}"
                ),
                "type_vehicule": form.cleaned_data["vehicle_type"],
                "marque": form.cleaned_data.get("vehicle_brand", ""),
                "modele": form.cleaned_data.get("vehicle_model", ""),
                "couleur": form.cleaned_data.get("vehicle_color", ""),
                "puissance_fiscale_cv": form.cleaned_data["engine_power_cv"],
                "cylindree_cm3": form.cleaned_data.get("engine_capacity_cc"),
                "source_energie": form.cleaned_data["energy_source"],
                "date_premiere_circulation": form.cleaned_data["first_circulation_date"],
                "categorie_vehicule": form.cleaned_data["vehicle_category"],
                "nom_proprietaire": form.cleaned_data["owner_name"],
            }

            vehicle = Vehicule.objects.create(**vehicle_data)
            return vehicle

        except Exception as e:
            return None


# ============================================================================
# TASK 4.5: CASH PAYMENT SEARCH CUSTOMER VIEW (AJAX)
# ============================================================================


class CashPaymentSearchCustomerView(LoginRequiredMixin, AgentPartenaireMixin, View):
    """
    Search for customers by name, phone, or vehicle plate (AJAX)
    Requirements: 2
    """

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse({"results": []})

        # Search in multiple fields
        vehicles = (
            Vehicule.objects.filter(
                Q(plaque_immatriculation__icontains=query)
                | Q(nom_proprietaire__icontains=query)
                | Q(proprietaire__first_name__icontains=query)
                | Q(proprietaire__last_name__icontains=query)
                | Q(proprietaire__email__icontains=query)
                | Q(proprietaire__profile__phone_number__icontains=query)
            )
            .select_related("proprietaire", "type_vehicule")
            .distinct()[:10]
        )

        results = []
        for vehicle in vehicles:
            owner = vehicle.proprietaire
            results.append(
                {
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plaque_immatriculation or vehicle.numero_identification_temporaire,
                    "vehicle_type": vehicle.type_vehicule.nom if vehicle.type_vehicule else "",
                    "vehicle_brand": vehicle.marque or "",
                    "vehicle_model": vehicle.modele or "",
                    "owner_name": vehicle.nom_proprietaire or owner.get_full_name() or owner.username,
                    "owner_email": owner.email,
                    "owner_phone": owner.profile.phone_number if hasattr(owner, "profile") else "",
                    "engine_power_cv": vehicle.puissance_fiscale_cv,
                    "engine_capacity_cc": vehicle.cylindree_cm3,
                }
            )

        return JsonResponse({"results": results})


# ============================================================================
# TASK 4.6: CASH PAYMENT CALCULATE TAX VIEW (AJAX)
# ============================================================================


class CashPaymentCalculateTaxView(LoginRequiredMixin, AgentPartenaireMixin, View):
    """
    Calculate tax for vehicle (AJAX)
    Requirements: 1, 2, 3, 4
    """

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Get vehicle or create temporary vehicle object for calculation
            vehicle_id = data.get("vehicle_id")

            if vehicle_id:
                # Existing vehicle
                vehicle = get_object_or_404(Vehicule, id=vehicle_id)
            else:
                # Create temporary vehicle object for calculation
                vehicle_type_id = data.get("vehicle_type_id")
                vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)

                vehicle = Vehicule(
                    type_vehicule=vehicle_type,
                    puissance_fiscale_cv=data.get("engine_power_cv", 0),
                    cylindree_cm3=data.get("engine_capacity_cc"),
                    source_energie=data.get("energy_source", "essence"),
                    categorie_vehicule=data.get("vehicle_category", "particulier"),
                    date_premiere_circulation=(
                        datetime.strptime(data.get("first_circulation_date"), "%Y-%m-%d").date()
                        if data.get("first_circulation_date")
                        else timezone.now().date()
                    ),
                )

            # Calculate tax
            tax_year = data.get("tax_year", timezone.now().year)
            tax_service = TaxCalculationService()
            tax_info = tax_service.calculate_tax(vehicle, tax_year)

            if tax_info.get("error"):
                return JsonResponse({"success": False, "error": tax_info["error"]})

            return JsonResponse(
                {
                    "success": True,
                    "tax_amount": str(tax_info.get("amount", 0)),
                    "is_exempt": tax_info.get("is_exempt", False),
                    "tax_details": tax_info.get("details", {}),
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


# ============================================================================
# TASK 4.7: RECEIPT PRINT VIEW
# ============================================================================


class ReceiptPrintView(LoginRequiredMixin, AgentPartenaireMixin, DetailView):
    """
    Generate and display receipt
    Requirements: 5
    """

    model = CashReceipt
    template_name = "payments/cash/receipt_preview.html"
    context_object_name = "receipt"

    def get_queryset(self):
        agent = self.get_agent_profile()
        return CashReceipt.objects.filter(transaction__collector=agent)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receipt = self.get_object()

        # Mark as printed if not already
        if not receipt.transaction.receipt_printed:
            receipt.transaction.receipt_printed = True
            receipt.transaction.receipt_print_time = timezone.now()
            receipt.transaction.save(update_fields=["receipt_printed", "receipt_print_time"])

        context["agent"] = self.get_agent_profile()
        context["transaction"] = receipt.transaction

        return context


# ============================================================================
# TASK 4.8: RECEIPT REPRINT VIEW
# ============================================================================


class ReceiptReprintView(LoginRequiredMixin, AgentPartenaireMixin, View):
    """
    Reprint existing receipt (marked as duplicate)
    Requirements: 5
    """

    def post(self, request, pk):
        agent = self.get_agent_profile()

        # Get original receipt
        original_receipt = get_object_or_404(CashReceipt, pk=pk, transaction__collector=agent)

        # Reprint using service
        duplicate_receipt, error = CashReceiptService.reprint_receipt(
            original_receipt=original_receipt, requested_by=request.user, request=request
        )

        if error:
            messages.error(request, error)
            return redirect("payments:cash_session_detail", pk=original_receipt.transaction.session.pk)

        messages.success(request, _(f"Reçu réimprimé: {duplicate_receipt.receipt_number} (DUPLICATA)"))
        return redirect("payments:cash_receipt_print", pk=duplicate_receipt.pk)


# ============================================================================
# TASK 4.9: RECEIPT DOWNLOAD VIEW
# ============================================================================


class ReceiptDownloadView(LoginRequiredMixin, AgentPartenaireMixin, View):
    """
    Generate PDF receipt and return as download
    Requirements: 5
    """

    def get(self, request, pk):
        agent = self.get_agent_profile()

        # Get receipt
        receipt = get_object_or_404(CashReceipt, pk=pk, transaction__collector=agent)

        # Generate PDF
        pdf_buffer = CashReceiptService.generate_cash_receipt_pdf(receipt)

        # Return as download
        response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
        filename = f"recu_{receipt.receipt_number}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


# ============================================================================
# TASK 4.10: COLLECTOR COMMISSION VIEW
# ============================================================================


class CollectorCommissionView(LoginRequiredMixin, AgentPartenaireMixin, ListView):
    """
    Display commission history with filters
    Requirements: 6
    """

    model = CommissionRecord
    template_name = "payments/cash/commission_list.html"
    context_object_name = "commissions"
    paginate_by = 20

    def get_queryset(self):
        agent = self.get_agent_profile()

        queryset = (
            CommissionRecord.objects.filter(collector=agent)
            .select_related("session", "transaction", "transaction__payment")
            .order_by("-created_at")
        )

        # Apply date filters
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        status = self.request.GET.get("status")

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if status:
            queryset = queryset.filter(payment_status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.get_agent_profile()

        # Get all commission records (not just paginated)
        all_commissions = self.get_queryset()

        # Calculate totals from all commissions (before pagination)
        totals = all_commissions.aggregate(
            total_commission=Sum("commission_amount"),
            total_records=Count("id"),
            total_tax_collected=Sum("tax_amount"),
        )

        # Calculate commission sum for table footer
        context["total_commission_sum"] = totals.get("total_commission") or Decimal("0")
        context["total_commission"] = context["total_commission_sum"]  # For summary cards
        context["total_transactions"] = totals.get("total_records") or 0
        context["total_tax_collected"] = totals.get("total_tax_collected") or Decimal("0")

        # Calculate paid and pending commissions
        paid_commission = all_commissions.filter(payment_status="paid").aggregate(total=Sum("commission_amount"))[
            "total"
        ] or Decimal("0")
        pending_commission = all_commissions.filter(payment_status="pending").aggregate(total=Sum("commission_amount"))[
            "total"
        ] or Decimal("0")

        context["paid_commission"] = paid_commission
        context["pending_commission"] = pending_commission

        # Get agent profile for commission rate
        context["agent_profile"] = agent

        # Add filter values
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["status"] = self.request.GET.get("status", "")

        return context


# ============================================================================
# TASK 4.11: COLLECTOR DASHBOARD VIEW
# ============================================================================


class CollectorDashboardView(LoginRequiredMixin, AgentPartenaireMixin, TemplateView):
    """
    Display collector dashboard with active session, today's transactions, and commission
    Requirements: 3, 6, 7
    """

    template_name = "payments/cash/agent_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.get_agent_profile()

        # Get active session
        active_session = CashSessionService.get_active_session(agent)
        context["active_session"] = active_session

        if active_session:
            # Get session summary
            session_summary = CashSessionService.get_session_summary(active_session)
            context["session_summary"] = session_summary

            # Get today's transactions
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_transactions = active_session.transactions.filter(
                is_voided=False, transaction_time__gte=today_start
            ).order_by("-transaction_time")[:10]
            context["today_transactions"] = today_transactions

        # Get today's commission (all sessions)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_commission = CashTransaction.objects.filter(
            collector=agent, is_voided=False, transaction_time__gte=today_start
        ).aggregate(
            total_commission=Sum("commission_amount"),
            total_transactions=Count("id"),
        )
        context["today_commission"] = today_commission

        # Get recent sessions
        recent_sessions = CashSession.objects.filter(collector=agent).order_by("-opening_time")[:5]
        context["recent_sessions"] = recent_sessions

        context["agent"] = agent

        return context


# ============================================================================
# TASK 4.12: CASH TRANSACTION VOID VIEW
# ============================================================================


class CashTransactionVoidView(LoginRequiredMixin, AgentPartenaireMixin, View):
    """
    Void a transaction (requires admin approval)
    Requirements: 13
    """

    template_name = "payments/cash/transaction_void.html"

    def get(self, request, pk):
        agent = self.get_agent_profile()

        # Get transaction
        transaction_obj = get_object_or_404(CashTransaction, pk=pk, collector=agent)

        # Check if voidable
        config = CashSystemConfig.get_config()
        time_limit = timezone.timedelta(minutes=config.void_time_limit_minutes)
        is_within_time_limit = timezone.now() - transaction_obj.transaction_time <= time_limit
        is_same_session = transaction_obj.session.status == "open"
        is_voidable = is_within_time_limit and is_same_session and not transaction_obj.is_voided

        context = {
            "transaction": transaction_obj,
            "agent": agent,
            "is_voidable": is_voidable,
            "time_limit_minutes": config.void_time_limit_minutes,
            "is_within_time_limit": is_within_time_limit,
            "is_same_session": is_same_session,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        agent = self.get_agent_profile()

        # Get transaction
        transaction_obj = get_object_or_404(CashTransaction, pk=pk, collector=agent)

        reason = request.POST.get("reason", "")

        if not reason:
            messages.error(request, _("Veuillez fournir une raison pour l'annulation."))
            return redirect("payments:cash_transaction_void", pk=pk)

        # Void transaction using service
        # Note: This requires admin approval in the service
        success, error = CashPaymentService.void_transaction(
            transaction=transaction_obj,
            admin_user=request.user,  # Will need admin approval
            reason=reason,
            request=request,
        )

        if error:
            messages.error(request, error)
            return redirect("payments:cash_transaction_void", pk=pk)

        messages.success(request, _(f"Transaction {transaction_obj.transaction_number} annulée avec succès."))
        return redirect("payments:cash_session_detail", pk=transaction_obj.session.pk)


# ============================================================================
# PAYMENT SUCCESS VIEW
# ============================================================================


class CashPaymentSuccessView(LoginRequiredMixin, AgentPartenaireMixin, DetailView):
    """Display payment success page with receipt"""

    model = CashTransaction
    template_name = "payments/cash/payment_success.html"
    context_object_name = "transaction"

    def get_queryset(self):
        agent = self.get_agent_profile()
        return CashTransaction.objects.filter(collector=agent)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_obj = self.get_object()

        context["agent"] = self.get_agent_profile()
        context["receipt"] = transaction_obj.receipt if hasattr(transaction_obj, "receipt") else None
        context["session"] = transaction_obj.session

        return context
