from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
import secrets
import string

class PaiementTaxe(models.Model):
    """Payment records for vehicle taxes"""
    
    STATUT_CHOICES = [
        ('IMPAYE', 'Impayé'),
        ('EN_ATTENTE', 'En attente'),
        ('PAYE', 'Payé'),
        ('EXONERE', 'Exonéré'),
        ('ANNULE', 'Annulé'),
    ]
    
    METHODE_PAIEMENT_CHOICES = [
        ('mvola', 'MVola'),
        ('orange_money', 'Orange Money'),
        ('airtel_money', 'Airtel Money'),
        ('carte_bancaire', 'Carte bancaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule_plaque = models.ForeignKey(
        'vehicles.Vehicule', 
        on_delete=models.CASCADE,
        to_field='plaque_immatriculation',
        related_name='paiements'
    )
    annee_fiscale = models.PositiveIntegerField(verbose_name="Année fiscale")
    montant_du_ariary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant dû (Ariary)"
    )
    montant_paye_ariary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant payé (Ariary)"
    )
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES,
        default='IMPAYE',
        verbose_name="Statut"
    )
    transaction_id = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True,
        verbose_name="ID de transaction"
    )
    methode_paiement = models.CharField(
        max_length=30, 
        choices=METHODE_PAIEMENT_CHOICES,
        null=True, blank=True,
        verbose_name="Méthode de paiement"
    )
    details_paiement = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Détails du paiement"
    )

    # --- Stripe integration fields ---
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Stripe Payment Intent ID"
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Stripe Customer ID"
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Stripe Charge ID"
    )

    STATUT_STRIPE_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('succeeded', 'Réussi'),
        ('failed', 'Échoué'),
        ('canceled', 'Annulé'),
        ('refunded', 'Remboursé'),
        ('partially_refunded', 'Partiellement remboursé'),
    ]

    stripe_status = models.CharField(
        max_length=30,
        choices=STATUT_STRIPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Statut Stripe"
    )

    stripe_payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Méthode de paiement Stripe"
    )

    stripe_receipt_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="URL du reçu Stripe"
    )

    stripe_created = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de création Stripe"
    )

    stripe_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées Stripe"
    )

    # Billing information
    billing_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Email de facturation"
    )
    billing_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Nom de facturation"
    )

    # Stripe amount (in smallest currency unit)
    amount_stripe = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Montant en centimes (Stripe)"
    )
    currency_stripe = models.CharField(
        max_length=3,
        default='MGA',
        verbose_name="Devise Stripe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement de taxe"
        verbose_name_plural = "Paiements de taxes"
        unique_together = [['vehicule_plaque', 'annee_fiscale']]
        indexes = [
            models.Index(fields=['vehicule_plaque', 'annee_fiscale']),
            models.Index(fields=['statut']),
            models.Index(fields=['date_paiement']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        alphabet = string.ascii_uppercase + string.digits
        return 'TX' + ''.join(secrets.choice(alphabet) for _ in range(10))
    
    def __str__(self):
        return f"{self.vehicule_plaque} - {self.annee_fiscale} - {self.statut}"
    
    def est_paye(self):
        """Check if payment is completed"""
        return self.statut in ['PAYE', 'EXONERE']


class StripeConfig(models.Model):
    """Configuration for Stripe keys and behavior by environment"""

    ENV_CHOICES = [
        ('development', 'Development'),
        ('production', 'Production'),
    ]

    environment = models.CharField(max_length=20, choices=ENV_CHOICES, unique=True)
    publishable_key = models.CharField(max_length=255, blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default='MGA')
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
        self.save(update_fields=['is_active', 'updated_at'])


class StripeWebhookEvent(models.Model):
    """Store Stripe webhook events for audit and retry"""
    stripe_event_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Stripe Event ID"
    )
    type = models.CharField(
        max_length=100,
        verbose_name="Type d'événement"
    )
    data = models.JSONField(
        verbose_name="Données de l'événement"
    )
    processed = models.BooleanField(
        default=False,
        verbose_name="Traité"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement"
    )

    class Meta:
        verbose_name = "Événement Webhook Stripe"
        verbose_name_plural = "Événements Webhook Stripe"
        ordering = ['-created_at']

    def __str__(self):
        return f"Stripe Event: {self.type} - {self.stripe_event_id}"

class QRCode(models.Model):
    """QR codes for vehicle tax verification"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule_plaque = models.ForeignKey(
        'vehicles.Vehicule',
        on_delete=models.CASCADE,
        to_field='plaque_immatriculation',
        related_name='qr_codes'
    )
    annee_fiscale = models.PositiveIntegerField(verbose_name="Année fiscale")
    token = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name="Token de vérification"
    )
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    date_expiration = models.DateTimeField(verbose_name="Date d'expiration")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    nombre_scans = models.PositiveIntegerField(default=0, verbose_name="Nombre de scans")
    derniere_verification = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Dernière vérification"
    )
    
    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        unique_together = [['vehicule_plaque', 'annee_fiscale']]
        indexes = [
            models.Index(fields=['token'], condition=models.Q(est_actif=True), name='qr_token_actif_idx'),
            models.Index(fields=['vehicule_plaque', 'annee_fiscale']),
            models.Index(fields=['date_expiration'], condition=models.Q(est_actif=True), name='qr_expiration_actif_idx'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Generate unique verification token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def __str__(self):
        return f"QR-{self.vehicule_plaque}-{self.annee_fiscale}"
    
    def increment_scan_count(self):
        """Increment scan counter and update last verification"""
        from django.utils import timezone
        self.nombre_scans += 1
        self.derniere_verification = timezone.now()
        self.save(update_fields=['nombre_scans', 'derniere_verification'])
    
    def est_valide(self):
        """Check if QR code is valid"""
        from django.utils import timezone
        return (
            self.est_actif and 
            self.date_expiration > timezone.now() and
            hasattr(self, 'vehicule_plaque') and
            self.vehicule_plaque.paiements.filter(
                annee_fiscale=self.annee_fiscale,
                statut__in=['PAYE', 'EXONERE']
            ).exists()
        )
