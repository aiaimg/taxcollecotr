# Design Document - Conformité aux Standards d'Interopérabilité

## Overview

Ce document décrit l'architecture et la conception technique pour mettre en conformité la plateforme TaxCollector avec les standards d'interopérabilité du gouvernement malgache. La solution **s'appuie sur l'infrastructure API v1 existante** et l'étend avec des composants de sécurité, monitoring, et documentation conformes aux normes UGD.

### Infrastructure Existante

**Déjà en place:**
- ✅ API REST v1 complète (`/api/v1/`) avec Django REST Framework
- ✅ Authentification JWT via `djangorestframework-simplejwt`
- ✅ Documentation OpenAPI 3.0 avec `drf-spectacular`
- ✅ Swagger UI et ReDoc configurés
- ✅ Rate limiting avec throttle classes personnalisées
- ✅ Health check endpoint fonctionnel
- ✅ Support multilingue (Django i18n pour fr/mg)
- ✅ CORS configuré
- ✅ Redis pour cache et sessions

### Objectifs Principaux

1. **Étendre** le système d'authentification avec API keys pour intégrations système-à-système
2. **Ajouter** un système d'audit logging complet et structuré
3. **Standardiser** les erreurs selon RFC 7807
4. **Implémenter** un système de webhooks pour notifications temps réel
5. **Améliorer** la documentation avec exemples et traductions
6. **Ajouter** monitoring et métriques (Prometheus)

### Contraintes

- **Réutiliser** l'infrastructure Django/DRF existante
- **Maintenir** la compatibilité avec les APIs v1 actuelles
- **Minimiser** l'impact sur les performances
- **Préserver** le support multilingue (Français/Malgache)
- **Assurer** la conformité RGPD et protection des données
- **Éviter** les breaking changes pour les clients existants

## Architecture

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Rate Limiter │  │ Auth Manager │  │ API Versioning│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    API Documentation Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OpenAPI Spec │  │  Swagger UI  │  │  ReDoc UI    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vehicles   │  │   Payments   │  │Contraventions│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Cross-Cutting Concerns                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Audit Logger │  │  Monitoring  │  │   Webhooks   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Composants Principaux

1. **API Gateway**: Point d'entrée centralisé avec rate limiting et authentification
2. **Documentation Layer**: OpenAPI/Swagger pour documentation interactive
3. **Business Logic**: APIs métier existantes étendues
4. **Audit & Monitoring**: Traçabilité et métriques
5. **Webhook System**: Notifications asynchrones


## Components and Interfaces

### 1. API Gateway Component (Extension)

**État:** ⚠️ Partiellement implémenté - Besoin d'extensions

**Existant:**
- ✅ DRF avec viewsets et routers dans `api/v1/`
- ✅ JWT authentication via `JWTAuthentication`
- ✅ Throttle classes: `AnonBurstThrottle`, `UserBurstThrottle`, `AuthThrottle`, `PaymentThrottle`
- ✅ Versioning via URL path (`/api/v1/`)

**À Ajouter:**
- ❌ API Key authentication backend
- ❌ Middleware pour audit logging automatique
- ❌ Middleware pour correlation ID
- ❌ Rate limiting per-API-key

**Technologies:**
- Django REST Framework (existant)
- djangorestframework-simplejwt (existant)
- Custom middleware pour audit et correlation

**Nouvelles Interfaces:**

```python
# api/authentication.py (nouveau)
class APIKeyAuthentication(BaseAuthentication):
    """Authentication backend pour API keys"""
    
    def authenticate(self, request):
        """Authentifie via API key dans header X-API-Key"""
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            key_obj = APIKey.objects.select_related('organization').get(
                key=api_key, 
                is_active=True
            )
            # Vérifier expiration
            if key_obj.is_expired():
                raise AuthenticationFailed('API key expired')
            
            # Mettre à jour last_used_at
            key_obj.update_last_used()
            
            return (None, key_obj)  # Pas d'user, mais API key
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

# api/middleware/audit.py (nouveau)
class AuditLoggingMiddleware:
    """Middleware pour logger toutes les requêtes API"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Générer correlation ID
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID') or str(uuid.uuid4())
        request.correlation_id = correlation_id
        
        # Capturer le début
        start_time = time.time()
        
        # Traiter la requête
        response = self.get_response(request)
        
        # Logger après réponse
        if request.path.startswith('/api/'):
            self.log_api_request(request, response, start_time, correlation_id)
        
        # Ajouter correlation ID à la réponse
        response['X-Correlation-ID'] = correlation_id
        
        return response
```

