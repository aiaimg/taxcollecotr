"""
Management command to calculate and apply late payment penalties for unpaid contraventions.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from contraventions.models import ConfigurationSysteme, Contravention, ContraventionAuditLog
from notifications.services import NotificationService


class Command(BaseCommand):
    help = "Calcule et applique les pénalités de retard pour les contraventions impayées"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Affiche les actions sans les exécuter")
        parser.add_argument(
            "--send-notifications", action="store_true", help="Envoie des notifications aux conducteurs"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        send_notifications = options["send_notifications"]

        self.stdout.write(self.style.SUCCESS("Calcul des pénalités de retard..."))

        # Get configuration
        config = ConfigurationSysteme.get_config()
        today = timezone.now().date()

        # Find all unpaid contraventions past their due date
        overdue_contraventions = Contravention.objects.filter(
            statut="IMPAYEE", date_limite_paiement__lt=today
        ).select_related("type_infraction", "conducteur", "vehicule", "agent_controleur")

        total_contraventions = overdue_contraventions.count()
        self.stdout.write(f"Contraventions en retard trouvées: {total_contraventions}")

        if total_contraventions == 0:
            self.stdout.write(self.style.SUCCESS("Aucune contravention en retard."))
            return

        penalties_applied = 0
        total_penalty_amount = Decimal("0")

        for contravention in overdue_contraventions:
            days_overdue = (today - contravention.date_limite_paiement).days

            # Calculate penalty
            penalty_amount = contravention.calculer_penalite_retard()

            if penalty_amount > 0:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[DRY RUN] {contravention.numero_pv}: "
                            f"{days_overdue} jours de retard, "
                            f"pénalité: {penalty_amount:,.2f} Ar "
                            f"(montant actuel: {contravention.montant_amende_ariary:,.2f} Ar)"
                        )
                    )
                else:
                    # Apply penalty in a transaction
                    with transaction.atomic():
                        # Update the amount to include penalty
                        old_amount = contravention.montant_amende_ariary
                        new_amount = old_amount + penalty_amount

                        contravention.montant_amende_ariary = new_amount
                        contravention.save(update_fields=["montant_amende_ariary", "updated_at"])

                        # Create audit log entry
                        ContraventionAuditLog.objects.create(
                            action_type="UPDATE",
                            user=None,  # System action
                            contravention=contravention,
                            action_data={
                                "action": "penalty_applied",
                                "days_overdue": days_overdue,
                                "penalty_percentage": float(config.penalite_retard_pct),
                                "penalty_amount": float(penalty_amount),
                                "old_amount": float(old_amount),
                                "new_amount": float(new_amount),
                                "date_limite_paiement": contravention.date_limite_paiement.isoformat(),
                                "applied_at": timezone.now().isoformat(),
                            },
                            ip_address=None,
                            user_agent="System - calculate_penalties command",
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ {contravention.numero_pv}: "
                                f"Pénalité appliquée: {penalty_amount:,.2f} Ar "
                                f"({old_amount:,.2f} → {new_amount:,.2f} Ar)"
                            )
                        )

                        # Send notification if requested
                        if send_notifications:
                            self._send_penalty_notification(contravention, penalty_amount, days_overdue)

                penalties_applied += 1
                total_penalty_amount += penalty_amount

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] {penalties_applied} pénalités à appliquer\n"
                    f"Montant total des pénalités: {total_penalty_amount:,.2f} Ar"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {penalties_applied} pénalités appliquées avec succès\n"
                    f"Montant total des pénalités: {total_penalty_amount:,.2f} Ar"
                )
            )
        self.stdout.write("=" * 60)

    def _send_penalty_notification(self, contravention, penalty_amount, days_overdue):
        """Send notification to driver about penalty"""
        try:
            # Try to get user from conducteur or vehicle owner
            user = None
            if contravention.conducteur and hasattr(contravention.conducteur, "user"):
                user = contravention.conducteur.user
            elif contravention.vehicule and contravention.vehicule.proprietaire:
                user = contravention.vehicule.proprietaire

            if user:
                titre = f"Pénalité de retard appliquée - {contravention.numero_pv}"
                contenu = f"""
Bonjour,

Une pénalité de retard a été appliquée à votre contravention {contravention.numero_pv}.

Détails:
- Jours de retard: {days_overdue}
- Montant de la pénalité: {penalty_amount:,.2f} Ar
- Nouveau montant total: {contravention.get_montant_total():,.2f} Ar

Veuillez régulariser votre situation dans les plus brefs délais pour éviter des poursuites judiciaires.

Payer maintenant: https://taxcollector.mg/contraventions/verify/{contravention.qr_code.token if contravention.qr_code else contravention.numero_pv}/

Cordialement,
Service des Contraventions
                """.strip()

                NotificationService.create_notification(
                    user=user,
                    type_notification="system",
                    titre=titre,
                    contenu=contenu,
                    langue="fr",
                    metadata={
                        "contravention_id": str(contravention.id),
                        "numero_pv": contravention.numero_pv,
                        "penalty_amount": float(penalty_amount),
                        "days_overdue": days_overdue,
                    },
                    send_email=True,
                )

                self.stdout.write(f"  → Notification envoyée pour {contravention.numero_pv}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ⚠ Erreur lors de l'envoi de la notification: {str(e)}"))
