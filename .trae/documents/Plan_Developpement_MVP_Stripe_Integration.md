# Plan de Développement MVP - Intégration Stripe Complète

## Vue d'ensemble
Ce document met à jour le plan de développement pour remplacer le système de paiement simulé par une intégration complète avec Stripe, utilisant des cartes de test pour le développement et les tests.

## Phase 1 : Intégration Stripe Complète (2-3 semaines)

### 1.1 Configuration Stripe et Environnement

**Semaine 1 : Configuration de base**

#### Installation et Configuration Stripe
```bash
# Installation du SDK Stripe Python
pip install stripe

# Ajout aux requirements.txt
echo "stripe>=5.0.0" >> requirements.txt
```

#### Configuration des Variables d'Environnement
```python
# .env.example - Ajouter ces variables
STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle_publique
STRIPE_SECRET_KEY=sk_test_votre_cle_secrete
STRIPE_WEBHOOK_SECRET=whsec_votre_secret_webhook
STRIPE_CURRENCY=MGA  # Ariary malgache
STRIPE_SUCCESS_URL=http://localhost:8000/payments/success/
STRIPE_CANCEL_URL=http://localhost:8000/payments/cancel/
```

#### Configuration Django Settings
```python
# taxcollector_project/settings.py
import stripe
from decouple import config

# Configuration Stripe
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')
STRIPE_CURRENCY = config('STRIPE_CURRENCY', default='MGA')
STRIPE_SUCCESS_URL = config('STRIPE_SUCCESS_URL')
STRIPE_CANCEL_URL = config('STRIPE_CANCEL_URL')

# Initialisation Stripe
stripe.api_key = STRIPE_SECRET_KEY
```

### 1.2 Extensions des Modèles Django

#### Mise à jour du modèle PaiementTaxe
```python
# payments/models.py
from django.db import models
import stripe

class PaiementTaxe(models.Model):
    # Champs existants...
    
    # Nouveaux champs Stripe
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
        default='pending',
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
    
    # Métadonnées Stripe
    stripe_metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Métadonnées Stripe"
    )
    
    # Informations de facturation
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
    
    # Conversion devise
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
    
    class Meta:
        verbose_name = "Paiement de taxe"
        verbose_name_plural = "Paiements de taxes"
        indexes = [
            models.Index(fields=['vehicule_plaque', 'annee_fiscale']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_status']),
            models.Index(fields=['date_paiement']),
        ]
```

#### Nouveau modèle pour les Webhooks Stripe
```python
# payments/models.py
class StripeWebhookEvent(models.Model):
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

### 1.3 Vues et URLs Stripe

#### Vues de Paiement
```python
# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import PaiementTaxe, QRCode, StripeWebhookEvent
from vehicles.models import Vehicule
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class StripeCheckoutView(View):
    def post(self, request, vehicle_id):
        try:
            vehicle = get_object_or_404(Vehicule, id=vehicle_id)
            
            # Calculer le montant de la taxe
            montant_taxe = vehicle.calculer_taxe_annuelle()
            
            # Convertir en centimes pour Stripe (MGA)
            amount_stripe = int(montant_taxe * 100)
            
            # Créer ou récupérer le customer Stripe
            customer = self.get_or_create_stripe_customer(request.user)
            
            # Créer le Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=amount_stripe,
                currency=settings.STRIPE_CURRENCY.lower(),
                customer=customer.id,
                metadata={
                    'vehicle_id': vehicle.id,
                    'user_id': request.user.id,
                    'vehicle_plate': vehicle.plaque_immatriculation,
                },
                description=f"Taxe annuelle véhicule - {vehicle.plaque_immatriculation}",
                receipt_email=request.user.email,
            )
            
            # Créer l'enregistrement de paiement
            paiement = PaiementTaxe.objects.create(
                vehicule_plaque=vehicle.plaque_immatriculation,
                annee_fiscale=datetime.now().year,
                montant_paye=montant_taxe,
                methode_paiement='stripe',
                statut='pending',
                utilisateur=request.user,
                stripe_payment_intent_id=intent.id,
                stripe_customer_id=customer.id,
                amount_stripe=amount_stripe,
                billing_email=request.user.email,
                billing_name=f"{request.user.first_name} {request.user.last_name}",
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                'payment_id': paiement.id,
            })
            
        except Exception as e:
            logger.error(f"Erreur création Payment Intent: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    def get_or_create_stripe_customer(self, user):
        try:
            # Vérifier si l'utilisateur a déjà un customer_id
            if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
                return stripe.Customer.retrieve(user.stripe_customer_id)
        except:
            pass
        
        # Créer un nouveau customer
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={'user_id': user.id}
        )
        
        # Sauvegarder le customer_id (à implémenter dans le modèle UserProfile)
        if hasattr(user, 'profile'):
            user.profile.stripe_customer_id = customer.id
            user.profile.save()
        
        return customer

