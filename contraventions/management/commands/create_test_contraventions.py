import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from contraventions.models import (
    Conducteur,
    ConfigurationSysteme,
    Contestation,
    Contravention,
    DossierFourriere,
    TypeInfraction,
)
from core.models import User
from vehicles.models import Vehicule


class Command(BaseCommand):
    help = "Crée des données de test pour le système de contraventions"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50, help="Nombre de contraventions à créer (par défaut: 50)")
        parser.add_argument("--agents", type=int, default=5, help="Nombre d'agents à créer (par défaut: 5)")
        parser.add_argument(
            "--conducteurs", type=int, default=20, help="Nombre de conducteurs à créer (par défaut: 20)"
        )
        parser.add_argument("--force", action="store_true", help="Forcer la création même si des données existent")

    def handle(self, *args, **options):
        count = options["count"]
        agents_count = options["agents"]
        conducteurs_count = options["conducteurs"]
        force = options["force"]

        if not force and Contravention.objects.exists():
            self.stdout.write(self.style.WARNING("Des contraventions existent déjà. Utilisez --force pour écraser."))
            return

        self.stdout.write("Création des données de test...")

        with transaction.atomic():
            # Create configuration if it doesn't exist
            self.create_configuration()

            # Create agents
            agents = self.create_agents(agents_count)

            # Create conducteurs
            conducteurs = self.create_conducteurs(conducteurs_count)

            # Create contraventions
            self.create_contraventions(count, agents, conducteurs)

            # Create some fourrière cases
            self.create_fourriere_cases()

            # Create some contestations
            self.create_contestations()

        self.stdout.write(self.style.SUCCESS(f"Succès! {count} contraventions créées."))

    def create_configuration(self):
        """Create system configuration if it doesn't exist"""
        if not ConfigurationSysteme.objects.exists():
            ConfigurationSysteme.objects.create(
                nom_service="Service des Contraventions de Madagascar",
                adresse_service="Antananarivo, Madagascar",
                numero_contact="+261 20 22 123 45",
                email_contact="contraventions@gov.mg",
                delai_paiement_jours=30,
                taux_majoration_recidive=50.0,
                mvola_enabled=True,
                stripe_enabled=True,
                cash_enabled=True,
                qr_code_enabled=True,
                audit_enabled=True,
            )
            self.stdout.write("Configuration système créée")

    def create_agents(self, count):
        """Create test agents"""
        agents = []

        for i in range(count):
            user = User.objects.create_user(
                username=f"agent{i+1}",
                email=f"agent{i+1}@contraventions.mg",
                first_name=f"Agent",
                last_name=f"{i+1}",
                password="password123",
                user_type="agent_government",
            )

            profile = user.agent_profile
            profile.matricule = f"AGT{1000 + i}"
            profile.grade = random.choice(["Agent", "Chef Agent", "Superviseur"])
            profile.service = "Service des Contraventions"
            profile.zone_affectation = random.choice(
                ["Antananarivo", "Toamasina", "Mahajanga", "Toliara", "Antsiranana"]
            )
            profile.telephone = f"+261 32 {random.randint(1000000, 9999999):07d}"
            profile.est_actif = True
            profile.save()

            agents.append(user)

        self.stdout.write(f"{count} agents créés")
        return agents

    def create_conducteurs(self, count):
        """Create test conducteurs"""
        conducteurs = []

        noms = ["Rakoto", "Rabe", "Randria", "Rasoa", "Rafara", "Rakotoniaina", "Rabeanto", "Randriamanana"]
        prenoms = ["Jean", "Marie", "Pierre", "Claire", "Marc", "Sophie", "André", "Lalao"]

        for i in range(count):
            conducteur = Conducteur.objects.create(
                nom=random.choice(noms),
                prenom=random.choice(prenoms),
                date_naissance=timezone.now() - timedelta(days=random.randint(6570, 18250)),  # 18-50 years
                adresse=f'{random.randint(1, 999)} Rue {random.choice(["de l\'Indépendance", "du Commerce", "de l\'Église", "du Marché"])}',
                telephone=f"+261 34 {random.randint(1000000, 9999999):07d}",
                email=f"conducteur{i+1}@email.mg",
                numero_permis=f"C{random.randint(100000, 999999)}MG",
                date_delivrance_permis=timezone.now() - timedelta(days=random.randint(365, 3650)),
                lieu_delivrance_permis=random.choice(["Antananarivo", "Toamasina", "Mahajanga"]),
                categorie_permis=random.choice(["A", "B", "C", "D"]),
                est_valide=True,
            )
            conducteurs.append(conducteur)

        self.stdout.write(f"{count} conducteurs créés")
        return conducteurs

    def create_contraventions(self, count, agents, conducteurs):
        """Create test contraventions"""
        types_infraction = list(TypeInfraction.objects.all())
        if not types_infraction:
            self.stdout.write(self.style.WARNING("Aucun type d'infraction trouvé. Création de types par défaut..."))
            types_infraction = self.create_default_infraction_types()

        # Get some vehicles
        vehicles = list(Vehicule.objects.all()[:50])  # Limit to avoid too many queries

        for i in range(count):
            agent = random.choice(agents)
            type_infraction = random.choice(types_infraction)

            # Create contravention
            contravention = Contravention.objects.create(
                type_infraction=type_infraction,
                lieu_infraction=random.choice(
                    [
                        "Route Nationale 1, PK 15",
                        "Avenue de l'Indépendance, Antananarivo",
                        "Rue du Commerce, Toamasina",
                        "Boulevard de la République, Mahajanga",
                        "Route de l'Aéroport, Toliara",
                    ]
                ),
                date_infraction=timezone.now() - timedelta(days=random.randint(0, 90)),
                description=f"Infraction de type {type_infraction.nom} constatée",
                agent=agent,
                statut=random.choice(["active", "paid", "contested", "cancelled"]),
                montant_total_ariary=type_infraction.montant_min_ariary,
            )

            # Add vehicle (80% chance)
            if vehicles and random.random() < 0.8:
                contravention.vehicule = random.choice(vehicles)

            # Add driver (70% chance)
            if conducteurs and random.random() < 0.7:
                contravention.conducteur = random.choice(conducteurs)

            # Set status-specific dates
            if contravention.statut == "paid":
                contravention.date_paiement = contravention.date_infraction + timedelta(days=random.randint(1, 30))
            elif contravention.statut == "contested":
                contravention.date_contestation = contravention.date_infraction + timedelta(days=random.randint(1, 15))
            elif contravention.statut == "cancelled":
                contravention.date_annulation = contravention.date_infraction + timedelta(days=random.randint(1, 10))
                contravention.motif_annulation = random.choice(
                    [
                        "Erreur de procédure",
                        "Preuve de paiement fournie",
                        "Infraction non conforme",
                        "Demande de l'autorité supérieure",
                    ]
                )

            contravention.save()

        self.stdout.write(f"{count} contraventions créées")

    def create_fourriere_cases(self):
        """Create some fourrière cases"""
        contraventions = Contravention.objects.filter(type_infraction__fourriere_obligatoire=True, statut="active")[:10]

        for contravention in contraventions:
            if random.random() < 0.7:  # 70% chance to create fourrière
                DossierFourriere.objects.create(
                    contravention=contravention,
                    numero_dossier=f"FOUR{contravention.id:06d}",
                    date_mise_fourriere=contravention.date_infraction + timedelta(hours=random.randint(1, 24)),
                    lieu_fourriere=random.choice(
                        ["Fourrière Municipale Antananarivo", "Fourrière de Toamasina", "Fourrière de Mahajanga"]
                    ),
                    responsable_fourriere=random.choice(["M. Rakoto", "Mme Rabe", "M. Randria"]),
                    contact_responsable=f"+261 32 {random.randint(1000000, 9999999):07d}",
                    frais_fourriere_par_jour=Decimal("5000"),
                    frais_remorquage=Decimal("25000"),
                    duree_maximale_jours=30,
                    motif_fourriere="Infraction avec fourrière obligatoire",
                    observations="Véhicule en attente de paiement de l'amende",
                    statut=random.choice(["en_fourriere", "libere"]),
                )

        self.stdout.write(f"{len(contraventions)} dossiers de fourrière créés")

    def create_contestations(self):
        """Create some contestations"""
        contraventions = Contravention.objects.filter(statut="contested")[:5]

        for contravention in contraventions:
            Contestation.objects.create(
                contravention=contravention,
                nom=random.choice(["Jean Rakoto", "Marie Rabe", "Pierre Randria"]),
                email=f"contestation{contravention.id}@email.mg",
                telephone=f"+261 34 {random.randint(1000000, 9999999):07d}",
                adresse=f"{random.randint(1, 999)} Rue de la Contestation",
                motif=f'Je conteste cette contravention car {random.choice(["je n\'étais pas au volant", "l\'infraction n\'est pas justifiée", "il y a une erreur dans les informations"])}',
                type_contestation=random.choice(["erreur_identite", "erreur_fait", "erreur_procedure"]),
                informations_complementaires="Veuillez examiner mon dossier attentivement",
                statut=random.choice(["en_attente", "en_cours", "acceptee", "rejetee"]),
            )

        self.stdout.write(f"{len(contraventions)} contestations créées")

    def create_default_infraction_types(self):
        """Create default infraction types if none exist"""
        infractions_data = [
            {
                "article_code": "R.121-1",
                "nom": "Excès de vitesse",
                "categorie": "vitesse",
                "description": "Dépassement de la vitesse autorisée",
                "montant_min_ariary": 50000,
                "montant_max_ariary": 200000,
                "montant_variable": True,
                "fourriere_obligatoire": False,
            },
            {
                "article_code": "R.412-6",
                "nom": "Stationnement gênant",
                "categorie": "stationnement",
                "description": "Stationnement en double file ou gênant la circulation",
                "montant_min_ariary": 25000,
                "montant_max_ariary": 50000,
                "montant_variable": False,
                "fourriere_obligatoire": True,
            },
            {
                "article_code": "R.233-1",
                "nom": "Feu rouge grillé",
                "categorie": "signalisation",
                "description": "Non-respect d'un feu de signalisation",
                "montant_min_ariary": 75000,
                "montant_max_ariary": 150000,
                "montant_variable": False,
                "fourriere_obligatoire": False,
            },
            {
                "article_code": "R.322-2",
                "nom": "Non-port du casque",
                "categorie": "sécurité",
                "description": "Non-port du casque pour les deux-roues motorisés",
                "montant_min_ariary": 20000,
                "montant_max_ariary": 40000,
                "montant_variable": False,
                "fourriere_obligatoire": False,
            },
            {
                "article_code": "R.511-1",
                "nom": "Permis de conduire non valide",
                "categorie": "documents",
                "description": "Conduite sans permis valide",
                "montant_min_ariary": 100000,
                "montant_max_ariary": 300000,
                "montant_variable": True,
                "fourriere_obligatoire": True,
            },
        ]

        types_infraction = []
        for data in infractions_data:
            type_infraction = TypeInfraction.objects.create(**data)
            types_infraction.append(type_infraction)

        self.stdout.write(f"{len(types_infraction)} types d'infraction créés")
        return types_infraction
