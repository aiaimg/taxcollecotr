# Spécifications Techniques - Modèles Django Étendus

## Vue d'ensemble

Ce document détaille les modifications et extensions nécessaires aux modèles Django existants pour implémenter toutes les fonctionnalités MVP du système de collecte de taxes véhicules.

---

## 1. Extensions du Modèle Vehicule

### 1.1 Nouveaux Champs Obligatoires

```python
# vehicles/models.py - Ajouts au modèle existant

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import uuid

class Vehicule(models.Model):
    # === CHAMPS EXISTANTS CONSERVÉS ===
    # proprietaire, plaque_immatriculation, puissance_fiscale_cv, etc.
    
    # === NOUVEAUX CHAMPS IDENTIFICATION VÉHICULE ===
    vin_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-HJ-NPR-Z0-9]{17}$',
            message='Le VIN doit contenir exactement 17 caractères alphanumériques (sans I, O, Q)'
        )],
        verbose_name="Numéro VIN",
        help_text="Numéro d'identification du véhicule (17 caractères)"
    )
    
    marque = models.CharField(
        max_length=50,
        verbose_name="Marque du véhicule",
        help_text="Ex: Toyota, Peugeot, Honda, Hyundai"
    )
    
    modele = models.CharField(
        max_length=100,
        verbose_name="Modèle du véhicule",
        help_text="Ex: Corolla, 206, Civic, Accent"
    )
    
    version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Version/Finition",
        help_text="Ex: GLX, Sport, Comfort"
    )
    
    # === CARACTÉRISTIQUES PHYSIQUES ===
    couleur_principale = models.CharField(
        max_length=30,
        choices=[
            ('blanc', 'Blanc'),
            ('noir', 'Noir'),
            ('gris', 'Gris'),
            ('rouge', 'Rouge'),
            ('bleu', 'Bleu'),
            ('vert', 'Vert'),
            ('jaune', 'Jaune'),
            ('orange', 'Orange'),
            ('marron', 'Marron'),
            ('violet', 'Violet'),
            ('argent', 'Argent'),
            ('autre', 'Autre')
        ],
        verbose_name="Couleur principale"
    )
    
    couleur_secondaire = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Couleur secondaire"
    )
    
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Nombre de places assises"
    )
    
    nombre_portes = models.PositiveIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(6)],
        null=True, blank=True,
        verbose_name="Nombre de portes"
    )
    
    # === POIDS ET DIMENSIONS ===
    poids_vide_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Poids à vide (kg)",
        help_text="Poids du véhicule sans chargement"
    )
    
    poids_total_autorise_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Poids total autorisé en charge (kg)"
    )
    
    charge_utile_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Charge utile maximale (kg)"
    )
    
    longueur_mm = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Longueur (mm)"
    )
    
    largeur_mm = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Largeur (mm)"
    )
    
    hauteur_mm = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Hauteur (mm)"
    )
    
    # === INFORMATIONS CARTE GRISE ===
    numero_carte_grise = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de carte grise",
        help_text="Numéro officiel de la carte grise"
    )
    
    date_delivrance_carte_grise = models.DateField(
        verbose_name="Date de délivrance carte grise"
    )
    
    prefecture_delivrance = models.CharField(
        max_length=100,
        verbose_name="Préfecture de délivrance",
        help_text="Lieu de délivrance de la carte grise"
    )
    
    numero_serie_carte_grise = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numéro de série carte grise"
    )
    
    # === STATUT ET VÉRIFICATION ===
    statut_verification = models.CharField(
        max_length=25,
        choices=[
            ('en_attente', 'En attente de vérification'),
            ('documents_incomplets', 'Documents incomplets'),
            ('en_cours_verification', 'En cours de vérification'),
            ('verifie', 'Vérifié et validé'),
            ('rejete', 'Rejeté'),
            ('suspendu', 'Suspendu')
        ],
        default='en_attente',
        verbose_name="Statut de vérification"
    )
    
    date_derniere_verification = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de dernière vérification"
    )
    
    verifie_par = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vehicules_verifies',
        verbose_name="Vérifié par (agent)"
    )
    
    commentaires_verification = models.TextField(
        blank=True,
        verbose_name="Commentaires de vérification"
    )
    
    # === DONNÉES OCR ===
    donnees_ocr_extraites = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données extraites par OCR",
        help_text="Données automatiquement extraites des documents scannés"
    )
    
    precision_ocr = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Précision OCR (0-1)",
        help_text="Niveau de confiance de l'extraction OCR"
    )
    
    ocr_necessite_verification = models.BooleanField(
        default=False,
        verbose_name="OCR nécessite vérification manuelle"
    )
    
    # === MÉTADONNÉES ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        indexes = [
            models.Index(fields=['vin_number']),
            models.Index(fields=['numero_carte_grise']),
            models.Index(fields=['marque', 'modele']),
            models.Index(fields=['statut_verification']),
            models.Index(fields=['proprietaire', 'statut_verification']),
        ]
    
    def __str__(self):
        return f"{self.plaque_immatriculation} - {self.marque} {self.modele}"
    
    # === NOUVELLES MÉTHODES ===
    def est_completement_verifie(self):
        """Vérifie si le véhicule est complètement vérifié"""
        return (
            self.statut_verification == 'verifie' and
            self.documents.filter(
                type_document='carte_grise',
                statut_verification='valide'
            ).exists()
        )
    
    def get_documents_manquants(self):
        """Retourne la liste des documents manquants"""
        documents_requis = ['carte_grise']
        documents_existants = list(
            self.documents.filter(
                statut_verification__in=['valide', 'en_cours']
            ).values_list('type_document', flat=True)
        )
        return [doc for doc in documents_requis if doc not in documents_existants]
    
    def peut_generer_qr_code(self):
        """Vérifie si le véhicule peut générer un QR code"""
        return (
            self.est_completement_verifie() and
            self.paiements.filter(
                statut='PAYE',
                annee_fiscale=timezone.now().year
            ).exists()
        )
```

