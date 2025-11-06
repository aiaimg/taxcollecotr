# Spécifications Techniques - Fonctionnalités Manquantes MVP

## 1. Extensions des Modèles de Données

### 1.1 Extension du Modèle IndividualProfile

```python
# Ajouts nécessaires au modèle core/models.py - IndividualProfile

class IndividualProfile(models.Model):
    # Champs existants...
    
    # Nouveaux champs pour carte d'identité nationale
    national_id_number = models.CharField(
        max_length=20, 
        blank=True, 
        unique=True,
        validators=[RegexValidator(r'^\d{12}$', 'Format: 12 chiffres')],
        verbose_name="Numéro de carte d'identité nationale"
    )
    national_id_issue_date = models.DateField(
        null=True, blank=True,
        verbose_name="Date d'émission de la CIN"
    )
    national_id_expiry_date = models.DateField(
        null=True, blank=True,
        verbose_name="Date d'expiration de la CIN"
    )
    national_id_issue_place = models.CharField(
        max_length=100, blank=True,
        verbose_name="Lieu d'émission de la CIN"
    )
    
    # Documents scannés
    national_id_front_scan = models.URLField(
        max_length=500, blank=True,
        verbose_name="Scan recto de la CIN"
    )
    national_id_back_scan = models.URLField(
        max_length=500, blank=True,
        verbose_name="Scan verso de la CIN"
    )
    
    # Validation automatique
    id_verification_status = models.CharField(
        max_length=20,
        choices=[
            ('not_provided', 'Non fournie'),
            ('pending', 'En attente de vérification'),
            ('verified', 'Vérifiée'),
            ('rejected', 'Rejetée'),
            ('expired', 'Expirée')
        ],
        default='not_provided',
        verbose_name="Statut de vérification CIN"
    )
    id_verified_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de vérification CIN"
    )
    id_verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='verified_ids',
        verbose_name="Vérifié par"
    )
```

### 1.2 Nouveau Modèle VehicleRegistrationDocument

```python
# Nouveau modèle à ajouter dans vehicles/models.py

class VehicleRegistrationDocument(models.Model):
    """Documents de carte grise et informations détaillées du véhicule"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule = models.OneToOneField(
        Vehicule, 
        on_delete=models.CASCADE,
        related_name='registration_document'
    )
    
    # Informations de la carte grise
    carte_grise_numero = models.CharField(
        max_length=50, unique=True,
        verbose_name="Numéro de carte grise"
    )
    vin_number = models.CharField(
        max_length=17, blank=True,
        validators=[RegexValidator(r'^[A-HJ-NPR-Z0-9]{17}$', 'Format VIN invalide')],
        verbose_name="Numéro de série (VIN)"
    )
    
    # Détails du véhicule
    marque = models.CharField(max_length=50, verbose_name="Marque")
    modele = models.CharField(max_length=100, verbose_name="Modèle")
    couleur = models.CharField(max_length=30, verbose_name="Couleur")
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Nombre de places"
    )
    poids_vide_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Poids à vide (kg)"
    )
    charge_utile_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Charge utile (kg)"
    )
    
    # Documents scannés
    carte_grise_scan_front = models.URLField(
        max_length=500, blank=True,
        verbose_name="Scan recto carte grise"
    )
    carte_grise_scan_back = models.URLField(
        max_length=500, blank=True,
        verbose_name="Scan verso carte grise"
    )
    
    # Validation et vérification
    document_verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('verified', 'Vérifié'),
            ('rejected', 'Rejeté'),
            ('incomplete', 'Incomplet')
        ],
        default='pending',
        verbose_name="Statut de vérification"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='verified_vehicle_docs'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Document d'immatriculation"
        verbose_name_plural = "Documents d'immatriculation"
        indexes = [
            models.Index(fields=['carte_grise_numero']),
            models.Index(fields=['vin_number']),
            models.Index(fields=['document_verification_status']),
        ]
```