@method_decorator(login_required, name='dispatch')
class PaymentSuccessView(View):
    def get(self, request):
        payment_id = request.GET.get('payment_id')
        paiement = get_object_or_404(PaiementTaxe, id=payment_id, utilisateur=request.user)
        
        # Vérifier le statut Stripe
        if paiement.stripe_status == 'succeeded':
            # Générer le QR code
            qr_code = QRCode.objects.create(
                vehicule_plaque=paiement.vehicule_plaque,
                annee_fiscale=paiement.annee_fiscale,
                payment=paiement
            )
            
            context = {
                'paiement': paiement,
                'qr_code': qr_code,
                'success': True
            }
        else:
            context = {'success': False, 'error': 'Paiement non confirmé'}
        
        return render(request, 'payments/payment_success.html', context)

@method_decorator(login_required, name='dispatch')
class PaymentCancelView(View):
    def get(self, request):
        payment_id = request.GET.get('payment_id')
        if payment_id:
            PaiementTaxe.objects.filter(id=payment_id, utilisateur=request.user).update(
                stripe_status='canceled',
                statut='failed'
            )
        
        return render(request, 'payments/payment_cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        # Vérifier la signature du webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Sauvegarder l'événement
        webhook_event = StripeWebhookEvent.objects.create(
            stripe_event_id=event['id'],
            type=event['type'],
            data=event['data']
        )
        
        # Traiter l'événement
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_intent_failed(event['data']['object'])
        elif event['type'] == 'charge.refunded':
            handle_charge_refunded(event['data']['object'])
        
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()
        
        return HttpResponse(status=200)
        
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

def handle_payment_intent_succeeded(payment_intent):
    try:
        paiement = PaiementTaxe.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        
        # Mettre à jour le statut
        paiement.stripe_status = 'succeeded'
        paiement.stripe_payment_method = payment_intent.get('payment_method_types', ['card'])[0]
        paiement.stripe_created = timezone.now()
        paiement.statut = 'completed'
        paiement.date_paiement = timezone.now()
        
        # Sauvegarder les métadonnées
        if 'charges' in payment_intent and payment_intent['charges']['data']:
            charge = payment_intent['charges']['data'][0]
            paiement.stripe_charge_id = charge['id']
            paiement.stripe_receipt_url = charge.get('receipt_url')
        
        paiement.save()
        
        logger.info(f"Paiement réussi: {paiement.id}")
        
    except PaiementTaxe.DoesNotExist:
        logger.error(f"Paiement non trouvé pour intent: {payment_intent['id']}")
```

#### URLs Stripe
```python
# payments/urls.py
from django.urls import path
from .views import (
    StripeCheckoutView,
    PaymentSuccessView,
    PaymentCancelView,
    stripe_webhook,
)

urlpatterns = [
    path('stripe/create-payment/<int:vehicle_id>/', StripeCheckoutView.as_view(), name='stripe_create_payment'),
    path('stripe/success/', PaymentSuccessView.as_view(), name='stripe_payment_success'),
    path('stripe/cancel/', PaymentCancelView.as_view(), name='stripe_payment_cancel'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
]
```

### 1.4 Templates de Paiement Stripe

#### Template de Paiement Principal
```html
<!-- templates/payments/stripe_payment.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Paiement de la Taxe Annuelle</h4>
                </div>
                <div class="card-body">
                    <div class="mb-4">
                        <h5>Véhicule: {{ vehicle.plaque_immatriculation }}</h5>
                        <p class="text-muted">Année fiscale: {% now "Y" %}</p>
                        <h3 class="text-primary">Montant: {{ montant_taxe|floatformat:2 }} MGA</h3>
                    </div>
                    
                    <form id="payment-form">
                        {% csrf_token %}
                        <div id="payment-element" class="mb-3">
                            <!-- Stripe Elements sera monté ici -->
                        </div>
                        
                        <div id="payment-message" class="alert alert-danger d-none"></div>
                        
                        <button type="submit" class="btn btn-success btn-block" id="submit-button">
                            <span id="button-text">Payer maintenant</span>
                            <span id="spinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                        </button>
                    </form>
                    
                    <div class="mt-3 text-center">
                        <small class="text-muted">
                            <i class="fas fa-lock"></i> Paiement sécurisé par Stripe
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://js.stripe.com/v3/"></script>
<script>
const stripe = Stripe('{{ stripe_publishable_key }}');
const clientSecret = '{{ client_secret }}';

const elements = stripe.elements({ clientSecret });
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

const form = document.getElementById('payment-form');
const submitButton = document.getElementById('submit-button');
const spinner = document.getElementById('spinner');
const buttonText = document.getElementById('button-text');
const messageDiv = document.getElementById('payment-message');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    submitButton.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Traitement...';
    
    const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: '{{ stripe_success_url }}?payment_id={{ payment_id }}',
        },
    });
    
    if (error) {
        messageDiv.textContent = error.message;
        messageDiv.classList.remove('d-none');
        submitButton.disabled = false;
        spinner.classList.add('d-none');
        buttonText.textContent = 'Payer maintenant';
    }
});
</script>
{% endblock %}
```

### 1.5 Cartes de Test Stripe Recommandées

#### Cartes de Test pour le Développement
```python
# Cartes de test à utiliser en développement
CARTES_TEST_STRIPE = {
    'success': {
        'number': '4242424242424242',
        'description': 'Paiement réussi sans authentification 3D Secure',
        'expected_result': 'succeeded'
    },
    'success_3ds': {
        'number': '4000002500003155',
        'description': 'Paiement réussi avec authentification 3D Secure',
        'expected_result': 'succeeded'
    },
    'declined': {
        'number': '4000000000000002',
        'description': 'Carte refusée - generic_decline',
        'expected_result': 'failed'
    },
    'insufficient_funds': {
        'number': '4000000000009995',
        'description': 'Fonds insuffisants',
        'expected_result': 'failed'
    },
    'expired': {
        'number': '4000000000000069',
        'description': 'Carte expirée',
        'expected_result': 'failed'
    },
    'incorrect_cvc': {
        'number': '4000000000000127',
        'description': 'CVC incorrect',
        'expected_result': 'failed'
    },
    'processing_error': {
        'number': '4000000000000119',
        'description': 'Erreur de traitement',
        'expected_result': 'failed'
    }
}