### 1.2 Migration Django

```python
# vehicles/migrations/0003_extend_vehicule_model.py

from django.db import migrations, models
import django.core.validators
import uuid

class Migration(migrations.Migration):
    
    dependencies = [
        ('vehicles', '0002_previous_migration'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='vehicule',
            name='vin_number',
            field=models.CharField(
                max_length=17,
                unique=True,
                validators=[django.core.validators.RegexValidator(
                    regex='^[A-HJ-NPR-Z0-9]{17}$',
                    message='Le VIN doit contenir exactement 17 caractères alphanumériques'
                )],
                verbose_name='Numéro VIN',
                null=True  # Temporaire pour migration
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='marque',
            field=models.CharField(max_length=50, verbose_name='Marque du véhicule', null=True),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='modele',
            field=models.CharField(max_length=100, verbose_name='Modèle du véhicule', null=True),
        ),
        # ... autres champs
        
        # Ajout des index
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_vehicule_vin ON vehicles_vehicule(vin_number);",
            reverse_sql="DROP INDEX IF EXISTS idx_vehicule_vin;"
        ),
    ]
```

---

## 2. Extension du Modèle IndividualProfile

### 2.1 Ajout des Informations CIN

```python
# core/models.py - Extension du modèle existant

class IndividualProfile(models.Model):
    # === CHAMPS EXISTANTS CONSERVÉS ===
    # user, identity_number, etc.
    
    # === INFORMATIONS CIN DÉTAILLÉES ===
    numero_cin = models.CharField(
        max_length=12,
        unique=True,
        null=True, blank=True,
        validators=[RegexValidator(
            regex=r'^\d{12}$',
            message='Le numéro CIN doit contenir exactement 12 chiffres'
        )],
        verbose_name="Numéro CIN",
        help_text="Numéro de Carte d'Identité Nationale (12 chiffres)"
    )
    
    date_delivrance_cin = models.DateField(
        null=True, blank=True,
        verbose_name="Date de délivrance CIN"
    )
    
    lieu_delivrance_cin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Lieu de délivrance CIN",
        help_text="Commune ou fokontany de délivrance"
    )
    
    date_expiration_cin = models.DateField(
        null=True, blank=True,
        verbose_name="Date d'expiration CIN"
    )
    
    # === INFORMATIONS PERSONNELLES COMPLÉMENTAIRES ===
    nom_pere = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du père"
    )
    
    nom_mere = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom de la mère"
    )
    
    profession = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Profession"
    )
    
    situation_familiale = models.CharField(
        max_length=20,
        choices=[
            ('celibataire', 'Célibataire'),
            ('marie', 'Marié(e)'),
            ('divorce', 'Divorcé(e)'),
            ('veuf', 'Veuf/Veuve'),
            ('concubinage', 'En concubinage')
        ],
        blank=True,
        verbose_name="Situation familiale"
    )
    
    # === ADRESSE DÉTAILLÉE ===
    region = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Région"
    )
    
    district = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="District"
    )
    
    commune = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Commune"
    )
    
    fokontany = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fokontany"
    )
    
    adresse_complete = models.TextField(
        blank=True,
        verbose_name="Adresse complète"
    )
    
    # === VÉRIFICATION CIN ===
    cin_verifie = models.BooleanField(
        default=False,
        verbose_name="CIN vérifié"
    )
    
    date_verification_cin = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de vérification CIN"
    )
    
    cin_verifie_par = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cin_verifies',
        verbose_name="CIN vérifié par"
    )
    
    def cin_est_valide(self):
        """Vérifie si le CIN est valide et non expiré"""
        if not self.numero_cin or not self.date_expiration_cin:
            return False
        return self.date_expiration_cin > timezone.now().date()
    
    def peut_posseder_vehicule(self):
        """Vérifie si la personne peut posséder un véhicule"""
        return self.cin_verifie and self.cin_est_valide()
```