### 1.3 Extension du Modèle PaiementTaxe

```python
# Ajouts au modèle payments/models.py - PaiementTaxe

class PaiementTaxe(models.Model):
    # Champs existants...
    
    # Nouveaux champs pour intégration paiement
    payment_provider_transaction_id = models.CharField(
        max_length=200, blank=True,
        verbose_name="ID transaction fournisseur"
    )
    payment_provider_reference = models.CharField(
        max_length=200, blank=True,
        verbose_name="Référence fournisseur"
    )
    payment_callback_data = models.JSONField(
        default=dict, blank=True,
        verbose_name="Données callback paiement"
    )
    
    # Gestion des échecs et reprises
    payment_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de tentatives"
    )
    last_payment_error = models.TextField(
        blank=True,
        verbose_name="Dernière erreur de paiement"
    )
    
    # Remboursements
    refund_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant remboursé"
    )
    refund_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de remboursement"
    )
    refund_reason = models.TextField(
        blank=True,
        verbose_name="Raison du remboursement"
    )
```

## 2. Services d'Intégration

### 2.1 Service de Vérification d'Identité

```python
# Nouveau fichier: core/services/identity_verification.py

class IdentityVerificationService:
    """Service de vérification des cartes d'identité nationales"""
    
    @staticmethod
    def verify_national_id(national_id_number, user_profile):
        """
        Vérifie un numéro de CIN avec les bases de données officielles
        """
        try:
            # Intégration avec l'API gouvernementale de vérification d'identité
            response = requests.post(
                settings.NATIONAL_ID_VERIFICATION_API_URL,
                headers={
                    'Authorization': f'Bearer {settings.NATIONAL_ID_API_TOKEN}',
                    'Content-Type': 'application/json'
                },
                json={
                    'national_id': national_id_number,
                    'first_name': user_profile.user.first_name,
                    'last_name': user_profile.user.last_name
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': data.get('valid', False),
                    'details': data.get('details', {}),
                    'message': data.get('message', '')
                }
            else:
                return {
                    'valid': False,
                    'error': f'API Error: {response.status_code}',
                    'message': 'Erreur de vérification'
                }
                
        except requests.RequestException as e:
            logger.error(f"Identity verification error: {e}")
            return {
                'valid': False,
                'error': str(e),
                'message': 'Service de vérification indisponible'
            }
    
    @staticmethod
    def extract_data_from_id_scan(image_url):
        """
        Extraction OCR des données depuis le scan de CIN
        """
        # Intégration avec service OCR (Google Vision, AWS Textract, etc.)
        pass
```

### 2.2 Service de Vérification des Immatriculations

```python
# Nouveau fichier: vehicles/services/registration_verification.py

class VehicleRegistrationVerificationService:
    """Service de vérification des immatriculations"""
    
    @staticmethod
    def verify_license_plate(plate_number):
        """
        Vérifie l'existence et la validité d'une plaque d'immatriculation
        """
        try:
            response = requests.get(
                f"{settings.VEHICLE_REGISTRY_API_URL}/verify/{plate_number}",
                headers={
                    'Authorization': f'Bearer {settings.VEHICLE_REGISTRY_API_TOKEN}'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exists': data.get('exists', False),
                    'valid': data.get('valid', False),
                    'details': data.get('vehicle_details', {}),
                    'owner_info': data.get('owner_info', {}),
                    'status': data.get('status', 'unknown')  # active, suspended, stolen
                }
            else:
                return {
                    'exists': False,
                    'valid': False,
                    'error': f'API Error: {response.status_code}'
                }
                
        except requests.RequestException as e:
            logger.error(f"Vehicle verification error: {e}")
            return {
                'exists': None,  # Unknown due to service unavailability
                'valid': None,
                'error': str(e)
            }
    
    @staticmethod
    def get_vehicle_history(plate_number):
        """
        Récupère l'historique d'un véhicule
        """
        # Implémentation similaire pour l'historique
        pass
```