# Données de test génériques
DONNEES_TEST_CARTE = {
    'exp_month': 12,
    'exp_year': datetime.now().year + 2,
    'cvc': '123',
    'postal_code': '101',
    'address_line1': 'Adresse de test'
}
```

### 1.6 Sécurité et Conformité

#### Middleware de Sécurité Stripe
```python
# payments/middleware.py
import stripe
from django.conf import settings
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class StripeSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier les IPs Stripe pour les webhooks
        if request.path == '/payments/stripe/webhook/':
            stripe_ip_ranges = self.get_stripe_ip_ranges()
            client_ip = self.get_client_ip(request)
            
            if client_ip not in stripe_ip_ranges:
                logger.warning(f"Tentative d'accès webhook depuis IP non autorisée: {client_ip}")
                return JsonResponse({'error': 'Non autorisé'}, status=403)
        
        response = self.get_response(request)
        return response
    
    def get_stripe_ip_ranges(self):
        # Récupérer les plages IP officielles de Stripe
        # En production, ces données devraient être mises en cache
        return [
            '3.18.12.63', '3.130.192.231', '13.235.14.237', '13.235.122.149',
            '18.211.135.69', '52.15.183.38', '52.86.251.1', '54.163.224.46',
            '54.187.174.169', '54.187.205.235', '54.206.174.187'
        ]
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

#### Validation des Données Sensibles
```python
# payments/validators.py
import re
from django.core.exceptions import ValidationError

def validate_stripe_payment_intent_id(payment_intent_id):
    """Valider le format d'un Payment Intent ID Stripe"""
    pattern = r'^pi_[A-Za-z0-9]{24,}$'
    if not re.match(pattern, payment_intent_id):
        raise ValidationError('Invalid Stripe Payment Intent ID format')

def validate_stripe_customer_id(customer_id):
    """Valider le format d'un Customer ID Stripe"""
    pattern = r'^cus_[A-Za-z0-9]{14,}$'
    if not re.match(pattern, customer_id):
        raise ValidationError('Invalid Stripe Customer ID format')

def validate_stripe_webhook_signature(signature):
    """Valider la signature d'un webhook Stripe"""
    if not signature or not signature.startswith('t=') or 'v1=' not in signature:
        raise ValidationError('Invalid Stripe webhook signature format')
```

