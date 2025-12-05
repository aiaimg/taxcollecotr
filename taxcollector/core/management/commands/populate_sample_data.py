from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from taxcollector.vehicles.models import GrilleTarifaire, TarifVehicule


class Command(BaseCommand):
    help = "Populate the database with sample tax grid data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating sample tax grid data..."))

        # Create tax grid for current year
        current_year = timezone.now().year

        # Check if tax grid already exists for current year
        grille, created = GrilleTarifaire.objects.get_or_create(
            annee=current_year,
            defaults={
                "nom": f"Grille Tarifaire {current_year}",
                "description": f"Grille tarifaire officielle pour l'année {current_year}",
                "date_debut": datetime(current_year, 1, 1).date(),
                "date_fin": datetime(current_year, 12, 31).date(),
                "est_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created tax grid for year {current_year}"))
        else:
            self.stdout.write(self.style.WARNING(f"Tax grid for year {current_year} already exists"))

        # Define tariff data
        tarifs_data = [
            # Voitures particulières
            {
                "type_vehicule": "VOITURE",
                "puissance_min": 1,
                "puissance_max": 5,
                "montant_base": Decimal("50000"),
                "penalite_mensuelle": Decimal("5000"),
            },
            {
                "type_vehicule": "VOITURE",
                "puissance_min": 6,
                "puissance_max": 10,
                "montant_base": Decimal("75000"),
                "penalite_mensuelle": Decimal("7500"),
            },
            {
                "type_vehicule": "VOITURE",
                "puissance_min": 11,
                "puissance_max": 15,
                "montant_base": Decimal("100000"),
                "penalite_mensuelle": Decimal("10000"),
            },
            {
                "type_vehicule": "VOITURE",
                "puissance_min": 16,
                "puissance_max": 20,
                "montant_base": Decimal("150000"),
                "penalite_mensuelle": Decimal("15000"),
            },
            {
                "type_vehicule": "VOITURE",
                "puissance_min": 21,
                "puissance_max": 50,
                "montant_base": Decimal("200000"),
                "penalite_mensuelle": Decimal("20000"),
            },
            # Motos
            {
                "type_vehicule": "MOTO",
                "puissance_min": 1,
                "puissance_max": 5,
                "montant_base": Decimal("25000"),
                "penalite_mensuelle": Decimal("2500"),
            },
            {
                "type_vehicule": "MOTO",
                "puissance_min": 6,
                "puissance_max": 15,
                "montant_base": Decimal("40000"),
                "penalite_mensuelle": Decimal("4000"),
            },
            {
                "type_vehicule": "MOTO",
                "puissance_min": 16,
                "puissance_max": 30,
                "montant_base": Decimal("60000"),
                "penalite_mensuelle": Decimal("6000"),
            },
            # Camions
            {
                "type_vehicule": "CAMION",
                "puissance_min": 1,
                "puissance_max": 10,
                "montant_base": Decimal("150000"),
                "penalite_mensuelle": Decimal("15000"),
            },
            {
                "type_vehicule": "CAMION",
                "puissance_min": 11,
                "puissance_max": 20,
                "montant_base": Decimal("250000"),
                "penalite_mensuelle": Decimal("25000"),
            },
            {
                "type_vehicule": "CAMION",
                "puissance_min": 21,
                "puissance_max": 50,
                "montant_base": Decimal("400000"),
                "penalite_mensuelle": Decimal("40000"),
            },
            # Autobus
            {
                "type_vehicule": "AUTOBUS",
                "puissance_min": 1,
                "puissance_max": 15,
                "montant_base": Decimal("200000"),
                "penalite_mensuelle": Decimal("20000"),
            },
            {
                "type_vehicule": "AUTOBUS",
                "puissance_min": 16,
                "puissance_max": 30,
                "montant_base": Decimal("350000"),
                "penalite_mensuelle": Decimal("35000"),
            },
            {
                "type_vehicule": "AUTOBUS",
                "puissance_min": 31,
                "puissance_max": 50,
                "montant_base": Decimal("500000"),
                "penalite_mensuelle": Decimal("50000"),
            },
            # Tracteur
            {
                "type_vehicule": "TRACTEUR",
                "puissance_min": 1,
                "puissance_max": 20,
                "montant_base": Decimal("100000"),
                "penalite_mensuelle": Decimal("10000"),
            },
            {
                "type_vehicule": "TRACTEUR",
                "puissance_min": 21,
                "puissance_max": 50,
                "montant_base": Decimal("180000"),
                "penalite_mensuelle": Decimal("18000"),
            },
        ]

        # Create tariff entries
        created_count = 0
        for tarif_data in tarifs_data:
            tarif, created = TarifVehicule.objects.get_or_create(
                grille_tarifaire=grille,
                type_vehicule=tarif_data["type_vehicule"],
                puissance_min=tarif_data["puissance_min"],
                puissance_max=tarif_data["puissance_max"],
                defaults={
                    "montant_base": tarif_data["montant_base"],
                    "penalite_mensuelle": tarif_data["penalite_mensuelle"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    f"Created tariff: {tarif.get_type_vehicule_display()} "
                    f"{tarif.puissance_min}-{tarif.puissance_max}CV = {tarif.montant_base}Ar"
                )

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} tariff entries"))
        else:
            self.stdout.write(self.style.WARNING("All tariff entries already exist"))

        self.stdout.write(self.style.SUCCESS("Sample data population completed!"))