### 2. API Key Management Component (Nouveau)

**État:** ❌ À implémenter entièrement

**Responsabilités:**
- Génération sécurisée des API keys
- Association des permissions et scopes
- Révocation et rotation des clés
- Tracking de l'utilisation

**Modèles de données:**

```python
# api/models.py (nouveau fichier)
import secrets
from django.db import models
from django.utils import timezone

class APIKey(models.Model):
    """Clé API pour accès système-à-système"""
    
    # Identification
    key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255, help_text="Nom descriptif de la clé")
    organization = models.CharField(max_length=255)
    contact_email = models.EmailField()
    
    # État
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_api_keys')
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Rate limiting
    rate_limit_per_hour = models.IntegerField(default=1000)
    rate_limit_per_day = models.IntegerField(default=10000)
    
    # Métadonnées
    description = models.TextField(blank=True)
    ip_whitelist = models.JSONField(default=list, blank=True, help_text="Liste d'IPs autorisées")
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization})"
    
    @classmethod
    def generate_key(cls):
        """Génère une clé API sécurisée"""
        return f"tc_{secrets.token_urlsafe(48)}"
    
    def is_expired(self):
        """Vérifie si la clé est expirée"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def update_last_used(self):
        """Met à jour la date de dernière utilisation"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    def revoke(self, revoked_by=None):
        """Révoque la clé immédiatement"""
        self.is_active = False
        self.save(update_fields=['is_active'])
        
        # Logger l'événement
        APIKeyEvent.objects.create(
            api_key=self,
            event_type='REVOKED',
            performed_by=revoked_by,
            details={'revoked_at': timezone.now().isoformat()}
        )

class APIKeyPermission(models.Model):
    """Permissions associées à une API key"""
    
    SCOPE_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read & Write'),
        ('admin', 'Full Admin'),
    ]
    
    RESOURCE_CHOICES = [
        ('vehicles', 'Vehicles'),
        ('payments', 'Payments'),
        ('users', 'Users'),
        ('documents', 'Documents'),
        ('qrcodes', 'QR Codes'),
        ('notifications', 'Notifications'),
        ('*', 'All Resources'),
    ]
    
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='permissions')
    resource = models.CharField(max_length=100, choices=RESOURCE_CHOICES)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'api_key_permissions'
        unique_together = [['api_key', 'resource']]
    
    def __str__(self):
        return f"{self.api_key.name} - {self.resource}:{self.scope}"

class APIKeyEvent(models.Model):
    """Événements liés aux API keys (création, révocation, etc.)"""
    
    EVENT_TYPES = [
        ('CREATED', 'Created'),
        ('REVOKED', 'Revoked'),
        ('RENEWED', 'Renewed'),
        ('PERMISSIONS_CHANGED', 'Permissions Changed'),
    ]
    
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    performed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    details = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'api_key_events'
        ordering = ['-timestamp']
```

### 3. Audit Logging Component

**Responsabilités:**
- Enregistrement de toutes les requêtes API
- Capture des modifications de données
- Génération de rapports d'audit

**Modèles de données:**

