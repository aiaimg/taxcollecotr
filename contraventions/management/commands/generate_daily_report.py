"""
Management command to generate daily reports for contraventions.
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from contraventions.models import AgentControleurProfile, Contestation, Contravention, DossierFourriere, TypeInfraction


class Command(BaseCommand):
    help = "Génère un rapport quotidien des contraventions"

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, help="Date du rapport (format: YYYY-MM-DD). Par défaut: hier")
        parser.add_argument("--send-email", action="store_true", help="Envoie le rapport par email aux administrateurs")
        parser.add_argument(
            "--format",
            type=str,
            choices=["text", "json", "html"],
            default="text",
            help="Format du rapport (text, json, html)",
        )

    def handle(self, *args, **options):
        # Determine report date (yesterday by default)
        if options["date"]:
            try:
                report_date = datetime.strptime(options["date"], "%Y-%m-%d").date()
            except ValueError:
                self.stdout.write(self.style.ERROR("Format de date invalide. Utilisez YYYY-MM-DD"))
                return
        else:
            report_date = (timezone.now() - timedelta(days=1)).date()

        send_email = options["send_email"]
        report_format = options["format"]

        self.stdout.write(self.style.SUCCESS(f"Génération du rapport quotidien pour le {report_date}..."))

        # Generate report data
        report_data = self._generate_report_data(report_date)

        # Format and display report
        if report_format == "json":
            report_output = self._format_json(report_data)
        elif report_format == "html":
            report_output = self._format_html(report_data)
        else:
            report_output = self._format_text(report_data)

        self.stdout.write("\n" + report_output)

        # Send email if requested
        if send_email:
            self._send_email_report(report_data, report_date, report_output)

        self.stdout.write(self.style.SUCCESS("\n✓ Rapport quotidien généré avec succès"))

    def _generate_report_data(self, report_date):
        """Generate comprehensive report data"""
        start_datetime = timezone.make_aware(datetime.combine(report_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(report_date, datetime.max.time()))

        # Get contraventions for the day
        daily_contraventions = Contravention.objects.filter(created_at__range=(start_datetime, end_datetime))

        # Overall statistics
        total_created = daily_contraventions.count()
        total_paid = daily_contraventions.filter(statut="PAYEE").count()
        total_contested = daily_contraventions.filter(statut="CONTESTEE").count()
        total_cancelled = daily_contraventions.filter(statut="ANNULEE").count()
        total_unpaid = daily_contraventions.filter(statut="IMPAYEE").count()

        # Financial statistics
        total_amount = daily_contraventions.aggregate(total=Sum("montant_amende_ariary"))["total"] or Decimal("0")

        paid_amount = daily_contraventions.filter(statut="PAYEE").aggregate(total=Sum("montant_amende_ariary"))[
            "total"
        ] or Decimal("0")

        # Payment rate
        payment_rate = (total_paid / total_created * 100) if total_created > 0 else 0

        # Statistics by infraction type
        by_infraction = (
            daily_contraventions.values("type_infraction__nom", "type_infraction__article_code")
            .annotate(count=Count("id"), total_amount=Sum("montant_amende_ariary"))
            .order_by("-count")[:10]
        )

        # Statistics by agent
        by_agent = (
            daily_contraventions.values(
                "agent_controleur__matricule", "agent_controleur__nom_complet", "agent_controleur__unite_affectation"
            )
            .annotate(count=Count("id"), total_amount=Sum("montant_amende_ariary"))
            .order_by("-count")[:10]
        )

        # Statistics by status
        by_status = daily_contraventions.values("statut").annotate(count=Count("id")).order_by("-count")

        # Fourrière statistics
        fourriere_created = DossierFourriere.objects.filter(
            date_mise_fourriere__range=(start_datetime, end_datetime)
        ).count()

        fourriere_released = DossierFourriere.objects.filter(
            date_sortie_fourriere__range=(start_datetime, end_datetime), statut="RESTITUE"
        ).count()

        # Contestation statistics
        contestations_created = Contestation.objects.filter(
            date_soumission__range=(start_datetime, end_datetime)
        ).count()

        contestations_accepted = Contestation.objects.filter(
            date_examen__range=(start_datetime, end_datetime), statut="ACCEPTEE"
        ).count()

        contestations_rejected = Contestation.objects.filter(
            date_examen__range=(start_datetime, end_datetime), statut="REJETEE"
        ).count()

        # Cumulative statistics (all time)
        cumulative_total = Contravention.objects.count()
        cumulative_paid = Contravention.objects.filter(statut="PAYEE").count()
        cumulative_unpaid = Contravention.objects.filter(statut="IMPAYEE").count()

        cumulative_amount = Contravention.objects.aggregate(total=Sum("montant_amende_ariary"))["total"] or Decimal("0")

        cumulative_paid_amount = Contravention.objects.filter(statut="PAYEE").aggregate(
            total=Sum("montant_amende_ariary")
        )["total"] or Decimal("0")

        return {
            "report_date": report_date,
            "daily": {
                "total_created": total_created,
                "total_paid": total_paid,
                "total_contested": total_contested,
                "total_cancelled": total_cancelled,
                "total_unpaid": total_unpaid,
                "total_amount": float(total_amount),
                "paid_amount": float(paid_amount),
                "payment_rate": round(payment_rate, 2),
                "by_infraction": list(by_infraction),
                "by_agent": list(by_agent),
                "by_status": list(by_status),
                "fourriere_created": fourriere_created,
                "fourriere_released": fourriere_released,
                "contestations_created": contestations_created,
                "contestations_accepted": contestations_accepted,
                "contestations_rejected": contestations_rejected,
            },
            "cumulative": {
                "total": cumulative_total,
                "paid": cumulative_paid,
                "unpaid": cumulative_unpaid,
                "total_amount": float(cumulative_amount),
                "paid_amount": float(cumulative_paid_amount),
            },
        }

    def _format_text(self, data):
        """Format report as text"""
        report_date = data["report_date"]
        daily = data["daily"]
        cumulative = data["cumulative"]

        lines = []
        lines.append("=" * 80)
        lines.append(f'RAPPORT QUOTIDIEN DES CONTRAVENTIONS - {report_date.strftime("%d/%m/%Y")}')
        lines.append("=" * 80)
        lines.append("")

        # Daily statistics
        lines.append("📊 STATISTIQUES DU JOUR")
        lines.append("-" * 80)
        lines.append(f'Contraventions créées:     {daily["total_created"]:>6}')
        lines.append(f'  - Payées:                {daily["total_paid"]:>6} ({daily["payment_rate"]:>5.1f}%)')
        lines.append(f'  - Impayées:              {daily["total_unpaid"]:>6}')
        lines.append(f'  - Contestées:            {daily["total_contested"]:>6}')
        lines.append(f'  - Annulées:              {daily["total_cancelled"]:>6}')
        lines.append("")
        lines.append(f"💰 MONTANTS")
        lines.append(f'Montant total émis:        {daily["total_amount"]:>15,.2f} Ar')
        lines.append(f'Montant collecté:          {daily["paid_amount"]:>15,.2f} Ar')
        lines.append("")

        # Fourrière
        if daily["fourriere_created"] > 0 or daily["fourriere_released"] > 0:
            lines.append(f"🚗 FOURRIÈRE")
            lines.append(f'Véhicules mis en fourrière: {daily["fourriere_created"]:>6}')
            lines.append(f'Véhicules restitués:        {daily["fourriere_released"]:>6}')
            lines.append("")

        # Contestations
        if daily["contestations_created"] > 0:
            lines.append(f"⚖️  CONTESTATIONS")
            lines.append(f'Nouvelles contestations:   {daily["contestations_created"]:>6}')
            lines.append(f'Contestations acceptées:   {daily["contestations_accepted"]:>6}')
            lines.append(f'Contestations rejetées:    {daily["contestations_rejected"]:>6}')
            lines.append("")

        # Top infractions
        if daily["by_infraction"]:
            lines.append("🚨 TOP 10 INFRACTIONS")
            lines.append("-" * 80)
            for i, infraction in enumerate(daily["by_infraction"][:10], 1):
                nom = infraction["type_infraction__nom"] or "Non spécifié"
                article = infraction["type_infraction__article_code"] or "N/A"
                count = infraction["count"]
                amount = infraction["total_amount"] or 0
                lines.append(f"{i:>2}. {article:<10} {nom:<40} {count:>4} ({amount:>12,.0f} Ar)")
            lines.append("")

        # Top agents
        if daily["by_agent"]:
            lines.append("👮 TOP 10 AGENTS CONTRÔLEURS")
            lines.append("-" * 80)
            for i, agent in enumerate(daily["by_agent"][:10], 1):
                matricule = agent["agent_controleur__matricule"] or "N/A"
                nom = agent["agent_controleur__nom_complet"] or "Non spécifié"
                unite = agent["agent_controleur__unite_affectation"] or "N/A"
                count = agent["count"]
                lines.append(f"{i:>2}. {matricule:<12} {nom:<30} {unite:<20} {count:>4} PV")
            lines.append("")

        # Cumulative statistics
        lines.append("📈 STATISTIQUES CUMULÉES (TOTAL)")
        lines.append("-" * 80)
        lines.append(f'Total contraventions:      {cumulative["total"]:>10,}')
        lines.append(f'  - Payées:                {cumulative["paid"]:>10,}')
        lines.append(f'  - Impayées:              {cumulative["unpaid"]:>10,}')
        lines.append(f'Montant total émis:        {cumulative["total_amount"]:>15,.2f} Ar')
        lines.append(f'Montant total collecté:    {cumulative["paid_amount"]:>15,.2f} Ar')
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_json(self, data):
        """Format report as JSON"""
        # Convert date to string for JSON serialization
        data["report_date"] = data["report_date"].isoformat()
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_html(self, data):
        """Format report as HTML"""
        report_date = data["report_date"]
        daily = data["daily"]
        cumulative = data["cumulative"]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rapport Quotidien - {report_date.strftime("%d/%m/%Y")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .stat-box {{ display: inline-block; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ font-size: 14px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1>📊 Rapport Quotidien des Contraventions</h1>
    <p><strong>Date:</strong> {report_date.strftime("%d/%m/%Y")}</p>
    
    <h2>Statistiques du Jour</h2>
    <div>
        <div class="stat-box">
            <div class="stat-value">{daily['total_created']}</div>
            <div class="stat-label">Contraventions créées</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{daily['total_paid']}</div>
            <div class="stat-label">Payées ({daily['payment_rate']:.1f}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{daily['total_amount']:,.0f} Ar</div>
            <div class="stat-label">Montant total émis</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{daily['paid_amount']:,.0f} Ar</div>
            <div class="stat-label">Montant collecté</div>
        </div>
    </div>
    
    <h2>Top 10 Infractions</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Article</th>
            <th>Infraction</th>
            <th>Nombre</th>
            <th>Montant Total</th>
        </tr>
"""

        for i, infraction in enumerate(daily["by_infraction"][:10], 1):
            nom = infraction["type_infraction__nom"] or "Non spécifié"
            article = infraction["type_infraction__article_code"] or "N/A"
            count = infraction["count"]
            amount = infraction["total_amount"] or 0
            html += f"""
        <tr>
            <td>{i}</td>
            <td>{article}</td>
            <td>{nom}</td>
            <td>{count}</td>
            <td>{amount:,.0f} Ar</td>
        </tr>
"""

        html += """
    </table>
    
    <h2>Statistiques Cumulées</h2>
    <table>
        <tr>
            <th>Indicateur</th>
            <th>Valeur</th>
        </tr>
"""

        html += f"""
        <tr><td>Total contraventions</td><td>{cumulative['total']:,}</td></tr>
        <tr><td>Contraventions payées</td><td>{cumulative['paid']:,}</td></tr>
        <tr><td>Contraventions impayées</td><td>{cumulative['unpaid']:,}</td></tr>
        <tr><td>Montant total émis</td><td>{cumulative['total_amount']:,.2f} Ar</td></tr>
        <tr><td>Montant total collecté</td><td>{cumulative['paid_amount']:,.2f} Ar</td></tr>
    </table>
</body>
</html>
"""

        return html

    def _send_email_report(self, data, report_date, report_output):
        """Send report via email to administrators"""
        try:
            from administration.email_utils import send_email

            # Get administrators
            admin_group = Group.objects.filter(name__in=["Administrateur Contraventions", "Administrateurs"]).first()

            if not admin_group:
                self.stdout.write(self.style.WARNING("⚠ Aucun groupe d'administrateurs trouvé"))
                return

            admin_users = admin_group.user_set.filter(is_active=True, email__isnull=False).exclude(email="")

            if not admin_users.exists():
                self.stdout.write(self.style.WARNING("⚠ Aucun administrateur avec email trouvé"))
                return

            recipient_list = [user.email for user in admin_users]

            subject = f'Rapport Quotidien Contraventions - {report_date.strftime("%d/%m/%Y")}'

            # Use HTML format for email
            message_html = self._format_html(data)

            success, message, logs = send_email(
                subject=subject,
                message=report_output,  # Plain text fallback
                recipient_list=recipient_list,
                email_type="rapport",
                related_object_type="DailyReport",
                related_object_id=None,
                fail_silently=False,
                html_message=message_html,
            )

            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Rapport envoyé par email à {len(recipient_list)} administrateur(s)")
                )
            else:
                self.stdout.write(self.style.ERROR(f"✗ Erreur lors de l'envoi: {message}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Erreur lors de l'envoi du rapport: {str(e)}"))
