"""
Tests pour le service de contraventions.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.utils import timezone

from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contravention,
    ContraventionAuditLog,
    TypeInfraction,
)
from contraventions.services.contravention_service import ContraventionService
from core.models import UserProfile
from vehicles.models import Vehicule


class ContraventionServiceAnnulationTest(TestCase):
    """Tests pour la méthode annuler_contravention"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer la configuration système
        self.config = ConfigurationSysteme.get_config()

        # Créer un utilisateur agent
        self.agent_user = User.objects.create_user(username="agent001", password="testpass123", email="agent@test.com")

        # Créer le profil agent
        self.agent_profile = AgentControleurProfile.objects.create(
            user=self.agent_user,
            matricule="AG001",
            nom_complet="Agent Test",
            unite_affectation="Brigade Test",
            grade="Brigadier",
            autorite_type="POLICE_NATIONALE",
            juridiction="Antananarivo",
            telephone="0340000001",
        )

        # Créer un superviseur
        self.superviseur_user = User.objects.create_user(
            username="superviseur001", password="testpass123", email="superviseur@test.com"
        )
        superviseur_group = Group.objects.create(name="Superviseur Police")
        self.superviseur_user.groups.add(superviseur_group)

        # Créer un type d'infraction
        self.type_infraction = TypeInfraction.objects.create(
            nom="Excès de vitesse",
            article_code="L7.2-5",
            categorie="CIRCULATION",
            montant_min_ariary=Decimal("100000"),
            montant_max_ariary=Decimal("500000"),
        )

        # Créer un conducteur
        self.conducteur = Conducteur.objects.create(
            cin="123456789012", nom_complet="Conducteur Test", telephone="0340000002"
        )

        # Créer une contravention de test
        self.contravention = Contravention.objects.create(
            agent_controleur=self.agent_profile,
            type_infraction=self.type_infraction,
            conducteur=self.conducteur,
            date_heure_infraction=timezone.now(),
            lieu_infraction="RN1, Antananarivo",
            montant_amende_ariary=Decimal("200000"),
            statut="IMPAYEE",
            delai_paiement_jours=15,
        )

    def test_annulation_directe_par_agent_dans_delai(self):
        """Test: Agent peut annuler sa contravention dans les 24h"""
        success, message = ContraventionService.annuler_contravention(
            contravention=self.contravention, user=self.agent_user, motif="Erreur de saisie"
        )

        self.assertTrue(success)
        self.assertIn("annulée avec succès", message)

        # Vérifier que le statut a changé
        self.contravention.refresh_from_db()
        self.assertEqual(self.contravention.statut, "ANNULEE")

    def test_annulation_hors_delai_sans_superviseur_echoue(self):
        """Test: Agent ne peut pas annuler après 24h sans superviseur"""
        # Modifier la date de création pour simuler 25h écoulées
        self.contravention.created_at = timezone.now() - timedelta(hours=25)
        self.contravention.save()

        with self.assertRaises(PermissionDenied) as context:
            ContraventionService.annuler_contravention(
                contravention=self.contravention, user=self.agent_user, motif="Erreur de saisie"
            )

        self.assertIn("délai d'annulation directe", str(context.exception))

    def test_annulation_par_superviseur_apres_delai(self):
        """Test: Superviseur peut annuler après 24h"""
        # Modifier la date de création pour simuler 25h écoulées
        self.contravention.created_at = timezone.now() - timedelta(hours=25)
        self.contravention.save()

        success, message = ContraventionService.annuler_contravention(
            contravention=self.contravention, user=self.superviseur_user, motif="Erreur administrative"
        )

        self.assertTrue(success)
        self.contravention.refresh_from_db()
        self.assertEqual(self.contravention.statut, "ANNULEE")

    def test_annulation_contravention_deja_annulee_echoue(self):
        """Test: Ne peut pas annuler une contravention déjà annulée"""
        self.contravention.statut = "ANNULEE"
        self.contravention.save()

        with self.assertRaises(ValidationError) as context:
            ContraventionService.annuler_contravention(
                contravention=self.contravention, user=self.agent_user, motif="Test"
            )

        self.assertIn("déjà annulée", str(context.exception))

    def test_annulation_contravention_payee_marque_paiement_annule(self):
        """Test: Annulation d'une contravention payée marque le paiement comme annulé"""
        from django.contrib.auth.models import User

        from payments.models import PaiementTaxe
        from vehicles.models import VehicleType, Vehicule

        # Créer un utilisateur pour le propriétaire du véhicule
        vehicle_owner = User.objects.create_user(username="vehicle_owner", password="testpass123")

        # Créer un type de véhicule
        vehicle_type, created = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Véhicule particulier"}
        )

        # Créer un véhicule pour le paiement
        vehicule = Vehicule.objects.create(
            plaque_immatriculation="1234TAA",
            proprietaire=vehicle_owner,
            marque="Toyota",
            modele="Corolla",
            couleur="Blanc",
            vin="TESTCHASSIS123",
            puissance_fiscale_cv=13,
            cylindree_cm3=1800,
            source_energie="Essence",
            date_premiere_circulation="2020-01-01",
            categorie_vehicule="Personnel",
            type_vehicule=vehicle_type,
        )

        # Marquer la contravention comme payée
        self.contravention.statut = "PAYEE"
        self.contravention.date_paiement = timezone.now()
        self.contravention.save()

        # Créer un paiement associé
        paiement = PaiementTaxe.objects.create(
            type_paiement="AMENDE_CONTRAVENTION",
            contravention=self.contravention,
            vehicule_plaque=vehicule,
            annee_fiscale=2025,
            montant_du_ariary=Decimal("200000"),
            montant_paye_ariary=Decimal("200000"),
            statut="PAYE",
            methode_paiement="mvola",
        )

        success, message = ContraventionService.annuler_contravention(
            contravention=self.contravention, user=self.superviseur_user, motif="Erreur judiciaire"
        )

        self.assertTrue(success)
        self.assertIn("remboursement", message)

        # Vérifier que le paiement est marqué comme annulé
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut, "ANNULE")
        self.assertIn("annulation", paiement.details_paiement)


