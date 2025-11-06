# Plan de Développement MVP Révisé - Système de Collecte de Taxes Véhicules

## Vue d'ensemble de la Stratégie Révisée

**Nouvelle Approche :** Développement par phases avec paiement simulé pour valider le workflow complet avant l'intégration des vrais systèmes de paiement.

**Objectif :** Avoir un MVP fonctionnel avec toutes les fonctionnalités métier avant d'intégrer les APIs de paiement externes.

---

## PHASE 1 - PRIORITÉ ABSOLUE (4-6 semaines)

### 1.1 Mise à Jour des Modèles Django

#### Extension du Modèle Vehicule

```python
# vehicles/models.py - Extensions à ajouter

class Vehicule(models.Model):
    # Champs existants conservés...
    
    # NOUVEAUX CHAMPS OBLIGATOIRES
    vin_number = models.CharField(
        max_length=17, 
        unique=True,
        validators=[RegexValidator(r'^[A-HJ-NPR-Z0-9]{17}$', 'VIN invalide')],
        verbose_name="Numéro VIN",
        help_text="Numéro d'identification du véhicule (17 caractères)"
    )
    
    marque = models.CharField(
        max_length=50,
        verbose_name="Marque du véhicule",
        help_text="Ex: Toyota, Peugeot, Honda"
    )
    
    modele = models.CharField(
        max_length=100,
        verbose_name="Modèle du véhicule",
        help_text="Ex: Corolla, 206, Civic"
    )
    
    couleur_principale = models.CharField(
        max_length=30,
        verbose_name="Couleur principale"
    )
    
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
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
    
    # Informations carte grise
    numero_carte_grise = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de carte grise"
    )
    
    date_delivrance_carte_grise = models.DateField(
        verbose_name="Date de délivrance carte grise"
    )
    
    prefecture_delivrance = models.CharField(
        max_length=100,
        verbose_name="Préfecture de délivrance"
    )
    
    # Statut de vérification
    statut_verification = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente de vérification'),
            ('verifie', 'Vérifié'),
            ('rejete', 'Rejeté'),
            ('documents_manquants', 'Documents manquants')
        ],
        default='en_attente',
        verbose_name="Statut de vérification"
    )
    
    # Métadonnées OCR
    donnees_ocr_extraites = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données extraites par OCR"
    )
    
    precision_ocr = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Précision OCR (0-1)"
    )
```

#### Extension des Modèles Utilisateur

```python
# core/models.py - Extensions à ajouter

class IndividualProfile(models.Model):
    # Champs existants conservés...
    
    # NOUVEAUX CHAMPS CIN
    numero_cin = models.CharField(
        max_length=12,
        unique=True,
        null=True, blank=True,
        validators=[RegexValidator(r'^\d{12}$', 'CIN doit contenir 12 chiffres')],
        verbose_name="Numéro CIN"
    )
    
    date_delivrance_cin = models.DateField(
        null=True, blank=True,
        verbose_name="Date de délivrance CIN"
    )
    
    lieu_delivrance_cin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Lieu de délivrance CIN"
    )
    
    date_expiration_cin = models.DateField(
        null=True, blank=True,
        verbose_name="Date d'expiration CIN"
    )
    
    # Informations complémentaires
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
            ('veuf', 'Veuf/Veuve')
        ],
        blank=True,
        verbose_name="Situation familiale"
    )
```

#### Nouveau Modèle pour Documents

```python
# core/models.py - Nouveau modèle

class DocumentVehicule(models.Model):
    """Documents associés aux véhicules"""
    
    TYPE_DOCUMENT_CHOICES = [
        ('carte_grise', 'Carte grise'),
        ('certificat_immatriculation', 'Certificat d\'immatriculation'),
        ('controle_technique', 'Contrôle technique'),
        ('assurance', 'Attestation d\'assurance'),
        ('facture_achat', 'Facture d\'achat'),
        ('autre', 'Autre document')
    ]
    
    STATUT_VERIFICATION_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de vérification'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('expire', 'Expiré')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicule = models.ForeignKey(
        'vehicles.Vehicule',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    type_document = models.CharField(
        max_length=30,
        choices=TYPE_DOCUMENT_CHOICES,
        verbose_name="Type de document"
    )
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
    
    # Données OCR
    donnees_extraites = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données extraites par OCR"
    )
    
    # Vérification
    statut_verification = models.CharField(
        max_length=20,
        choices=STATUT_VERIFICATION_CHOICES,
        default='en_attente',
        verbose_name="Statut de vérification"
    )
    
    verifie_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
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
    
    # Métadonnées
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Document véhicule"
        verbose_name_plural = "Documents véhicules"
        indexes = [
            models.Index(fields=['vehicule', 'type_document']),
            models.Index(fields=['statut_verification']),
        ]
```

### 1.2 Système de Documents et OCR

#### Service OCR pour Cartes Grises