```python
# api/models.py
class APIAuditLog(models.Model):
    """Journal d'audit des appels API"""
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    api_key = models.ForeignKey(APIKey, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=255, db_index=True)
    query_params = models.JSONField(null=True)
    request_body = models.JSONField(null=True)
    response_status = models.IntegerField(db_index=True)
    response_time_ms = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
class DataChangeLog(models.Model):
    """Journal des modifications de données"""
    timestamp = models.DateTimeField(auto_now_add=True)
    audit_log = models.ForeignKey(APIAuditLog, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20)  # create, update, delete
    before_state = models.JSONField(null=True)
    after_state = models.JSONField(null=True)
```

### 4. OpenAPI Documentation Component

**Responsabilités:**
- Génération automatique de la spécification OpenAPI
- Exposition de Swagger UI et ReDoc
- Maintenance du changelog API

**Configuration:**

```python
# settings.py
SPECTACULAR_SETTINGS = {
    'TITLE': 'TaxCollector API',
    'DESCRIPTION': 'API de collecte de taxes - Conforme aux standards UGD',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'SERVERS': [
        {'url': 'https://api.taxcollector.gov.mg', 'description': 'Production'},
        {'url': 'https://sandbox.taxcollector.gov.mg', 'description': 'Sandbox'},
    ],
    'LANGUAGES': ['fr', 'mg'],
    'CONTACT': {
        'name': 'Support API TaxCollector',
        'email': 'api-support@taxcollector.gov.mg',
    },
}
```

### 5. Webhook System Component

**Responsabilités:**
- Enregistrement des webhooks
- Envoi de notifications d'événements
- Gestion des retries et échecs

**Modèles de données:**

```python
# api/models.py
class WebhookSubscription(models.Model):
    """Abonnement webhook pour notifications"""
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    url = models.URLField()
    events = models.JSONField()  # Liste des événements souscrits
    secret = models.CharField(max_length=64)  # Pour HMAC signature
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class WebhookDelivery(models.Model):
    """Historique des livraisons webhook"""
    subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField(null=True)
    attempts = models.IntegerField(default=0)
    delivered_at = models.DateTimeField(null=True)
    next_retry_at = models.DateTimeField(null=True)
```

### 6. Error Handling Component (Refactoring)

**État:** ⚠️ Format personnalisé existe, besoin de migration vers RFC 7807

**Format Actuel:**
```python
# Format existant dans api/v1/views.py
{
    "success": False,
    "error": {
        "code": "validation_error",
        "message": "Invalid credentials",
        "details": {...}
    }
}
```

**Format Cible RFC 7807:**
```python
{
    "type": "https://api.taxcollector.gov.mg/errors/validation_error",
    "title": "Erreur de validation",
    "status": 400,
    "detail": "Les identifiants fournis sont invalides",
    "instance": "/api/v1/auth/login",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
    "errors": [...]  # Pour validation errors
}
```

**Responsabilités:**
- Standardisation des réponses d'erreur (RFC 7807)
- Traduction des messages d'erreur (fr/mg)
- Masquage des informations sensibles
- Ajout de correlation ID
- Compatibilité avec format existant (transition)

**Implémentation:**

