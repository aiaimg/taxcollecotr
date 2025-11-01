from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid

class UserProfile(models.Model):
    """Extended user profile with role-based access control"""
    
    USER_TYPE_CHOICES = [
        ('individual', 'Individual Citizen'),
        ('company', 'Company/Business'),
        ('emergency', 'Emergency Service Provider'),
        ('government', 'Government Administrator'),
        ('law_enforcement', 'Law Enforcement Officer'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='individual',
        verbose_name="Type d'utilisateur"
    )
    telephone = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\+?261\d{9}$', 'Format: +261xxxxxxxxx')]
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        verbose_name="Statut de vérification"
    )
    langue_preferee = models.CharField(
        max_length=5, 
        choices=[('fr', 'Français'), ('mg', 'Malagasy')], 
        default='fr'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Legacy field for backward compatibility
    est_entreprise = models.BooleanField(default=False, verbose_name="Est une entreprise")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        indexes = [
            models.Index(fields=['telephone']),
            models.Index(fields=['user_type']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['est_entreprise']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        # Update legacy field for backward compatibility
        self.est_entreprise = (self.user_type == 'company')
        super().save(*args, **kwargs)
    
    @property
    def is_verified(self):
        """Check if user is verified"""
        return self.verification_status == 'verified'
    
    @property
    def can_register_vehicles(self):
        """Check if user can register vehicles"""
        return self.is_verified or self.user_type in ['individual', 'company']
    
    def get_allowed_vehicle_categories(self):
        """Get allowed vehicle categories for this user type"""
        if self.user_type == 'individual':
            return ['Personnel']
        elif self.user_type == 'company':
            return ['Commercial', 'Transport']
        elif self.user_type == 'emergency':
            return ['Ambulance', 'Sapeurs-pompiers', 'Secours']
        elif self.user_type == 'government':
            return ['Administratif', 'Personnel', 'Commercial', 'Transport', 'Ambulance', 'Sapeurs-pompiers']
        elif self.user_type == 'law_enforcement':
            return ['Police', 'Gendarmerie', 'Personnel']
        return []
    
    def get_allowed_terrestrial_subtypes(self):
        """Get allowed terrestrial vehicle subtypes for this user type"""
        if self.user_type == 'individual':
            return ['moto', 'scooter', 'voiture']
        elif self.user_type == 'company':
            return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']
        elif self.user_type == 'emergency':
            return ['voiture', 'camion', 'bus', 'camionnette']  # Emergency vehicles
        elif self.user_type == 'government':
            return ['moto', 'scooter', 'voiture', 'camion', 'bus', 'camionnette', 'remorque']  # All types
        elif self.user_type == 'law_enforcement':
            return ['moto', 'scooter', 'voiture', 'camion']  # Police vehicles
        return []

class EntrepriseProfile(models.Model):
    """Profile for company users - Legacy model, kept for backward compatibility"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='entreprise_profile')
    nom_entreprise = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    numero_contribuable = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Numéro de contribuable"
    )
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    contact_principal = models.CharField(max_length=100, blank=True, verbose_name="Contact principal")
    secteur_activite = models.CharField(max_length=100, blank=True, verbose_name="Secteur d'activité")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil entreprise"
        verbose_name_plural = "Profils entreprises"
        indexes = [
            models.Index(fields=['numero_contribuable']),
            models.Index(fields=['nom_entreprise']),
        ]
    
    def __str__(self):
        return self.nom_entreprise


class IndividualProfile(models.Model):
    """Profile for individual citizens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='individual_profile')
    identity_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro d'identité")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    address = models.TextField(blank=True, verbose_name="Adresse")
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name="Contact d'urgence")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil individuel"
        verbose_name_plural = "Profils individuels"
    
    def __str__(self):
        return f"Profil individuel - {self.user_profile.user.get_full_name() or self.user_profile.user.username}"


class CompanyProfile(models.Model):
    """Profile for company/business users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    tax_id = models.CharField(max_length=50, unique=True, verbose_name="Numéro fiscal (NIF)")
    business_registration_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro d'immatriculation")
    industry_sector = models.CharField(max_length=100, blank=True, verbose_name="Secteur d'activité")
    fleet_size = models.IntegerField(default=0, verbose_name="Taille de la flotte")
    address = models.TextField(blank=True, verbose_name="Adresse")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil entreprise"
        verbose_name_plural = "Profils entreprises"
        indexes = [
            models.Index(fields=['tax_id']),
            models.Index(fields=['company_name']),
        ]
    
    def __str__(self):
        return self.company_name


class EmergencyServiceProfile(models.Model):
    """Profile for emergency service providers"""
    
    SERVICE_TYPE_CHOICES = [
        ('ambulance', 'Service d\'ambulance'),
        ('fire', 'Sapeurs-pompiers'),
        ('rescue', 'Service de secours'),
        ('medical', 'Service médical d\'urgence'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='emergency_profile')
    organization_name = models.CharField(max_length=200, verbose_name="Nom de l'organisation")
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, verbose_name="Type de service")
    official_license = models.CharField(max_length=100, blank=True, verbose_name="Licence officielle")
    department_contact = models.CharField(max_length=100, blank=True, verbose_name="Contact du département")
    verification_document_url = models.URLField(max_length=500, blank=True, verbose_name="Document de vérification")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil service d'urgence"
        verbose_name_plural = "Profils services d'urgence"
    
    def __str__(self):
        return f"{self.organization_name} ({self.get_service_type_display()})"


class GovernmentAdminProfile(models.Model):
    """Profile for government administrators"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='government_profile')
    department = models.CharField(max_length=100, verbose_name="Département")
    position = models.CharField(max_length=100, blank=True, verbose_name="Poste")
    employee_id = models.CharField(max_length=50, blank=True, verbose_name="ID employé")
    access_level = models.IntegerField(
        default=1, 
        choices=[(i, f"Niveau {i}") for i in range(1, 6)],
        verbose_name="Niveau d'accès"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil administrateur gouvernemental"
        verbose_name_plural = "Profils administrateurs gouvernementaux"
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.department}"


class LawEnforcementProfile(models.Model):
    """Profile for law enforcement officers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='law_enforcement_profile')
    badge_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de badge")
    department = models.CharField(max_length=100, verbose_name="Département")
    rank = models.CharField(max_length=50, blank=True, verbose_name="Grade")
    jurisdiction = models.CharField(max_length=100, blank=True, verbose_name="Juridiction")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil forces de l'ordre"
        verbose_name_plural = "Profils forces de l'ordre"
        indexes = [
            models.Index(fields=['badge_number']),
        ]
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - Badge {self.badge_number}"


class VerificationDocument(models.Model):
    """Documents uploaded for user verification"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('identity', 'Pièce d\'identité'),
        ('business_license', 'Licence commerciale'),
        ('tax_certificate', 'Certificat fiscal'),
        ('official_authorization', 'Autorisation officielle'),
        ('badge_photo', 'Photo de badge'),
        ('department_letter', 'Lettre du département'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('under_review', 'En cours d\'examen'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, verbose_name="Type de document")
    file_url = models.URLField(max_length=500, verbose_name="URL du fichier")
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending',
        verbose_name="Statut de vérification"
    )
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vérifié par")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Téléchargé le")
    
    class Meta:
        verbose_name = "Document de vérification"
        verbose_name_plural = "Documents de vérification"
        indexes = [
            models.Index(fields=['verification_status']),
            models.Index(fields=['document_type']),
        ]
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user_profile.user.username}"

class AuditLog(models.Model):
    """Audit trail for all important actions"""
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('PAYMENT', 'Paiement'),
        ('VERIFICATION', 'Vérification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    table_concernee = models.CharField(max_length=50, verbose_name="Table concernée")
    objet_id = models.CharField(max_length=50, blank=True, verbose_name="ID de l'objet")
    donnees_avant = models.JSONField(null=True, blank=True, verbose_name="Données avant")
    donnees_apres = models.JSONField(null=True, blank=True, verbose_name="Données après")
    adresse_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="ID de session")
    date_action = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'action")
    
    class Meta:
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['user', 'date_action']),
            models.Index(fields=['action', 'date_action']),
            models.Index(fields=['table_concernee', 'objet_id']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.table_concernee} - {self.date_action}"
