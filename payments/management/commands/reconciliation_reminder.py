"""
Management command to send daily reconciliation reminders for unreconciled sessions
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Sum
from django.utils import timezone

from administration.email_utils import send_email
from notifications.services import NotificationService
from payments.models import AgentPartenaireProfile, CashSession

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send daily reconciliation reminders for unreconciled cash sessions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Number of days to look back for unreconciled sessions (default: 1)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be sent without actually sending notifications",
        )
        parser.add_argument(
            "--email-admins",
            action="store_true",
            help="Also send summary email to admin staff",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        days_back = options["days"]
        email_admins = options["email_admins"]

        # Calculate cutoff date
        now = timezone.now()
        cutoff_date = now - timedelta(days=days_back)

        self.stdout.write(
            self.style.WARNING(
                f"Looking for unreconciled sessions from the last {days_back} day(s) "
                f'(since {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
            )
        )

        # Find closed but unreconciled sessions
        unreconciled_sessions = (
            CashSession.objects.filter(status="closed", closing_time__gte=cutoff_date, closing_time__lt=now)
            .select_related("collector", "collector__user")
            .order_by("closing_time")
        )

        if not unreconciled_sessions.exists():
            self.stdout.write(self.style.SUCCESS("No unreconciled sessions found."))
            return

        self.stdout.write(self.style.WARNING(f"Found {unreconciled_sessions.count()} unreconciled session(s)"))
        self.stdout.write("")

        # Group sessions by collector
        sessions_by_collector = {}
        for session in unreconciled_sessions:
            collector_id = session.collector.id
            if collector_id not in sessions_by_collector:
                sessions_by_collector[collector_id] = {"collector": session.collector, "sessions": []}
            sessions_by_collector[collector_id]["sessions"].append(session)

        # Send reminders to collectors
        reminder_count = 0
        error_count = 0

        for collector_id, data in sessions_by_collector.items():
            collector = data["collector"]
            sessions = data["sessions"]

            try:
                if dry_run:
                    self.stdout.write(
                        f"  [DRY RUN] Would send reminder to {collector.full_name} " f"for {len(sessions)} session(s)"
                    )
                    reminder_count += 1
                    continue

                # Send notification to collector
                self._send_collector_reminder(collector, sessions)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Sent reminder to {collector.full_name} "
                        f"({collector.user.email}) for {len(sessions)} session(s)"
                    )
                )
                reminder_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Failed to send reminder to {collector.full_name}: {e}", exc_info=True)
                self.stdout.write(self.style.ERROR(f"  ✗ Failed to send reminder to {collector.full_name}: {e}"))

        # Send summary to admins if requested
        if email_admins and not dry_run:
            self._send_admin_summary(unreconciled_sessions, days_back)

        # Summary
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"[DRY RUN] Would send {reminder_count} reminder(s)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent {reminder_count} reminder(s)"))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f"Failed to send {error_count} reminder(s)"))

    def _send_collector_reminder(self, collector, sessions):
        """Send reminder notification to collector"""

        # Calculate totals
        total_expected = sum(session.expected_balance or Decimal("0.00") for session in sessions)
        total_discrepancy = sum(abs(session.discrepancy_amount or Decimal("0.00")) for session in sessions)

        # Create session list
        session_list = "\n".join(
            [
                f"  - Session {session.session_number} "
                f'(fermée le {session.closing_time.strftime("%Y-%m-%d à %H:%M")})'
                for session in sessions
            ]
        )

        # Notification content
        titre = "Rappel: Réconciliation de session(s) en attente"
        contenu = (
            f"Bonjour {collector.full_name},\n\n"
            f"Vous avez {len(sessions)} session(s) fermée(s) en attente de réconciliation:\n\n"
            f"{session_list}\n\n"
            f"Solde total attendu: {total_expected:,.2f} Ar\n"
        )

        if total_discrepancy > 0:
            contenu += f"Écarts totaux: {total_discrepancy:,.2f} Ar\n"

        contenu += (
            "\n"
            "Veuillez contacter l'administration pour finaliser la réconciliation "
            "de ces sessions dès que possible.\n\n"
            "Merci de votre collaboration."
        )

        # Send notification
        NotificationService.create_notification(
            user=collector.user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue="fr",
            metadata={
                "type": "reconciliation_reminder",
                "session_count": len(sessions),
                "session_ids": [str(s.id) for s in sessions],
                "total_expected": str(total_expected),
                "total_discrepancy": str(total_discrepancy),
            },
            send_email=True,
        )

    def _send_admin_summary(self, unreconciled_sessions, days_back):
        """Send summary email to admin staff"""

        # Get admin email addresses
        admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True), email__isnull=False).exclude(
            email=""
        )
        recipients = list(admin_users.values_list("email", flat=True))

        if not recipients:
            self.stdout.write(self.style.WARNING("No admin email addresses found for summary"))
            return

        # Calculate statistics
        stats = unreconciled_sessions.aggregate(
            total_sessions=Count("id"),
            total_expected=Sum("expected_balance"),
            total_discrepancy=Sum("discrepancy_amount"),
        )

        # Group by collector
        collectors_with_sessions = {}
        for session in unreconciled_sessions:
            collector_id = session.collector.id
            if collector_id not in collectors_with_sessions:
                collectors_with_sessions[collector_id] = {
                    "collector": session.collector,
                    "sessions": [],
                    "total_expected": Decimal("0.00"),
                    "total_discrepancy": Decimal("0.00"),
                }
            collectors_with_sessions[collector_id]["sessions"].append(session)
            collectors_with_sessions[collector_id]["total_expected"] += session.expected_balance or Decimal("0.00")
            collectors_with_sessions[collector_id]["total_discrepancy"] += abs(
                session.discrepancy_amount or Decimal("0.00")
            )

        # Generate email content
        subject = f'Rappel: {stats["total_sessions"]} session(s) en attente de réconciliation'

        # Plain text message
        message = self._generate_text_summary(stats, collectors_with_sessions, days_back)

        # HTML message
        html_message = self._generate_html_summary(stats, collectors_with_sessions, days_back)

        # Send email
        try:
            success, msg, logs = send_email(
                subject=subject,
                message=message,
                recipient_list=recipients,
                html_message=html_message,
                email_type="reconciliation_reminder",
                fail_silently=False,
            )

            if success:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Admin summary sent to {len(recipients)} recipient(s)"))
                for email in recipients:
                    self.stdout.write(f"  → {email}")
            else:
                self.stdout.write(self.style.ERROR(f"\n✗ Failed to send admin summary: {msg}"))
        except Exception as e:
            logger.error(f"Failed to send admin summary email: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"\n✗ Failed to send admin summary: {e}"))

    def _generate_text_summary(self, stats, collectors_with_sessions, days_back):
        """Generate plain text summary email"""
        lines = [
            f"RAPPEL DE RÉCONCILIATION - Sessions des {days_back} dernier(s) jour(s)",
            "=" * 80,
            "",
            "RÉSUMÉ:",
            f'  Sessions non réconciliées: {stats["total_sessions"]}',
            f'  Solde total attendu: {stats["total_expected"] or 0:,.2f} Ar',
            f'  Écarts totaux: {abs(stats["total_discrepancy"] or 0):,.2f} Ar',
            "",
            "PAR AGENT PARTENAIRE:",
            "",
        ]

        for data in collectors_with_sessions.values():
            collector = data["collector"]
            sessions = data["sessions"]
            lines.extend(
                [
                    f"{collector.full_name} ({collector.agent_id})",
                    f"  Sessions: {len(sessions)}",
                    f'  Solde attendu: {data["total_expected"]:,.2f} Ar',
                    f'  Écarts: {data["total_discrepancy"]:,.2f} Ar',
                    f"  Sessions:",
                ]
            )

            for session in sessions:
                lines.append(
                    f"    - {session.session_number} "
                    f'(fermée le {session.closing_time.strftime("%Y-%m-%d à %H:%M")})'
                )

            lines.append("")

        lines.extend(
            [
                "",
                "ACTION REQUISE:",
                "  Veuillez procéder à la réconciliation de ces sessions dans le système.",
                "",
                "Ce message a été généré automatiquement.",
            ]
        )

        return "\n".join(lines)

    def _generate_html_summary(self, stats, collectors_with_sessions, days_back):
        """Generate HTML summary email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #e67e22; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .summary {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                .collector {{ background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .collector h3 {{ color: #495057; margin-top: 0; }}
                ul {{ margin: 10px 0; padding-left: 20px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; flex: 1; margin: 0 10px; }}
                .stat-value {{ font-size: 1.5em; font-weight: bold; color: #e67e22; }}
                .action {{ background-color: #d1ecf1; padding: 15px; border-left: 4px solid #0c5460; margin: 20px 0; }}
                .footer {{ color: #6c757d; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }}
            </style>
        </head>
        <body>
            <h1>⚠️ Rappel de Réconciliation</h1>
            <p>Sessions des {days_back} dernier(s) jour(s) en attente de réconciliation</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div>Sessions</div>
                    <div class="stat-value">{stats["total_sessions"]}</div>
                </div>
                <div class="stat-box">
                    <div>Solde Attendu</div>
                    <div class="stat-value">{stats["total_expected"] or 0:,.0f} Ar</div>
                </div>
                <div class="stat-box">
                    <div>Écarts Totaux</div>
                    <div class="stat-value">{abs(stats["total_discrepancy"] or 0):,.0f} Ar</div>
                </div>
            </div>
            
            <h2>Par Agent Partenaire</h2>
        """

        for data in collectors_with_sessions.values():
            collector = data["collector"]
            sessions = data["sessions"]

            html += f"""
            <div class="collector">
                <h3>{collector.full_name} ({collector.agent_id})</h3>
                <p>
                    <strong>Sessions:</strong> {len(sessions)} | 
                    <strong>Solde attendu:</strong> {data["total_expected"]:,.2f} Ar | 
                    <strong>Écarts:</strong> {data["total_discrepancy"]:,.2f} Ar
                </p>
                <ul>
            """

            for session in sessions:
                html += f"""
                    <li>
                        Session {session.session_number} 
                        (fermée le {session.closing_time.strftime("%Y-%m-%d à %H:%M")})
                    </li>
                """

            html += """
                </ul>
            </div>
            """

        html += """
            <div class="action">
                <h2>Action Requise</h2>
                <p>Veuillez procéder à la réconciliation de ces sessions dans le système d'administration.</p>
            </div>
            
            <div class="footer">
                <p>Ce message a été généré automatiquement par le système de gestion des paiements en espèces.</p>
            </div>
        </body>
        </html>
        """

        return html
