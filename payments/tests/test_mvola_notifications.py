"""
Tests for MVola notification integration

This module tests that notifications are created correctly for MVola payment events:
- Payment initiated
- Payment confirmed
- Payment failed
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from notifications.models import Notification
from notifications.services import NotificationService
from payments.models import PaiementTaxe
from vehicles.models import VehicleType, Vehicule


class MvolaNotificationIntegrationTests(TestCase):
    """Test MVola notification integration"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Get or create vehicle type
        self.vehicle_type, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Voiture particulière", "est_actif": True, "ordre_affichage": 1}
        )

        # Create test vehicle
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234AB01",
            proprietaire=self.user,
            type_vehicule=self.vehicle_type,
            marque="Toyota",
            modele="Corolla",
            annee_fabrication=2020,
            puissance_fiscale=5,
            categorie_vehicule="particulier",
        )

    def test_payment_initiated_notification_french(self):
        """Test that payment initiated notification is created in French"""
        # Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="EN_ATTENTE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="pending",
        )

        # Create notification
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Paiement MVola initié",
            contenu=f"Votre paiement MVola pour le véhicule {self.vehicle.plaque_immatriculation} a été initié.",
            langue="fr",
            metadata={
                "event": "mvola_payment_initiated",
                "payment_id": str(payment.id),
                "server_correlation_id": payment.mvola_server_correlation_id,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.type_notification, "system")
        self.assertEqual(notification.langue, "fr")
        self.assertIn("MVola", notification.titre)
        self.assertIn("initié", notification.titre)
        self.assertFalse(notification.est_lue)
        self.assertEqual(notification.metadata["event"], "mvola_payment_initiated")

    def test_payment_initiated_notification_malagasy(self):
        """Test that payment initiated notification is created in Malagasy"""
        # Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="EN_ATTENTE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="pending",
        )

        # Create notification in Malagasy
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Fandoavam-bola MVola natomboka",
            contenu=f"Ny fandoavam-bola MVola ho an'ny fiara {self.vehicle.plaque_immatriculation} dia natomboka.",
            langue="mg",
            metadata={
                "event": "mvola_payment_initiated",
                "payment_id": str(payment.id),
                "server_correlation_id": payment.mvola_server_correlation_id,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.langue, "mg")
        self.assertIn("MVola", notification.titre)
        self.assertIn("natomboka", notification.titre)

    def test_payment_confirmed_notification_french(self):
        """Test that payment confirmation notification is created in French"""
        # Create completed payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("100000.00"),
            statut="PAYE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_transaction_reference="TXN123456",
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_gateway_fees=Decimal("500.00"),
            mvola_status="completed",
            date_paiement=timezone.now(),
        )

        # Create notification
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Paiement MVola confirmé",
            contenu=f"Votre paiement MVola pour le véhicule {self.vehicle.plaque_immatriculation} a été confirmé.",
            langue="fr",
            metadata={
                "event": "mvola_payment_completed",
                "payment_id": str(payment.id),
                "amount": str(payment.montant_paye_ariary),
                "server_correlation_id": payment.mvola_server_correlation_id,
                "transaction_reference": payment.mvola_transaction_reference,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.langue, "fr")
        self.assertIn("confirmé", notification.titre)
        self.assertEqual(notification.metadata["event"], "mvola_payment_completed")
        self.assertIn("transaction_reference", notification.metadata)

    def test_payment_confirmed_notification_malagasy(self):
        """Test that payment confirmation notification is created in Malagasy"""
        # Create completed payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("100000.00"),
            statut="PAYE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_transaction_reference="TXN123456",
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="completed",
            date_paiement=timezone.now(),
        )

        # Create notification in Malagasy
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Fandoavam-bola MVola vita soa aman-tsara",
            contenu=f"Ny fandoavam-bola MVola ho an'ny fiara {self.vehicle.plaque_immatriculation} dia vita.",
            langue="mg",
            metadata={
                "event": "mvola_payment_completed",
                "payment_id": str(payment.id),
                "amount": str(payment.montant_paye_ariary),
                "server_correlation_id": payment.mvola_server_correlation_id,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.langue, "mg")
        self.assertIn("vita", notification.titre)

    def test_payment_failed_notification_french(self):
        """Test that payment failed notification is created in French"""
        # Create failed payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="ANNULE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="failed",
        )

        # Create notification
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Échec du paiement MVola",
            contenu=f"Le paiement MVola pour le véhicule {self.vehicle.plaque_immatriculation} a échoué.",
            langue="fr",
            metadata={
                "event": "mvola_payment_failed",
                "payment_id": str(payment.id),
                "server_correlation_id": payment.mvola_server_correlation_id,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.langue, "fr")
        self.assertIn("Échec", notification.titre)
        self.assertEqual(notification.metadata["event"], "mvola_payment_failed")

    def test_payment_failed_notification_malagasy(self):
        """Test that payment failed notification is created in Malagasy"""
        # Create failed payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="ANNULE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="failed",
        )

        # Create notification in Malagasy
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Tsy nahomby ny fandoavam-bola MVola",
            contenu=f"Tsy nahomby ny fandoavam-bola MVola ho an'ny fiara {self.vehicle.plaque_immatriculation}.",
            langue="mg",
            metadata={
                "event": "mvola_payment_failed",
                "payment_id": str(payment.id),
                "server_correlation_id": payment.mvola_server_correlation_id,
            },
        )

        # Verify notification was created
        self.assertIsNotNone(notification)
        self.assertEqual(notification.langue, "mg")
        self.assertIn("nahomby", notification.titre)

    def test_notification_includes_transaction_reference(self):
        """Test that notifications include MVola transaction reference"""
        # Create payment with transaction reference
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("100000.00"),
            statut="PAYE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id="SERVER123",
            mvola_transaction_reference="TXN789",
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="completed",
            date_paiement=timezone.now(),
        )

        # Create notification with transaction reference
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Paiement confirmé",
            contenu=f"Référence: {payment.mvola_transaction_reference}",
            langue="fr",
            metadata={
                "event": "mvola_payment_completed",
                "payment_id": str(payment.id),
                "server_correlation_id": payment.mvola_server_correlation_id,
                "transaction_reference": payment.mvola_transaction_reference,
            },
        )

        # Verify transaction reference is included
        self.assertIn("TXN789", notification.contenu)
        self.assertEqual(notification.metadata["transaction_reference"], "TXN789")
        self.assertEqual(notification.metadata["server_correlation_id"], "SERVER123")

    def test_notification_metadata_structure(self):
        """Test that notification metadata has correct structure"""
        # Create payment
        payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="EN_ATTENTE",
            methode_paiement="mvola",
            mvola_x_correlation_id=str(uuid.uuid4()),
            mvola_server_correlation_id=str(uuid.uuid4()),
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="pending",
        )

        # Create notification
        notification = NotificationService.create_notification(
            user=self.user,
            type_notification="system",
            titre="Test notification",
            contenu="Test content",
            langue="fr",
            metadata={
                "event": "mvola_payment_initiated",
                "payment_id": str(payment.id),
                "base_amount": "100000.00",
                "platform_fee": "3000.00",
                "total_amount": "103000.00",
                "server_correlation_id": payment.mvola_server_correlation_id,
                "vehicle_plate": self.vehicle.plaque_immatriculation,
                "tax_year": 2024,
                "customer_msisdn": "0340000000",
            },
        )

        # Verify metadata structure
        self.assertIn("event", notification.metadata)
        self.assertIn("payment_id", notification.metadata)
        self.assertIn("server_correlation_id", notification.metadata)
        self.assertIn("vehicle_plate", notification.metadata)
        self.assertIn("tax_year", notification.metadata)
        self.assertEqual(notification.metadata["event"], "mvola_payment_initiated")