```python
# vehicles/services/ocr_service.py

import cv2
import pytesseract
import re
from typing import Dict, Optional, Tuple
import logging

class CarteGriseOCRService:
    """Service d'extraction OCR pour cartes grises malgaches"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extraire_donnees_carte_grise(self, image_path: str) -> Dict:
        """
        Extrait les données d'une carte grise malgache
        
        Returns:
            Dict contenant les données extraites et la précision
        """
        try:
            # Préprocessing de l'image
            image = self._preprocess_image(image_path)
            
            # Extraction du texte
            texte_brut = pytesseract.image_to_string(
                image, 
                lang='fra',
                config='--psm 6'
            )
            
            # Parsing des données spécifiques
            donnees = self._parser_carte_grise(texte_brut)
            
            # Calcul de la précision
            precision = self._calculer_precision(donnees)
            
            return {
                'donnees': donnees,
                'precision': precision,
                'texte_brut': texte_brut,
                'statut': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur OCR: {str(e)}")
            return {
                'donnees': {},
                'precision': 0.0,
                'texte_brut': '',
                'statut': 'error',
                'erreur': str(e)
            }
    
    def _preprocess_image(self, image_path: str):
        """Préprocessing de l'image pour améliorer l'OCR"""
        image = cv2.imread(image_path)
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Réduction du bruit
        denoised = cv2.medianBlur(gray, 3)
        
        # Amélioration du contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def _parser_carte_grise(self, texte: str) -> Dict:
        """Parse le texte extrait pour identifier les champs"""
        donnees = {}
        
        # Patterns de reconnaissance pour cartes grises malgaches
        patterns = {
            'numero_immatriculation': r'(\d{1,4}\s[A-Z]{2,3})',
            'vin': r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})',
            'marque': r'MARQUE[:\s]*([A-Z\s]+)',
            'modele': r'MODÈLE[:\s]*([A-Z0-9\s\-]+)',
            'couleur': r'COULEUR[:\s]*([A-Z\s]+)',
            'puissance_cv': r'PUISSANCE[:\s]*(\d+)\s*CV',
            'cylindree': r'CYLINDRÉE[:\s]*(\d+)\s*CM3',
            'date_premiere_circulation': r'PREMIÈRE\s+CIRCULATION[:\s]*(\d{2}/\d{2}/\d{4})',
            'numero_carte_grise': r'N°\s*CARTE[:\s]*([A-Z0-9]+)',
        }
        
        for champ, pattern in patterns.items():
            match = re.search(pattern, texte.upper())
            if match:
                donnees[champ] = match.group(1).strip()
        
        return donnees
    
    def _calculer_precision(self, donnees: Dict) -> float:
        """Calcule la précision basée sur les champs extraits"""
        champs_obligatoires = [
            'numero_immatriculation', 'marque', 'modele', 
            'puissance_cv', 'date_premiere_circulation'
        ]
        
        champs_trouves = sum(1 for champ in champs_obligatoires if champ in donnees)
        return champs_trouves / len(champs_obligatoires)
```

#### API d'Upload de Documents

```python
# vehicles/api_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .services.ocr_service import CarteGriseOCRService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document_vehicule(request):
    """Upload et traitement OCR d'un document véhicule"""
    
    if 'document' not in request.FILES:
        return Response(
            {'error': 'Aucun fichier fourni'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    fichier = request.FILES['document']
    type_document = request.data.get('type_document', 'carte_grise')
    vehicule_id = request.data.get('vehicule_id')
    
    try:
        # Validation du fichier
        if not fichier.name.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            return Response(
                {'error': 'Format de fichier non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sauvegarde sécurisée
        nom_fichier = f"documents/{vehicule_id}/{type_document}_{fichier.name}"
        chemin_fichier = default_storage.save(nom_fichier, fichier)
        
        # Traitement OCR si c'est une carte grise
        donnees_ocr = {}
        precision_ocr = 0.0
        
        if type_document == 'carte_grise':
            ocr_service = CarteGriseOCRService()
            resultat_ocr = ocr_service.extraire_donnees_carte_grise(
                default_storage.path(chemin_fichier)
            )
            donnees_ocr = resultat_ocr['donnees']
            precision_ocr = resultat_ocr['precision']
        
        # Création de l'enregistrement
        document = DocumentVehicule.objects.create(
            vehicule_id=vehicule_id,
            type_document=type_document,
            fichier_url=default_storage.url(chemin_fichier),
            nom_fichier_original=fichier.name,
            taille_fichier=fichier.size,
            donnees_extraites=donnees_ocr
        )
        
        # Mise à jour du véhicule si OCR réussi
        if precision_ocr > 0.7:  # Seuil de confiance
            vehicule = document.vehicule
            vehicule.donnees_ocr_extraites = donnees_ocr
            vehicule.precision_ocr = precision_ocr
            vehicule.save()
        
        return Response({
            'document_id': document.id,
            'donnees_extraites': donnees_ocr,
            'precision_ocr': precision_ocr,
            'message': 'Document uploadé et traité avec succès'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du traitement: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### 1.3 Système de Paiement Simulé

#### Modèle de Paiement Simulé

```python
# payments/models.py - Extension

