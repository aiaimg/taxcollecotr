import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class UserProfile(models.Model):
    """Extended user profile with role-based access control"""

    USER_TYPE_CHOICES = [
        ("individual", "Particulier (Citoyen)"),
        ("company", "Entreprise/Société"),
        ("public_institution", "Administration Publique et Institution"),
        ("international_organization", "Organisation Internationale"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
        ("under_review", "Under Review"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(
        max_length=30, choices=USER_TYPE_CHOICES, default="individual", verbose_name="Type d'utilisateur"
    )
    telephone = models.CharField(
        max_length=20, blank=True, validators=[RegexValidator(r"^\+?261\d{9}$", "Format: +261xxxxxxxxx")]
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True, verbose_name="Photo de profil"
    )
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="pending", verbose_name="Statut de vérification"
    )
    langue_preferee = models.CharField(max_length=5, choices=[("fr", "Français"), ("mg", "Malagasy")], default="fr")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Legacy field for backward compatibility
    est_entreprise = models.BooleanField(default=False, verbose_name="Est une entreprise")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        indexes = [
            models.Index(fields=["telephone"]),
            models.Index(fields=["user_type"]),
            models.Index(fields=["verification_status"]),
            models.Index(fields=["est_entreprise"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_user_type_display()})"

    def save(self, *args, **kwargs):
        # Update legacy field for backward compatibility
        self.est_entreprise = self.user_type == "company"

        # Optimize profile picture if it's being uploaded
        if self.profile_picture and hasattr(self.profile_picture, "file"):
            try:
                from core.utils import ImageOptimizer

                # Check if this is a new upload (not already optimized)
                if not self.profile_picture.name.endswith(".webp"):
                    optimized_image = ImageOptimizer.optimize_profile_picture(self.profile_picture)
                    self.profile_picture = optimized_image
            except Exception as e:
                # Log error but don't fail the save
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error optimizing profile picture: {str(e)}")

        super().save(*args, **kwargs)

    @property
    def is_verified(self):
        """Check if user is verified"""
        return self.verification_status == "verified"

    @property
    def can_register_vehicles(self):
        """Check if user can register vehicles"""
        # All user types can register vehicles, but some may need verification
        return self.is_verified or self.user_type in [
            "individual",
            "company",
            "public_institution",
            "international_organization",
        ]

    def get_allowed_vehicle_categories(self):
        """Retourne les catégories de véhicules autorisées pour ce type d'utilisateur"""
        if self.user_type == "individual":
            return ["Personnel"]
        elif self.user_type == "company":
            return ["Commercial"]  # Note: 'Transport' n'existe pas dans le modèle, utilisez 'Commercial'
        elif self.user_type == "public_institution":
            # Administration publique peut enregistrer tous types de véhicules administratifs
            # Note: Les véhicules de police et gendarmerie utilisent la catégorie 'Administratif'
            return [
                "Administratif",
                "Ambulance",
                "Sapeurs-pompiers",
                "Personnel",  # Pour les fonctionnaires
            ]
        elif self.user_type == "international_organization":
            # Organisations internationales peuvent enregistrer des véhicules sous convention internationale
            return [
                "Convention_internationale",
            ]
        return []

    def get_allowed_terrestrial_subtypes(self):
        """Retourne les sous-types de véhicules terrestres autorisés pour ce type d'utilisateur"""
        if self.user_type == "individual":
            return ["moto", "scooter", "voiture"]
        elif self.user_type == "company":
            return ["moto", "scooter", "voiture", "camion", "bus", "camionnette", "remorque"]
        elif self.user_type == "public_institution":
            # Administration publique peut enregistrer tous types de véhicules
            return ["moto", "scooter", "voiture", "camion", "bus", "camionnette", "remorque"]
        elif self.user_type == "international_organization":
            # Organisations internationales peuvent enregistrer tous types de véhicules
            return ["moto", "scooter", "voiture", "camion", "bus", "camionnette", "remorque"]
        return []

    def has_google_account(self):
        """Check if user has a linked Google account"""
        return self.user.socialaccount_set.filter(provider='google').exists()

    def get_google_email(self):
        """Get the email address associated with the linked Google account"""
        google_account = self.user.socialaccount_set.filter(provider='google').first()
        if google_account:
            return google_account.extra_data.get('email')
        return None


class EntrepriseProfile(models.Model):
    """Profile for company users - Legacy model, kept for backward compatibility"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="entreprise_profile")
    nom_entreprise = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    numero_contribuable = models.CharField(max_length=50, unique=True, verbose_name="Numéro de contribuable")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    contact_principal = models.CharField(max_length=100, blank=True, verbose_name="Contact principal")
    secteur_activite = models.CharField(max_length=100, blank=True, verbose_name="Secteur d'activité")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil entreprise"
        verbose_name_plural = "Profils entreprises"
        indexes = [
            models.Index(fields=["numero_contribuable"]),
            models.Index(fields=["nom_entreprise"]),
        ]

    def __str__(self):
        return self.nom_entreprise


class IndividualProfile(models.Model):
    """Profile for individual citizens"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="individual_profile")
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
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="company_profile")
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
            models.Index(fields=["tax_id"]),
            models.Index(fields=["company_name"]),
        ]

    def __str__(self):
        return self.company_name


class EmergencyServiceProfile(models.Model):
    """Profile for emergency service providers"""

    SERVICE_TYPE_CHOICES = [
        ("ambulance", "Service d'ambulance"),
        ("fire", "Sapeurs-pompiers"),
        ("rescue", "Service de secours"),
        ("medical", "Service médical d'urgence"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="emergency_profile")
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
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="government_profile")
    department = models.CharField(max_length=100, verbose_name="Département")
    position = models.CharField(max_length=100, blank=True, verbose_name="Poste")
    employee_id = models.CharField(max_length=50, blank=True, verbose_name="ID employé")
    access_level = models.IntegerField(
        default=1, choices=[(i, f"Niveau {i}") for i in range(1, 6)], verbose_name="Niveau d'accès"
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
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="law_enforcement_profile")
    badge_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de badge")
    department = models.CharField(max_length=100, verbose_name="Département")
    rank = models.CharField(max_length=50, blank=True, verbose_name="Grade")
    jurisdiction = models.CharField(max_length=100, blank=True, verbose_name="Juridiction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil forces de l'ordre"
        verbose_name_plural = "Profils forces de l'ordre"
        indexes = [
            models.Index(fields=["badge_number"]),
        ]

    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - Badge {self.badge_number}"


class PublicInstitutionProfile(models.Model):
    """Profil pour les administrations publiques et institutions"""

    INSTITUTION_TYPE_CHOICES = [
        ("ministere", "Ministère"),
        ("primature", "Primature"),
        ("assemblee_nationale", "Assemblée Nationale"),
        ("commune", "Commune"),
        ("service_urgence", "Service d'urgence"),
        ("forces_ordre", "Forces de l'ordre"),
        ("autre", "Autre institution publique"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="public_institution_profile"
    )
    institution_name = models.CharField(max_length=200, verbose_name="Nom de l'institution")
    institution_type = models.CharField(
        max_length=50, choices=INSTITUTION_TYPE_CHOICES, verbose_name="Type d'institution"
    )
    department = models.CharField(max_length=100, blank=True, verbose_name="Département/Service")
    official_registration_number = models.CharField(
        max_length=50, blank=True, verbose_name="Numéro d'enregistrement officiel"
    )
    address = models.TextField(blank=True, verbose_name="Adresse")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne de contact")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Administration Publique"
        verbose_name_plural = "Profils Administrations Publiques"
        indexes = [
            models.Index(fields=["institution_type"]),
            models.Index(fields=["institution_name"]),
        ]

    def __str__(self):
        return f"{self.institution_name} ({self.get_institution_type_display()})"


class InternationalOrganizationProfile(models.Model):
    """Profil pour les organisations internationales et missions diplomatiques"""

    ORGANIZATION_TYPE_CHOICES = [
        ("ambassade", "Ambassade"),
        ("consulat", "Consulat"),
        ("mission_diplomatique", "Mission diplomatique"),
        ("organisation_internationale", "Organisation internationale (ONU, etc.)"),
        ("ong_internationale", "ONG internationale"),
        ("autre", "Autre organisation sous convention internationale"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="international_organization_profile"
    )
    organization_name = models.CharField(max_length=200, verbose_name="Nom de l'organisation")
    organization_type = models.CharField(
        max_length=50, choices=ORGANIZATION_TYPE_CHOICES, verbose_name="Type d'organisation"
    )
    country_of_origin = models.CharField(max_length=100, blank=True, verbose_name="Pays d'origine")
    convention_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de convention")
    diplomatic_immunity = models.BooleanField(default=False, verbose_name="Immunité diplomatique")
    address = models.TextField(blank=True, verbose_name="Adresse")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne de contact")
    official_document_url = models.URLField(
        max_length=500, blank=True, verbose_name="Document officiel (convention, accord)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Organisation Internationale"
        verbose_name_plural = "Profils Organisations Internationales"
        indexes = [
            models.Index(fields=["organization_type"]),
            models.Index(fields=["organization_name"]),
            models.Index(fields=["country_of_origin"]),
        ]

    def __str__(self):
        return f"{self.organization_name} ({self.get_organization_type_display()})"


class VerificationDocument(models.Model):
    """Documents uploaded for user verification"""

    DOCUMENT_TYPE_CHOICES = [
        ("identity", "Pièce d'identité"),
        ("business_license", "Licence commerciale"),
        ("tax_certificate", "Certificat fiscal"),
        ("official_authorization", "Autorisation officielle"),
        ("badge_photo", "Photo de badge"),
        ("department_letter", "Lettre du département"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvé"),
        ("rejected", "Rejeté"),
        ("under_review", "En cours d'examen"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="verification_documents")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, verbose_name="Type de document")
    file_url = models.URLField(max_length=500, verbose_name="URL du fichier")
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="pending", verbose_name="Statut de vérification"
    )
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vérifié par")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Téléchargé le")

    class Meta:
        verbose_name = "Document de vérification"
        verbose_name_plural = "Documents de vérification"
        indexes = [
            models.Index(fields=["verification_status"]),
            models.Index(fields=["document_type"]),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user_profile.user.username}"


class AuditLog(models.Model):
    """Audit trail for all important actions"""

    ACTION_CHOICES = [
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
        ("LOGIN", "Connexion"),
        ("LOGOUT", "Déconnexion"),
        ("PAYMENT", "Paiement"),
        ("VERIFICATION", "Vérification"),
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
        ordering = ["-date_action"]
        indexes = [
            models.Index(fields=["user", "date_action"]),
            models.Index(fields=["action", "date_action"]),
            models.Index(fields=["table_concernee", "objet_id"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.table_concernee} - {self.date_action}"
