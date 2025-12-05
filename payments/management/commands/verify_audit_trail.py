"""
Management command to verify the integrity of the cash audit trail hash chain
"""

import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from administration.email_utils import send_email
from payments.services.cash_audit_service import CashAuditService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Verify hash chain integrity of cash audit trail and alert if tampering detected"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            type=str,
            help="Start date for verification (YYYY-MM-DD). Defaults to 30 days ago",
        )
        parser.add_argument(
            "--end-date",
            type=str,
            help="End date for verification (YYYY-MM-DD). Defaults to now",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Verify entire audit trail (may take time for large datasets)",
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Email address to send alert to if tampering detected",
        )
        parser.add_argument(
            "--alert-on-tampering",
            action="store_true",
            help="Send email alert to all admins if tampering is detected",
        )

    def handle(self, *args, **options):
        # Determine date range
        if options["full"]:
            start_date = None
            end_date = None
            date_range_str = "entire audit trail"
        else:
            now = timezone.now()

            if options["start_date"]:
                try:
                    start_date = datetime.strptime(options["start_date"], "%Y-%m-%d").replace(
                        tzinfo=timezone.get_current_timezone()
                    )
                except ValueError:
                    self.stdout.write(self.style.ERROR("Invalid start date format. Use YYYY-MM-DD"))
                    return
            else:
                # Default to 30 days ago
                start_date = now - timedelta(days=30)

            if options["end_date"]:
                try:
                    end_date = datetime.strptime(options["end_date"], "%Y-%m-%d").replace(
                        tzinfo=timezone.get_current_timezone()
                    )
                    # Set to end of day
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    self.stdout.write(self.style.ERROR("Invalid end date format. Use YYYY-MM-DD"))
                    return
            else:
                end_date = now

            date_range_str = f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'

        self.stdout.write(self.style.WARNING(f"Verifying audit trail integrity for: {date_range_str}"))
        self.stdout.write("")

        # Perform verification
        audit_service = CashAuditService()

        try:
            is_valid, tampered_entries = audit_service.verify_audit_trail(start_date=start_date, end_date=end_date)
        except Exception as e:
            logger.error(f"Failed to verify audit trail: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"✗ Verification failed: {e}"))
            return

        # Display results
        if is_valid:
            self.stdout.write(self.style.SUCCESS("✓ Audit trail integrity verified - No tampering detected"))
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("All hash chains are intact and valid."))
        else:
            self.stdout.write(self.style.ERROR(f"✗ TAMPERING DETECTED - {len(tampered_entries)} issue(s) found"))
            self.stdout.write("")

            # Display tampered entries
            for i, entry in enumerate(tampered_entries, 1):
                self.stdout.write(self.style.ERROR(f"Issue #{i}:"))
                self.stdout.write(f'  Log ID: {entry["log_id"]}')
                self.stdout.write(f'  Timestamp: {entry["timestamp"]}')
                self.stdout.write(f'  Action Type: {entry["action_type"]}')
                self.stdout.write(f'  Error: {entry["error"]}')

                if "expected_previous_hash" in entry:
                    self.stdout.write(f'  Expected Previous Hash: {entry["expected_previous_hash"][:16]}...')
                    self.stdout.write(f'  Actual Previous Hash: {entry["actual_previous_hash"][:16]}...')

                if "expected_hash" in entry:
                    self.stdout.write(f'  Expected Hash: {entry["expected_hash"][:16]}...')
                    self.stdout.write(f'  Actual Hash: {entry["actual_hash"][:16]}...')

                self.stdout.write("")

            # Send alert if requested
            if options["alert_on_tampering"] or options["email"]:
                self._send_tampering_alert(tampered_entries, date_range_str, options["email"])

    def _send_tampering_alert(self, tampered_entries, date_range_str, recipient_email=None):
        """Send email alert about detected tampering"""

        # Determine recipients
        if recipient_email:
            recipients = [recipient_email]
        else:
            # Send to all superusers with email addresses
            admin_users = User.objects.filter(is_superuser=True, email__isnull=False).exclude(email="")
            recipients = list(admin_users.values_list("email", flat=True))

        if not recipients:
            self.stdout.write(self.style.WARNING("No recipient email addresses found for alert"))
            return

        # Generate email content
        subject = "🚨 ALERTE SÉCURITÉ: Altération détectée dans le journal d'audit"

        # Plain text message
        message = self._generate_text_alert(tampered_entries, date_range_str)

        # HTML message
        html_message = self._generate_html_alert(tampered_entries, date_range_str)

        # Send email
        try:
            success, msg, logs = send_email(
                subject=subject,
                message=message,
                recipient_list=recipients,
                html_message=html_message,
                email_type="security_alert",
                fail_silently=False,
            )

            if success:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Security alert sent to {len(recipients)} recipient(s)"))
                for email in recipients:
                    self.stdout.write(f"  → {email}")
            else:
                self.stdout.write(self.style.ERROR(f"\n✗ Failed to send alert: {msg}"))
        except Exception as e:
            logger.error(f"Failed to send tampering alert email: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"\n✗ Failed to send alert: {e}"))

    def _generate_text_alert(self, tampered_entries, date_range_str):
        """Generate plain text alert email"""
        lines = [
            "🚨 ALERTE SÉCURITÉ: ALTÉRATION DÉTECTÉE",
            "=" * 80,
            "",
            f"Une altération potentielle a été détectée dans le journal d'audit des paiements en espèces.",
            f"Période vérifiée: {date_range_str}",
            f"Nombre d'anomalies détectées: {len(tampered_entries)}",
            "",
            "DÉTAILS DES ANOMALIES:",
            "",
        ]

        for i, entry in enumerate(tampered_entries, 1):
            lines.extend(
                [
                    f"Anomalie #{i}:",
                    f'  ID du journal: {entry["log_id"]}',
                    f'  Horodatage: {entry["timestamp"]}',
                    f'  Type d\'action: {entry["action_type"]}',
                    f'  Erreur: {entry["error"]}',
                    "",
                ]
            )

        lines.extend(
            [
                "",
                "ACTION REQUISE:",
                "1. Vérifiez immédiatement les journaux d'audit",
                "2. Enquêtez sur les entrées signalées",
                "3. Contactez l'équipe de sécurité si nécessaire",
                "4. Examinez les accès système récents",
                "",
                "Ce message a été généré automatiquement par le système de vérification d'audit.",
            ]
        )

        return "\n".join(lines)

    def _generate_html_alert(self, tampered_entries, date_range_str):
        """Generate HTML alert email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .alert {{ background-color: #f8d7da; border: 2px solid #dc3545; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .alert h1 {{ color: #721c24; margin-top: 0; }}
                .summary {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .issue {{ background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-left: 4px solid #dc3545; }}
                .issue h3 {{ color: #dc3545; margin-top: 0; }}
                .actions {{ background-color: #d1ecf1; padding: 15px; border-left: 4px solid #0c5460; margin: 20px 0; }}
                .actions h2 {{ color: #0c5460; margin-top: 0; }}
                ul {{ margin: 10px 0; padding-left: 20px; }}
                .footer {{ color: #6c757d; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h1>🚨 ALERTE SÉCURITÉ: ALTÉRATION DÉTECTÉE</h1>
                <p><strong>Une altération potentielle a été détectée dans le journal d'audit des paiements en espèces.</strong></p>
            </div>
            
            <div class="summary">
                <p><strong>Période vérifiée:</strong> {date_range_str}</p>
                <p><strong>Nombre d'anomalies détectées:</strong> {len(tampered_entries)}</p>
            </div>
            
            <h2>Détails des Anomalies</h2>
        """

        for i, entry in enumerate(tampered_entries, 1):
            html += f"""
            <div class="issue">
                <h3>Anomalie #{i}</h3>
                <p><strong>ID du journal:</strong> {entry["log_id"]}</p>
                <p><strong>Horodatage:</strong> {entry["timestamp"]}</p>
                <p><strong>Type d'action:</strong> {entry["action_type"]}</p>
                <p><strong>Erreur:</strong> {entry["error"]}</p>
            </div>
            """

        html += """
            <div class="actions">
                <h2>Action Requise</h2>
                <ul>
                    <li>Vérifiez immédiatement les journaux d'audit dans le système</li>
                    <li>Enquêtez sur les entrées signalées ci-dessus</li>
                    <li>Contactez l'équipe de sécurité si nécessaire</li>
                    <li>Examinez les accès système récents</li>
                    <li>Documentez toutes les découvertes</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Ce message a été généré automatiquement par le système de vérification d'audit.</p>
                <p>Ne répondez pas à cet email. Pour toute question, contactez l'administrateur système.</p>
            </div>
        </body>
        </html>
        """

        return html