### 1.7 Tests et Validation

#### Tests d'Intégration Stripe
```python
# payments/tests/test_stripe_integration.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import stripe
from payments.models import PaiementTaxe
from vehicles.models import Vehicule

class StripeIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicule.objects.create(
            plaque_immatriculation='1234ABCD',
            proprietaire=self.user,
            puissance_fiscale_cv=10,
            source_energie='essence'
        )
    
    @patch('stripe.PaymentIntent.create')
    @patch('stripe.Customer.create')
    def test_create_payment_intent_success(self, mock_customer_create, mock_payment_intent_create):
        # Mock Stripe responses
        mock_customer = MagicMock()
        mock_customer.id = 'cus_test123'
        mock_customer_create.return_value = mock_customer
        
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = 'pi_test123'
        mock_payment_intent.client_secret = 'pi_test123_secret'
        mock_payment_intent_create.return_value = mock_payment_intent
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('stripe_create_payment', args=[self.vehicle.id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('client_secret', data)
        self.assertEqual(data['client_secret'], 'pi_test123_secret')
        
        # Vérifier que le paiement a été créé
        paiement = PaiementTaxe.objects.get(stripe_payment_intent_id='pi_test123')
        self.assertEqual(paiement.utilisateur, self.user)
        self.assertEqual(paiement.vehicule_plaque, '1234ABCD')
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_success(self, mock_construct_event):
        # Créer un paiement de test
        paiement = PaiementTaxe.objects.create(
            vehicule_plaque='1234ABCD',
            annee_fiscale=2024,
            montant_paye=100000,
            utilisateur=self.user,
            stripe_payment_intent_id='pi_test123',
            stripe_status='pending'
        )
        
        # Mock webhook event
        mock_event = {
            'id': 'evt_test123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test123',
                    'status': 'succeeded',
                    'charges': {
                        'data': [{
                            'id': 'ch_test123',
                            'receipt_url': 'https://receipt.stripe.com/test'
                        }]
                    }
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        response = self.client.post(
            reverse('stripe_webhook'),
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=123,v1=abc'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le paiement a été mis à jour
        paiement.refresh_from_db()
        self.assertEqual(paiement.stripe_status, 'succeeded')
        self.assertEqual(paiement.statut, 'completed')
```

## Phase 2 : Notifications et Administration (6-8 semaines)

### 2.1 Système de Notifications
- Intégration avec le système de notifications existant
- Notifications de paiement réussi/échoué
- Rappels de renouvellement de taxe

### 2.2 Interface d'Administration Stripe
- Tableau de bord des paiements
- Gestion des remboursements
- Analyse des transactions
- Export des données financières

## Phase 3 : Optimisations et Sécurité Avancée (2-4 semaines)

### 3.1 Optimisations
- Mise en cache des données Stripe
- Optimisation des requêtes API
- Gestion des erreurs avancée

### 3.2 Sécurité Renforcée
- Chiffrement additionnel des données sensibles
- Audit logs détaillés
- Monitoring en temps réel
- Conformité PCI DSS complète

## Cartes de Test Recommandées - Récapitulatif

| Numéro de Carte | Résultat Attendu | Utilisation |
|------------------|------------------|-------------|
| 4242424242424242 | ✅ Succès | Tests de succès principal |
| 4000002500003155 | ✅ Succès (3DS) | Test authentification 3D |
| 4000000000000002 | ❌ Échec | Test carte refusée |
| 4000000000009995 | ❌ Échec | Test fonds insuffisants |
| 4000000000000069 | ❌ Échec | Test carte expirée |

## Points de Vigilance

1. **Sécurité**: Ne jamais stocker les numéros de cartes en base de données
2. **Webhooks**: Toujours vérifier la signature des webhooks Stripe
3. **Tests**: Utiliser exclusivement les cartes de test en environnement de développement
4. **Logs**: Ne jamais logger les données sensibles des cartes
5. **Conformité**: S'assurer de la conformité PCI DSS en production

## Code Prêt à l'Emploi

Tous les codes fournis dans ce document sont prêts à être implémentés. Il suffit de :

1. Installer Stripe SDK
2. Configurer les variables d'environnement
3. Créer les modèles étendus
4. Implémenter les vues et URLs
5. Configurer les webhooks dans le dashboard Stripe
6. Tester avec les cartes de test fournies

Le système de paiement Stripe est maintenant prêt pour une intégration complète et sécurisée.