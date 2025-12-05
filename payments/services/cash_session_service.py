"""
Cash Session Service
Handles cash collection session management
"""

from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from payments.models import (
    AgentPartenaireProfile,
    CashSession,
    CashSystemConfig,
    CashTransaction,
)

from .cash_audit_service import CashAuditService


class CashSessionService:
    """Service for managing cash sessions"""

    @staticmethod
    @transaction.atomic
    def open_session(
        collector: AgentPartenaireProfile, opening_balance: Decimal, request=None
    ) -> Tuple[Optional[CashSession], Optional[str]]:
        """
        Open a new cash collection session

        Args:
            collector: The agent partenaire opening the session
            opening_balance: The starting cash amount
            request: HTTP request object for audit logging

        Returns:
            Tuple of (CashSession, error_message)
        """
        try:
            # 1. Validate no open session exists
            existing_session = CashSession.objects.filter(collector=collector, status="open").first()

            if existing_session:
                return None, "Vous avez déjà une session ouverte. Veuillez la fermer avant d'en ouvrir une nouvelle."

            # 2. Create CashSession record
            session = CashSession.objects.create(collector=collector, opening_balance=opening_balance, status="open")

            # 3. Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="session_open",
                user=collector.user,
                session=session,
                data={
                    "session_number": session.session_number,
                    "opening_balance": str(opening_balance),
                    "collector_id": collector.agent_id,
                    "collector_name": collector.full_name,
                },
                request=request,
            )

            return session, None

        except Exception as e:
            return None, f"Erreur lors de l'ouverture de la session: {str(e)}"

    @staticmethod
    @transaction.atomic
    def close_session(
        session: CashSession, closing_balance: Decimal, counted_by: User, discrepancy_notes: str = "", request=None
    ) -> Tuple[Optional[CashSession], Optional[Decimal]]:
        """
        Close a cash session

        Args:
            session: The cash session to close
            closing_balance: The actual cash counted
            counted_by: The user who counted the cash
            discrepancy_notes: Notes about any discrepancy
            request: HTTP request object for audit logging

        Returns:
            Tuple of (CashSession, discrepancy_amount)
        """
        try:
            if session.status != "open":
                return None, None

            # 1. Calculate expected balance
            totals = CashSessionService.calculate_session_totals(session)
            expected_balance = totals["expected_balance"]

            # 2. Calculate discrepancy
            discrepancy_amount = closing_balance - expected_balance

            # 3. Check if discrepancy exceeds tolerance
            config = CashSystemConfig.get_config()
            requires_approval = abs(discrepancy_amount) > config.reconciliation_tolerance

            # 4. Update session status
            session.closing_balance = closing_balance
            session.expected_balance = expected_balance
            session.closing_time = timezone.now()
            session.discrepancy_amount = discrepancy_amount
            session.discrepancy_notes = discrepancy_notes
            session.status = "closed"

            if requires_approval:
                session.approved_by = None  # Requires admin approval
            else:
                session.approved_by = counted_by

            session.save()

            # 5. Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="session_close",
                user=counted_by,
                session=session,
                data={
                    "session_number": session.session_number,
                    "opening_balance": str(session.opening_balance),
                    "closing_balance": str(closing_balance),
                    "expected_balance": str(expected_balance),
                    "discrepancy_amount": str(discrepancy_amount),
                    "requires_approval": requires_approval,
                    "discrepancy_notes": discrepancy_notes,
                },
                request=request,
            )

            return session, discrepancy_amount

        except Exception as e:
            return None, None

    @staticmethod
    def get_active_session(collector: AgentPartenaireProfile) -> Optional[CashSession]:
        """
        Get collector's active session

        Args:
            collector: The agent partenaire

        Returns:
            Active CashSession or None
        """
        return CashSession.objects.filter(collector=collector, status="open").first()

    @staticmethod
    def calculate_session_totals(session: CashSession) -> Dict[str, Any]:
        """
        Calculate session totals (transactions, commission, etc.)

        Args:
            session: The cash session

        Returns:
            Dictionary with session totals
        """
        # Get all non-voided transactions
        transactions = session.transactions.filter(is_voided=False)

        # Calculate totals
        totals = transactions.aggregate(
            total_transactions=Count("id"),
            total_tax_collected=Sum("tax_amount"),
            total_cash_received=Sum("amount_tendered"),
            total_change_given=Sum("change_given"),
            total_commission=Sum("commission_amount"),
        )

        # Calculate net cash (cash received - change given)
        net_cash = (totals["total_cash_received"] or Decimal("0.00")) - (
            totals["total_change_given"] or Decimal("0.00")
        )

        # Calculate expected balance
        expected_balance = session.opening_balance + net_cash

        # Count pending approvals
        pending_approvals = transactions.filter(requires_approval=True, approved_by__isnull=True).count()

        return {
            "transaction_count": totals["total_transactions"] or 0,
            "total_tax_collected": totals["total_tax_collected"] or Decimal("0.00"),
            "total_cash_received": totals["total_cash_received"] or Decimal("0.00"),
            "total_change_given": totals["total_change_given"] or Decimal("0.00"),
            "net_cash": net_cash,
            "total_commission": totals["total_commission"] or Decimal("0.00"),
            "expected_balance": expected_balance,
            "opening_balance": session.opening_balance,
            "pending_approvals": pending_approvals,
        }

    @staticmethod
    def get_session_summary(session: CashSession) -> Dict[str, Any]:
        """
        Get comprehensive session summary

        Args:
            session: The cash session

        Returns:
            Dictionary with session summary
        """
        totals = CashSessionService.calculate_session_totals(session)

        summary = {
            "session": session,
            "collector": session.collector,
            "status": session.get_status_display(),
            "opening_time": session.opening_time,
            "closing_time": session.closing_time,
            "duration": None,
            **totals,
        }

        # Calculate session duration
        if session.closing_time:
            duration = session.closing_time - session.opening_time
            summary["duration"] = duration
        elif session.status == "open":
            duration = timezone.now() - session.opening_time
            summary["duration"] = duration

        # Add closing information if session is closed
        if session.status in ["closed", "reconciled"]:
            summary.update(
                {
                    "closing_balance": session.closing_balance,
                    "expected_balance": session.expected_balance,
                    "discrepancy_amount": session.discrepancy_amount,
                    "discrepancy_notes": session.discrepancy_notes,
                    "approved_by": session.approved_by,
                }
            )

        return summary

    @staticmethod
    @transaction.atomic
    def approve_session_closure(
        session: CashSession, admin_user: User, notes: str = "", request=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Approve a session closure with discrepancy

        Args:
            session: The cash session to approve
            admin_user: The admin user approving
            notes: Approval notes
            request: HTTP request object for audit logging

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if session.status != "closed":
                return False, "Seules les sessions fermées peuvent être approuvées."

            if session.approved_by:
                return False, "Cette session a déjà été approuvée."

            # Update session
            session.approved_by = admin_user
            if notes:
                session.discrepancy_notes = (
                    f"{session.discrepancy_notes}\n\nApprobation: {notes}"
                    if session.discrepancy_notes
                    else f"Approbation: {notes}"
                )
            session.status = "reconciled"
            session.save()

            # Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="reconciliation",
                user=admin_user,
                session=session,
                data={
                    "session_number": session.session_number,
                    "discrepancy_amount": str(session.discrepancy_amount),
                    "notes": notes,
                },
                request=request,
            )

            return True, None

        except Exception as e:
            return False, f"Erreur lors de l'approbation: {str(e)}"

    @staticmethod
    def get_collector_sessions(
        collector: AgentPartenaireProfile,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        status: Optional[str] = None,
    ):
        """
        Get sessions for a collector with optional filters

        Args:
            collector: The agent partenaire
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter

        Returns:
            QuerySet of CashSession objects
        """
        sessions = CashSession.objects.filter(collector=collector)

        if start_date:
            sessions = sessions.filter(opening_time__gte=start_date)

        if end_date:
            sessions = sessions.filter(opening_time__lte=end_date)

        if status:
            sessions = sessions.filter(status=status)

        return sessions.order_by("-opening_time")

    @staticmethod
    def check_session_timeout(session: CashSession) -> bool:
        """
        Check if a session has exceeded the timeout period

        Args:
            session: The cash session to check

        Returns:
            Boolean indicating if session has timed out
        """
        if session.status != "open":
            return False

        config = CashSystemConfig.get_config()
        timeout_hours = config.session_timeout_hours
        timeout_duration = timezone.timedelta(hours=timeout_hours)

        return timezone.now() - session.opening_time > timeout_duration
