import hashlib
import json
import secrets
import string
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class PaiementTaxe(models.Model):
    """Payment records for vehicle taxes and contraventions"""

    TYPE_PAIEMENT_CHOICES = [
        ("TAXE_VEHICULE", "Taxe véhicule"),
        ("AMENDE_CONTRAVENTION", "Amende contravention"),
    ]

    STATUT_CHOICES = [
        ("IMPAYE", "Impayé"),
        ("EN_ATTENTE", "En attente"),
        ("PAYE", "Payé"),
        ("EXONERE", "Exonéré"),
        ("ANNULE", "Annulé"),
    ]

    METHODE_PAIEMENT_CHOICES = [
        ("mvola", "MVola"),
        ("orange_money", "Orange Money"),
        ("airtel_money", "Airtel Money"),
        ("carte_bancaire", "Carte bancaire"),
        ("cash", "Espèces"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_paiement = models.CharField(
        max_length=30,
        choices=TYPE_PAIEMENT_CHOICES,
        default="TAXE_VEHICULE",
        verbose_name="Type de paiement",
        help_text="Type de paiement: taxe véhicule ou amende contravention",
    )
    contravention = models.ForeignKey(
        "contraventions.Contravention",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="paiements",
        verbose_name="Contravention",
        help_text="Contravention associée si type_paiement est AMENDE_CONTRAVENTION",
    )
    vehicule_plaque = models.ForeignKey(
        "vehicles.Vehicule", on_delete=models.CASCADE, to_field="plaque_immatriculation", related_name="paiements"
    )
    annee_fiscale = models.PositiveIntegerField(verbose_name="Année fiscale")
    montant_du_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant dû (Ariary)",
    )
    montant_paye_ariary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant payé (Ariary)",
    )
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="IMPAYE", verbose_name="Statut")
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, verbose_name="ID de transaction")
    methode_paiement = models.CharField(
        max_length=30, choices=METHODE_PAIEMENT_CHOICES, null=True, blank=True, verbose_name="Méthode de paiement"
    )
    details_paiement = models.JSONField(default=dict, blank=True, verbose_name="Détails du paiement")

    # --- Stripe integration fields ---
    stripe_payment_intent_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True, verbose_name="Stripe Payment Intent ID"
    )
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Stripe Customer ID")
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Stripe Charge ID")

    STATUT_STRIPE_CHOICES = [
        ("pending", "En attente"),
        ("processing", "En cours de traitement"),
        ("succeeded", "Réussi"),
        ("failed", "Échoué"),
        ("canceled", "Annulé"),
        ("refunded", "Remboursé"),
        ("partially_refunded", "Partiellement remboursé"),
    ]

    stripe_status = models.CharField(
        max_length=30, choices=STATUT_STRIPE_CHOICES, null=True, blank=True, verbose_name="Statut Stripe"
    )

    stripe_payment_method = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Méthode de paiement Stripe"
    )

    stripe_receipt_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL du reçu Stripe")

    stripe_created = models.DateTimeField(null=True, blank=True, verbose_name="Date de création Stripe")

    stripe_metadata = models.JSONField(default=dict, blank=True, verbose_name="Métadonnées Stripe")

    # Billing information
    billing_email = models.EmailField(null=True, blank=True, verbose_name="Email de facturation")
    billing_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nom de facturation")

    # Stripe amount (in smallest currency unit)
    amount_stripe = models.IntegerField(null=True, blank=True, verbose_name="Montant en centimes (Stripe)")
    currency_stripe = models.CharField(max_length=3, default="MGA", verbose_name="Devise Stripe")

    # MVola mobile money fields
    mvola_x_correlation_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="MVola X-Correlation-ID",
        help_text="Request correlation ID generated by our system",
    )

    mvola_server_correlation_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="MVola Server Correlation ID",
        help_text="Transaction identifier from MVola",
    )

    mvola_transaction_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="MVola Transaction Reference",
        help_text="Final transaction reference from MVola",
    )

    mvola_customer_msisdn = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Customer MSISDN",
        help_text="Customer phone number for MVola payment",
    )

    mvola_platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="MVola Platform Fee (3%)",
        help_text="3% platform fee charged to customer",
    )

    mvola_gateway_fees = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="MVola Gateway Fees",
        help_text="Actual fees charged by MVola gateway",
    )

    mvola_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ("pending", "En attente"),
            ("completed", "Complété"),
            ("failed", "Échoué"),
        ],
        verbose_name="Statut MVola",
    )

    # Cash payment fields
    collected_by = models.ForeignKey(
        "AgentPartenaireProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_payments",
        verbose_name="Collecté par",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement de taxe"
        verbose_name_plural = "Paiements de taxes"
        constraints = [
            models.UniqueConstraint(
                fields=["vehicule_plaque", "annee_fiscale"],
                condition=models.Q(type_paiement="TAXE_VEHICULE"),
                name="unique_vehicle_tax_per_year",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicule_plaque", "annee_fiscale"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["date_paiement"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["stripe_payment_intent_id"]),
            models.Index(fields=["stripe_status"]),
            models.Index(fields=["mvola_server_correlation_id"]),
            models.Index(fields=["mvola_status"]),
            models.Index(fields=["type_paiement"]),
            models.Index(fields=["contravention"]),
        ]

    def clean(self):
        """Validate payment data based on type"""
        super().clean()

        # Validate contravention requirement for amende payments
        if self.type_paiement == "AMENDE_CONTRAVENTION" and not self.contravention:
            raise ValidationError({"contravention": "Une contravention doit être associée pour un paiement d'amende."})

        # Validate that taxe payments don't have contravention
        if self.type_paiement == "TAXE_VEHICULE" and self.contravention:
            raise ValidationError(
                {"contravention": "Un paiement de taxe véhicule ne peut pas avoir de contravention associée."}
            )

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        alphabet = string.ascii_uppercase + string.digits
        return "TX" + "".join(secrets.choice(alphabet) for _ in range(10))

    def __str__(self):
        if self.type_paiement == "AMENDE_CONTRAVENTION" and self.contravention:
            return f"Amende {self.contravention.numero_pv} - {self.statut}"
        return f"{self.vehicule_plaque} - {self.annee_fiscale} - {self.statut}"

    def est_paye(self):
        """Check if payment is completed"""
        return self.statut in ["PAYE", "EXONERE"]


class StripeConfig(models.Model):
    """Configuration for Stripe keys and behavior by environment"""

    ENV_CHOICES = [
        ("development", "Development"),
        ("production", "Production"),
    ]

    environment = models.CharField(max_length=20, choices=ENV_CHOICES, unique=True)
    publishable_key = models.CharField(max_length=255, blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default="MGA")
    success_url = models.URLField(max_length=500, blank=True, null=True)
    cancel_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stripe configuration"
        verbose_name_plural = "Stripe configurations"

    def __str__(self):
        return f"StripeConfig({self.environment}){'*' if self.is_active else ''}"

    @classmethod
    def get_active(cls):
        """Return the active Stripe configuration, if any."""
        return cls.objects.filter(is_active=True).first()

    def activate(self):
        """Activate this configuration and deactivate others."""
        StripeConfig.objects.exclude(pk=self.pk).update(is_active=False)
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])