### 2.3 Services de Paiement

```python
# Nouveau fichier: payments/services/payment_providers.py

class MVolaPaymentProvider:
    """Intégration avec MVola"""
    
    def __init__(self):
        self.api_url = settings.MVOLA_API_URL
        self.merchant_id = settings.MVOLA_MERCHANT_ID
        self.api_key = settings.MVOLA_API_KEY
    
    def initiate_payment(self, amount, phone_number, reference):
        """
        Initie un paiement MVola
        """
        payload = {
            'merchant_id': self.merchant_id,
            'amount': str(amount),
            'phone_number': phone_number,
            'reference': reference,
            'callback_url': settings.MVOLA_CALLBACK_URL
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/payments/initiate",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'transaction_id': data.get('transaction_id'),
                    'status': data.get('status'),
                    'message': data.get('message')
                }
            else:
                return {
                    'success': False,
                    'error': f'API Error: {response.status_code}',
                    'message': 'Erreur lors de l\'initiation du paiement'
                }
                
        except requests.RequestException as e:
            logger.error(f"MVola payment error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Service de paiement indisponible'
            }
    
    def verify_payment(self, transaction_id):
        """
        Vérifie le statut d'un paiement
        """
        # Implémentation de la vérification
        pass

class OrangeMoneyPaymentProvider:
    """Intégration avec Orange Money"""
    # Implémentation similaire à MVola
    pass

class AirtelMoneyPaymentProvider:
    """Intégration avec Airtel Money"""
    # Implémentation similaire à MVola
    pass
```

## 3. Système de Notifications

### 3.1 Configuration Celery

```python
# Nouveau fichier: taxcollector_project/celery.py

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxcollector_project.settings')

app = Celery('taxcollector')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'send-payment-reminders': {
        'task': 'notifications.tasks.send_payment_reminders',
        'schedule': 86400.0,  # Tous les jours
    },
    'check-expired-qr-codes': {
        'task': 'payments.tasks.check_expired_qr_codes',
        'schedule': 3600.0,  # Toutes les heures
    },
}
```

### 3.2 Tâches de Notification

```python
# Nouveau fichier: notifications/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .services import NotificationService

@shared_task
def send_payment_reminders():
    """
    Envoie des rappels de paiement automatiques
    """
    # Logique pour identifier les paiements en retard
    from payments.models import PaiementTaxe
    
    # Paiements dus dans 30 jours
    upcoming_due = PaiementTaxe.objects.filter(
        statut='IMPAYE',
        # Logique de calcul de date d'échéance
    )
    
    for paiement in upcoming_due:
        NotificationService.send_payment_reminder(
            paiement.vehicule_plaque.proprietaire,
            paiement,
            reminder_type='upcoming'
        )
    
    # Paiements en retard
    overdue = PaiementTaxe.objects.filter(
        statut='IMPAYE',
        # Logique pour paiements en retard
    )
    
    for paiement in overdue:
        NotificationService.send_payment_reminder(
            paiement.vehicule_plaque.proprietaire,
            paiement,
            reminder_type='overdue'
        )

@shared_task
def send_sms_notification(phone_number, message):
    """
    Envoie une notification SMS
    """
    from .services import SMSService
    return SMSService.send_sms(phone_number, message)

@shared_task
def send_email_notification(email, subject, message, template=None):
    """
    Envoie une notification email
    """
    from .services import EmailService
    return EmailService.send_email(email, subject, message, template)
```

### 3.3 Services de Notification

