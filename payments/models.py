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
