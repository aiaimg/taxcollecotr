from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import uuid
from .utils import (
    get_puissance_fiscale_from_cylindree, 
    get_plage_cv_description,
    valider_coherence_cylindree_cv
)


class VehicleType(models.Model):
    """Dynamic vehicle type model to replace fixed choices"""
    
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du type de véhicule",
        help_text="Ex: Voiture, Moto, Scooter, Camionnette, etc."
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description optionnelle du type de véhicule"
    )
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Est actif",
        help_text="Décochez pour désactiver ce type de véhicule"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Ordre d'affichage dans les listes (0 = premier)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Type de véhicule"
        verbose_name_plural = "Types de véhicules"
        ordering = ['ordre_affichage', 'nom']
        indexes = [
            models.Index(fields=['est_actif']),
            models.Index(fields=['ordre_affichage']),
        ]
    
    def __str__(self):
        return self.nom
    
    @classmethod
    def get_active_types(cls):
        """Retourne tous les types de véhicules actifs"""
        return cls.objects.filter(est_actif=True).order_by('ordre_affichage', 'nom')

class Vehicule(models.Model):
    """Vehicle model supporting all types (terrestrial, railway, maritime, aerial)"""
    
    SOURCE_ENERGIE_CHOICES = [
        ('Essence', 'Essence'),
        ('Diesel', 'Diesel'),
        ('Electrique', 'Électrique'),
        ('Hybride', 'Hybride'),
    ]
    
    CATEGORIE_CHOICES = [
        ('Personnel', 'Personnel'),
        ('Commercial', 'Commercial'),
        ('Ambulance', 'Ambulance'),
        ('Sapeurs-pompiers', 'Sapeurs-pompiers'),
        ('Administratif', 'Administratif'),
        ('Convention_internationale', 'Convention internationale'),
    ]
    
    # Vehicle types are now dynamic through VehicleType model
    
    plaque_immatriculation = models.CharField(
        max_length=15, 
        primary_key=True,
        validators=[RegexValidator(r'^[0-9]{1,4}\s[A-Z]{2,3}$', 'Format: 1234 TAA')]
    )
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicules')
    puissance_fiscale_cv = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Puissance Fiscale (en CV)",
        help_text="Trouvez cette information sur votre carte grise. Elle est utilisée pour le calcul de la taxe."
    )
    cylindree_cm3 = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cylindrée (en Cm3 ou cc)",
        help_text="Ex: 110 pour un scooter, 1900 pour une voiture",
        default=1000  # Default value for existing records (typical small car engine)
    )
    source_energie = models.CharField(
        max_length=20, 
        choices=SOURCE_ENERGIE_CHOICES,
        verbose_name="Source d'énergie"
    )
    date_premiere_circulation = models.DateField(verbose_name="Date de première circulation")
    categorie_vehicule = models.CharField(
        max_length=50, 
        choices=CATEGORIE_CHOICES,
        default='Personnel',
        verbose_name="Catégorie de véhicule"
    )
    type_vehicule = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        verbose_name="Type de véhicule",
        help_text="Type spécifique du véhicule (Voiture, Moto, Scooter, etc.)",
        related_name='vehicules'
    )
    specifications_techniques = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Spécifications techniques"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        indexes = [
            models.Index(fields=['proprietaire']),
            models.Index(fields=['categorie_vehicule']),
            models.Index(fields=['type_vehicule']),
            models.Index(fields=['source_energie']),
            models.Index(fields=['puissance_fiscale_cv']),
        ]
    
    def __str__(self):
        return f"{self.plaque_immatriculation} - {self.proprietaire.get_full_name()}"
    
    def get_age_annees(self):
        """Calculate vehicle age in years"""
        today = timezone.now().date()
        return today.year - self.date_premiere_circulation.year
    
    def est_exonere(self):
        """Check if vehicle is exempt from tax"""
        return self.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']
    
    def auto_determine_puissance_fiscale(self):
        """
        Détermine automatiquement la puissance fiscale à partir de la cylindrée
        """
        return get_puissance_fiscale_from_cylindree(self.cylindree_cm3)
    
    def get_plage_cv_description(self):
        """
        Retourne la description de la plage de CV pour cette cylindrée
        """
        return get_plage_cv_description(self.cylindree_cm3)
    
    def clean(self):
        """
        Validation personnalisée pour vérifier la cohérence cylindrée/CV
        """
        super().clean()
        
        if self.cylindree_cm3 and self.puissance_fiscale_cv:
            est_coherent, message = valider_coherence_cylindree_cv(
                self.cylindree_cm3, 
                self.puissance_fiscale_cv
            )
            if not est_coherent:
                raise ValidationError({
                    'puissance_fiscale_cv': message
                })
    
    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation automatique
        """
        self.full_clean()
        super().save(*args, **kwargs)

class GrilleTarifaire(models.Model):
    """Tax grid for calculating vehicle taxes"""
    
    SOURCE_ENERGIE_CHOICES = [
        ('Essence', 'Essence'),
        ('Diesel', 'Diesel'),
        ('Electrique', 'Électrique'),
        ('Hybride', 'Hybride'),
    ]
    
    puissance_min_cv = models.PositiveIntegerField(verbose_name="Puissance min (CV)")
    puissance_max_cv = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Puissance max (CV)"
    )
    source_energie = models.CharField(
        max_length=20, 
        choices=SOURCE_ENERGIE_CHOICES,
        verbose_name="Source d'énergie"
    )
    age_min_annees = models.PositiveIntegerField(
        default=0,
        verbose_name="Âge minimum (années)"
    )
    age_max_annees = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Âge maximum (années)"
    )
    montant_ariary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant (Ariary)"
    )
    annee_fiscale = models.PositiveIntegerField(verbose_name="Année fiscale")
    est_active = models.BooleanField(default=True, verbose_name="Est active")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Grille tarifaire"
        verbose_name_plural = "Grilles tarifaires"
        unique_together = [
            ['puissance_min_cv', 'puissance_max_cv', 'source_energie', 
             'age_min_annees', 'age_max_annees', 'annee_fiscale']
        ]
        indexes = [
            models.Index(fields=['annee_fiscale', 'est_active']),
            models.Index(fields=['puissance_min_cv', 'puissance_max_cv', 'source_energie']),
        ]
    
    def __str__(self):
        puissance_range = f"{self.puissance_min_cv}"
        if self.puissance_max_cv:
            puissance_range += f"-{self.puissance_max_cv}"
        else:
            puissance_range += "+"
        
        age_range = f"{self.age_min_annees}"
        if self.age_max_annees:
            age_range += f"-{self.age_max_annees}"
        else:
            age_range += "+"
            
        return f"{puissance_range}CV {self.source_energie} {age_range}ans - {self.montant_ariary} Ar ({self.annee_fiscale})"
    
    def est_applicable(self, vehicule):
        """Check if this tax rate applies to a vehicle"""
        # Check power range
        if vehicule.puissance_fiscale_cv < self.puissance_min_cv:
            return False
        if self.puissance_max_cv and vehicule.puissance_fiscale_cv > self.puissance_max_cv:
            return False
        
        # Check energy source
        if vehicule.source_energie != self.source_energie:
            return False
        
        # Check age range
        age = vehicule.get_age_annees()
        if age < self.age_min_annees:
            return False
        if self.age_max_annees and age > self.age_max_annees:
            return False
        
        return True
    
    # Properties for template compatibility
    @property
    def rate(self):
        """Rate amount in Ariary (for template compatibility)"""
        return self.montant_ariary
    
    @property
    def name(self):
        """Grid name (for template compatibility)"""
        return f"{self.puissance_min_cv}CV {self.source_energie}"
    
    @property
    def code(self):
        """Grid code (for template compatibility)"""
        return f"GT-{self.puissance_min_cv}-{self.source_energie}"
    
    @property
    def fiscal_year(self):
        """Fiscal year (for template compatibility)"""
        return self.annee_fiscale
    
    @property
    def energy_source(self):
        """Energy source (for template compatibility)"""
        return self.source_energie
    
    @property
    def vehicle_category(self):
        """Vehicle category (for template compatibility)"""
        return "All Vehicles"  # Default since we don't have this field
    
    @property
    def is_active(self):
        """Active status (for template compatibility)"""
        return self.est_active
    
    @property
    def effective_date(self):
        """Effective date (for template compatibility)"""
        return self.created_at.date()
    
    @property
    def description(self):
        """Description (for template compatibility)"""
        age_range = f"{self.age_min_annees}"
        if self.age_max_annees:
            age_range += f"-{self.age_max_annees}"
        else:
            age_range += "+"
        
        puissance_range = f"{self.puissance_min_cv}"
        if self.puissance_max_cv:
            puissance_range += f"-{self.puissance_max_cv}"
        else:
            puissance_range += "+"
        
        return f"Tax rate for {puissance_range}CV {self.source_energie} vehicles, age {age_range} years"


class DocumentVehicule(models.Model):
    """Documents liés à un véhicule (carte grise, assurance, contrôle technique, etc.)"""
    DOCUMENT_TYPE_CHOICES = [
        ('carte_grise', 'Carte grise'),
        ('assurance', 'Assurance'),
        ('controle_technique', 'Contrôle technique'),
        ('photo_plaque', 'Photo de la plaque'),
        ('autre', 'Autre document'),
    ]
    VERIFICATION_STATUS_CHOICES = [
        ('soumis', 'Soumis'),
        ('verifie', 'Vérifié'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    fichier = models.FileField(upload_to='vehicle_documents/%Y/%m/%d')
    note = models.TextField(blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='soumis')
    verification_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document du véhicule"
        verbose_name_plural = "Documents du véhicule"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicule']),
            models.Index(fields=['document_type']),
            models.Index(fields=['verification_status']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.vehicule.plaque_immatriculation}"
