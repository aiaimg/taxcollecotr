"""
Tests for MVola callback endpoint
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from notifications.models import Notification
from payments.models import PaiementTaxe, QRCode
from vehicles.models import VehicleType, Vehicule


class MvolaCallbackViewTestCase(TestCase):
    """Test MVola callback endpoint"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Create or get vehicle type
        self.vehicle_type, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Voiture particulière"}
        )

        # Create test vehicle
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234AB01",
            proprietaire=self.user,
            type_vehicule=self.vehicle_type,
            categorie_vehicule="PARTICULIER",
            puissance_fiscale=5,
            nombre_places=5,
        )

        # Create test payment
        self.payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            montant_du_ariary=Decimal("100000.00"),
            montant_paye_ariary=Decimal("0.00"),
            statut="EN_ATTENTE",
            methode_paiement="mvola",
            mvola_x_correlation_id="test-x-correlation-id",
            mvola_server_correlation_id="test-server-correlation-id",
            mvola_customer_msisdn="0340000000",
            mvola_platform_fee=Decimal("3000.00"),
            mvola_status="pending",
        )

        # Create API client
        self.client = APIClient()

    def test_callback_successful_payment(self):
        """Test callback with successful payment"""
        callback_data = {
            "serverCorrelationId": "test-server-correlation-id",
            "transactionStatus": "completed",
            "transactionReference": "MVL123456789",
            "fees": [{"feeAmount": "500"}],
        }

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "received")

        # Refresh payment from database
        self.payment.refresh_from_db()

        # Verify payment status updated
        self.assertEqual(self.payment.statut, "PAYE")
        self.assertEqual(self.payment.mvola_status, "completed")
        self.assertEqual(self.payment.mvola_transaction_reference, "MVL123456789")
        self.assertEqual(self.payment.mvola_gateway_fees, Decimal("500"))
        self.assertEqual(self.payment.montant_paye_ariary, Decimal("100000.00"))
        self.assertIsNotNone(self.payment.date_paiement)

        # Verify notification created
        notifications = Notification.objects.filter(user=self.user, metadata__event="mvola_payment_completed")
        self.assertEqual(notifications.count(), 1)

        # Verify QR code generated
        qr_codes = QRCode.objects.filter(vehicule_plaque=self.vehicle, annee_fiscale=2024)
        self.assertEqual(qr_codes.count(), 1)

    def test_callback_failed_payment(self):
        """Test callback with failed payment"""
        callback_data = {
            "serverCorrelationId": "test-server-correlation-id",
            "transactionStatus": "failed",
            "transactionReference": "MVL123456789",
        }

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh payment from database
        self.payment.refresh_from_db()

        # Verify payment status updated
        self.assertEqual(self.payment.statut, "ANNULE")
        self.assertEqual(self.payment.mvola_status, "failed")

        # Verify notification created
        notifications = Notification.objects.filter(user=self.user, metadata__event="mvola_payment_failed")
        self.assertEqual(notifications.count(), 1)

        # Verify no QR code generated
        qr_codes = QRCode.objects.filter(vehicule_plaque=self.vehicle, annee_fiscale=2024)
        self.assertEqual(qr_codes.count(), 0)

    def test_callback_missing_server_correlation_id(self):
        """Test callback with missing serverCorrelationId"""
        callback_data = {"transactionStatus": "completed"}

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_callback_missing_transaction_status(self):
        """Test callback with missing transactionStatus"""
        callback_data = {"serverCorrelationId": "test-server-correlation-id"}

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_callback_payment_not_found(self):
        """Test callback with non-existent payment"""
        callback_data = {"serverCorrelationId": "non-existent-id", "transactionStatus": "completed"}

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["status"], "error")

    def test_callback_no_authentication_required(self):
        """Test that callback endpoint doesn't require authentication"""
        # Don't authenticate the client
        callback_data = {"serverCorrelationId": "test-server-correlation-id", "transactionStatus": "completed"}

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        # Should succeed without authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_callback_extracts_gateway_fees(self):
        """Test that callback extracts gateway fees correctly"""
        callback_data = {
            "serverCorrelationId": "test-server-correlation-id",
            "transactionStatus": "completed",
            "fees": [{"feeAmount": "1500"}],
        }

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh payment
        self.payment.refresh_from_db()

        # Verify gateway fees extracted
        self.assertEqual(self.payment.mvola_gateway_fees, Decimal("1500"))

    def test_callback_qr_code_not_duplicated(self):
        """Test that QR code is not duplicated if already exists"""
        # Create existing QR code
        existing_qr = QRCode.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=2024,
            date_expiration=timezone.now() + timezone.timedelta(days=365),
        )

        callback_data = {"serverCorrelationId": "test-server-correlation-id", "transactionStatus": "completed"}

        response = self.client.put("/api/payments/mvola/callback/", callback_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only one QR code exists
        qr_codes = QRCode.objects.filter(vehicule_plaque=self.vehicle, annee_fiscale=2024)
        self.assertEqual(qr_codes.count(), 1)
        self.assertEqual(qr_codes.first().id, existing_qr.id)
