"""
Management command to create test data for the Tax Collector system
Creates test users, vehicles, payments, QR codes, and verification agents
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from administration.models import AgentVerification
from core.models import UserProfile
from payments.models import PaiementTaxe, QRCode
from vehicles.models import GrilleTarifaire, VehicleType, Vehicule


class Command(BaseCommand):
    help = "Create test data for the Tax Collector system"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=3, help="Number of test users to create")
        parser.add_argument("--vehicles-per-user", type=int, default=2, help="Number of vehicles per user")
        parser.add_argument("--create-agent", action="store_true", help="Create a verification agent")
        parser.add_argument("--clean", action="store_true", help="Clean existing test data before creating new")

    def handle(self, *args, **options):
        num_users = options["users"]
        vehicles_per_user = options["vehicles_per_user"]
        create_agent = options["create_agent"]
        clean = options["clean"]

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("Creating Test Data for Tax Collector System"))
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Clean existing test data if requested
        if clean:
            self.clean_test_data()

        # Ensure vehicle types exist
        self.create_vehicle_types()

        # Create test users with vehicles and payments
        users_created = []
        for i in range(1, num_users + 1):
            user = self.create_test_user(i)
            users_created.append(user)

            # Create vehicles for this user
            for j in range(1, vehicles_per_user + 1):
                vehicle = self.create_test_vehicle(user, j)

                # Create payment and QR code
                payment = self.create_test_payment(vehicle)
                qr_code = self.create_qr_code(payment)

                qr_info = f"QR: {qr_code.token[:8]}..." if qr_code else "QR: N/A (unpaid)"
                self.stdout.write(
                    f"  ✓ Vehicle: {vehicle.plaque_immatriculation} | "
                    f"Payment: {payment.montant_du_ariary} Ar ({payment.get_statut_display()}) | "
                    f"{qr_info}"
                )

        # Create verification agent if requested
        if create_agent:
            agent = self.create_verification_agent()

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("✓ Test Data Created Successfully!"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("📊 Summary:")
        self.stdout.write(f"  • Users created: {len(users_created)}")
        self.stdout.write(f"  • Vehicles per user: {vehicles_per_user}")
        self.stdout.write(f"  • Total vehicles: {len(users_created) * vehicles_per_user}")
        self.stdout.write(f"  • Total payments: {len(users_created) * vehicles_per_user}")
        self.stdout.write(f"  • Total QR codes: {len(users_created) * vehicles_per_user}")

        if create_agent:
            self.stdout.write(f"  • Verification agent: Yes")

        self.stdout.write("")
        self.stdout.write("👥 Test Users:")
        for user in users_created:
            self.stdout.write(f"  • Username: {user.username} | Password: test123 | Email: {user.email}")

        if create_agent:
            self.stdout.write("")
            self.stdout.write("🔍 Verification Agent:")
            self.stdout.write(f"  • Username: {agent.user.username} | Password: agent123")
            self.stdout.write(f"  • Badge: {agent.numero_badge}")
            self.stdout.write(f"  • Zone: {agent.zone_affectation}")

        self.stdout.write("")
        self.stdout.write("🔗 Quick Links:")
        self.stdout.write("  • Admin: http://127.0.0.1:8000/admin/")
        self.stdout.write("  • Vehicles: http://127.0.0.1:8000/vehicles/")
        self.stdout.write("  • Payments: http://127.0.0.1:8000/payments/")
        self.stdout.write("  • QR Codes: http://127.0.0.1:8000/admin/payments/qrcode/")
        self.stdout.write("")

        # Show sample QR codes
        sample_qr = QRCode.objects.filter(est_actif=True).first()
        if sample_qr:
            self.stdout.write("📱 Sample QR Code to Test:")
            self.stdout.write(f"  • Token: {sample_qr.token}")
            self.stdout.write(f"  • Vehicle: {sample_qr.vehicule_plaque.plaque_immatriculation}")
            self.stdout.write(f"  • Valid until: {sample_qr.date_expiration.strftime('%d/%m/%Y')}")
            self.stdout.write(f"  • Scan URL: http://127.0.0.1:8000/payments/qr/verify/{sample_qr.token}/")

        self.stdout.write("")

    def clean_test_data(self):
        """Clean existing test data"""
        self.stdout.write("🧹 Cleaning existing test data...")

        # Delete test users and related data
        test_users = User.objects.filter(username__startswith="testuser")
        agent_users = User.objects.filter(username__startswith="agent")

        count = test_users.count() + agent_users.count()
        test_users.delete()
        agent_users.delete()

        self.stdout.write(f"  ✓ Cleaned {count} test users and related data")
        self.stdout.write("")

    def create_vehicle_types(self):
        """Ensure vehicle types exist"""
        vehicle_types = [
            {"nom": "Voiture", "description": "Véhicule de tourisme"},
            {"nom": "Moto", "description": "Motocyclette"},
            {"nom": "Camion", "description": "Véhicule utilitaire"},
            {"nom": "Bus", "description": "Transport en commun"},
        ]

        for i, vt_data in enumerate(vehicle_types, 1):
            VehicleType.objects.get_or_create(
                nom=vt_data["nom"],
                defaults={"description": vt_data["description"], "est_actif": True, "ordre_affichage": i},
            )

    def create_test_user(self, index):
        """Create a test user with profile"""
        username = f"testuser{index}"
        email = f"testuser{index}@example.com"

        # Create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": f"Test", "last_name": f"User {index}", "is_active": True},
        )

        if created:
            user.set_password("test123")
            user.save()

        # Create or update profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": "citoyen",
                "telephone": f"+261{32 + index}{random.randint(1000000, 9999999)}",
                "adresse": f"{index} Rue de Test, Antananarivo",
                "est_verifie": True,
            },
        )

        if created:
            self.stdout.write(f"✓ Created user: {username} (password: test123)")

        return user

    def create_test_vehicle(self, user, index):
        """Create a test vehicle for a user"""
        vehicle_types = list(VehicleType.objects.filter(est_actif=True))
        if not vehicle_types:
            self.stdout.write(self.style.ERROR("No vehicle types found!"))
            return None

        vehicle_type = random.choice(vehicle_types)

        # Generate unique plate number (no spaces allowed by validation)
        plate_number = f'{random.randint(1000, 9999)}T{"AB" if index % 2 == 0 else "CD"}'

        # Random vehicle data
        brands = ["Toyota", "Renault", "Peugeot", "Honda", "Nissan", "Hyundai"]
        models_list = ["Corolla", "Civic", "Megane", "308", "Accent", "Sunny"]
        colors = ["Blanc", "Noir", "Gris", "Rouge", "Bleu", "Argent"]
        sources_energie = ["Essence", "Diesel", "Electrique", "Hybride"]

        # Random vehicle specs for tax calculation
        # Use realistic cylindree values
        cylindree_options = [1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500, 3000]
        cylindree = random.choice(cylindree_options)
        annee_fabrication = random.randint(2010, 2023)
        
        marque = random.choice(brands)
        modele = random.choice(models_list)
        couleur = random.choice(colors)
        vin = f"VIN{random.randint(100000, 999999)}"

        # Specifications techniques
        specs = {
            "marque": marque,
            "modele": modele,
            "annee_fabrication": annee_fabrication,
            "couleur": couleur,
            "numero_chassis": vin,
            "numero_moteur": f"ENG{random.randint(100000, 999999)}",
        }

        # Calculate puissance fiscale from cylindree
        # Formula: CV = (cylindree / 100) + 1 (minimum)
        puissance_cv = int((cylindree / 100) + 1)

        # Create vehicle
        vehicle, created = Vehicule.objects.get_or_create(
            plaque_immatriculation=plate_number,
            defaults={
                "proprietaire": user,
                "type_vehicule": vehicle_type,
                "marque": marque,
                "modele": modele,
                "couleur": couleur,
                "vin": vin,
                "puissance_fiscale_cv": puissance_cv,
                "cylindree_cm3": cylindree,
                "source_energie": random.choice(sources_energie),
                "date_premiere_circulation": date(annee_fabrication, random.randint(1, 12), random.randint(1, 28)),
                "categorie_vehicule": "Personnel",
                "specifications_techniques": specs,
                "est_actif": True,
            },
        )

        return vehicle

    def create_test_payment(self, vehicle):
        """Create a test payment for a vehicle"""
        # Calculate tax using the official grid
        current_year = timezone.now().year

        # Find applicable tax rate
        age = vehicle.get_age_annees()
        tax_grid = (
            GrilleTarifaire.objects.filter(
                annee_fiscale=current_year,
                est_active=True,
                source_energie=vehicle.source_energie,
                puissance_min_cv__lte=vehicle.puissance_fiscale_cv,
            )
            .filter(
                models.Q(puissance_max_cv__gte=vehicle.puissance_fiscale_cv) | models.Q(puissance_max_cv__isnull=True)
            )
            .filter(age_min_annees__lte=age)
            .filter(models.Q(age_max_annees__gte=age) | models.Q(age_max_annees__isnull=True))
            .first()
        )

        if tax_grid:
            montant = tax_grid.montant_ariary
        else:
            # Default amount if no grid found
            montant = Decimal("50000")

        # Random payment status
        statuses = ["PAYE", "PAYE", "PAYE", "EN_ATTENTE"]  # More paid than pending
        statut = random.choice(statuses)

        # Payment date
        if statut == "PAYE":
            date_paiement = timezone.now() - timedelta(days=random.randint(1, 90))
            date_expiration = date_paiement.date() + timedelta(days=365)
        else:
            date_paiement = None
            date_expiration = timezone.now().date() + timedelta(days=30)

        # Generate unique transaction ID
        transaction_id = f"TEST{random.randint(100000, 999999)}{current_year}"

        payment, created = PaiementTaxe.objects.get_or_create(
            vehicule_plaque=vehicle,
            annee_fiscale=current_year,
            defaults={
                "montant_paye_ariary": montant if statut == "PAYE" else Decimal("0"),
                "montant_du_ariary": montant,
                "statut": statut,
                "methode_paiement": random.choice(["carte_bancaire", "mvola", "orange_money", "airtel_money"]),
                "date_paiement": date_paiement,
                "transaction_id": transaction_id,
                "details_paiement": {
                    "test_data": True,
                    "created_by": "create_test_data_command",
                    "note": "Paiement de test créé automatiquement",
                },
            },
        )

        return payment

    def create_qr_code(self, payment):
        """Create a QR code for a payment"""
        # Only create QR code for paid payments
        if payment.statut != "PAYE":
            return None

        # Check if QR code already exists
        existing_qr = QRCode.objects.filter(
            vehicule_plaque=payment.vehicule_plaque, annee_fiscale=payment.annee_fiscale
        ).first()
        if existing_qr:
            return existing_qr

        # QR code expiration (1 year from payment)
        if payment.date_paiement:
            date_expiration = payment.date_paiement + timedelta(days=365)
        else:
            date_expiration = timezone.now() + timedelta(days=365)

        qr_code = QRCode.objects.create(
            vehicule_plaque=payment.vehicule_plaque,
            annee_fiscale=payment.annee_fiscale,
            date_expiration=date_expiration,
            est_actif=True,
        )

        return qr_code

    def create_verification_agent(self):
        """Create a verification agent"""
        username = "agent1"

        # Create agent user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": "agent1@taxcollector.mg",
                "first_name": "Agent",
                "last_name": "Verification",
                "is_staff": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password("agent123")
            user.save()
            self.stdout.write(f"✓ Created agent user: {username} (password: agent123)")

        # Create agent profile
        agent, created = AgentVerification.objects.get_or_create(
            user=user,
            defaults={
                "numero_badge": f"AGENT{random.randint(1000, 9999)}",
                "zone_affectation": "Antananarivo Centre",
                "est_actif": True,
            },
        )

        if created:
            self.stdout.write(f"✓ Created verification agent: {agent.numero_badge}")

        return agent