---

## 3. Nouveau Modèle DocumentVehicule

### 3.1 Modèle Complet

```python
# core/models.py - Nouveau modèle

class DocumentVehicule(models.Model):
    """
    Modèle pour gérer tous les documents associés aux véhicules
    Supporte l'upload, l'OCR et la vérification manuelle
    """
    
    TYPE_DOCUMENT_CHOICES = [
        ('carte_grise', 'Carte grise'),
        ('certificat_immatriculation', 'Certificat d\'immatriculation'),
        ('controle_technique', 'Contrôle technique'),
        ('assurance', 'Attestation d\'assurance'),
        ('facture_achat', 'Facture d\'achat'),
        ('permis_conduire', 'Permis de conduire'),
        ('cin_proprietaire', 'CIN du propriétaire'),
        ('procuration', 'Procuration (si applicable)'),
        ('autre', 'Autre document')
    ]
    
    STATUT_VERIFICATION_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de vérification'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('expire', 'Expiré'),
        ('incomplet', 'Document incomplet')
    ]
    
    NIVEAU_PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('critique', 'Critique')
    ]
    
    # === IDENTIFICATION ===
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    vehicule = models.ForeignKey(
        'vehicles.Vehicule',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Véhicule associé"
    )
    
    # === TYPE ET MÉTADONNÉES ===
    type_document = models.CharField(
        max_length=30,
        choices=TYPE_DOCUMENT_CHOICES,
        verbose_name="Type de document"
    )
    
    titre_document = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Titre du document"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # === FICHIER ===
    fichier_url = models.URLField(
        max_length=500,
        verbose_name="URL du fichier"
    )
    
    nom_fichier_original = models.CharField(
        max_length=255,
        verbose_name="Nom du fichier original"
    )
    
    taille_fichier = models.PositiveIntegerField(
        verbose_name="Taille du fichier (bytes)"
    )
    
    type_mime = models.CharField(
        max_length=100,
        verbose_name="Type MIME"
    )
    
    hash_fichier = models.CharField(
        max_length=64,
        verbose_name="Hash SHA-256 du fichier",
        help_text="Pour vérifier l'intégrité"
    )
    
    # === DONNÉES OCR ===
    donnees_extraites = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données extraites par OCR"
    )
    
    precision_ocr = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Précision OCR (0-1)"
    )
    
    texte_brut_ocr = models.TextField(
        blank=True,
        verbose_name="Texte brut extrait par OCR"
    )
    
    ocr_traite = models.BooleanField(
        default=False,
        verbose_name="OCR traité"
    )
    
    date_traitement_ocr = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de traitement OCR"
    )
    
    # === VÉRIFICATION ===
    statut_verification = models.CharField(
        max_length=20,
        choices=STATUT_VERIFICATION_CHOICES,
        default='en_attente',
        verbose_name="Statut de vérification"
    )
    
    priorite_verification = models.CharField(
        max_length=15,
        choices=NIVEAU_PRIORITE_CHOICES,
        default='normale',
        verbose_name="Priorité de vérification"
    )
    
    verifie_par = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documents_verifies',
        verbose_name="Vérifié par"
    )
    
    date_verification = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de vérification"
    )
    
    commentaires_verification = models.TextField(
        blank=True,
        verbose_name="Commentaires de vérification"
    )
    
    score_confiance = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score de confiance global"
    )
    
    # === VALIDITÉ ===
    date_expiration_document = models.DateField(
        null=True, blank=True,
        verbose_name="Date d'expiration du document"
    )
    
    est_expire = models.BooleanField(
        default=False,
        verbose_name="Document expiré"
    )
    
    # === AUDIT ===
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documents_uploades',
        verbose_name="Uploadé par"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'upload"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    version = models.PositiveIntegerField(
        default=1,
        verbose_name="Version du document"
    )
    
    class Meta:
        verbose_name = "Document véhicule"
        verbose_name_plural = "Documents véhicules"
        unique_together = [
            ('vehicule', 'type_document', 'version')
        ]
        indexes = [
            models.Index(fields=['vehicule', 'type_document']),
            models.Index(fields=['statut_verification', 'priorite_verification']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['date_expiration_document']),
        ]
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.vehicule.plaque_immatriculation}"
    
    # === MÉTHODES ===
    def est_valide(self):
        """Vérifie si le document est valide"""
        return (
            self.statut_verification == 'valide' and
            not self.est_expire and
            (not self.date_expiration_document or 
             self.date_expiration_document > timezone.now().date())
        )
    
    def necessite_renouvellement(self, jours_avant=30):
        """Vérifie si le document nécessite un renouvellement"""
        if not self.date_expiration_document:
            return False
        
        date_limite = timezone.now().date() + timedelta(days=jours_avant)
        return self.date_expiration_document <= date_limite
    
    def get_url_securisee(self):
        """Retourne une URL sécurisée avec token temporaire"""
        # Implémentation avec token JWT ou signature
        pass
    
    def marquer_comme_expire(self):
        """Marque le document comme expiré"""
        self.est_expire = True
        self.statut_verification = 'expire'
        self.save()
    
    def creer_nouvelle_version(self, nouveau_fichier_url, uploaded_by):
        """Crée une nouvelle version du document"""
        nouvelle_version = DocumentVehicule.objects.create(
            vehicule=self.vehicule,
            type_document=self.type_document,
            fichier_url=nouveau_fichier_url,
            version=self.version + 1,
            uploaded_by=uploaded_by,
            # ... autres champs
        )
        
        # Marquer l'ancienne version comme obsolète
        self.statut_verification = 'expire'
        self.save()
        
        return nouvelle_version
```