```python
# api/exceptions.py (à étendre)
from rest_framework.views import exception_handler as drf_exception_handler
from django.utils.translation import gettext as _

class RFC7807Exception(Exception):
    """Exception API standardisée RFC 7807"""
    
    def __init__(self, status_code, error_code, title, detail, instance=None, errors=None):
        self.status_code = status_code
        self.error_code = error_code
        self.title = title
        self.detail = detail
        self.instance = instance
        self.errors = errors or []
        super().__init__(detail)
    
    def to_dict(self, correlation_id, language='fr'):
        """Convertit en dictionnaire RFC 7807"""
        # Activer la langue
        from django.utils import translation
        translation.activate(language)
        
        response = {
            'type': f'https://api.taxcollector.gov.mg/errors/{self.error_code}',
            'title': _(self.title),
            'status': self.status_code,
            'detail': _(self.detail),
            'correlation_id': str(correlation_id),
        }
        
        if self.instance:
            response['instance'] = self.instance
        
        if self.errors:
            response['errors'] = self.errors
        
        return response

def custom_exception_handler(exc, context):
    """
    Handler personnalisé pour convertir les exceptions en RFC 7807
    Maintient la compatibilité avec le format existant via header
    """
    # Obtenir la réponse DRF standard
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        request = context.get('request')
        correlation_id = getattr(request, 'correlation_id', str(uuid.uuid4()))
        language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'fr')[:2]
        
        # Vérifier si le client veut RFC 7807
        use_rfc7807 = request.META.get('HTTP_ACCEPT', '').find('application/problem+json') >= 0
        
        if use_rfc7807 or True:  # Toujours utiliser RFC 7807 par défaut
            # Convertir en RFC 7807
            if isinstance(exc, RFC7807Exception):
                response.data = exc.to_dict(correlation_id, language)
            else:
                # Convertir exception DRF en RFC 7807
                response.data = {
                    'type': f'https://api.taxcollector.gov.mg/errors/{exc.__class__.__name__}',
                    'title': exc.__class__.__name__,
                    'status': response.status_code,
                    'detail': str(exc),
                    'correlation_id': correlation_id,
                }
            
            response['Content-Type'] = 'application/problem+json'
        
        # Ajouter correlation ID header
        response['X-Correlation-ID'] = correlation_id
    
    return response

# Exceptions prédéfinies
class ValidationError(RFC7807Exception):
    def __init__(self, detail, errors=None, instance=None):
        super().__init__(
            status_code=400,
            error_code='validation_error',
            title='Validation Error',
            detail=detail,
            instance=instance,
            errors=errors
        )

class AuthenticationError(RFC7807Exception):
    def __init__(self, detail, instance=None):
        super().__init__(
            status_code=401,
            error_code='authentication_failed',
            title='Authentication Failed',
            detail=detail,
            instance=instance
        )

class RateLimitError(RFC7807Exception):
    def __init__(self, detail, retry_after=None, instance=None):
        super().__init__(
            status_code=429,
            error_code='rate_limit_exceeded',
            title='Rate Limit Exceeded',
            detail=detail,
            instance=instance
        )
        self.retry_after = retry_after
```

### 7. Monitoring & Metrics Component

**Responsabilités:**
- Collection de métriques de performance
- Exposition des métriques au format Prometheus
- Génération d'alertes

**Métriques collectées:**
- Nombre de requêtes par endpoint
- Temps de réponse (p50, p95, p99)
- Taux d'erreur par code HTTP
- Utilisation des API keys
- Taux de succès des webhooks


## Data Models

### API Key Management Schema

```python
APIKey
├── key: CharField(64) [unique, indexed]
├── name: CharField(255)
├── organization: CharField(255)
├── contact_email: EmailField
├── is_active: BooleanField
├── created_at: DateTimeField [indexed]
├── expires_at: DateTimeField [nullable]
├── rate_limit: IntegerField
└── last_used_at: DateTimeField [nullable]

APIKeyPermission
├── api_key: ForeignKey(APIKey)
├── resource: CharField(100)
├── scope: CharField(20)
└── granted_at: DateTimeField

APIKeyUsageStats
├── api_key: ForeignKey(APIKey)
├── date: DateField [indexed]
├── request_count: IntegerField
├── error_count: IntegerField
└── avg_response_time_ms: IntegerField
```

### Audit Logging Schema

```python
APIAuditLog
├── id: BigAutoField [primary key]
├── timestamp: DateTimeField [indexed]
├── correlation_id: UUIDField [indexed]
├── api_key: ForeignKey(APIKey) [nullable]
├── user: ForeignKey(User) [nullable]
├── method: CharField(10)
├── endpoint: CharField(255) [indexed]
├── query_params: JSONField
├── request_body: JSONField [masked]
├── response_status: IntegerField [indexed]
├── response_time_ms: IntegerField
├── ip_address: GenericIPAddressField
└── user_agent: TextField

DataChangeLog
├── id: BigAutoField
├── timestamp: DateTimeField [indexed]
├── audit_log: ForeignKey(APIAuditLog)
├── model_name: CharField(100)
├── object_id: CharField(100)
├── action: CharField(20)
├── before_state: JSONField
└── after_state: JSONField
```