class MvolaConfiguration(models.Model):
    """MVola Payment Gateway Configuration"""

    ENVIRONMENT_CHOICES = [
        ("sandbox", "Sandbox (Test)"),
        ("production", "Production (Live)"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la configuration",
        help_text="Nom descriptif pour identifier cette configuration MVola",
    )

    # Environment
    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default="sandbox",
        verbose_name="Environnement",
        help_text="Sandbox pour les tests, Production pour les paiements réels",
    )

    # API Credentials
    consumer_key = models.CharField(
        max_length=255,
        verbose_name="Client ID (Consumer Key)",
        help_text="Clé d'API fournie par MVola (aussi appelée Client ID)",
    )
    consumer_secret = models.CharField(
        max_length=255, verbose_name="Client Secret (Consumer Secret)", help_text="Secret d'API fourni par MVola"
    )

    # Merchant Information
    merchant_msisdn = models.CharField(
        max_length=20,
        verbose_name="Merchant Number (MSISDN)",
        help_text="Numéro de téléphone MVola du marchand (ex: 0343151968)",
    )
    merchant_name = models.CharField(
        max_length=100,
        default="TaxCollector",
        verbose_name="Nom du marchand",
        help_text="Nom qui apparaîtra dans les transactions MVola",
    )

    # API URLs (auto-populated based on environment)
    base_url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="URL de base de l'API",
        help_text="Laissez vide pour utiliser l'URL par défaut selon l'environnement",
    )
    callback_url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="URL de callback",
        help_text="URL pour recevoir les notifications de statut de paiement",
    )

    # Payment Limits
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(100)],
        verbose_name="Montant minimum",
        help_text="Montant minimum autorisé pour un paiement (Ariary)",
    )
    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000000,
        validators=[MinValueValidator(1000)],
        verbose_name="Montant maximum",
        help_text="Montant maximum autorisé pour un paiement (Ariary)",
    )

    # Fee Configuration
    platform_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=3.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Frais de plateforme (%)",
        help_text="Pourcentage de frais ajouté au montant de la taxe",
    )

    # Logo
    logo = models.ImageField(
        upload_to="payment_gateways/mvola/",
        blank=True,
        null=True,
        verbose_name="Logo MVola",
        help_text="Logo à afficher sur les pages de paiement",
    )

    # Configuration Status
    is_active = models.BooleanField(
        default=False,
        verbose_name="Configuration active",
        help_text="Une seule configuration peut être active à la fois",
    )
    is_enabled = models.BooleanField(
        default=True, verbose_name="MVola activé", help_text="Active ou désactive les paiements MVola sur la plateforme"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Configuration vérifiée",
        help_text="Indique si la configuration a été testée avec succès",
    )
    last_test_date = models.DateTimeField(null=True, blank=True, verbose_name="Dernière date de test")
    last_test_result = models.TextField(blank=True, verbose_name="Résultat du dernier test")

    # Statistics
    total_transactions = models.IntegerField(
        default=0, verbose_name="Total des transactions", help_text="Nombre total de transactions effectuées"
    )
    successful_transactions = models.IntegerField(default=0, verbose_name="Transactions réussies")
    failed_transactions = models.IntegerField(default=0, verbose_name="Transactions échouées")
    total_amount_processed = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Montant total traité (Ariary)"
    )

    # Metadata
    description = models.TextField(
        blank=True, verbose_name="Description", help_text="Notes ou description de cette configuration"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="mvola_configs_created", verbose_name="Créé par"
    )
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="mvola_configs_modified", verbose_name="Modifié par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Configuration MVola"
        verbose_name_plural = "Configurations MVola"
        ordering = ["-is_active", "-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_enabled"]),
            models.Index(fields=["environment"]),
        ]

    def __str__(self):
        status = "✓ Active" if self.is_active else "Inactive"
        env = "🔴 LIVE" if self.environment == "production" else "🟡 TEST"
        return f"{self.name} ({env}) - {status}"

    def clean(self):
        """Validate that only one configuration is active"""
        if self.is_active:
            active_configs = MvolaConfiguration.objects.filter(is_active=True)
            if self.pk:
                active_configs = active_configs.exclude(pk=self.pk)
            if active_configs.exists():
                raise ValidationError(
                    "Une configuration MVola est déjà active. " "Désactivez-la avant d'activer celle-ci."
                )

        # Validate MSISDN format
        if self.merchant_msisdn:
            from payments.services.mvola.exceptions import MvolaValidationError
            from payments.services.mvola.validators import validate_msisdn

            try:
                validate_msisdn(self.merchant_msisdn)
            except MvolaValidationError as e:
                raise ValidationError({"merchant_msisdn": str(e)})

    def save(self, *args, **kwargs):
        # Auto-populate base_url if not provided
        if not self.base_url:
            if self.environment == "production":
                self.base_url = "https://api.mvola.mg"
            else:
                self.base_url = "https://devapi.mvola.mg"

        # Auto-populate callback_url if not provided
        if not self.callback_url:
            from django.conf import settings

            site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
            self.callback_url = f"{site_url}/payments/mvola/callback/"

        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active_config(cls):
        """Get the active MVola configuration"""
        try:
            return cls.objects.get(is_active=True, is_enabled=True)
        except cls.DoesNotExist:
            return None

    def test_connection(self):
        """Test MVola API connection and return result"""
        from django.utils import timezone

        from payments.services.mvola.api_client import MvolaAPIClient
        from payments.services.mvola.exceptions import MvolaAPIError, MvolaAuthenticationError

        try:
            # Temporarily override settings for testing
            from django.conf import settings

            original_settings = {
                "MVOLA_BASE_URL": getattr(settings, "MVOLA_BASE_URL", None),
                "MVOLA_CONSUMER_KEY": getattr(settings, "MVOLA_CONSUMER_KEY", None),
                "MVOLA_CONSUMER_SECRET": getattr(settings, "MVOLA_CONSUMER_SECRET", None),
                "MVOLA_PARTNER_MSISDN": getattr(settings, "MVOLA_PARTNER_MSISDN", None),
                "MVOLA_PARTNER_NAME": getattr(settings, "MVOLA_PARTNER_NAME", None),
                "MVOLA_CALLBACK_URL": getattr(settings, "MVOLA_CALLBACK_URL", None),
            }

            # Apply test configuration
            settings.MVOLA_BASE_URL = self.base_url
            settings.MVOLA_CONSUMER_KEY = self.consumer_key
            settings.MVOLA_CONSUMER_SECRET = self.consumer_secret
            settings.MVOLA_PARTNER_MSISDN = self.merchant_msisdn
            settings.MVOLA_PARTNER_NAME = self.merchant_name
            settings.MVOLA_CALLBACK_URL = self.callback_url

            # Test authentication
            client = MvolaAPIClient()
            token = client.get_access_token()

            if token:
                # Update test results
                self.is_verified = True
                self.last_test_date = timezone.now()
                self.last_test_result = "✓ Authentification réussie avec l'API MVola"
                self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])

                # Restore original settings
                for key, value in original_settings.items():
                    setattr(settings, key, value)

                return True, "Connexion MVola réussie"
            else:
                raise MvolaAuthenticationError("Échec de l'obtention du token d'accès")

        except MvolaAuthenticationError as e:
            error_msg = f"✗ Erreur d'authentification: {str(e)}"
            self.is_verified = False
            self.last_test_date = timezone.now()
            self.last_test_result = error_msg
            self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])

            # Restore original settings
            for key, value in original_settings.items():
                setattr(settings, key, value)

            return False, error_msg

        except MvolaAPIError as e:
            error_msg = f"✗ Erreur API MVola: {str(e)}"
            self.is_verified = False
            self.last_test_date = timezone.now()
            self.last_test_result = error_msg
            self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])

            # Restore original settings
            for key, value in original_settings.items():
                setattr(settings, key, value)

            return False, error_msg

        except Exception as e:
            error_msg = f"✗ Erreur inattendue: {str(e)}"
            self.is_verified = False
            self.last_test_date = timezone.now()
            self.last_test_result = error_msg
            self.save(update_fields=["is_verified", "last_test_date", "last_test_result"])

            # Restore original settings
            for key, value in original_settings.items():
                setattr(settings, key, value)

            return False, error_msg

    def apply_to_settings(self):
        """Apply this configuration to Django settings"""
        from django.conf import settings

        settings.MVOLA_BASE_URL = self.base_url
        settings.MVOLA_CONSUMER_KEY = self.consumer_key
        settings.MVOLA_CONSUMER_SECRET = self.consumer_secret
        settings.MVOLA_PARTNER_MSISDN = self.merchant_msisdn
        settings.MVOLA_PARTNER_NAME = self.merchant_name
        settings.MVOLA_CALLBACK_URL = self.callback_url
        settings.MVOLA_MIN_AMOUNT = int(self.min_amount)
        settings.MVOLA_MAX_AMOUNT = int(self.max_amount)

    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_transactions == 0:
            return 0
        return round((self.successful_transactions / self.total_transactions) * 100, 2)


