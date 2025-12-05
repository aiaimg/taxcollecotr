"""
Commission Service
Handles commission calculations and tracking for agent partenaires
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
    CashTransaction,
    CommissionRecord,
)


class CommissionService:
    """Service for commission management"""

    @staticmethod
    def calculate_commission(tax_amount: Decimal, commission_rate: Decimal) -> Decimal:
        """
        Calculate commission amount

        Args:
            tax_amount: The tax amount
            commission_rate: The commission rate (percentage)

        Returns:
            Commission amount
        """
        try:
            tax_amount = Decimal(str(tax_amount))
            commission_rate = Decimal(str(commission_rate))

            # Calculate commission: (tax_amount * commission_rate) / 100
            commission = (tax_amount * commission_rate) / Decimal("100")

            # Round to 2 decimal places
            return commission.quantize(Decimal("0.01"))

        except (ValueError, TypeError):
            return Decimal("0.00")

    @staticmethod
    @transaction.atomic
    def record_commission(
        transaction: CashTransaction, collector: AgentPartenaireProfile, session: CashSession
    ) -> Optional[CommissionRecord]:
        """
        Record commission for a transaction

        Args:
            transaction: The cash transaction
            collector: The agent partenaire
            session: The cash session

        Returns:
            CommissionRecord or None
        """
        try:
            # Check if commission already exists
            if hasattr(transaction, "commission"):
                return transaction.commission

            # Get commission rate
            commission_rate = collector.get_commission_rate()

            # Calculate commission amount
            commission_amount = CommissionService.calculate_commission(transaction.tax_amount, commission_rate)

            # Create commission record
            commission_record = CommissionRecord.objects.create(
                collector=collector,
                session=session,
                transaction=transaction,
                tax_amount=transaction.tax_amount,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                payment_status="pending",
            )

            return commission_record

        except Exception as e:
            return None

    @staticmethod
    def get_session_commission(session: CashSession) -> Dict[str, Any]:
        """
        Get total commission for a session

        Args:
            session: The cash session

        Returns:
            Dictionary with commission totals
        """
        # Get all commissions for the session (excluding cancelled)
        commissions = session.commissions.exclude(payment_status="cancelled")

        totals = commissions.aggregate(
            total_commission=Sum("commission_amount"),
            total_tax=Sum("tax_amount"),
            transaction_count=Count("id"),
            pending_count=Count("id", filter=Q(payment_status="pending")),
            paid_count=Count("id", filter=Q(payment_status="paid")),
        )

        return {
            "total_commission": totals["total_commission"] or Decimal("0.00"),
            "total_tax": totals["total_tax"] or Decimal("0.00"),
            "transaction_count": totals["transaction_count"] or 0,
            "pending_count": totals["pending_count"] or 0,
            "paid_count": totals["paid_count"] or 0,
            "average_commission_rate": (
                (totals["total_commission"] / totals["total_tax"] * 100)
                if totals["total_tax"] and totals["total_tax"] > 0
                else Decimal("0.00")
            ),
        }

    @staticmethod
    def get_collector_commission_report(
        collector: AgentPartenaireProfile,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        payment_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate commission report for collector

        Args:
            collector: The agent partenaire
            start_date: Optional start date filter
            end_date: Optional end date filter
            payment_status: Optional payment status filter

        Returns:
            Dictionary with commission report data
        """
        # Build query
        commissions = CommissionRecord.objects.filter(collector=collector)

        if start_date:
            commissions = commissions.filter(created_at__gte=start_date)

        if end_date:
            commissions = commissions.filter(created_at__lte=end_date)

        if payment_status:
            commissions = commissions.filter(payment_status=payment_status)

        # Calculate totals
        totals = commissions.aggregate(
            total_commission=Sum("commission_amount"),
            total_tax=Sum("tax_amount"),
            transaction_count=Count("id"),
            pending_amount=Sum("commission_amount", filter=Q(payment_status="pending")),
            paid_amount=Sum("commission_amount", filter=Q(payment_status="paid")),
            cancelled_amount=Sum("commission_amount", filter=Q(payment_status="cancelled")),
        )

        # Get session breakdown
        session_breakdown = (
            commissions.values("session__session_number", "session__opening_time", "session__status")
            .annotate(session_commission=Sum("commission_amount"), session_transactions=Count("id"))
            .order_by("-session__opening_time")
        )

        return {
            "collector": collector,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "totals": {
                "total_commission": totals["total_commission"] or Decimal("0.00"),
                "total_tax": totals["total_tax"] or Decimal("0.00"),
                "transaction_count": totals["transaction_count"] or 0,
                "pending_amount": totals["pending_amount"] or Decimal("0.00"),
                "paid_amount": totals["paid_amount"] or Decimal("0.00"),
                "cancelled_amount": totals["cancelled_amount"] or Decimal("0.00"),
            },
            "session_breakdown": list(session_breakdown),
            "commissions": commissions.order_by("-created_at"),
        }

    @staticmethod
    @transaction.atomic
    def mark_commissions_as_paid(
        commission_ids: list, paid_by: User, payment_date: Optional[timezone.datetime] = None
    ) -> Tuple[int, Optional[str]]:
        """
        Mark commissions as paid

        Args:
            commission_ids: List of commission record IDs
            paid_by: The user marking as paid
            payment_date: Optional payment date (defaults to now)

        Returns:
            Tuple of (count_updated, error_message)
        """
        try:
            if payment_date is None:
                payment_date = timezone.now()

            # Update commissions
            count = CommissionRecord.objects.filter(id__in=commission_ids, payment_status="pending").update(
                payment_status="paid", paid_date=payment_date, paid_by=paid_by
            )

            return count, None

        except Exception as e:
            return 0, f"Erreur lors du marquage des commissions: {str(e)}"

    @staticmethod
    def get_pending_commissions(
        collector: Optional[AgentPartenaireProfile] = None, min_amount: Optional[Decimal] = None
    ):
        """
        Get pending commissions

        Args:
            collector: Optional collector filter
            min_amount: Optional minimum amount filter

        Returns:
            QuerySet of pending CommissionRecord objects
        """
        commissions = CommissionRecord.objects.filter(payment_status="pending")

        if collector:
            commissions = commissions.filter(collector=collector)

        if min_amount:
            commissions = commissions.filter(commission_amount__gte=min_amount)

        return commissions.order_by("-created_at")

    @staticmethod
    def get_commission_summary_by_period(
        start_date: timezone.datetime, end_date: timezone.datetime, group_by: str = "collector"
    ) -> Dict[str, Any]:
        """
        Get commission summary grouped by period

        Args:
            start_date: Start date
            end_date: End date
            group_by: Grouping field ('collector', 'session', 'date')

        Returns:
            Dictionary with summary data
        """
        commissions = CommissionRecord.objects.filter(created_at__gte=start_date, created_at__lte=end_date).exclude(
            payment_status="cancelled"
        )

        if group_by == "collector":
            summary = (
                commissions.values("collector__agent_id", "collector__full_name")
                .annotate(
                    total_commission=Sum("commission_amount"),
                    total_tax=Sum("tax_amount"),
                    transaction_count=Count("id"),
                    pending_amount=Sum("commission_amount", filter=Q(payment_status="pending")),
                    paid_amount=Sum("commission_amount", filter=Q(payment_status="paid")),
                )
                .order_by("-total_commission")
            )

        elif group_by == "session":
            summary = (
                commissions.values("session__session_number", "session__collector__full_name", "session__opening_time")
                .annotate(
                    total_commission=Sum("commission_amount"),
                    total_tax=Sum("tax_amount"),
                    transaction_count=Count("id"),
                )
                .order_by("-session__opening_time")
            )

        else:  # group by date
            summary = (
                commissions.extra(select={"date": "DATE(created_at)"})
                .values("date")
                .annotate(
                    total_commission=Sum("commission_amount"),
                    total_tax=Sum("tax_amount"),
                    transaction_count=Count("id"),
                )
                .order_by("-date")
            )

        # Calculate overall totals
        overall_totals = commissions.aggregate(
            total_commission=Sum("commission_amount"),
            total_tax=Sum("tax_amount"),
            transaction_count=Count("id"),
            pending_amount=Sum("commission_amount", filter=Q(payment_status="pending")),
            paid_amount=Sum("commission_amount", filter=Q(payment_status="paid")),
        )

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "group_by": group_by,
            "summary": list(summary),
            "totals": {
                "total_commission": overall_totals["total_commission"] or Decimal("0.00"),
                "total_tax": overall_totals["total_tax"] or Decimal("0.00"),
                "transaction_count": overall_totals["transaction_count"] or 0,
                "pending_amount": overall_totals["pending_amount"] or Decimal("0.00"),
                "paid_amount": overall_totals["paid_amount"] or Decimal("0.00"),
            },
        }