### Webhook System Schema

```python
WebhookSubscription
├── id: AutoField
├── api_key: ForeignKey(APIKey)
├── url: URLField
├── events: JSONField  # ['vehicle.created', 'payment.completed']
├── secret: CharField(64)
├── is_active: BooleanField
├── created_at: DateTimeField
└── last_delivery_at: DateTimeField [nullable]

WebhookDelivery
├── id: BigAutoField
├── subscription: ForeignKey(WebhookSubscription)
├── event_type: CharField(100)
├── payload: JSONField
├── signature: CharField(128)
├── status_code: IntegerField [nullable]
├── attempts: IntegerField
├── delivered_at: DateTimeField [nullable]
├── next_retry_at: DateTimeField [nullable]
└── error_message: TextField [nullable]
```

### API Version Management

```python
APIVersion
├── version: CharField(10) [unique]  # 'v1', 'v2'
├── is_active: BooleanField
├── is_deprecated: BooleanField
├── deprecation_date: DateField [nullable]
├── sunset_date: DateField [nullable]
└── changelog: TextField
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: JSON UTF-8 Response Format
*For any* API response, the content should be valid JSON with UTF-8 encoding.
**Validates: Requirements 1.3**

### Property 2: HTTP Status Code Correctness
*For any* API request outcome (success, client error, server error), the HTTP status code should match the appropriate range (2xx, 4xx, 5xx respectively).
**Validates: Requirements 1.4**

### Property 3: API URL Versioning
*For any* public API endpoint, the URL path should include version prefix matching pattern `/api/v[0-9]+/`.
**Validates: Requirements 1.5**

### Property 4: Documentation Examples Completeness
*For any* documented API endpoint in OpenAPI spec, request and response examples should be present.
**Validates: Requirements 2.3**

### Property 5: Multilingual Error Documentation
*For any* error code defined in the system, descriptions should exist in both French and Malagasy languages.
**Validates: Requirements 2.4**

### Property 6: OAuth 2.0 Token Validation
*For any* OAuth 2.0 access token (valid or invalid), the authentication system should correctly validate or reject it based on signature and expiration.
**Validates: Requirements 3.2**

### Property 7: JWT Signature Verification
*For any* JWT token presented to protected endpoints, the system should verify the signature before granting access.
**Validates: Requirements 3.3**

### Property 8: API Key Authentication
*For any* API key (valid, invalid, or expired), the authentication system should correctly authenticate or reject the request.
**Validates: Requirements 3.4**

### Property 9: Rate Limiting Enforcement
*For any* API key with configured rate limit, exceeding the limit within the time window should result in HTTP 429 (Too Many Requests) response.
**Validates: Requirements 3.5**

### Property 10: Authentication Error Sanitization
*For any* authentication failure, the error response should not expose sensitive information such as whether a user exists or internal system details.
**Validates: Requirements 3.6**

### Property 11: RBAC Access Control
*For any* user with specific role permissions, API access should be granted only to endpoints within their authorized scope.
**Validates: Requirements 4.1**

### Property 12: Permission Scope Enforcement
*For any* API key with specific scopes (read, write, admin), operations outside the granted scopes should be rejected with HTTP 403.
**Validates: Requirements 4.3**

### Property 13: API Key Revocation Immediacy
*For any* API key that is revoked, subsequent requests using that key should immediately fail authentication.
**Validates: Requirements 4.4**

### Property 14: API Key Operation Logging
*For any* API key operation (creation, modification, revocation), an audit log entry should be created with timestamp and actor information.
**Validates: Requirements 4.5**

### Property 15: Complete Audit Logging
*For any* API request, an audit log entry should be created containing timestamp, source IP, authentication identity, endpoint, and response status.
**Validates: Requirements 5.1**

### Property 16: Data Modification Tracking
*For any* data modification via API (create, update, delete), a change log should record the before and after states.
**Validates: Requirements 5.3**

### Property 17: RFC 7807 Error Format
*For any* error response, the structure should conform to RFC 7807 Problem Details format with type, title, status, detail, and instance fields.
**Validates: Requirements 6.1**

### Property 18: Error Response Completeness
*For any* error that occurs, the response should include error code, human-readable message, and correlation ID for tracing.
**Validates: Requirements 6.2**

### Property 19: Multilingual Error Messages
*For any* error response with Accept-Language header set to 'fr' or 'mg', the error message should be returned in the requested language.
**Validates: Requirements 6.3**

### Property 20: Validation Error Detail
*For any* request that fails validation, the error response should include field-level details indicating which fields failed and why.
**Validates: Requirements 6.5**

### Property 21: Webhook Event Delivery
*For any* event that occurs and has active webhook subscriptions, HTTP POST notifications should be sent to all subscribed URLs.
**Validates: Requirements 8.3**

### Property 22: Data Export Format Correctness
*For any* data export request specifying format (JSON, CSV, XML), the response should be valid and well-formed in the requested format.
**Validates: Requirements 8.5**

### Property 23: Sensitive Data Masking in Logs
*For any* audit log entry containing sensitive personal data (NIF, phone numbers, passwords), the data should be masked or hashed.
**Validates: Requirements 9.2**

### Property 24: Consent Verification for Personal Data
*For any* API request accessing personal data, the system should verify that appropriate consent exists before returning the data.
**Validates: Requirements 9.3**

### Property 25: Multilingual API Responses
*For any* API request with Accept-Language header, the response content (labels, messages) should be in the requested language (French or Malagasy).
**Validates: Requirements 10.1, 10.2**

### Property 26: Default Language Fallback
*For any* API request without Accept-Language header, the response should default to French language.
**Validates: Requirements 10.4**

### Property 27: Translation Completeness
*For any* translatable content (error messages, field labels), translations should exist in both French and Malagasy.
**Validates: Requirements 10.3**

### Property 28: Metrics Collection
*For any* API request, metrics should be collected including response time, endpoint, status code, and timestamp.
**Validates: Requirements 11.1**

### Property 29: Deprecation Warning Headers
*For any* request to a deprecated API endpoint, the response should include deprecation warning headers (Sunset, Deprecation).
**Validates: Requirements 12.3**

### Property 30: Sandbox Response Marking
*For any* API response from sandbox environment, the response should include clear indicators (headers or body fields) marking it as test data.
**Validates: Requirements 13.3**

### Property 31: ISO 8601 Date Format
*For any* date or datetime value in API responses, the format should conform to ISO 8601 standard.
**Validates: Requirements 14.1**

### Property 32: ISO 4217 Currency Codes
*For any* monetary value in API responses, the currency should be specified using ISO 4217 codes (MGA for Malagasy Ariary).
**Validates: Requirements 14.2**

### Property 33: Pagination Link Headers
*For any* paginated API response, Link headers should be present with rel values (first, prev, next, last) following RFC 5988.
**Validates: Requirements 14.3**

### Property 34: Content Negotiation
*For any* API request with Accept header, the response Content-Type should match the requested media type if supported.
**Validates: Requirements 14.4**

### Property 35: CORS Headers
*For any* cross-origin API request, appropriate CORS headers (Access-Control-Allow-Origin, etc.) should be present in the response.
**Validates: Requirements 14.5**

### Property 36: Webhook HMAC Signature
*For any* webhook delivery, the HTTP request should include an HMAC-SHA256 signature header computed from the payload and subscription secret.
**Validates: Requirements 15.3**

### Property 37: Webhook Retry with Exponential Backoff
*For any* failed webhook delivery, the system should retry up to 3 times with exponentially increasing delays between attempts.
**Validates: Requirements 15.4**


## Error Handling

### Error Response Structure (RFC 7807)

Toutes les erreurs suivent le format RFC 7807 Problem Details:

```json
{
  "type": "https://api.taxcollector.gov.mg/errors/rate-limit-exceeded",
  "title": "Limite de taux dépassée",
  "status": 429,
  "detail": "Vous avez dépassé la limite de 1000 requêtes par heure pour cette clé API",
  "instance": "/api/v1/vehicles/ABC123",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "retry_after": 3600
}
```

### Error Categories

1. **Authentication Errors (401)**
   - `invalid_token`: Token JWT invalide ou expiré
   - `missing_credentials`: Identifiants manquants
   - `invalid_api_key`: Clé API invalide ou révoquée

2. **Authorization Errors (403)**
   - `insufficient_permissions`: Permissions insuffisantes
   - `scope_not_granted`: Scope non accordé pour cette ressource
   - `resource_forbidden`: Accès à la ressource interdit

3. **Rate Limiting Errors (429)**
   - `rate_limit_exceeded`: Limite de taux dépassée
   - `quota_exceeded`: Quota mensuel dépassé

4. **Validation Errors (400)**
   - `invalid_request`: Requête malformée
   - `validation_failed`: Échec de validation avec détails par champ
   - `missing_required_field`: Champ requis manquant

5. **Resource Errors (404, 409)**
   - `resource_not_found`: Ressource non trouvée
   - `resource_conflict`: Conflit de ressource (doublon)

6. **Server Errors (500, 503)**
   - `internal_error`: Erreur interne du serveur
   - `service_unavailable`: Service temporairement indisponible
   - `external_service_error`: Erreur du service externe

### Error Handling Middleware

```python
# api/middleware/error_handler.py
class StandardErrorHandlerMiddleware:
    """Middleware pour standardiser les réponses d'erreur"""
    
    def process_exception(self, request, exception):
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID', uuid.uuid4())
        language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'fr')[:2]
        
        # Convertir l'exception en réponse RFC 7807
        error_response = self.exception_to_rfc7807(
            exception, 
            correlation_id, 
            language
        )
        
        # Logger l'erreur
        self.log_error(request, exception, correlation_id)
        
        return JsonResponse(error_response, status=error_response['status'])