```python
# Nouveau fichier: notifications/services.py

class NotificationService:
    """Service central de notifications"""
    
    @staticmethod
    def send_payment_reminder(user, paiement, reminder_type='upcoming'):
        """
        Envoie un rappel de paiement
        """
        profile = getattr(user, 'profile', None)
        if not profile:
            return False
        
        # Préparer le message
        if reminder_type == 'upcoming':
            message = f"Rappel: Votre taxe véhicule {paiement.vehicule_plaque} est due bientôt. Montant: {paiement.montant_du_ariary} Ar"
        else:
            message = f"URGENT: Votre taxe véhicule {paiement.vehicule_plaque} est en retard. Montant: {paiement.montant_du_ariary} Ar"
        
        # Envoyer SMS si numéro disponible
        if profile.telephone:
            SMSService.send_sms(profile.telephone, message)
        
        # Envoyer email si disponible
        if user.email:
            EmailService.send_payment_reminder_email(user.email, paiement, reminder_type)
        
        return True

class SMSService:
    """Service d'envoi de SMS"""
    
    @staticmethod
    def send_sms(phone_number, message):
        """
        Envoie un SMS via les fournisseurs locaux
        """
        # Intégration avec Orange, Telma, Airtel SMS APIs
        providers = [
            OrangeSMSProvider(),
            TelmaSMSProvider(),
            AirtelSMSProvider()
        ]
        
        for provider in providers:
            try:
                result = provider.send_sms(phone_number, message)
                if result['success']:
                    return result
            except Exception as e:
                logger.error(f"SMS provider {provider.__class__.__name__} failed: {e}")
                continue
        
        return {'success': False, 'error': 'All SMS providers failed'}

class EmailService:
    """Service d'envoi d'emails"""
    
    @staticmethod
    def send_payment_reminder_email(email, paiement, reminder_type):
        """
        Envoie un email de rappel de paiement
        """
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        template_name = f'emails/payment_reminder_{reminder_type}.html'
        
        context = {
            'paiement': paiement,
            'vehicule': paiement.vehicule_plaque,
            'proprietaire': paiement.vehicule_plaque.proprietaire
        }
        
        html_message = render_to_string(template_name, context)
        
        subject = f"Rappel de paiement - Taxe véhicule {paiement.vehicule_plaque}"
        
        return send_mail(
            subject=subject,
            message='',  # Version texte
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
```

## 4. API de Vérification QR Code

### 4.1 API pour Forces de l'Ordre

```python
# Nouveau fichier: payments/api_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import QRCode
from .serializers import QRCodeVerificationSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_qr_code(request):
    """
    API de vérification des QR codes pour les forces de l'ordre
    """
    serializer = QRCodeVerificationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Données invalides', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token = serializer.validated_data['token']
    
    try:
        qr_code = QRCode.objects.get(token=token, est_actif=True)
        
        # Vérifier la validité
        if not qr_code.est_valide():
            return Response({
                'valid': False,
                'message': 'QR Code expiré ou paiement non effectué',
                'status': 'invalid'
            }, status=status.HTTP_200_OK)
        
        # Incrémenter le compteur de scans
        qr_code.increment_scan_count()
        
        # Enregistrer la géolocalisation du scan si fournie
        if 'latitude' in request.data and 'longitude' in request.data:
            # Enregistrer la géolocalisation du contrôle
            pass
        
        # Retourner les informations du véhicule
        vehicule = qr_code.vehicule_plaque
        paiement = vehicule.paiements.filter(
            annee_fiscale=qr_code.annee_fiscale,
            statut__in=['PAYE', 'EXONERE']
        ).first()
        
        return Response({
            'valid': True,
            'message': 'Taxe payée - Véhicule en règle',
            'status': 'valid',
            'vehicle_info': {
                'plate': vehicule.plaque_immatriculation,
                'owner': vehicule.proprietaire.get_full_name(),
                'type': vehicule.type_vehicule.nom,
                'category': vehicule.get_categorie_vehicule_display(),
                'fiscal_year': qr_code.annee_fiscale,
                'payment_date': paiement.date_paiement.isoformat() if paiement else None,
                'amount_paid': str(paiement.montant_paye_ariary) if paiement else None
            },
            'scan_info': {
                'scan_count': qr_code.nombre_scans,
                'last_scan': qr_code.derniere_verification.isoformat() if qr_code.derniere_verification else None
            }
        }, status=status.HTTP_200_OK)
        
    except QRCode.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'QR Code invalide ou non trouvé',
            'status': 'not_found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"QR Code verification error: {e}")
        return Response({
            'valid': False,
            'message': 'Erreur lors de la vérification',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## 5. Configuration de Sécurité

### 5.1 Chiffrement des Données Sensibles

```python
# Nouveau fichier: core/encryption.py