class ContraventionServiceConsultationTest(TestCase):
    """Tests pour la méthode get_contraventions_impayees"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un agent
        agent_user = User.objects.create_user(username="agent002", password="test")
        self.agent_profile = AgentControleurProfile.objects.create(
            user=agent_user,
            matricule="AG002",
            nom_complet="Agent Test 2",
            unite_affectation="Brigade Test",
            grade="Brigadier",
            autorite_type="POLICE_NATIONALE",
            juridiction="Antananarivo",
            telephone="0340000003",
        )

        # Créer un type d'infraction
        self.type_infraction = TypeInfraction.objects.create(
            nom="Stationnement interdit",
            article_code="L7.3-2",
            categorie="CIRCULATION",
            montant_min_ariary=Decimal("50000"),
            montant_max_ariary=Decimal("100000"),
        )

        # Créer deux conducteurs
        self.conducteur1 = Conducteur.objects.create(cin="111111111111", nom_complet="Conducteur 1")
        self.conducteur2 = Conducteur.objects.create(cin="222222222222", nom_complet="Conducteur 2")

        # Créer des contraventions
        Contravention.objects.create(
            agent_controleur=self.agent_profile,
            type_infraction=self.type_infraction,
            conducteur=self.conducteur1,
            date_heure_infraction=timezone.now(),
            lieu_infraction="Test 1",
            montant_amende_ariary=Decimal("50000"),
            statut="IMPAYEE",
        )

        Contravention.objects.create(
            agent_controleur=self.agent_profile,
            type_infraction=self.type_infraction,
            conducteur=self.conducteur1,
            date_heure_infraction=timezone.now(),
            lieu_infraction="Test 2",
            montant_amende_ariary=Decimal("50000"),
            statut="PAYEE",
        )

        Contravention.objects.create(
            agent_controleur=self.agent_profile,
            type_infraction=self.type_infraction,
            conducteur=self.conducteur2,
            date_heure_infraction=timezone.now(),
            lieu_infraction="Test 3",
            montant_amende_ariary=Decimal("50000"),
            statut="IMPAYEE",
        )

    def test_get_contraventions_impayees_par_conducteur(self):
        """Test: Récupération des contraventions impayées d'un conducteur"""
        contraventions = ContraventionService.get_contraventions_impayees(conducteur=self.conducteur1)

        # Le conducteur1 a 2 contraventions dont 1 impayée
        self.assertEqual(contraventions.count(), 1)
        self.assertEqual(contraventions.first().statut, "IMPAYEE")

    def test_get_contraventions_impayees_sans_parametre_echoue(self):
        """Test: Erreur si aucun paramètre n'est fourni"""
        with self.assertRaises(ValidationError) as context:
            ContraventionService.get_contraventions_impayees()

        self.assertIn("Au moins un paramètre", str(context.exception))

    def test_get_contraventions_impayees_inclut_contestees(self):
        """Test: Les contraventions contestées sont incluses"""
        # Créer une contravention contestée
        contravention_contestee = Contravention.objects.create(
            agent_controleur=self.agent_profile,
            type_infraction=self.type_infraction,
            conducteur=self.conducteur1,
            date_heure_infraction=timezone.now(),
            lieu_infraction="Test Contestée",
            montant_amende_ariary=Decimal("50000"),
            statut="CONTESTEE",
        )

        contraventions = ContraventionService.get_contraventions_impayees(conducteur=self.conducteur1)

        # Doit inclure l'impayée et la contestée
        self.assertEqual(contraventions.count(), 2)
        statuts = [c.statut for c in contraventions]
        self.assertIn("IMPAYEE", statuts)
        self.assertIn("CONTESTEE", statuts)