```

### Sensitive Data Masking

Les données sensibles sont masquées dans les logs:
- NIF: `1234567890123` → `123****90123`
- Téléphone: `+261340000000` → `+261****0000`
- Email: `user@example.com` → `u***@example.com`
- Mots de passe: Jamais loggés


## Testing Strategy

### Unit Testing

Les tests unitaires couvrent les composants individuels:

**Composants à tester:**
- Validation de tokens JWT
- Génération et validation de signatures HMAC
- Masquage de données sensibles
- Formatage des erreurs RFC 7807
- Traduction des messages
- Parsing et validation des headers

**Framework:** pytest avec Django test client

**Exemples de tests unitaires:**
```python
def test_jwt_token_validation():
    """Vérifie la validation des tokens JWT"""
    # Test avec token valide
    # Test avec token expiré
    # Test avec signature invalide
    
def test_sensitive_data_masking():
    """Vérifie le masquage des données sensibles"""
    # Test masquage NIF
    # Test masquage téléphone
    # Test masquage email
```

### Property-Based Testing

Les tests basés sur les propriétés vérifient les comportements universels du système.

**Framework:** Hypothesis (Python)

**Configuration:** Minimum 100 itérations par propriété

**Stratégie de génération:**
- Générateurs de tokens JWT (valides/invalides/expirés)
- Générateurs de requêtes API avec headers variés
- Générateurs de données sensibles à masquer
- Générateurs de payloads webhook

**Exemples de tests de propriétés:**

```python
from hypothesis import given, strategies as st