class StripeWebhookEvent(models.Model):
    """Store Stripe webhook events for audit and retry"""

    stripe_event_id = models.CharField(max_length=255, unique=True, verbose_name="Stripe Event ID")
    type = models.CharField(max_length=100, verbose_name="Type d'événement")
    data = models.JSONField(verbose_name="Données de l'événement")
    processed = models.BooleanField(default=False, verbose_name="Traité")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")

    class Meta:
        verbose_name = "Événement Webhook Stripe"
        verbose_name_plural = "Événements Webhook Stripe"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Stripe Event: {self.type} - {self.stripe_event_id}"


class QRCode(models.Model):
    """QR codes for vehicle tax verification and contraventions"""

    TYPE_CODE_CHOICES = [
        ("TAXE_VEHICULE", "Taxe véhicule"),
        ("CONTRAVENTION", "Contravention"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Type de QR code
    type_code = models.CharField(
        max_length=30, choices=TYPE_CODE_CHOICES, default="TAXE_VEHICULE", verbose_name="Type de QR code"
    )

    # Code unique (numéro PV pour contravention, ou token pour taxe)
    code = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Code unique",
        help_text="Numéro PV pour contravention ou token pour taxe véhicule",
    )

    # Champs pour taxe véhicule (optionnels pour contraventions)
    vehicule_plaque = models.ForeignKey(
        "vehicles.Vehicule",
        on_delete=models.CASCADE,
        to_field="plaque_immatriculation",
        related_name="qr_codes",
        null=True,
        blank=True,
    )
    annee_fiscale = models.PositiveIntegerField(null=True, blank=True, verbose_name="Année fiscale")

    # Token de vérification (pour compatibilité avec ancien système)
    token = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="Token de vérification")

    # Données additionnelles (JSON pour flexibilité)
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données additionnelles",
        help_text="Données spécifiques au type de QR code",
    )

    # Métadonnées communes
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    date_expiration = models.DateTimeField(null=True, blank=True, verbose_name="Date d'expiration")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    nombre_scans = models.PositiveIntegerField(default=0, verbose_name="Nombre de scans")
    derniere_verification = models.DateTimeField(null=True, blank=True, verbose_name="Dernière vérification")

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["token"], condition=models.Q(est_actif=True), name="qr_token_actif_idx"),
            models.Index(fields=["vehicule_plaque", "annee_fiscale"]),
            models.Index(
                fields=["date_expiration"], condition=models.Q(est_actif=True), name="qr_expiration_actif_idx"
            ),
            models.Index(fields=["type_code"]),
        ]

    def save(self, *args, **kwargs):
        # Pour les taxes véhicules, générer un token si pas fourni
        if self.type_code == "TAXE_VEHICULE" and not self.token:
            self.token = self.generate_token()
            if not self.code:
                self.code = self.token

        # Pour les contraventions, le code est le numéro PV
        if self.type_code == "CONTRAVENTION" and not self.code:
            raise ValidationError("Le code (numéro PV) est obligatoire pour les contraventions")

        super().save(*args, **kwargs)

    def generate_token(self):
        """Generate unique verification token"""
        alphabet = string.ascii_letters + string.digits
        token = "".join(secrets.choice(alphabet) for _ in range(32))

        # Ensure uniqueness
        while QRCode.objects.filter(token=token).exists():
            token = "".join(secrets.choice(alphabet) for _ in range(32))

        return token

    def __str__(self):
        if self.type_code == "CONTRAVENTION":
            return f"QR-CONTRAVENTION-{self.code}"
        return f"QR-{self.vehicule_plaque}-{self.annee_fiscale}"

    def increment_scan_count(self):
        """Increment scan counter and update last verification"""
        from django.utils import timezone

        self.nombre_scans += 1
        self.derniere_verification = timezone.now()
        self.save(update_fields=["nombre_scans", "derniere_verification"])

    def est_valide(self):
        """Check if QR code is valid"""
        from django.utils import timezone

        # Check basic validity
        if not self.est_actif:
            return False

        if self.date_expiration and self.date_expiration < timezone.now():
            return False

        # Type-specific validation
        if self.type_code == "TAXE_VEHICULE":
            return (
                hasattr(self, "vehicule_plaque")
                and self.vehicule_plaque
                and self.vehicule_plaque.paiements.filter(
                    annee_fiscale=self.annee_fiscale, statut__in=["PAYE", "EXONERE"]
                ).exists()
            )
        elif self.type_code == "CONTRAVENTION":
            # For contraventions, check if it exists and is valid
            return True  # Basic validity, specific checks done in contravention views

        return False


