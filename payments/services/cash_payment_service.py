"""
Cash Payment Service
Handles cash payment processing, change calculation, and dual verification
"""

from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from core.models import UserProfile
from payments.models import (
    AgentPartenaireProfile,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    PaiementTaxe,
)
from vehicles.models import Vehicule
from vehicles.services import TaxCalculationService

from .cash_audit_service import CashAuditService
from .commission_service import CommissionService


class CashPaymentService:
    """Service for processing cash payments"""

    @staticmethod
    def calculate_change(tax_amount: Decimal, amount_tendered: Decimal) -> Tuple[Decimal, bool, Optional[str]]:
        """
        Calculate change with validation

        Args:
            tax_amount: The tax amount due
            amount_tendered: The amount of cash provided by customer

        Returns:
            Tuple of (change_amount, is_valid, error_message)
        """
        try:
            tax_amount = Decimal(str(tax_amount))
            amount_tendered = Decimal(str(amount_tendered))

            if amount_tendered < tax_amount:
                return (
                    Decimal("0.00"),
                    False,
                    f"Montant insuffisant. Montant dû: {tax_amount} Ar, Montant remis: {amount_tendered} Ar",
                )

            change = amount_tendered - tax_amount
            return (change, True, None)

        except (ValueError, TypeError) as e:
            return (Decimal("0.00"), False, f"Erreur de calcul: {str(e)}")

    @staticmethod
    def requires_dual_verification(amount: Decimal) -> bool:
        """
        Check if amount requires admin approval

        Args:
            amount: The payment amount to check

        Returns:
            Boolean indicating if dual verification is required
        """
        config = CashSystemConfig.get_config()
        return amount >= config.dual_verification_threshold

    @staticmethod
    @transaction.atomic
    def create_cash_payment(
        collector: AgentPartenaireProfile,
        vehicle: Vehicule,
        customer_data: Dict[str, Any],
        amount_tendered: Decimal,
        tax_year: Optional[int] = None,
        request=None,
    ) -> Tuple[Optional[CashTransaction], Optional[str]]:
        """
        Create a new cash payment transaction for new or existing customers

        Args:
            collector: The agent partenaire collecting the payment
            vehicle: The vehicle for which tax is being paid
            customer_data: Dictionary containing customer information
            amount_tendered: The amount of cash tendered
            tax_year: The tax year (defaults to current year)
            request: HTTP request object for audit logging

        Returns:
            Tuple of (CashTransaction, error_message)
        """
        try:
            # 1. Validate collector session is open
            active_session = CashSession.objects.filter(collector=collector, status="open").first()

            if not active_session:
                return None, "Aucune session active. Veuillez ouvrir une session avant de traiter les paiements."

            # 2. Calculate tax amount
            if tax_year is None:
                tax_year = timezone.now().year

            tax_service = TaxCalculationService()
            tax_info = tax_service.calculate_tax(vehicle, tax_year)

            if tax_info.get("error"):
                return None, tax_info["error"]

            if tax_info.get("is_exempt"):
                return None, "Ce véhicule est exonéré de taxe."

            tax_amount = tax_info.get("amount")
            if not tax_amount:
                return None, "Impossible de calculer le montant de la taxe."

            # 3. Validate tendered amount
            change, is_valid, error_msg = CashPaymentService.calculate_change(tax_amount, amount_tendered)
            if not is_valid:
                return None, error_msg

            # 4. Check if payment already exists for this year (exclude ANNULE)
            existing_payment = (
                PaiementTaxe.objects.filter(vehicule_plaque=vehicle, annee_fiscale=tax_year)
                .exclude(statut="ANNULE")
                .first()
            )

            if existing_payment:
                if existing_payment.statut == "PAYE":
                    return None, f"Un paiement a déjà été effectué pour ce véhicule pour l'année {tax_year}."
                elif existing_payment.statut == "EN_ATTENTE":
                    if existing_payment.methode_paiement == "cash":
                        return (
                            None,
                            f"Un paiement en espèces est déjà en attente d'approbation pour ce véhicule pour l'année {tax_year}.",
                        )
                    else:
                        return None, f"Un paiement est déjà en cours pour ce véhicule pour l'année {tax_year}."
                else:
                    return None, f"Un paiement existe déjà pour ce véhicule pour l'année {tax_year}."

            # 5. Check for dual verification requirement
            requires_approval = CashPaymentService.requires_dual_verification(tax_amount)

            # 6. Create PaiementTaxe record
            payment = PaiementTaxe.objects.create(
                vehicule_plaque=vehicle,
                annee_fiscale=tax_year,
                montant_du_ariary=tax_amount,
                montant_paye_ariary=tax_amount,
                date_paiement=timezone.now() if not requires_approval else None,
                statut="EN_ATTENTE" if requires_approval else "PAYE",
                methode_paiement="cash",
                collected_by=collector,
                details_paiement={
                    "amount_tendered": str(amount_tendered),
                    "change_given": str(change),
                    "collector_id": collector.agent_id,
                    "collector_name": collector.full_name,
                    "session_id": str(active_session.id),
                    "requires_approval": requires_approval,
                },
            )

            # 7. Create CashTransaction record
            cash_transaction = CashTransaction.objects.create(
                session=active_session,
                payment=payment,
                customer_name=customer_data.get("owner_name", vehicle.nom_proprietaire or ""),
                vehicle_plate=vehicle.plaque_immatriculation or vehicle.numero_identification_temporaire or "",
                tax_amount=tax_amount,
                amount_tendered=amount_tendered,
                change_given=change,
                commission_amount=Decimal("0.00"),  # Will be calculated next
                collector=collector,
                requires_approval=requires_approval,
            )

            # 8. Calculate and record commission
            commission_service = CommissionService()
            commission_amount = commission_service.calculate_commission(tax_amount, collector.get_commission_rate())
            cash_transaction.commission_amount = commission_amount
            cash_transaction.save(update_fields=["commission_amount"])

            commission_service.record_commission(
                transaction=cash_transaction, collector=collector, session=active_session
            )

            # 9. Update session totals
            active_session.total_commission += commission_amount
            active_session.save(update_fields=["total_commission"])

            # 10. If payment is automatically approved (no approval required), handle payment success
            if not requires_approval:
                # Use unified payment success service (same workflow as MVola and Stripe)
                from .payment_success_service import PaymentSuccessService

                qr_code, error = PaymentSuccessService.handle_payment_success(payment=payment, send_notification=True)

                if error:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.error(f"Error in payment success handler: {error}")
                elif qr_code:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.info(f"Cash payment success handled: payment_id={payment.id}, qr_code_token={qr_code.token}")

            # 11. Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="transaction_create",
                user=collector.user,
                session=active_session,
                transaction=cash_transaction,
                data={
                    "vehicle_plate": cash_transaction.vehicle_plate,
                    "tax_amount": str(tax_amount),
                    "amount_tendered": str(amount_tendered),
                    "change_given": str(change),
                    "requires_approval": requires_approval,
                },
                request=request,
            )

            return cash_transaction, None

        except Exception as e:
            return None, f"Erreur lors de la création du paiement: {str(e)}"

    @staticmethod
    @transaction.atomic
    def process_existing_customer_payment(
        collector: AgentPartenaireProfile,
        vehicle_plate: str,
        amount_tendered: Decimal,
        tax_year: Optional[int] = None,
        request=None,
    ) -> Tuple[Optional[CashTransaction], Optional[str]]:
        """
        Process payment for existing customer

        Args:
            collector: The agent partenaire collecting the payment
            vehicle_plate: The vehicle plate number
            amount_tendered: The amount of cash tendered
            tax_year: The tax year (defaults to current year)
            request: HTTP request object for audit logging

        Returns:
            Tuple of (CashTransaction, error_message)
        """
        try:
            # Find the vehicle
            vehicle = Vehicule.objects.filter(plaque_immatriculation=vehicle_plate).first()

            if not vehicle:
                return None, f"Véhicule avec plaque {vehicle_plate} introuvable."

            # Get customer data from vehicle
            customer_data = {
                "owner_name": vehicle.nom_proprietaire or "",
            }

            # Use the main create_cash_payment method
            return CashPaymentService.create_cash_payment(
                collector=collector,
                vehicle=vehicle,
                customer_data=customer_data,
                amount_tendered=amount_tendered,
                tax_year=tax_year,
                request=request,
            )

        except Exception as e:
            return None, f"Erreur lors du traitement du paiement: {str(e)}"

    @staticmethod
    @transaction.atomic
    def approve_transaction(
        transaction: CashTransaction, admin_user: User, notes: str = "", request=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Approve a transaction requiring dual verification

        Args:
            transaction: The cash transaction to approve
            admin_user: The admin user approving the transaction
            notes: Optional approval notes
            request: HTTP request object for audit logging

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not transaction.requires_approval:
                return False, "Cette transaction ne nécessite pas d'approbation."

            if transaction.approved_by:
                return False, "Cette transaction a déjà été approuvée."

            # Update transaction
            transaction.approved_by = admin_user
            transaction.approval_time = timezone.now()
            if notes:
                transaction.notes = notes
            transaction.save(update_fields=["approved_by", "approval_time", "notes"])

            # Update payment status
            payment = transaction.payment
            payment.statut = "PAYE"
            payment.date_paiement = timezone.now()
            payment.save(update_fields=["statut", "date_paiement"])

            # Use unified payment success service (same workflow as MVola and Stripe)
            from .payment_success_service import PaymentSuccessService

            qr_code, error = PaymentSuccessService.handle_payment_success(payment=payment, send_notification=True)

            if error:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error in payment success handler during approval: {error}")
            elif qr_code:
                import logging

                logger = logging.getLogger(__name__)
                logger.info(
                    f"Cash payment approved and success handled: payment_id={payment.id}, qr_code_token={qr_code.token}"
                )

            # Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="transaction_approve",
                user=admin_user,
                session=transaction.session,
                transaction=transaction,
                data={
                    "transaction_number": transaction.transaction_number,
                    "tax_amount": str(transaction.tax_amount),
                    "notes": notes,
                },
                request=request,
            )

            return True, None

        except Exception as e:
            return False, f"Erreur lors de l'approbation: {str(e)}"

    @staticmethod
    @transaction.atomic
    def void_transaction(
        transaction: CashTransaction, admin_user: User, reason: str, request=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Void a transaction (must be in current open session and within time limit)

        Args:
            transaction: The cash transaction to void
            admin_user: The admin user voiding the transaction
            reason: Reason for voiding
            request: HTTP request object for audit logging

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if transaction.is_voided:
                return False, "Cette transaction a déjà été annulée."

            # Check if session is still open
            if transaction.session.status != "open":
                return False, "Impossible d'annuler une transaction d'une session fermée."

            # Check time limit
            config = CashSystemConfig.get_config()
            time_limit = timezone.timedelta(minutes=config.void_time_limit_minutes)
            if timezone.now() - transaction.transaction_time > time_limit:
                return False, f"Le délai d'annulation de {config.void_time_limit_minutes} minutes est dépassé."

            # Mark transaction as voided
            transaction.is_voided = True
            transaction.voided_by = admin_user
            transaction.void_time = timezone.now()
            transaction.notes = f"{transaction.notes}\n\nAnnulé: {reason}" if transaction.notes else f"Annulé: {reason}"
            transaction.save(update_fields=["is_voided", "voided_by", "void_time", "notes"])

            # Update payment status
            payment = transaction.payment
            payment.statut = "ANNULE"
            payment.save(update_fields=["statut"])

            # Reverse session balance (subtract amounts)
            session = transaction.session
            session.total_commission -= transaction.commission_amount
            session.save(update_fields=["total_commission"])

            # Cancel commission
            if hasattr(transaction, "commission"):
                commission = transaction.commission
                commission.payment_status = "cancelled"
                commission.save(update_fields=["payment_status"])

            # Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="transaction_void",
                user=admin_user,
                session=transaction.session,
                transaction=transaction,
                data={
                    "transaction_number": transaction.transaction_number,
                    "tax_amount": str(transaction.tax_amount),
                    "reason": reason,
                },
                request=request,
            )

            return True, None

        except Exception as e:
            return False, f"Erreur lors de l'annulation: {str(e)}"