@given(st.text(), st.sampled_from(['fr', 'mg']))
def test_property_multilingual_errors(error_code, language):
    """Property 5: Multilingual Error Documentation
    
    Feature: government-interoperability-standards, Property 5
    Validates: Requirements 2.4
    """
    # Pour tout code d'erreur et langue, une traduction doit exister
    error_message = get_error_message(error_code, language)
    assert error_message is not None
    assert len(error_message) > 0

@given(st.builds(generate_jwt_token))
def test_property_jwt_validation(token):
    """Property 7: JWT Signature Verification
    
    Feature: government-interoperability-standards, Property 7
    Validates: Requirements 3.3
    """
    # Pour tout token JWT, la validation doit vérifier la signature
    result = validate_jwt_token(token)
    if token.is_valid:
        assert result.success is True
    else:
        assert result.success is False
        assert 'signature' in result.error_message.lower()

@given(st.builds(generate_api_key), st.integers(min_value=1, max_value=2000))
def test_property_rate_limiting(api_key, request_count):
    """Property 9: Rate Limiting Enforcement
    
    Feature: government-interoperability-standards, Property 9
    Validates: Requirements 3.5
    """
    # Pour toute clé API avec limite, dépasser la limite doit rejeter
    responses = []
    for _ in range(request_count):
        response = make_api_request(api_key)
        responses.append(response)
    
    exceeded_count = sum(1 for r in responses if r.status_code == 429)
    if request_count > api_key.rate_limit:
        assert exceeded_count > 0

