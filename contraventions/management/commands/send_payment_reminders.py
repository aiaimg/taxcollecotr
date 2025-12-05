from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from contraventions.models import Contestation, Contravention


class Command(BaseCommand):
    help = "Envoie des rappels de paiement pour les contraventions impayées"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-before-due",
            type=int,
            default=7,
            help="Nombre de jours avant l'échéance pour envoyer un rappel (par défaut: 7)",
        )
        parser.add_argument(
            "--days-after-due",
            type=int,
            default=3,
            help="Nombre de jours après l'échéance pour envoyer un rappel (par défaut: 3)",
        )
        parser.add_argument("--dry-run", action="store_true", help="Affiche les actions sans les exécuter")

    def handle(self, *args, **options):
        days_before_due = options["days_before_due"]
        days_after_due = options["days_after_due"]
        dry_run = options["dry_run"]

        self.stdout.write("Envoi des rappels de paiement...")

        today = timezone.now().date()

        # Find unpaid contraventions that need reminders
        # 1. Those approaching due date
        approaching_due = Contravention.objects.filter(
            statut="active", date_echeance__date=today + timedelta(days=days_before_due)
        )

        # 2. Those past due date
        past_due = Contravention.objects.filter(
            statut="active", date_echeance__date__lt=today - timedelta(days=days_after_due)
        )

        # 3. Those very overdue (30+ days)
        very_overdue = Contravention.objects.filter(statut="active", date_echeance__date__lt=today - timedelta(days=30))

        total_reminders = 0

        # Process approaching due date
        for contravention in approaching_due:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Rappel approchant échéance pour {contravention.numero_contravention} "
                        f"(échéance: {contravention.date_echeance.date()})"
                    )
                )
            else:
                self.send_payment_reminder(contravention, "approaching_due")
            total_reminders += 1

        # Process past due
        for contravention in past_due:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Rappel dépassé échéance pour {contravention.numero_contravention} "
                        f"(échéance: {contravention.date_echeance.date()})"
                    )
                )
            else:
                self.send_payment_reminder(contravention, "past_due")
            total_reminders += 1

        # Process very overdue
        for contravention in very_overdue:
            if dry_run:
                self.stdout.write(
                    self.style.ERROR(
                        f"[DRY RUN] Rappel très en retard pour {contravention.numero_contravention} "
                        f"(échéance: {contravention.date_echeance.date()})"
                    )
                )
            else:
                self.send_payment_reminder(contravention, "very_overdue")
            total_reminders += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY RUN] {total_reminders} rappels à envoyer"))
        else:
            self.stdout.write(self.style.SUCCESS(f"{total_reminders} rappels envoyés avec succès"))

    def send_payment_reminder(self, contravention, reminder_type):
        """Send payment reminder based on type"""

        # Get contact information
        email = None
        phone = None

        if contravention.conducteur:
            email = contravention.conducteur.email
            phone = contravention.conducteur.telephone
        elif contravention.vehicule and contravention.vehicule.proprietaire:
            email = contravention.vehicule.proprietaire.email
            phone = contravention.vehicule.proprietaire.telephone

        # Determine message based on reminder type
        if reminder_type == "approaching_due":
            subject = f"Rappel: Paiement de contravention {contravention.numero_contravention}"
            message = f"""
            Bonjour,
            
            Nous vous rappelons que la contravention {contravention.numero_contravention} 
            doit être payée avant le {contravention.date_echeance.strftime("%d/%m/%Y")}.
            
            Montant: {contravention.montant_total_ariary:,} Ar
            
            Pour payer: https://taxcollector.mg/contraventions/public/{contravention.numero_contravention}/pay/
            
            Cordialement,
            Service des Contraventions
            """

        elif reminder_type == "past_due":
            subject = f"URGENT: Contravention impayée {contravention.numero_contravention}"
            message = f"""
            Bonjour,
            
            Votre contravention {contravention.numero_contravention} est maintenant en retard.
            La date limite de paiement ({contravention.date_echeance.strftime("%d/%m/%Y")}) est dépassée.
            
            Montant: {contravention.montant_total_ariary:,} Ar
            Frais de retard peuvent s\'appliquer.
            
            Payez immédiatement: https://taxcollector.mg/contraventions/public/{contravention.numero_contravention}/pay/
            
            Cordialement,
            Service des Contraventions
            """

        elif reminder_type == "very_overdue":
            subject = f"AVERTISSEMENT: Contravention très en retard {contravention.numero_contravention}"
            message = f"""
            Bonjour,
            
            Votre contravention {contravention.numero_contravention} est très en retard 
            (plus de 30 jours depuis la date limite).
            
            Montant: {contravention.montant_total_ariary:,} Ar
            
            Des poursuites judiciaires peuvent être engagées.
            
            Payez immédiatement: https://taxcollector.mg/contraventions/public/{contravention.numero_contravention}/pay/
            
            Pour toute question: +261 20 22 123 45
            
            Cordialement,
            Service des Contraventions
            """

        # Here you would integrate with your notification system
        # For now, just log the reminder
        self.stdout.write(
            f"Rappel envoyé pour {contravention.numero_contravention} ({reminder_type}) "
            f"-> Email: {email}, Tél: {phone}"
        )
