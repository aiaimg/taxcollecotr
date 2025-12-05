"""
Management command to automatically close expired cash sessions
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from notifications.services import NotificationService
from payments.models import CashSession, CashSystemConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Auto-close cash sessions that have exceeded the timeout period"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show which sessions would be closed without actually closing them",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force close sessions even if they have transactions",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        # Get system configuration
        config = CashSystemConfig.get_config()
        timeout_hours = config.session_timeout_hours

        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(hours=timeout_hours)

        self.stdout.write(
            self.style.WARNING(
                f"Looking for open sessions older than {timeout_hours} hours "
                f'(before {cutoff_time.strftime("%Y-%m-%d %H:%M:%S")})'
            )
        )

        # Find expired open sessions
        expired_sessions = CashSession.objects.filter(status="open", opening_time__lt=cutoff_time).select_related(
            "collector", "collector__user"
        )

        if not expired_sessions.exists():
            self.stdout.write(self.style.SUCCESS("No expired sessions found."))
            return

        self.stdout.write(self.style.WARNING(f"Found {expired_sessions.count()} expired session(s)"))

        closed_count = 0
        error_count = 0

        for session in expired_sessions:
            try:
                # Get transaction count
                transaction_count = session.transactions.count()

                if dry_run:
                    self.stdout.write(
                        f"  [DRY RUN] Would close session {session.session_number} "
                        f"for {session.collector.full_name} "
                        f'(opened: {session.opening_time.strftime("%Y-%m-%d %H:%M:%S")}, '
                        f"transactions: {transaction_count})"
                    )
                    closed_count += 1
                    continue

                # Calculate expected balance
                from payments.services.cash_session_service import CashSessionService

                totals = CashSessionService.calculate_session_totals(session)

                # Auto-close the session
                session.status = "closed"
                session.closing_time = timezone.now()
                session.expected_balance = totals["expected_balance"]
                session.closing_balance = totals["expected_balance"]  # Assume no discrepancy
                session.discrepancy_amount = 0
                session.discrepancy_notes = (
                    f"Session auto-closed after {timeout_hours} hours timeout. " f"Please verify physical cash count."
                )
                session.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Closed session {session.session_number} "
                        f"for {session.collector.full_name} "
                        f"(transactions: {transaction_count}, "
                        f"expected balance: {session.expected_balance} Ar)"
                    )
                )

                # Send notification to the agent
                try:
                    NotificationService.create_notification(
                        user=session.collector.user,
                        type_notification="system",
                        titre="Session automatiquement fermée",
                        contenu=(
                            f"Votre session {session.session_number} a été automatiquement "
                            f"fermée après {timeout_hours} heures d'inactivité. "
                            f"Veuillez vérifier le solde physique et contacter l'administration "
                            f"si nécessaire."
                        ),
                        langue="fr",
                        metadata={
                            "session_id": str(session.id),
                            "session_number": session.session_number,
                            "expected_balance": str(session.expected_balance),
                            "auto_closed": True,
                        },
                        send_email=True,
                    )
                    self.stdout.write(self.style.SUCCESS(f"    → Notification sent to {session.collector.full_name}"))
                except Exception as e:
                    logger.error(f"Failed to send notification for session {session.session_number}: {e}")
                    self.stdout.write(self.style.WARNING(f"    ⚠ Failed to send notification: {e}"))

                closed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Failed to close session {session.session_number}: {e}", exc_info=True)
                self.stdout.write(self.style.ERROR(f"  ✗ Failed to close session {session.session_number}: {e}"))

        # Summary
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"[DRY RUN] Would close {closed_count} session(s)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully closed {closed_count} session(s)"))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f"Failed to close {error_count} session(s)"))