@given(st.text(min_size=1), st.sampled_from(['json', 'csv', 'xml']))
def test_property_export_format(data, format_type):
    """Property 22: Data Export Format Correctness
    
    Feature: government-interoperability-standards, Property 22
    Validates: Requirements 8.5
    """
    # Pour tout export dans un format, le résultat doit être valide
    exported = export_data(data, format_type)
    assert is_valid_format(exported, format_type)

@given(st.datetimes())
def test_property_iso8601_dates(dt):
    """Property 31: ISO 8601 Date Format
    
    Feature: government-interoperability-standards, Property 31
    Validates: Requirements 14.1
    """
    # Pour toute date dans une réponse API, le format doit être ISO 8601
    response = create_api_response_with_date(dt)
    date_string = response['timestamp']
    # Vérifier que c'est un ISO 8601 valide
    parsed = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    assert parsed is not None

@given(st.builds(generate_webhook_payload))
def test_property_webhook_signature(payload):
    """Property 36: Webhook HMAC Signature
    
    Feature: government-interoperability-standards, Property 36
    Validates: Requirements 15.3
    """
    # Pour tout webhook, la signature HMAC doit être correcte
    secret = 'test_secret'
    signature = generate_webhook_signature(payload, secret)
    assert verify_webhook_signature(payload, signature, secret)
```

### Integration Testing

Tests d'intégration pour les flux complets:

**Scénarios:**
1. Enregistrement d'une clé API → Authentification → Appel API → Audit log
2. Dépassement de rate limit → Erreur 429 → Retry après délai
3. Webhook subscription → Événement → Delivery → Retry sur échec
4. Requête multilingue → Réponse traduite → Vérification langue
5. Accès données personnelles → Vérification consentement → Masquage logs

**Framework:** pytest avec fixtures Django

### Load Testing

Tests de charge pour valider les performances:

**Outils:** Locust ou Apache JMeter

**Scénarios:**
- 1000 requêtes/seconde pendant 5 minutes
- Vérifier temps de réponse < 2s pour 95% des requêtes
- Vérifier rate limiting fonctionne sous charge
- Vérifier pas de perte de logs d'audit

### Security Testing

Tests de sécurité:

**Vérifications:**
- Injection SQL dans paramètres API
- XSS dans réponses API
- Exposition de données sensibles dans erreurs
- Validation des tokens expirés
- Bypass de rate limiting
- CORS misconfiguration

**Outils:** OWASP ZAP, Bandit (Python security linter)

### Compliance Testing

Tests de conformité aux standards:

**Vérifications:**
- OpenAPI spec valide selon OpenAPI 3.0 schema
- Erreurs conformes RFC 7807
- Dates conformes ISO 8601
- Devises conformes ISO 4217
- CORS headers conformes W3C spec
- JWT tokens conformes RFC 7519

