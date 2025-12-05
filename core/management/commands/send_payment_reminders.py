"""
Management command to send payment reminders to users with unpaid or expiring taxes.
Usage: python manage.py send_payment_reminders
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications.services import NotificationService
from payments.models import PaiementTaxe
from vehicles.models import Vehicule


class Command(BaseCommand):
    help = "Send payment reminders for unpaid and expiring vehicle taxes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be sent without actually sending",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No notifications will be sent"))

        current_year = timezone.now().year
        current_date = timezone.now().date()

        # Statistics
        unpaid_count = 0
        expiring_soon_count = 0
        expired_count = 0

        # Get all active vehicles
        vehicles = Vehicule.objects.filter(est_actif=True).select_related("proprietaire")

        for vehicle in vehicles:
            # Skip exempt vehicles
            if vehicle.est_exonere:
                continue

            owner = vehicle.proprietaire
            if not owner:
                continue

            # Get user's preferred language
            langue = "fr"
            if hasattr(owner, "profile"):
                langue = owner.profile.langue_preferee

            # Check for current year payment
            current_payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle, annee_fiscale=current_year, est_paye=True
            ).first()

            if not current_payment:
                # No payment for current year - send unpaid reminder
                if dry_run:
                    self.stdout.write(
                        f"  Would send UNPAID reminder to {owner.username} for {vehicle.plaque_immatriculation}"
                    )
                else:
                    NotificationService.create_payment_reminder_notification(
                        user=owner, vehicle=vehicle, reminder_type="unpaid", langue=langue
                    )
                unpaid_count += 1
            else:
                # Check if payment is expiring soon (within 30 days)
                payment_date = (
                    current_payment.date_paiement.date()
                    if hasattr(current_payment.date_paiement, "date")
                    else current_payment.date_paiement
                )
                expiry_date = payment_date.replace(year=payment_date.year + 1)
                days_until_expiry = (expiry_date - current_date).days

                if days_until_expiry <= 0:
                    # Payment has expired
                    if dry_run:
                        self.stdout.write(
                            f"  Would send EXPIRED reminder to {owner.username} for {vehicle.plaque_immatriculation}"
                        )
                    else:
                        NotificationService.create_payment_reminder_notification(
                            user=owner, vehicle=vehicle, reminder_type="expired", expiry_date=expiry_date, langue=langue
                        )
                    expired_count += 1
                elif days_until_expiry <= 30:
                    # Payment expiring soon
                    if dry_run:
                        self.stdout.write(
                            f"  Would send EXPIRING reminder to {owner.username} for {vehicle.plaque_immatriculation} ({days_until_expiry} days)"
                        )
                    else:
                        NotificationService.create_payment_reminder_notification(
                            user=owner,
                            vehicle=vehicle,
                            reminder_type="expiring",
                            days_remaining=days_until_expiry,
                            expiry_date=expiry_date,
                            langue=langue,
                        )
                    expiring_soon_count += 1

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"Total vehicles checked: {vehicles.count()}")
        self.stdout.write(self.style.ERROR(f"Unpaid taxes: {unpaid_count}"))
        self.stdout.write(self.style.WARNING(f"Expiring soon (≤30 days): {expiring_soon_count}"))
        self.stdout.write(self.style.ERROR(f"Expired: {expired_count}"))
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nThis was a dry run. Run without --dry-run to actually send notifications.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Sent {unpaid_count + expiring_soon_count + expired_count} payment reminders")
            )