---

## 4. Modèle de Suivi des Modifications

### 4.1 AuditLog Étendu

```python
# core/models.py

class AuditLogVehicule(models.Model):
    """
    Log d'audit spécifique aux véhicules et documents
    """
    
    ACTION_CHOICES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('verification', 'Vérification'),
        ('rejet', 'Rejet'),
        ('suppression', 'Suppression'),
        ('upload_document', 'Upload document'),
        ('ocr_traitement', 'Traitement OCR'),
        ('paiement', 'Paiement'),
        ('generation_qr', 'Génération QR code')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # === RÉFÉRENCES ===
    vehicule = models.ForeignKey(
        'vehicles.Vehicule',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='audit_logs'
    )
    
    document = models.ForeignKey(
        'DocumentVehicule',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='audit_logs'
    )
    
    # === ACTION ===
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action effectuée"
    )
    
    description = models.TextField(
        verbose_name="Description de l'action"
    )
    
    # === UTILISATEUR ===
    utilisateur = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Utilisateur"
    )
    
    adresse_ip = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="Adresse IP"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    # === DONNÉES ===
    donnees_avant = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données avant modification"
    )
    
    donnees_apres = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données après modification"
    )
    
    # === MÉTADONNÉES ===
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Horodatage"
    )
    
    session_id = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="ID de session"
    )
    
    class Meta:
        verbose_name = "Log d'audit véhicule"
        verbose_name_plural = "Logs d'audit véhicules"
        indexes = [
            models.Index(fields=['vehicule', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['utilisateur', 'timestamp']),
        ]
        ordering = ['-timestamp']
```