class PaiementTaxe(models.Model):
    # Champs existants conservés...
    
    # NOUVEAU CHAMP
    est_simulation = models.BooleanField(
        default=True,
        verbose_name="Est une simulation",
        help_text="True pour les paiements simulés, False pour les vrais paiements"
    )
    
    # Méthodes simulées
    def simuler_paiement_mvola(self):
        """Simule un paiement MVola réussi"""
        import random
        import string
        
        self.statut = 'PAYE'
        self.date_paiement = timezone.now()
        self.montant_paye_ariary = self.montant_du_ariary
        self.methode_paiement = 'mvola'
        self.transaction_id = 'SIM_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.details_paiement = {
            'simulation': True,
            'numero_mvola': '034XX XX XXX',
            'frais': float(self.montant_du_ariary * Decimal('0.02'))  # 2% de frais simulés
        }
        self.save()
        
        # Génération automatique du QR code
        self.generer_qr_code()
        
        return True
    
    def generer_qr_code(self):
        """Génère le QR code après paiement"""
        from django.utils import timezone
        from datetime import timedelta
        
        qr_code, created = QRCode.objects.get_or_create(
            vehicule_plaque=self.vehicule_plaque,
            annee_fiscale=self.annee_fiscale,
            defaults={
                'date_expiration': timezone.now() + timedelta(days=365),
                'est_actif': True
            }
        )
        
        return qr_code
```

#### Interface de Paiement Simulé

```python
# payments/views.py

class PaiementSimuleView(LoginRequiredMixin, View):
    """Vue pour simuler un paiement"""
    
    def post(self, request, paiement_id):
        paiement = get_object_or_404(PaiementTaxe, id=paiement_id)
        
        # Vérification des permissions
        if paiement.vehicule_plaque.proprietaire != request.user:
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        
        # Simulation du paiement
        if paiement.simuler_paiement_mvola():
            return JsonResponse({
                'success': True,
                'message': 'Paiement simulé avec succès',
                'transaction_id': paiement.transaction_id,
                'qr_code_url': f'/qr/{paiement.vehicule_plaque.plaque_immatriculation}/'
            })
        else:
            return JsonResponse({'error': 'Erreur de simulation'}, status=500)
```

---

## PHASE 2 - Fonctionnalités Avancées (6-8 semaines)

### 2.1 Système de Notifications

```python
# notifications/models.py

class NotificationTemplate(models.Model):
    """Templates de notifications"""
    
    TYPE_CHOICES = [
        ('echeance_proche', 'Échéance proche'),
        ('echeance_depassee', 'Échéance dépassée'),
        ('paiement_confirme', 'Paiement confirmé'),
        ('document_rejete', 'Document rejeté'),
        ('verification_requise', 'Vérification requise')
    ]
    
    type_notification = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    message_sms = models.TextField()
    message_email = models.TextField()
    delai_envoi_jours = models.IntegerField(default=0)
    est_actif = models.BooleanField(default=True)
```

### 2.2 Interface d'Administration Complète

- Dashboard avec statistiques en temps réel
- Gestion des utilisateurs et vérifications
- Suivi des paiements et génération de rapports
- Interface de validation des documents OCR

---

## PHASE 3 - Intégration Finale (2-4 semaines)

### 3.1 Intégration Vrais Paiements

- Remplacement du système simulé par les vraies APIs
- Tests d'intégration avec MVola, Orange Money, Airtel Money
- Gestion des erreurs et des remboursements

### 3.2 Sécurité et Optimisations

- Chiffrement des données sensibles
- Audit trail complet
- Optimisations de performance
- Tests de charge

---

## Planning de Développement

### Semaine 1-2 : Modèles et Migrations
- Extension des modèles existants
- Création des nouveaux modèles
- Migrations Django
- Tests unitaires des modèles

### Semaine 3-4 : Système OCR et Documents
- Implémentation du service OCR
- API d'upload de documents
- Interface utilisateur pour upload
- Tests d'extraction de données

### Semaine 5-6 : Paiement Simulé et QR Codes
- Système de paiement simulé
- Génération automatique des QR codes
- Interface de vérification QR
- Tests end-to-end du workflow

---

## Livrables de la Phase 1

1. **Modèles étendus** avec tous les champs nécessaires
2. **Service OCR fonctionnel** pour cartes grises
3. **Système d'upload** de documents sécurisé
4. **Paiement simulé** avec génération QR automatique
5. **Interface de vérification QR** opérationnelle
6. **Tests complets** du workflow utilisateur

Cette approche permet de valider tout le processus métier avant d'investir dans les intégrations de paiement complexes.