from cryptography.fernet import Fernet
from django.conf import settings
import base64

class FieldEncryption:
    """Utilitaire de chiffrement pour les champs sensibles"""
    
    def __init__(self):
        self.cipher_suite = Fernet(settings.FIELD_ENCRYPTION_KEY.encode())
    
    def encrypt(self, data):
        """Chiffre une donnée"""
        if not data:
            return data
        
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data):
        """Déchiffre une donnée"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return encrypted_data  # Retourne la donnée non chiffrée si erreur

# Champs de modèle chiffrés
class EncryptedCharField(models.CharField):
    """Champ CharField avec chiffrement automatique"""
    
    def __init__(self, *args, **kwargs):
        self.encryption = FieldEncryption()
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.encryption.decrypt(value)
    
    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.encryption.encrypt(str(value))
```

### 5.2 Authentification à Deux Facteurs

```python
# Nouveau fichier: core/two_factor.py

import pyotp
import qrcode
from io import BytesIO
import base64

class TwoFactorAuthService:
    """Service d'authentification à deux facteurs"""
    
    @staticmethod
    def generate_secret_key(user):
        """Génère une clé secrète pour l'utilisateur"""
        secret = pyotp.random_base32()
        
        # Sauvegarder dans le profil utilisateur
        profile = getattr(user, 'profile', None)
        if profile:
            profile.two_factor_secret = secret
            profile.save()
        
        return secret
    
    @staticmethod
    def generate_qr_code(user, secret):
        """Génère un QR code pour la configuration 2FA"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email or user.username,
            issuer_name="Tax Collector Madagascar"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64 pour affichage web
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_token(user, token):
        """Vérifie un token 2FA"""
        profile = getattr(user, 'profile', None)
        if not profile or not profile.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(profile.two_factor_secret)
        return totp.verify(token, valid_window=1)
```

## 6. Configuration des Settings

### 6.1 Ajouts aux Settings Django

```python
# Ajouts à taxcollector_project/settings.py

# Configuration Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Indian/Antananarivo'

# APIs externes
NATIONAL_ID_VERIFICATION_API_URL = env('NATIONAL_ID_API_URL', default='')
NATIONAL_ID_API_TOKEN = env('NATIONAL_ID_API_TOKEN', default='')

VEHICLE_REGISTRY_API_URL = env('VEHICLE_REGISTRY_API_URL', default='')
VEHICLE_REGISTRY_API_TOKEN = env('VEHICLE_REGISTRY_API_TOKEN', default='')

# Fournisseurs de paiement
MVOLA_API_URL = env('MVOLA_API_URL', default='')
MVOLA_MERCHANT_ID = env('MVOLA_MERCHANT_ID', default='')
MVOLA_API_KEY = env('MVOLA_API_KEY', default='')
MVOLA_CALLBACK_URL = env('MVOLA_CALLBACK_URL', default='')

ORANGE_MONEY_API_URL = env('ORANGE_MONEY_API_URL', default='')
ORANGE_MONEY_MERCHANT_ID = env('ORANGE_MONEY_MERCHANT_ID', default='')
ORANGE_MONEY_API_KEY = env('ORANGE_MONEY_API_KEY', default='')

AIRTEL_MONEY_API_URL = env('AIRTEL_MONEY_API_URL', default='')
AIRTEL_MONEY_MERCHANT_ID = env('AIRTEL_MONEY_MERCHANT_ID', default='')
AIRTEL_MONEY_API_KEY = env('AIRTEL_MONEY_API_KEY', default='')

# Services SMS
ORANGE_SMS_API_URL = env('ORANGE_SMS_API_URL', default='')
ORANGE_SMS_API_KEY = env('ORANGE_SMS_API_KEY', default='')

TELMA_SMS_API_URL = env('TELMA_SMS_API_URL', default='')
TELMA_SMS_API_KEY = env('TELMA_SMS_API_KEY', default='')

AIRTEL_SMS_API_URL = env('AIRTEL_SMS_API_URL', default='')
AIRTEL_SMS_API_KEY = env('AIRTEL_SMS_API_KEY', default='')

# Chiffrement
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY', default='')

# Stockage des fichiers (pour les documents scannés)
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='')

# Configuration des logs de sécurité
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 7. Migrations Nécessaires

### 7.1 Migration pour IndividualProfile

```python
# Nouvelle migration: core/migrations/0003_add_national_id_fields.py

from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_companyprofile_emergencyserviceprofile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_number',
            field=models.CharField(
                blank=True, 
                max_length=20, 
                unique=True,
                validators=[django.core.validators.RegexValidator('^\\d{12}$', 'Format: 12 chiffres')],
                verbose_name="Numéro de carte d'identité nationale"
            ),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_issue_date',
            field=models.DateField(blank=True, null=True, verbose_name="Date d'émission de la CIN"),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_expiry_date',
            field=models.DateField(blank=True, null=True, verbose_name="Date d'expiration de la CIN"),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_issue_place',
            field=models.CharField(blank=True, max_length=100, verbose_name="Lieu d'émission de la CIN"),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_front_scan',
            field=models.URLField(blank=True, max_length=500, verbose_name='Scan recto de la CIN'),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='national_id_back_scan',
            field=models.URLField(blank=True, max_length=500, verbose_name='Scan verso de la CIN'),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='id_verification_status',
            field=models.CharField(
                choices=[
                    ('not_provided', 'Non fournie'),
                    ('pending', 'En attente de vérification'),
                    ('verified', 'Vérifiée'),
                    ('rejected', 'Rejetée'),
                    ('expired', 'Expirée')
                ],
                default='not_provided',
                max_length=20,
                verbose_name='Statut de vérification CIN'
            ),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='id_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de vérification CIN'),
        ),
        migrations.AddField(
            model_name='individualprofile',
            name='id_verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='verified_ids',
                to='auth.user',
                verbose_name='Vérifié par'
            ),
        ),
    ]
```

## 8. Tests Unitaires

### 8.1 Tests pour les Services de Vérification

```python
# Nouveau fichier: core/tests/test_identity_verification.py

from django.test import TestCase
from unittest.mock import patch, Mock
from core.services.identity_verification import IdentityVerificationService
from core.models import UserProfile, IndividualProfile
from django.contrib.auth.models import User

class IdentityVerificationServiceTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='John',
            last_name='Doe'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            user_type='individual'
        )
        self.individual_profile = IndividualProfile.objects.create(
            user_profile=self.user_profile
        )
    
    @patch('core.services.identity_verification.requests.post')
    def test_verify_national_id_success(self, mock_post):
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'details': {'name': 'John Doe'},
            'message': 'ID verified successfully'
        }
        mock_post.return_value = mock_response
        
        result = IdentityVerificationService.verify_national_id(
            '123456789012',
            self.user_profile
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['message'], 'ID verified successfully')
    
    @patch('core.services.identity_verification.requests.post')
    def test_verify_national_id_failure(self, mock_post):
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = IdentityVerificationService.verify_national_id(
            '123456789012',
            self.user_profile
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('API Error', result['error'])
```

Cette spécification technique fournit une base solide pour implémenter les fonctionnalités manquantes du MVP. Chaque section peut être développée indépendamment tout en maintenant la cohérence avec l'architecture existante.