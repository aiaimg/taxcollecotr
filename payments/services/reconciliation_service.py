"""
Reconciliation Service
Handles daily reconciliation and discrepancy reporting
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from payments.models import (
    AgentPartenaireProfile,
    CashSession,
    CashSystemConfig,
    CashTransaction,
)

from .cash_audit_service import CashAuditService
from .cash_session_service import CashSessionService


class ReconciliationService:
    """Service for cash reconciliation"""

    @staticmethod
    def generate_daily_report(date: datetime.date) -> Dict[str, Any]:
        """
        Generate daily cash collection report

        Args:
            date: The date for the report

        Returns:
            Dictionary with daily report data
        """
        # Get all sessions for the day
        start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(date, datetime.max.time()))

        sessions = CashSession.objects.filter(opening_time__gte=start_datetime, opening_time__lte=end_datetime)

        # Calculate totals across all sessions
        session_data = []
        total_opening_balance = Decimal("0.00")
        total_expected_balance = Decimal("0.00")
        total_closing_balance = Decimal("0.00")
        total_discrepancy = Decimal("0.00")
        total_tax_collected = Decimal("0.00")
        total_commission = Decimal("0.00")
        total_transactions = 0

        for session in sessions:
            session_totals = CashSessionService.calculate_session_totals(session)

            session_info = {
                "session": session,
                "collector": session.collector,
                "status": session.get_status_display(),
                **session_totals,
            }

            if session.status in ["closed", "reconciled"]:
                session_info.update(
                    {
                        "closing_balance": session.closing_balance,
                        "discrepancy_amount": session.discrepancy_amount,
                    }
                )
                total_closing_balance += session.closing_balance or Decimal("0.00")
                total_discrepancy += session.discrepancy_amount or Decimal("0.00")

            session_data.append(session_info)

            total_opening_balance += session.opening_balance
            total_expected_balance += session_totals["expected_balance"]
            total_tax_collected += session_totals["total_tax_collected"]
            total_commission += session_totals["total_commission"]
            total_transactions += session_totals["transaction_count"]

        return {
            "date": date,
            "sessions": session_data,
            "totals": {
                "session_count": sessions.count(),
                "total_opening_balance": total_opening_balance,
                "total_expected_balance": total_expected_balance,
                "total_closing_balance": total_closing_balance,
                "total_discrepancy": total_discrepancy,
                "total_tax_collected": total_tax_collected,
                "total_commission": total_commission,
                "total_transactions": total_transactions,
            },
            "status": {
                "open_sessions": sessions.filter(status="open").count(),
                "closed_sessions": sessions.filter(status="closed").count(),
                "reconciled_sessions": sessions.filter(status="reconciled").count(),
            },
        }

    @staticmethod
    @transaction.atomic
    def reconcile_day(
        date: datetime.date, admin_user: User, physical_count: Decimal, notes: str = "", request=None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Perform end-of-day reconciliation

        Args:
            date: The date to reconcile
            admin_user: The admin user performing reconciliation
            physical_count: The actual physical cash counted
            notes: Reconciliation notes
            request: HTTP request object for audit logging

        Returns:
            Tuple of (success, error_message, reconciliation_data)
        """
        try:
            # Get daily report
            daily_report = ReconciliationService.generate_daily_report(date)

            # Check if all sessions are closed
            open_sessions = daily_report["status"]["open_sessions"]
            if open_sessions > 0:
                return (
                    False,
                    f"Il y a encore {open_sessions} session(s) ouverte(s). Toutes les sessions doivent être fermées avant la réconciliation.",
                    None,
                )

            # Calculate expected total
            expected_total = daily_report["totals"]["total_expected_balance"]

            # Calculate discrepancy
            discrepancy = physical_count - expected_total

            # Check tolerance
            config = CashSystemConfig.get_config()
            requires_approval = abs(discrepancy) > config.reconciliation_tolerance

            if requires_approval and not notes:
                return (
                    False,
                    f"L'écart de {discrepancy} Ar dépasse la tolérance de {config.reconciliation_tolerance} Ar. Des notes explicatives sont requises.",
                    None,
                )

            # Mark all closed sessions as reconciled
            start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(date, datetime.max.time()))

            sessions_to_reconcile = CashSession.objects.filter(
                opening_time__gte=start_datetime, opening_time__lte=end_datetime, status="closed"
            )

            for session in sessions_to_reconcile:
                session.status = "reconciled"
                session.approved_by = admin_user
                session.save(update_fields=["status", "approved_by"])

            # Create audit log
            audit_service = CashAuditService()
            audit_service.log_action(
                action_type="reconciliation",
                user=admin_user,
                data={
                    "date": date.isoformat(),
                    "expected_total": str(expected_total),
                    "physical_count": str(physical_count),
                    "discrepancy": str(discrepancy),
                    "requires_approval": requires_approval,
                    "notes": notes,
                    "sessions_reconciled": sessions_to_reconcile.count(),
                },
                request=request,
            )

            reconciliation_data = {
                "date": date,
                "expected_total": expected_total,
                "physical_count": physical_count,
                "discrepancy": discrepancy,
                "requires_approval": requires_approval,
                "notes": notes,
                "sessions_reconciled": sessions_to_reconcile.count(),
                "daily_report": daily_report,
            }

            return True, None, reconciliation_data

        except Exception as e:
            return False, f"Erreur lors de la réconciliation: {str(e)}", None

    @staticmethod
    def get_discrepancy_report(
        start_date: datetime.date,
        end_date: datetime.date,
        collector: Optional[AgentPartenaireProfile] = None,
        min_discrepancy: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        Generate discrepancy tracking report

        Args:
            start_date: Start date
            end_date: End date
            collector: Optional collector filter
            min_discrepancy: Optional minimum discrepancy amount filter

        Returns:
            Dictionary with discrepancy report data
        """
        # Build query
        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        sessions = CashSession.objects.filter(
            opening_time__gte=start_datetime, opening_time__lte=end_datetime, status__in=["closed", "reconciled"]
        ).exclude(discrepancy_amount=0)

        if collector:
            sessions = sessions.filter(collector=collector)

        if min_discrepancy:
            sessions = sessions.filter(
                Q(discrepancy_amount__gte=min_discrepancy) | Q(discrepancy_amount__lte=-min_discrepancy)
            )

        # Calculate statistics
        discrepancy_stats = sessions.aggregate(
            total_discrepancy=Sum("discrepancy_amount"),
            avg_discrepancy=Avg("discrepancy_amount"),
            max_discrepancy=Sum("discrepancy_amount"),
            session_count=Count("id"),
            positive_discrepancies=Count("id", filter=Q(discrepancy_amount__gt=0)),
            negative_discrepancies=Count("id", filter=Q(discrepancy_amount__lt=0)),
        )

        # Group by collector
        collector_breakdown = (
            sessions.values("collector__agent_id", "collector__full_name")
            .annotate(
                total_discrepancy=Sum("discrepancy_amount"),
                avg_discrepancy=Avg("discrepancy_amount"),
                session_count=Count("id"),
            )
            .order_by("-total_discrepancy")
        )

        # Get detailed session list
        session_details = []
        for session in sessions.order_by("-opening_time"):
            session_details.append(
                {
                    "session_number": session.session_number,
                    "collector": session.collector.full_name,
                    "opening_time": session.opening_time,
                    "closing_time": session.closing_time,
                    "expected_balance": session.expected_balance,
                    "closing_balance": session.closing_balance,
                    "discrepancy_amount": session.discrepancy_amount,
                    "discrepancy_notes": session.discrepancy_notes,
                    "status": session.get_status_display(),
                    "approved_by": session.approved_by.get_full_name() if session.approved_by else None,
                }
            )

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "statistics": {
                "total_discrepancy": discrepancy_stats["total_discrepancy"] or Decimal("0.00"),
                "avg_discrepancy": discrepancy_stats["avg_discrepancy"] or Decimal("0.00"),
                "max_discrepancy": discrepancy_stats["max_discrepancy"] or Decimal("0.00"),
                "session_count": discrepancy_stats["session_count"] or 0,
                "positive_discrepancies": discrepancy_stats["positive_discrepancies"] or 0,
                "negative_discrepancies": discrepancy_stats["negative_discrepancies"] or 0,
            },
            "collector_breakdown": list(collector_breakdown),
            "session_details": session_details,
        }

    @staticmethod
    def get_reconciliation_history(start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get reconciliation history for a date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of daily reconciliation summaries
        """
        history = []
        current_date = start_date

        while current_date <= end_date:
            daily_report = ReconciliationService.generate_daily_report(current_date)

            # Check if day is fully reconciled
            is_reconciled = (
                daily_report["status"]["open_sessions"] == 0
                and daily_report["status"]["closed_sessions"] == 0
                and daily_report["totals"]["session_count"] > 0
            )

            history.append(
                {
                    "date": current_date,
                    "is_reconciled": is_reconciled,
                    "session_count": daily_report["totals"]["session_count"],
                    "total_tax_collected": daily_report["totals"]["total_tax_collected"],
                    "total_commission": daily_report["totals"]["total_commission"],
                    "total_transactions": daily_report["totals"]["total_transactions"],
                    "total_discrepancy": daily_report["totals"]["total_discrepancy"],
                    "status": daily_report["status"],
                }
            )

            current_date += timedelta(days=1)

        return history

    @staticmethod
    def get_unreconciled_sessions(max_age_days: Optional[int] = None):
        """
        Get sessions that are closed but not reconciled

        Args:
            max_age_days: Optional filter for sessions older than X days

        Returns:
            QuerySet of unreconciled CashSession objects
        """
        sessions = CashSession.objects.filter(status="closed")

        if max_age_days:
            cutoff_date = timezone.now() - timedelta(days=max_age_days)
            sessions = sessions.filter(closing_time__lte=cutoff_date)

        return sessions.order_by("closing_time")

    @staticmethod
    def get_reconciliation_summary(start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """
        Get overall reconciliation summary for a period

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with reconciliation summary
        """
        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        all_sessions = CashSession.objects.filter(opening_time__gte=start_datetime, opening_time__lte=end_datetime)

        summary = all_sessions.aggregate(
            total_sessions=Count("id"),
            open_sessions=Count("id", filter=Q(status="open")),
            closed_sessions=Count("id", filter=Q(status="closed")),
            reconciled_sessions=Count("id", filter=Q(status="reconciled")),
            total_opening_balance=Sum("opening_balance"),
            total_expected_balance=Sum("expected_balance"),
            total_closing_balance=Sum("closing_balance"),
            total_discrepancy=Sum("discrepancy_amount"),
            sessions_with_discrepancy=Count("id", filter=~Q(discrepancy_amount=0)),
        )

        # Calculate reconciliation rate
        total = summary["total_sessions"] or 0
        reconciled = summary["reconciled_sessions"] or 0
        reconciliation_rate = (reconciled / total * 100) if total > 0 else 0

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "summary": {
                "total_sessions": summary["total_sessions"] or 0,
                "open_sessions": summary["open_sessions"] or 0,
                "closed_sessions": summary["closed_sessions"] or 0,
                "reconciled_sessions": summary["reconciled_sessions"] or 0,
                "reconciliation_rate": round(reconciliation_rate, 2),
                "total_opening_balance": summary["total_opening_balance"] or Decimal("0.00"),
                "total_expected_balance": summary["total_expected_balance"] or Decimal("0.00"),
                "total_closing_balance": summary["total_closing_balance"] or Decimal("0.00"),
                "total_discrepancy": summary["total_discrepancy"] or Decimal("0.00"),
                "sessions_with_discrepancy": summary["sessions_with_discrepancy"] or 0,
            },
        }