# ============================================================================
# CASH PAYMENT SYSTEM MODELS
# ============================================================================


class CashSystemConfig(models.Model):
    """Singleton configuration model for cash payment system"""

    id = models.AutoField(primary_key=True)
    default_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Taux de commission par défaut (%)",
        help_text="Taux de commission par défaut pour les agents partenaires",
    )
    dual_verification_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("500000.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Seuil de double vérification (Ariary)",
        help_text="Montant au-dessus duquel une approbation admin est requise",
    )
    reconciliation_tolerance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1000.00"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Tolérance de réconciliation (Ariary)",
        help_text="Écart acceptable lors de la réconciliation",
    )
    session_timeout_hours = models.IntegerField(
        default=12,
        verbose_name="Délai d'expiration de session (heures)",
        help_text="Nombre d'heures avant qu'une session ouverte expire",
    )
    void_time_limit_minutes = models.IntegerField(
        default=30, verbose_name="Délai d'annulation (minutes)", help_text="Temps maximum pour annuler une transaction"
    )
    receipt_footer_text = models.TextField(
        blank=True,
        verbose_name="Texte de pied de page du reçu",
        help_text="Texte personnalisé pour le pied de page des reçus",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration du système de paiement en espèces"
        verbose_name_plural = "Configuration du système de paiement en espèces"

    def __str__(self):
        return "Configuration du système de paiement en espèces"

    @classmethod
    def get_config(cls):
        """Get or create singleton configuration"""
        config, created = cls.objects.get_or_create(pk=1)
        return config

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of singleton
        pass


class AgentPartenaireProfile(models.Model):
    """Profile for agent partenaires authorized to accept cash payments"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="agent_partenaire_profile", verbose_name="Utilisateur"
    )
    agent_id = models.CharField(
        max_length=50, unique=True, verbose_name="ID Agent", help_text="Identifiant unique de l'agent"
    )
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    collection_location = models.CharField(
        max_length=200, verbose_name="Lieu de collecte", help_text="Emplacement où l'agent collecte les paiements"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Taux de commission personnalisé (%)",
        help_text="Laissez vide pour utiliser le taux par défaut",
    )
    use_default_commission = models.BooleanField(default=True, verbose_name="Utiliser le taux de commission par défaut")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_agents", verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Profil Agent Partenaire"
        verbose_name_plural = "Profils Agents Partenaires"
        indexes = [
            models.Index(fields=["agent_id"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.agent_id})"

    def get_commission_rate(self):
        """Get effective commission rate (custom or default)"""
        if self.use_default_commission or not self.commission_rate:
            return CashSystemConfig.get_config().default_commission_rate
        return self.commission_rate

    def save(self, *args, **kwargs):
        if not self.agent_id:
            # Generate agent ID if not provided
            alphabet = string.ascii_uppercase + string.digits
            self.agent_id = "AG" + "".join(secrets.choice(alphabet) for _ in range(8))
        super().save(*args, **kwargs)


class CashSession(models.Model):
    """Cash collection session for an agent partenaire"""

    STATUS_CHOICES = [
        ("open", "Ouvert"),
        ("closed", "Fermé"),
        ("reconciled", "Réconcilié"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collector = models.ForeignKey(
        AgentPartenaireProfile, on_delete=models.CASCADE, related_name="sessions", verbose_name="Collecteur"
    )
    session_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de session")
    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Solde d'ouverture (Ariary)",
    )
    opening_time = models.DateTimeField(auto_now_add=True, verbose_name="Heure d'ouverture")
    closing_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Solde de clôture (Ariary)"
    )
    expected_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Solde attendu (Ariary)"
    )
    closing_time = models.DateTimeField(null=True, blank=True, verbose_name="Heure de clôture")
    discrepancy_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Montant de l'écart (Ariary)"
    )
    discrepancy_notes = models.TextField(blank=True, verbose_name="Notes sur l'écart")
    total_commission = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Commission totale (Ariary)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="Statut")
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_sessions",
        verbose_name="Approuvé par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Session de collecte"
        verbose_name_plural = "Sessions de collecte"
        ordering = ["-opening_time"]
        indexes = [
            models.Index(fields=["collector", "status"]),
            models.Index(fields=["session_number"]),
            models.Index(fields=["opening_time"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Session {self.session_number} - {self.collector.full_name}"

    def save(self, *args, **kwargs):
        if not self.session_number:
            # Generate session number: SESS-YYYYMMDD-XXXXXX
            from django.utils import timezone

            date_str = timezone.now().strftime("%Y%m%d")
            random_str = "".join(secrets.choice(string.digits) for _ in range(6))
            self.session_number = f"SESS-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class CashTransaction(models.Model):
    """Individual cash payment transaction"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        CashSession, on_delete=models.CASCADE, related_name="transactions", verbose_name="Session"
    )
    payment = models.OneToOneField(
        PaiementTaxe, on_delete=models.CASCADE, related_name="cash_transaction", verbose_name="Paiement"
    )
    transaction_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de transaction")
    customer_name = models.CharField(max_length=200, verbose_name="Nom du client")
    vehicle_plate = models.CharField(max_length=20, verbose_name="Plaque d'immatriculation")
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant de la taxe (Ariary)",
    )
    amount_tendered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant remis (Ariary)",
    )
    change_given = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Monnaie rendue (Ariary)",
    )
    commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Montant de la commission (Ariary)",
    )
    collector = models.ForeignKey(
        AgentPartenaireProfile, on_delete=models.CASCADE, related_name="transactions", verbose_name="Collecteur"
    )
    requires_approval = models.BooleanField(default=False, verbose_name="Nécessite une approbation")
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_transactions",
        verbose_name="Approuvé par",
    )
    approval_time = models.DateTimeField(null=True, blank=True, verbose_name="Heure d'approbation")
    transaction_time = models.DateTimeField(auto_now_add=True, verbose_name="Heure de transaction")
    receipt_printed = models.BooleanField(default=False, verbose_name="Reçu imprimé")
    receipt_print_time = models.DateTimeField(null=True, blank=True, verbose_name="Heure d'impression du reçu")
    is_voided = models.BooleanField(default=False, verbose_name="Annulé")
    voided_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voided_transactions",
        verbose_name="Annulé par",
    )
    void_time = models.DateTimeField(null=True, blank=True, verbose_name="Heure d'annulation")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Transaction en espèces"
        verbose_name_plural = "Transactions en espèces"
        ordering = ["-transaction_time"]
        indexes = [
            models.Index(fields=["session", "transaction_time"]),
            models.Index(fields=["transaction_number"]),
            models.Index(fields=["collector", "transaction_time"]),
            models.Index(fields=["requires_approval"]),
            models.Index(fields=["is_voided"]),
        ]

    def __str__(self):
        return f"Transaction {self.transaction_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Generate transaction number: CASH-YYYYMMDD-XXXXXX
            from django.utils import timezone

            date_str = timezone.now().strftime("%Y%m%d")
            random_str = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            self.transaction_number = f"CASH-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class CashReceipt(models.Model):
    """
    Cash payment receipt with QR code

    Integrates with the existing QRCode model to provide verification
    for cash payments. The QR code is shared across all payment methods
    (cash, mobile money, Stripe) for the same vehicle and tax year.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(
        CashTransaction, on_delete=models.CASCADE, related_name="receipt", verbose_name="Transaction"
    )
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de reçu")
    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cash_receipts",
        verbose_name="QR Code",
        help_text="QR code partagé avec tous les types de paiement pour ce véhicule et année fiscale",
    )
    vehicle_registration = models.CharField(max_length=20, verbose_name="Immatriculation du véhicule")
    vehicle_owner = models.CharField(max_length=200, verbose_name="Propriétaire du véhicule")
    tax_year = models.IntegerField(verbose_name="Année fiscale")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant de la taxe (Ariary)")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant payé (Ariary)")
    change_given = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monnaie rendue (Ariary)")
    collector_name = models.CharField(max_length=200, verbose_name="Nom du collecteur")
    collector_id = models.CharField(max_length=50, verbose_name="ID du collecteur")
    payment_date = models.DateTimeField(verbose_name="Date de paiement")
    qr_code_data = models.TextField(verbose_name="Données du QR code")
    is_duplicate = models.BooleanField(default=False, verbose_name="Est un duplicata")
    original_receipt = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
        verbose_name="Reçu original",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Reçu en espèces"
        verbose_name_plural = "Reçus en espèces"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["transaction"]),
            models.Index(fields=["vehicle_registration", "tax_year"]),
        ]

    def __str__(self):
        return f"Reçu {self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number: REC-YYYYMMDD-XXXXXX
            from django.utils import timezone

            date_str = timezone.now().strftime("%Y%m%d")
            random_str = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            self.receipt_number = f"REC-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class CommissionRecord(models.Model):
    """Commission tracking for agent partenaires"""

    PAYMENT_STATUS_CHOICES = [
        ("pending", "En attente"),
        ("paid", "Payé"),
        ("cancelled", "Annulé"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collector = models.ForeignKey(
        AgentPartenaireProfile, on_delete=models.CASCADE, related_name="commissions", verbose_name="Collecteur"
    )
    session = models.ForeignKey(
        CashSession, on_delete=models.CASCADE, related_name="commissions", verbose_name="Session"
    )
    transaction = models.OneToOneField(
        CashTransaction, on_delete=models.CASCADE, related_name="commission", verbose_name="Transaction"
    )
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant de la taxe (Ariary)")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux de commission (%)")
    commission_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Montant de la commission (Ariary)"
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending", verbose_name="Statut de paiement"
    )
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    paid_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="paid_commissions", verbose_name="Payé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Enregistrement de commission"
        verbose_name_plural = "Enregistrements de commissions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["collector", "payment_status"]),
            models.Index(fields=["session"]),
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        return f"Commission {self.collector.full_name} - {self.commission_amount} Ar"


class CashAuditLog(models.Model):
    """Immutable audit trail for cash operations"""

    ACTION_TYPE_CHOICES = [
        ("session_open", "Ouverture de session"),
        ("session_close", "Fermeture de session"),
        ("transaction_create", "Création de transaction"),
        ("transaction_approve", "Approbation de transaction"),
        ("transaction_void", "Annulation de transaction"),
        ("receipt_print", "Impression de reçu"),
        ("receipt_reprint", "Réimpression de reçu"),
        ("reconciliation", "Réconciliation"),
        ("config_change", "Modification de configuration"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES, verbose_name="Type d'action")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="cash_audit_logs", verbose_name="Utilisateur"
    )
    session = models.ForeignKey(
        CashSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs", verbose_name="Session"
    )
    transaction = models.ForeignKey(
        CashTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Transaction",
    )
    action_data = models.JSONField(default=dict, verbose_name="Données de l'action")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    previous_hash = models.CharField(max_length=64, blank=True, verbose_name="Hash précédent")
    current_hash = models.CharField(max_length=64, verbose_name="Hash actuel")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")

    class Meta:
        verbose_name = "Journal d'audit en espèces"
        verbose_name_plural = "Journaux d'audit en espèces"
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
            models.Index(fields=["session"]),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp}"

    def save(self, *args, **kwargs):
        if not self.current_hash:
            # Calculate hash for this entry
            self.current_hash = self.calculate_hash()
        super().save(*args, **kwargs)

    def calculate_hash(self):
        """Calculate SHA-256 hash of this log entry"""
        data = {
            "action_type": self.action_type,
            "user_id": str(self.user_id) if self.user_id else "",
            "session_id": str(self.session_id) if self.session_id else "",
            "transaction_id": str(self.transaction_id) if self.transaction_id else "",
            "action_data": json.dumps(self.action_data, sort_keys=True),
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat() if self.timestamp else timezone.now().isoformat(),
        }
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

    @classmethod
    def get_last_hash(cls):
        """Get the hash of the most recent log entry"""
        last_log = cls.objects.order_by("-timestamp").first()
        return last_log.current_hash if last_log else ""