---

## 5. Signaux Django pour Automatisation

### 5.1 Signaux de Gestion Automatique

```python
# vehicles/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Vehicule, DocumentVehicule
from core.models import AuditLogVehicule

@receiver(post_save, sender=DocumentVehicule)
def traiter_document_apres_upload(sender, instance, created, **kwargs):
    """
    Traite automatiquement le document après upload
    """
    if created and instance.type_document == 'carte_grise':
        # Déclencher le traitement OCR asynchrone
        from .tasks import traiter_ocr_carte_grise
        traiter_ocr_carte_grise.delay(instance.id)

@receiver(post_save, sender=Vehicule)
def log_modification_vehicule(sender, instance, created, **kwargs):
    """
    Log automatique des modifications de véhicule
    """
    action = 'creation' if created else 'modification'
    
    AuditLogVehicule.objects.create(
        vehicule=instance,
        action=action,
        description=f"Véhicule {action} - {instance.plaque_immatriculation}",
        # utilisateur sera ajouté via middleware
    )

@receiver(pre_save, sender=DocumentVehicule)
def verifier_expiration_document(sender, instance, **kwargs):
    """
    Vérifie automatiquement l'expiration des documents
    """
    if instance.date_expiration_document:
        if instance.date_expiration_document <= timezone.now().date():
            instance.est_expire = True
            instance.statut_verification = 'expire'
```

---

## 6. Commandes de Migration

### 6.1 Script de Migration Complète

```bash
# Commandes à exécuter dans l'ordre

# 1. Créer les migrations
python manage.py makemigrations core
python manage.py makemigrations vehicles

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer les index supplémentaires
python manage.py dbshell << EOF
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicule_verification_status 
ON vehicles_vehicule(statut_verification, date_derniere_verification);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_priorite_verification 
ON core_documentvehicule(priorite_verification, statut_verification, uploaded_at);
EOF

# 4. Mise à jour des données existantes (si nécessaire)
python manage.py shell << EOF
from vehicles.models import Vehicule
# Mise à jour des véhicules existants avec des valeurs par défaut
Vehicule.objects.filter(statut_verification__isnull=True).update(
    statut_verification='en_attente'
)
EOF
```

Cette architecture de modèles étendus fournit une base solide pour implémenter toutes les fonctionnalités MVP avec une traçabilité complète et une gestion automatisée des documents.