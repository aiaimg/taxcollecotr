"""
Tests for QR Code integration with cash payment system
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from payments.models import (
    AgentPartenaireProfile,
    CashReceipt,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    PaiementTaxe,
    QRCode,
)
from payments.services.cash_receipt_service import CashReceiptService
from vehicles.models import VehicleType, Vehicule


class QRCodeIntegrationTestCase(TestCase):
    """Test QR code integration with cash payment system"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        # Create agent user
        self.agent_user = User.objects.create_user(username="agent1", password="agentpass123")

        # Create agent profile
        self.agent = AgentPartenaireProfile.objects.create(
            user=self.agent_user,
            agent_id="AG001",
            full_name="Test Agent",
            phone_number="0340000000",
            collection_location="Test Location",
            is_active=True,
            created_by=self.user,
        )

        # Get or create vehicle type
        self.vehicle_type, _ = VehicleType.objects.get_or_create(nom="Voiture", defaults={"est_actif": True})

        # Create vehicle
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation="1234AB01",
            proprietaire=self.user,
            type_vehicule=self.vehicle_type,
            puissance_fiscale_cv=5,
            cylindree_cm3=1500,
            source_energie="essence",
            date_premiere_mise_en_circulation=timezone.now().date(),
            categorie="particulier",
            nom_proprietaire="Test Owner",
        )

        # Create cash session
        self.session = CashSession.objects.create(
            collector=self.agent, opening_balance=Decimal("10000.00"), status="open"
        )

        # Create payment
        self.payment = PaiementTaxe.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=timezone.now().year,
            montant_du_ariary=Decimal("50000.00"),
            montant_paye_ariary=Decimal("50000.00"),
            statut="PAYE",
            methode_paiement="cash",
            collected_by=self.agent,
            date_paiement=timezone.now(),
        )

        # Create cash transaction
        self.transaction = CashTransaction.objects.create(
            session=self.session,
            payment=self.payment,
            customer_name="Test Owner",
            vehicle_plate="1234AB01",
            tax_amount=Decimal("50000.00"),
            amount_tendered=Decimal("50000.00"),
            change_given=Decimal("0.00"),
            commission_amount=Decimal("1000.00"),
            collector=self.agent,
        )

    def test_qr_code_created_with_receipt(self):
        """Test that QR code is created when generating receipt"""
        # Generate receipt
        receipt, error = CashReceiptService.generate_cash_receipt(self.transaction)

        # Verify no error
        self.assertIsNone(error)
        self.assertIsNotNone(receipt)

        # Verify QR code was created
        self.assertIsNotNone(receipt.qr_code)
        self.assertEqual(receipt.qr_code.vehicule_plaque, self.vehicle)
        self.assertEqual(receipt.qr_code.annee_fiscale, self.payment.annee_fiscale)
        self.assertTrue(receipt.qr_code.est_actif)

    def test_qr_code_reused_for_same_vehicle_year(self):
        """Test that existing QR code is reused for same vehicle and year"""
        # Create QR code manually first
        existing_qr = QRCode.objects.create(
            vehicule_plaque=self.vehicle,
            annee_fiscale=self.payment.annee_fiscale,
            date_expiration=timezone.now() + timezone.timedelta(days=365),
            est_actif=True,
        )

        # Generate receipt
        receipt, error = CashReceiptService.generate_cash_receipt(self.transaction)

        # Verify no error
        self.assertIsNone(error)
        self.assertIsNotNone(receipt)

        # Verify the same QR code is used
        self.assertEqual(receipt.qr_code.id, existing_qr.id)
        self.assertEqual(receipt.qr_code.token, existing_qr.token)

        # Verify only one QR code exists for this vehicle/year
        qr_count = QRCode.objects.filter(vehicule_plaque=self.vehicle, annee_fiscale=self.payment.annee_fiscale).count()
        self.assertEqual(qr_count, 1)

    def test_qr_code_data_format(self):
        """Test that QR code data is in correct format"""
        # Generate receipt
        receipt, error = CashReceiptService.generate_cash_receipt(self.transaction)

        # Verify no error
        self.assertIsNone(error)
        self.assertIsNotNone(receipt)

        # Verify QR code data is the token (for compatibility with existing verification)
        self.assertEqual(receipt.qr_code_data, receipt.qr_code.token)
        self.assertTrue(len(receipt.qr_code_data) > 0)

    def test_receipt_links_to_qr_code(self):
        """Test that receipt properly links to QR code"""
        # Generate receipt
        receipt, error = CashReceiptService.generate_cash_receipt(self.transaction)

        # Verify no error
        self.assertIsNone(error)
        self.assertIsNotNone(receipt)

        # Verify receipt is in QR code's cash_receipts
        self.assertIn(receipt, receipt.qr_code.cash_receipts.all())

        # Verify QR code can be accessed from receipt
        self.assertEqual(receipt.qr_code.vehicule_plaque.plaque_immatriculation, "1234AB01")

    def test_duplicate_receipt_uses_same_qr_code(self):
        """Test that duplicate receipt uses the same QR code"""
        # Generate original receipt
        original_receipt, error = CashReceiptService.generate_cash_receipt(self.transaction)
        self.assertIsNone(error)

        # Reprint receipt
        duplicate_receipt, error = CashReceiptService.reprint_receipt(original_receipt, self.agent_user)

        # Verify no error
        self.assertIsNone(error)
        self.assertIsNotNone(duplicate_receipt)

        # Verify same QR code is used
        self.assertEqual(duplicate_receipt.qr_code.id, original_receipt.qr_code.id)
        self.assertEqual(duplicate_receipt.qr_code_data, original_receipt.qr_code_data)

        # Verify duplicate flag
        self.assertTrue(duplicate_receipt.is_duplicate)
        self.assertEqual(duplicate_receipt.original_receipt, original_receipt)
