"""
Management command to normalize vehicle plate numbers by removing spaces
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from vehicles.models import Vehicule


class Command(BaseCommand):
    help = "Normalize vehicle plate numbers by removing spaces"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without actually changing it",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(self.style.WARNING("Normalizing vehicle plate numbers..."))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get all vehicles with spaces in their plate numbers
        vehicles_with_spaces = []
        for vehicle in Vehicule.objects.all():
            if " " in vehicle.plaque_immatriculation:
                vehicles_with_spaces.append(vehicle)

        if not vehicles_with_spaces:
            self.stdout.write(self.style.SUCCESS("No vehicles found with spaces in plate numbers"))
            return

        self.stdout.write(f"Found {len(vehicles_with_spaces)} vehicles with spaces in plate numbers")

        updated_count = 0
        error_count = 0

        for vehicle in vehicles_with_spaces:
            old_plate = vehicle.plaque_immatriculation
            new_plate = Vehicule.normalize_plate(old_plate)

            self.stdout.write(f"  {old_plate} -> {new_plate}")

            if not dry_run:
                try:
                    with transaction.atomic():
                        # Check if normalized plate already exists
                        if (
                            new_plate != old_plate
                            and Vehicule.objects.filter(plaque_immatriculation=new_plate).exists()
                        ):
                            self.stdout.write(
                                self.style.ERROR(f"    ERROR: Plate {new_plate} already exists! Skipping {old_plate}")
                            )
                            error_count += 1
                            continue

                        # Update the plate
                        # We need to use raw SQL because we're changing the primary key
                        from django.db import connection

                        with connection.cursor() as cursor:
                            # Update related tables first (to avoid foreign key violations)

                            # Update payments_qrcode table
                            cursor.execute(
                                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'payments_qrcode')"
                            )
                            if cursor.fetchone()[0]:
                                cursor.execute(
                                    "UPDATE payments_qrcode SET vehicule_plaque_id = %s WHERE vehicule_plaque_id = %s",
                                    [new_plate, old_plate],
                                )

                            # Update payments_paiementtaxe table
                            cursor.execute(
                                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'payments_paiementtaxe')"
                            )
                            if cursor.fetchone()[0]:
                                cursor.execute(
                                    "UPDATE payments_paiementtaxe SET vehicule_plaque_id = %s WHERE vehicule_plaque_id = %s",
                                    [new_plate, old_plate],
                                )

                            # Update the vehicle table last
                            cursor.execute(
                                "UPDATE vehicles_vehicule SET plaque_immatriculation = %s WHERE plaque_immatriculation = %s",
                                [new_plate, old_plate],
                            )

                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"    Updated successfully"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    ERROR: {str(e)}"))
                    error_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: Would update {len(vehicles_with_spaces)} vehicles"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {updated_count} vehicles"))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f"Failed to update {error_count} vehicles"))
