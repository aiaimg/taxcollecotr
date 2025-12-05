"""
Management command to generate monthly commission reports for agent partenaires
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Sum
from django.utils import timezone

from administration.email_utils import send_email
from payments.models import AgentPartenaireProfile, CommissionRecord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate monthly commission reports and email them to admin"

    def add_arguments(self, parser):
        parser.add_argument(
            "--month",
            type=int,
            help="Month (1-12). Defaults to previous month",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="Year (e.g., 2024). Defaults to current year",
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Email address to send report to. If not provided, sends to all admin users",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Generate report without sending emails",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Determine the reporting period
        now = timezone.now()
        if options["month"]:
            month = options["month"]
            year = options["year"] or now.year
        else:
            # Default to previous month
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month = first_day_this_month - timedelta(days=1)
            month = last_month.month
            year = last_month.year

        # Validate month
        if month < 1 or month > 12:
            self.stdout.write(self.style.ERROR("Month must be between 1 and 12"))
            return

        # Calculate date range
        start_date = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone())

        month_name = start_date.strftime("%B %Y")

        self.stdout.write(self.style.WARNING(f"Generating commission report for {month_name}"))

        # Query commission records for the period
        commissions = CommissionRecord.objects.filter(
            created_at__gte=start_date, created_at__lt=end_date
        ).select_related("collector", "session", "transaction")

        if not commissions.exists():
            self.stdout.write(self.style.WARNING(f"No commission records found for {month_name}"))
            return

        # Generate report data
        report_data = self._generate_report_data(commissions, month_name)

        # Display report to console
        self._display_report(report_data)

        # Send email report
        if not dry_run:
            self._send_email_report(report_data, options["email"])
        else:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] Email report not sent"))

    def _generate_report_data(self, commissions, month_name):
        """Generate structured report data from commission records"""

        # Overall statistics
        total_commissions = commissions.aggregate(
            total_amount=Sum("commission_amount"), total_tax=Sum("tax_amount"), total_count=Count("id")
        )

        # By payment status
        status_breakdown = {}
        for status_code, status_label in CommissionRecord.PAYMENT_STATUS_CHOICES:
            status_commissions = commissions.filter(payment_status=status_code)
            status_breakdown[status_label] = {
                "count": status_commissions.count(),
                "amount": status_commissions.aggregate(total=Sum("commission_amount"))["total"] or Decimal("0.00"),
            }

        # By collector
        collectors = AgentPartenaireProfile.objects.filter(commissions__in=commissions).distinct()

        collector_breakdown = []
        for collector in collectors:
            collector_commissions = commissions.filter(collector=collector)
            collector_data = collector_commissions.aggregate(
                total_amount=Sum("commission_amount"),
                total_tax=Sum("tax_amount"),
                total_count=Count("id"),
                pending_amount=Sum("commission_amount", filter=Q(payment_status="pending")),
                paid_amount=Sum("commission_amount", filter=Q(payment_status="paid")),
            )

            collector_breakdown.append(
                {
                    "name": collector.full_name,
                    "agent_id": collector.agent_id,
                    "location": collector.collection_location,
                    "commission_rate": collector.get_commission_rate(),
                    "transaction_count": collector_data["total_count"],
                    "total_tax": collector_data["total_tax"] or Decimal("0.00"),
                    "total_commission": collector_data["total_amount"] or Decimal("0.00"),
                    "pending": collector_data["pending_amount"] or Decimal("0.00"),
                    "paid": collector_data["paid_amount"] or Decimal("0.00"),
                }
            )

        # Sort by total commission (descending)
        collector_breakdown.sort(key=lambda x: x["total_commission"], reverse=True)

        return {
            "month_name": month_name,
            "total_amount": total_commissions["total_amount"] or Decimal("0.00"),
            "total_tax": total_commissions["total_tax"] or Decimal("0.00"),
            "total_count": total_commissions["total_count"],
            "status_breakdown": status_breakdown,
            "collector_breakdown": collector_breakdown,
        }

    def _display_report(self, data):
        """Display report to console"""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(f'  COMMISSION REPORT - {data["month_name"]}'))
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write("")

        # Overall statistics
        self.stdout.write(self.style.WARNING("OVERALL STATISTICS:"))
        self.stdout.write(f'  Total Transactions: {data["total_count"]}')
        self.stdout.write(f'  Total Tax Collected: {data["total_tax"]:,.2f} Ar')
        self.stdout.write(f'  Total Commissions: {data["total_amount"]:,.2f} Ar')
        self.stdout.write("")

        # Status breakdown
        self.stdout.write(self.style.WARNING("BY PAYMENT STATUS:"))
        for status, stats in data["status_breakdown"].items():
            self.stdout.write(f'  {status}: {stats["count"]} transactions, {stats["amount"]:,.2f} Ar')
        self.stdout.write("")

        # Collector breakdown
        self.stdout.write(self.style.WARNING("BY AGENT PARTENAIRE:"))
        self.stdout.write("")
        for collector in data["collector_breakdown"]:
            self.stdout.write(f'  {collector["name"]} ({collector["agent_id"]})')
            self.stdout.write(f'    Location: {collector["location"]}')
            self.stdout.write(f'    Commission Rate: {collector["commission_rate"]}%')
            self.stdout.write(f'    Transactions: {collector["transaction_count"]}')
            self.stdout.write(f'    Tax Collected: {collector["total_tax"]:,.2f} Ar')
            self.stdout.write(f'    Total Commission: {collector["total_commission"]:,.2f} Ar')
            self.stdout.write(f'    Pending: {collector["pending"]:,.2f} Ar')
            self.stdout.write(f'    Paid: {collector["paid"]:,.2f} Ar')
            self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("=" * 80))

    def _send_email_report(self, data, recipient_email=None):
        """Send email report to admin users"""

        # Determine recipients
        if recipient_email:
            recipients = [recipient_email]
        else:
            # Send to all superusers and staff with email addresses
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True), email__isnull=False).exclude(
                email=""
            )
            recipients = list(admin_users.values_list("email", flat=True))

        if not recipients:
            self.stdout.write(self.style.WARNING("No recipient email addresses found"))
            return

        # Generate email content
        subject = f'Rapport de Commission - {data["month_name"]}'

        # Plain text message
        message = self._generate_text_report(data)

        # HTML message
        html_message = self._generate_html_report(data)

        # Send email
        try:
            success, msg, logs = send_email(
                subject=subject,
                message=message,
                recipient_list=recipients,
                html_message=html_message,
                email_type="commission_report",
                fail_silently=False,
            )

            if success:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Email report sent to {len(recipients)} recipient(s)"))
                for email in recipients:
                    self.stdout.write(f"  → {email}")
            else:
                self.stdout.write(self.style.ERROR(f"\n✗ Failed to send email: {msg}"))
        except Exception as e:
            logger.error(f"Failed to send commission report email: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"\n✗ Failed to send email: {e}"))

    def _generate_text_report(self, data):
        """Generate plain text email report"""
        lines = [
            f'RAPPORT DE COMMISSION - {data["month_name"]}',
            "=" * 80,
            "",
            "STATISTIQUES GLOBALES:",
            f'  Nombre total de transactions: {data["total_count"]}',
            f'  Total des taxes collectées: {data["total_amount"]:,.2f} Ar',
            f'  Total des commissions: {data["total_amount"]:,.2f} Ar',
            "",
            "PAR STATUT DE PAIEMENT:",
        ]

        for status, stats in data["status_breakdown"].items():
            lines.append(f'  {status}: {stats["count"]} transactions, {stats["amount"]:,.2f} Ar')

        lines.extend(["", "PAR AGENT PARTENAIRE:", ""])

        for collector in data["collector_breakdown"]:
            lines.extend(
                [
                    f'{collector["name"]} ({collector["agent_id"]})',
                    f'  Emplacement: {collector["location"]}',
                    f'  Taux de commission: {collector["commission_rate"]}%',
                    f'  Transactions: {collector["transaction_count"]}',
                    f'  Taxes collectées: {collector["total_tax"]:,.2f} Ar',
                    f'  Commission totale: {collector["total_commission"]:,.2f} Ar',
                    f'  En attente: {collector["pending"]:,.2f} Ar',
                    f'  Payé: {collector["paid"]:,.2f} Ar',
                    "",
                ]
            )

        return "\n".join(lines)

    def _generate_html_report(self, data):
        """Generate HTML email report"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .amount {{ font-weight: bold; color: #27ae60; }}
                .pending {{ color: #e67e22; }}
                .paid {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <h1>Rapport de Commission - {data["month_name"]}</h1>
            
            <div class="summary">
                <h2>Statistiques Globales</h2>
                <p><strong>Nombre total de transactions:</strong> {data["total_count"]}</p>
                <p><strong>Total des taxes collectées:</strong> <span class="amount">{data["total_tax"]:,.2f} Ar</span></p>
                <p><strong>Total des commissions:</strong> <span class="amount">{data["total_amount"]:,.2f} Ar</span></p>
            </div>
            
            <h2>Par Statut de Paiement</h2>
            <table>
                <tr>
                    <th>Statut</th>
                    <th>Transactions</th>
                    <th>Montant</th>
                </tr>
        """

        for status, stats in data["status_breakdown"].items():
            html += f"""
                <tr>
                    <td>{status}</td>
                    <td>{stats["count"]}</td>
                    <td>{stats["amount"]:,.2f} Ar</td>
                </tr>
            """

        html += """
            </table>
            
            <h2>Par Agent Partenaire</h2>
            <table>
                <tr>
                    <th>Agent</th>
                    <th>Emplacement</th>
                    <th>Taux</th>
                    <th>Transactions</th>
                    <th>Taxes</th>
                    <th>Commission</th>
                    <th>En attente</th>
                    <th>Payé</th>
                </tr>
        """

        for collector in data["collector_breakdown"]:
            html += f"""
                <tr>
                    <td>{collector["name"]}<br><small>({collector["agent_id"]})</small></td>
                    <td>{collector["location"]}</td>
                    <td>{collector["commission_rate"]}%</td>
                    <td>{collector["transaction_count"]}</td>
                    <td>{collector["total_tax"]:,.2f} Ar</td>
                    <td class="amount">{collector["total_commission"]:,.2f} Ar</td>
                    <td class="pending">{collector["pending"]:,.2f} Ar</td>
                    <td class="paid">{collector["paid"]:,.2f} Ar</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html
