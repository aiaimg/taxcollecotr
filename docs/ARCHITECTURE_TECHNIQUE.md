# Documentation Technique - TaxCollector Platform

**Version:** 2.0  
**Date:** Novembre 2025  
**Classification:** Document Technique Interne

---

## Table des Matières

1. [Vue d'Ensemble du Système](#1-vue-densemble-du-système)
2. [Architecture Applicative](#2-architecture-applicative)
3. [Infrastructure et Déploiement](#3-infrastructure-et-déploiement)
4. [Base de Données](#4-base-de-données)
5. [Sécurité](#5-sécurité)
6. [Monitoring et Observabilité](#6-monitoring-et-observabilité)
7. [Backup et Récupération](#7-backup-et-récupération)
8. [Haute Disponibilité et Réplication](#8-haute-disponibilité-et-réplication)
9. [Performance et Scalabilité](#9-performance-et-scalabilité)
10. [Procédures Opérationnelles](#10-procédures-opérationnelles)

---

## 1. Vue d'Ensemble du Système

### 1.1 Description Générale

TaxCollector est une plateforme de gestion des taxes sur les véhicules pour Madagascar, conforme au PLF 2026. Elle supporte:

- **Véhicules Terrestres**: Voitures, motos, camions, bus
- **Véhicules Aériens**: Avions, hélicoptères, drones, ULM
- **Véhicules Maritimes**: Bateaux, yachts, jet-skis

### 1.2 Stack Technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.2+ |
| API | Django REST Framework | 3.14+ |
| Base de données | PostgreSQL | 16 |
| Cache/Sessions | Redis | 7.x |
| Queue | Celery | 5.x |
| Serveur WSGI | Gunicorn | 21.x |
| Reverse Proxy | Nginx | 1.24+ |
| Conteneurisation | Docker | 24.x |

### 1.3 Diagramme d'Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    INTERNET                                      │
│                              (Utilisateurs / API Clients)                        │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CDN / CloudFlare                                    │
│  • Protection DDoS          • Cache statique (CSS, JS, Images)                  │
│  • SSL/TLS Termination      • Compression Gzip/Brotli                           │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LOAD BALANCER (Nginx / AWS ALB)                          │
│  • Health Checks            • SSL Termination                                    │
│  • Sticky Sessions          • Rate Limiting                                      │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ↓                               ↓
┌──────────────────────────────────────┐  ┌────────────────────────────────────┐
│      COUCHE APPLICATION              │  │     WORKERS ASYNCHRONES           │
│                                      │  │                                    │
│  ┌────────────────────────────────┐ │  │  ┌──────────────────────────────┐ │
│  │  Django + Gunicorn             │ │  │  │  Celery Workers              │ │
│  │  • API REST                    │ │  │  │  • Envoi emails              │ │
│  │  • Interface Web               │ │  │  │  • Traitement OCR            │ │
│  │  • Authentification            │ │  │  │  • Génération rapports       │ │
│  │  • Calcul taxes                │ │  │  │  • Webhooks                  │ │
│  └────────────────────────────────┘ │  │  └──────────────────────────────┘ │
│                                      │  │                                    │
│  Auto-Scaling: 6-16 instances        │  │  4-6 workers                       │
└──────────────────────────────────────┘  └────────────────────────────────────┘
                     │                               │
                     └───────────────┬───────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ↓                           ↓                           ↓
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   POSTGRESQL     │      │     REDIS        │      │     AWS S3       │
│                  │      │                  │      │                  │
│  • Primary       │      │  • Cache         │      │  • Documents     │
│  • 2 Replicas    │      │  • Sessions      │      │  • Images OCR    │
│  • PgBouncer     │      │  • Queue Celery  │      │  • Backups       │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## 2. Architecture Applicative

### 2.1 Structure des Modules Django

```
taxcollector/
├── api/                    # API REST v1
│   ├── v1/                 # Endpoints versionnés
│   ├── authentication.py   # Auth API Key + JWT
│   ├── models.py           # APIKey, AuditLog, Webhooks
│   └── middleware/         # Audit, Rate Limiting
├── vehicles/               # Gestion véhicules
│   ├── models.py           # Vehicule, VehicleType, GrilleTarifaire
│   ├── services.py         # Calcul taxes
│   └── forms.py            # Formulaires multi-catégories
├── payments/               # Paiements
│   ├── mvola/              # Intégration MVola
│   └── stripe/             # Intégration Stripe
├── notifications/          # Système de notifications
├── contraventions/         # Gestion contraventions
├── administration/         # Interface admin
├── core/                   # Utilitaires communs
└── cms/                    # Gestion contenu
```

### 2.2 Flux de Données

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUX DE REQUÊTE TYPIQUE                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. Requête Utilisateur
   │
   ↓
2. CDN (CloudFlare)
   ├── Ressource statique? → Retour cache
   └── Requête dynamique? → Continue
   │
   ↓
3. Load Balancer
   ├── Health check serveur
   └── Routage vers instance disponible
   │
   ↓
4. Django Application
   │
   ├── 4.1 Vérification Cache Redis
   │   ├── HIT → Retour données cachées
   │   └── MISS → Continue
   │
   ├── 4.2 Authentification
   │   ├── JWT Token
   │   ├── API Key
   │   └── Session
   │
   ├── 4.3 Autorisation
   │   ├── Permissions utilisateur
   │   └── Permissions API Key
   │
   ├── 4.4 Traitement Business Logic
   │   ├── Validation données
   │   ├── Calculs (taxes, etc.)
   │   └── Opérations DB
   │
   ├── 4.5 Mise en Cache
   │   └── Stockage Redis (TTL: 5-60 min)
   │
   └── 4.6 Audit Logging
       └── Enregistrement APIAuditLog
   │
   ↓
5. Réponse Client
```

### 2.3 Modèle de Données Principal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODÈLE DE DONNÉES                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│      User        │     │    Vehicule      │     │   VehicleType    │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id               │     │ id (UUID)        │     │ id               │
│ email            │────→│ proprietaire_id  │←────│ nom              │
│ first_name       │     │ type_vehicule_id │     │ categorie        │
│ last_name        │     │ plaque           │     │ description      │
│ user_type        │     │ marque           │     │ est_actif        │
│ is_active        │     │ modele           │     └──────────────────┘
└──────────────────┘     │ categorie        │
                         │ statut_paiement  │     ┌──────────────────┐
                         │ montant_taxe     │     │ GrilleTarifaire  │
                         └──────────────────┘     ├──────────────────┤
                                │                 │ grid_type        │
                                │                 │ annee_fiscale    │
                                ↓                 │ puissance_min    │
┌──────────────────┐     ┌──────────────────┐     │ puissance_max    │
│    Payment       │     │ VehicleDocument  │     │ montant          │
├──────────────────┤     ├──────────────────┤     └──────────────────┘
│ id               │     │ id               │
│ vehicule_id      │     │ vehicule_id      │
│ montant          │     │ type_document    │
│ methode          │     │ fichier          │
│ statut           │     │ date_upload      │
│ reference        │     │ est_verifie      │
└──────────────────┘     └──────────────────┘
```

---

## 3. Infrastructure et Déploiement

### 3.1 Configuration Docker

```yaml
# docker-compose.production.yml
version: "3.8"

services:
  web:
    build: .
    image: taxcollector:latest
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - DJANGO_SETTINGS_MODULE=taxcollector_project.settings_prod
      - DATABASE_URL=postgres://user:pass@db:5432/taxcollector
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build: .
    command: celery -A taxcollector_project worker -l info
    deploy:
      replicas: 2
    depends_on:
      - redis
      - db

  celery-beat:
    build: .
    command: celery -A taxcollector_project beat -l info
    deploy:
      replicas: 1
    depends_on:
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=taxcollector
      - POSTGRES_USER=taxcollector
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  nginx:
    image: nginx:1.24
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

### 3.2 Configuration Nginx

```nginx
# /etc/nginx/nginx.conf
upstream django {
    least_conn;
    server web1:8000 weight=5;
    server web2:8000 weight=5;
    server web3:8000 weight=5;
    server web4:8000 weight=5;
    keepalive 32;
}

server {
    listen 80;
    server_name taxcollector.mg;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name taxcollector.mg;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript;

    # Static Files
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /app/media/;
        expires 30d;
    }

    # API Rate Limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Application
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate Limiting Zones
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
```

### 3.3 Configuration Gunicorn

```python
# gunicorn.conf.py
import multiprocessing

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000

# Performance
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process Naming
proc_name = 'taxcollector'

# Server Socket
bind = '0.0.0.0:8000'
backlog = 2048

# SSL (si terminaison au niveau Gunicorn)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
```

---

## 4. Base de Données

### 4.1 Configuration PostgreSQL

```sql
-- postgresql.conf (paramètres optimisés pour 20K utilisateurs)

-- Mémoire
shared_buffers = 32GB                    -- 25% de la RAM
effective_cache_size = 96GB              -- 75% de la RAM
work_mem = 256MB                         -- Pour les opérations de tri
maintenance_work_mem = 2GB               -- Pour VACUUM, CREATE INDEX

-- Connexions
max_connections = 500
superuser_reserved_connections = 5

-- WAL et Réplication
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
synchronous_commit = on
synchronous_standby_names = 'replica1,replica2'

-- Checkpoints
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min
max_wal_size = 4GB
min_wal_size = 1GB

-- Query Planner
random_page_cost = 1.1                   -- Pour SSD
effective_io_concurrency = 200           -- Pour SSD
default_statistics_target = 100

-- Logging
log_min_duration_statement = 1000        -- Log requêtes > 1s
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

-- Autovacuum
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
```

### 4.2 Configuration PgBouncer (Connection Pooling)

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
taxcollector = host=primary.db.internal port=5432 dbname=taxcollector
taxcollector_replica = host=replica1.db.internal port=5432 dbname=taxcollector

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool Mode
pool_mode = transaction

# Pool Size
default_pool_size = 50
min_pool_size = 10
reserve_pool_size = 10
reserve_pool_timeout = 5
max_client_conn = 1000
max_db_connections = 100

# Timeouts
server_connect_timeout = 15
server_idle_timeout = 600
server_lifetime = 3600
client_idle_timeout = 0
client_login_timeout = 60
query_timeout = 0
query_wait_timeout = 120

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
stats_period = 60

# Admin
admin_users = postgres
stats_users = monitoring
```

### 4.3 Index Optimisés

```sql
-- Index pour les requêtes fréquentes

-- Véhicules par propriétaire
CREATE INDEX CONCURRENTLY idx_vehicule_proprietaire 
ON vehicles_vehicule(proprietaire_id);

-- Véhicules par catégorie
CREATE INDEX CONCURRENTLY idx_vehicule_categorie 
ON vehicles_vehicule(categorie_vehicule);

-- Véhicules par statut de paiement
CREATE INDEX CONCURRENTLY idx_vehicule_statut_paiement 
ON vehicles_vehicule(statut_paiement) 
WHERE statut_paiement IN ('IMPAYE', 'EN_ATTENTE');

-- Recherche par plaque (partiel)
CREATE INDEX CONCURRENTLY idx_vehicule_plaque_trgm 
ON vehicles_vehicule USING gin(plaque_immatriculation gin_trgm_ops);

-- Paiements récents
CREATE INDEX CONCURRENTLY idx_payment_date 
ON payments_payment(date_paiement DESC);

-- Audit logs par date
CREATE INDEX CONCURRENTLY idx_audit_timestamp 
ON api_audit_logs(timestamp DESC);

-- Audit logs par correlation_id
CREATE INDEX CONCURRENTLY idx_audit_correlation 
ON api_audit_logs(correlation_id);

-- API Keys actives
CREATE INDEX CONCURRENTLY idx_apikey_active 
ON api_keys(is_active) WHERE is_active = true;
```

---

## 5. Sécurité

### 5.1 Architecture de Sécurité

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COUCHES DE SÉCURITÉ                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 1: PÉRIMÈTRE                                                         │
│  • CloudFlare WAF (Web Application Firewall)                                │
│  • Protection DDoS                                                           │
│  • Rate Limiting au niveau CDN                                              │
│  • Blocage géographique (optionnel)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 2: RÉSEAU                                                            │
│  • VPC isolé                                                                 │
│  • Security Groups restrictifs                                              │
│  • Subnets privés pour DB/Redis                                             │
│  • NAT Gateway pour accès sortant                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 3: TRANSPORT                                                         │
│  • TLS 1.2/1.3 obligatoire                                                  │
│  • Certificats Let's Encrypt / ACM                                          │
│  • HSTS activé                                                               │
│  • Perfect Forward Secrecy                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 4: APPLICATION                                                       │
│  • Authentification JWT + API Keys                                          │
│  • RBAC (Role-Based Access Control)                                         │
│  • CSRF Protection                                                           │
│  • Input Validation                                                          │
│  • SQL Injection Prevention (ORM)                                           │
│  • XSS Prevention                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 5: DONNÉES                                                           │
│  • Chiffrement au repos (AES-256)                                           │
│  • Chiffrement en transit (TLS)                                             │
│  • Masquage PII dans les logs                                               │
│  • Rotation des secrets                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Configuration Authentification

```python
# settings.py - Configuration Sécurité

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# API Key Authentication
API_KEY_HEADER = 'X-API-Key'
API_KEY_PREFIX = 'tc_'
API_KEY_LENGTH = 48

# Rate Limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '1000/minute',
        'api_key_hour': '1000/hour',
        'api_key_day': '10000/day',
        'auth': '5/minute',
        'payment': '10/minute',
    },
}

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### 5.3 Gestion des Secrets

```yaml
# Utilisation AWS Secrets Manager ou HashiCorp Vault

# Structure des secrets
secrets/
├── database/
│   ├── primary_password
│   ├── replica_password
│   └── pgbouncer_password
├── redis/
│   └── auth_password
├── api/
│   ├── secret_key
│   ├── jwt_signing_key
│   └── encryption_key
├── external/
│   ├── mvola_consumer_key
│   ├── mvola_consumer_secret
│   ├── stripe_secret_key
│   └── smtp_password
└── ssl/
    ├── certificate
    └── private_key
```

```python
# secrets_manager.py
import boto3
from functools import lru_cache

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager')
    
    @lru_cache(maxsize=100)
    def get_secret(self, secret_name: str) -> str:
        response = self.client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    
    def rotate_secret(self, secret_name: str):
        self.client.rotate_secret(SecretId=secret_name)
        self.get_secret.cache_clear()
```

---

## 6. Monitoring et Observabilité

### 6.1 Stack de Monitoring

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STACK MONITORING                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   PROMETHEUS     │     │    GRAFANA       │     │    ALERTMANAGER  │
│                  │     │                  │     │                  │
│  • Métriques     │────→│  • Dashboards    │     │  • Alertes       │
│  • Scraping      │     │  • Visualisation │←────│  • Routing       │
│  • Storage       │     │  • Annotations   │     │  • Notifications │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        ↑                                                  │
        │                                                  ↓
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  DJANGO APP      │     │    ELK STACK     │     │   NOTIFICATION   │
│                  │     │                  │     │                  │
│  • django_prom   │     │  • Elasticsearch │     │  • Email         │
│  • Custom metrics│     │  • Logstash      │     │  • Slack         │
│  • Health checks │     │  • Kibana        │     │  • SMS           │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 6.2 Configuration Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  # Django Application
  - job_name: 'django'
    static_configs:
      - targets: ['web1:8000', 'web2:8000', 'web3:8000', 'web4:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  # Node Exporter (système)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # Celery
  - job_name: 'celery'
    static_configs:
      - targets: ['celery-exporter:9808']
```

### 6.3 Règles d'Alertes

```yaml
# /etc/prometheus/rules/alerts.yml
groups:
  - name: api_performance
    rules:
      - alert: HighErrorRate
        expr: sum(rate(api_error_total[5m])) / sum(rate(api_request_total[5m])) > 0.05
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'erreur API élevé"
          description: "Le taux d'erreur dépasse 5% depuis 10 minutes"

      - alert: HighLatencyP95
        expr: histogram_quantile(0.95, sum by (le) (rate(api_response_time_seconds_bucket[5m]))) > 1.0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Latence API élevée (P95)"
          description: "Le temps de réponse P95 dépasse 1 seconde"

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation CPU élevée"
          description: "CPU > 80% depuis 15 minutes sur {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation mémoire élevée"
          description: "Mémoire > 85% sur {{ $labels.instance }}"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connexions DB élevées"
          description: "Plus de 400 connexions actives à PostgreSQL"

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Mémoire Redis élevée"
          description: "Redis utilise plus de 80% de sa mémoire"

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "File Celery saturée"
          description: "Plus de 1000 tâches en attente"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 15
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Espace disque faible"
          description: "Moins de 15% d'espace disque disponible"
```

### 6.4 Dashboards Grafana

```json
// Dashboard principal - Métriques clés
{
  "dashboard": {
    "title": "TaxCollector - Vue d'ensemble",
    "panels": [
      {
        "title": "Requêtes par seconde",
        "type": "graph",
        "targets": [
          {"expr": "sum(rate(django_http_requests_total[5m]))"}
        ]
      },
      {
        "title": "Temps de réponse (P50, P95, P99)",
        "type": "graph",
        "targets": [
          {"expr": "histogram_quantile(0.50, rate(django_http_request_duration_seconds_bucket[5m]))"},
          {"expr": "histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m]))"},
          {"expr": "histogram_quantile(0.99, rate(django_http_request_duration_seconds_bucket[5m]))"}
        ]
      },
      {
        "title": "Taux d'erreur",
        "type": "singlestat",
        "targets": [
          {"expr": "sum(rate(django_http_responses_total{status=~'5..'}[5m])) / sum(rate(django_http_responses_total[5m])) * 100"}
        ]
      },
      {
        "title": "Connexions DB actives",
        "type": "gauge",
        "targets": [
          {"expr": "pg_stat_activity_count"}
        ]
      },
      {
        "title": "Mémoire Redis",
        "type": "gauge",
        "targets": [
          {"expr": "redis_memory_used_bytes / 1024 / 1024"}
        ]
      },
      {
        "title": "Tâches Celery",
        "type": "graph",
        "targets": [
          {"expr": "celery_tasks_total", "legendFormat": "Total"},
          {"expr": "celery_tasks_failed_total", "legendFormat": "Échecs"}
        ]
      }
    ]
  }
}
```

### 6.5 Logging Centralisé

```python
# settings.py - Configuration Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/taxcollector/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'logstash.internal',
            'port': 5000,
            'version': 1,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'logstash'],
            'level': 'INFO',
            'propagate': False,
        },
        'taxcollector': {
            'handlers': ['console', 'file', 'logstash'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file', 'logstash'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## 7. Backup et Récupération

### 7.1 Stratégie de Backup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STRATÉGIE DE BACKUP                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TYPE              │  FRÉQUENCE    │  RÉTENTION    │  STOCKAGE              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Snapshot DB       │  Toutes 6h    │  7 jours      │  S3 Standard           │
│  Backup complet    │  Quotidien    │  30 jours     │  S3 Standard           │
│  Backup mensuel    │  Mensuel      │  12 mois      │  S3 Glacier            │
│  Backup annuel     │  Annuel       │  7 ans        │  S3 Glacier Deep       │
│  WAL Archiving     │  Continu      │  7 jours      │  S3 Standard           │
│  Media files       │  Quotidien    │  30 jours     │  S3 Standard           │
│  Config files      │  À chaque     │  90 jours     │  S3 Standard           │
│                    │  modification │               │                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Scripts de Backup

```bash
#!/bin/bash
# /opt/scripts/backup_database.sh

set -e

# Configuration
DB_HOST="primary.db.internal"
DB_NAME="taxcollector"
DB_USER="backup_user"
S3_BUCKET="taxcollector-backups"
BACKUP_DIR="/tmp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="taxcollector_${DATE}.sql.gz"

# Créer le répertoire de backup
mkdir -p ${BACKUP_DIR}

# Backup PostgreSQL
echo "Starting database backup..."
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h ${DB_HOST} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -F c \
    -Z 9 \
    --no-owner \
    --no-acl \
    -f ${BACKUP_DIR}/${BACKUP_FILE}

# Vérifier l'intégrité
echo "Verifying backup integrity..."
pg_restore --list ${BACKUP_DIR}/${BACKUP_FILE} > /dev/null

# Upload vers S3
echo "Uploading to S3..."
aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE} \
    s3://${S3_BUCKET}/database/daily/${BACKUP_FILE} \
    --storage-class STANDARD_IA \
    --sse AES256

# Calculer et stocker le checksum
sha256sum ${BACKUP_DIR}/${BACKUP_FILE} > ${BACKUP_DIR}/${BACKUP_FILE}.sha256
aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE}.sha256 \
    s3://${S3_BUCKET}/database/daily/${BACKUP_FILE}.sha256

# Nettoyage local
rm -f ${BACKUP_DIR}/${BACKUP_FILE}*

# Notification
echo "Backup completed: ${BACKUP_FILE}"
curl -X POST "${SLACK_WEBHOOK}" \
    -H 'Content-type: application/json' \
    -d "{\"text\":\"✅ Database backup completed: ${BACKUP_FILE}\"}"
```

```bash
#!/bin/bash
# /opt/scripts/backup_media.sh

set -e

S3_SOURCE="s3://taxcollector-media"
S3_BACKUP="s3://taxcollector-backups/media"
DATE=$(date +%Y%m%d)

# Sync media files to backup bucket
aws s3 sync ${S3_SOURCE} ${S3_BACKUP}/${DATE}/ \
    --storage-class STANDARD_IA \
    --sse AES256

# Cleanup old backups (keep 30 days)
aws s3 ls ${S3_BACKUP}/ | while read -r line; do
    folder=$(echo $line | awk '{print $2}' | tr -d '/')
    folder_date=$(echo $folder | grep -oP '\d{8}' || echo "")
    if [ -n "$folder_date" ]; then
        age=$(( ($(date +%s) - $(date -d "$folder_date" +%s)) / 86400 ))
        if [ $age -gt 30 ]; then
            aws s3 rm ${S3_BACKUP}/${folder}/ --recursive
        fi
    fi
done
```

### 7.3 Procédure de Restauration

```bash
#!/bin/bash
# /opt/scripts/restore_database.sh

set -e

# Configuration
BACKUP_FILE=$1
DB_HOST="primary.db.internal"
DB_NAME="taxcollector"
DB_USER="admin"
S3_BUCKET="taxcollector-backups"
RESTORE_DIR="/tmp/restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 taxcollector_20251125_020000.sql.gz"
    exit 1
fi

# Créer le répertoire de restauration
mkdir -p ${RESTORE_DIR}

# Télécharger le backup
echo "Downloading backup from S3..."
aws s3 cp s3://${S3_BUCKET}/database/daily/${BACKUP_FILE} ${RESTORE_DIR}/

# Vérifier le checksum
echo "Verifying checksum..."
aws s3 cp s3://${S3_BUCKET}/database/daily/${BACKUP_FILE}.sha256 ${RESTORE_DIR}/
cd ${RESTORE_DIR} && sha256sum -c ${BACKUP_FILE}.sha256

# Arrêter les connexions actives
echo "Terminating active connections..."
PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -U ${DB_USER} -d postgres -c "
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
"

# Restaurer la base de données
echo "Restoring database..."
PGPASSWORD="${DB_PASSWORD}" pg_restore \
    -h ${DB_HOST} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    --clean \
    --if-exists \
    --no-owner \
    --no-acl \
    -j 4 \
    ${RESTORE_DIR}/${BACKUP_FILE}

# Vérifier la restauration
echo "Verifying restoration..."
PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT COUNT(*) as vehicles FROM vehicles_vehicule;
    SELECT COUNT(*) as users FROM auth_user;
    SELECT COUNT(*) as payments FROM payments_payment;
"

# Nettoyage
rm -rf ${RESTORE_DIR}

echo "Restoration completed successfully!"
```

### 7.4 Point-in-Time Recovery (PITR)

```bash
#!/bin/bash
# /opt/scripts/pitr_restore.sh

# Configuration pour PITR
RECOVERY_TARGET_TIME=$1  # Format: '2025-11-25 14:30:00'
BASE_BACKUP_DIR="/var/lib/postgresql/base_backup"
WAL_ARCHIVE_DIR="/var/lib/postgresql/wal_archive"
DATA_DIR="/var/lib/postgresql/16/main"

if [ -z "$RECOVERY_TARGET_TIME" ]; then
    echo "Usage: $0 '<recovery_target_time>'"
    echo "Example: $0 '2025-11-25 14:30:00'"
    exit 1
fi

# Arrêter PostgreSQL
sudo systemctl stop postgresql

# Sauvegarder le répertoire de données actuel
sudo mv ${DATA_DIR} ${DATA_DIR}.old.$(date +%Y%m%d_%H%M%S)

# Restaurer le base backup le plus récent avant la date cible
LATEST_BACKUP=$(ls -t ${BASE_BACKUP_DIR} | head -1)
sudo cp -r ${BASE_BACKUP_DIR}/${LATEST_BACKUP} ${DATA_DIR}

# Créer le fichier recovery.signal
sudo touch ${DATA_DIR}/recovery.signal

# Configurer la récupération
cat << EOF | sudo tee ${DATA_DIR}/postgresql.auto.conf
restore_command = 'cp ${WAL_ARCHIVE_DIR}/%f %p'
recovery_target_time = '${RECOVERY_TARGET_TIME}'
recovery_target_action = 'promote'
EOF

# Ajuster les permissions
sudo chown -R postgres:postgres ${DATA_DIR}

# Démarrer PostgreSQL
sudo systemctl start postgresql

# Attendre la fin de la récupération
echo "Waiting for recovery to complete..."
while [ -f ${DATA_DIR}/recovery.signal ]; do
    sleep 5
    echo "Recovery in progress..."
done

echo "PITR completed to ${RECOVERY_TARGET_TIME}"
```

---

## 8. Haute Disponibilité et Réplication

### 8.1 Architecture Haute Disponibilité

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE HAUTE DISPONIBILITÉ                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   DNS / Route53 │
                              │   Health Check  │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
                    ↓                                     ↓
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│      AVAILABILITY ZONE A        │   │      AVAILABILITY ZONE B        │
│                                 │   │                                 │
│  ┌───────────────────────────┐ │   │  ┌───────────────────────────┐ │
│  │     Load Balancer A       │ │   │  │     Load Balancer B       │ │
│  └─────────────┬─────────────┘ │   │  └─────────────┬─────────────┘ │
│                │               │   │                │               │
│  ┌─────────────┴─────────────┐ │   │  ┌─────────────┴─────────────┐ │
│  │                           │ │   │  │                           │ │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ │ │   │  │  ┌─────┐ ┌─────┐ ┌─────┐ │ │
│  │  │Web1 │ │Web2 │ │Web3 │ │ │   │  │  │Web4 │ │Web5 │ │Web6 │ │ │
│  │  └─────┘ └─────┘ └─────┘ │ │   │  │  └─────┘ └─────┘ └─────┘ │ │
│  │                           │ │   │  │                           │ │
│  │  ┌─────────┐ ┌─────────┐ │ │   │  │  ┌─────────┐ ┌─────────┐ │ │
│  │  │Celery 1 │ │Celery 2 │ │ │   │  │  │Celery 3 │ │Celery 4 │ │ │
│  │  └─────────┘ └─────────┘ │ │   │  │  └─────────┘ └─────────┘ │ │
│  └───────────────────────────┘ │   │  └───────────────────────────┘ │
│                                 │   │                                 │
│  ┌───────────────────────────┐ │   │  ┌───────────────────────────┐ │
│  │   PostgreSQL PRIMARY      │ │   │  │   PostgreSQL REPLICA 1    │ │
│  │   (Synchronous)           │←┼───┼──│   (Synchronous)           │ │
│  └───────────────────────────┘ │   │  └───────────────────────────┘ │
│                                 │   │                                 │
│  ┌───────────────────────────┐ │   │  ┌───────────────────────────┐ │
│  │   Redis Primary           │ │   │  │   Redis Replica           │ │
│  │   (Sentinel)              │←┼───┼──│   (Sentinel)              │ │
│  └───────────────────────────┘ │   │  └───────────────────────────┘ │
│                                 │   │                                 │
└─────────────────────────────────┘   └─────────────────────────────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                       ↓
                    ┌─────────────────────────────────┐
                    │      AVAILABILITY ZONE C        │
                    │                                 │
                    │  ┌───────────────────────────┐ │
                    │  │   PostgreSQL REPLICA 2    │ │
                    │  │   (Asynchronous)          │ │
                    │  └───────────────────────────┘ │
                    │                                 │
                    │  ┌───────────────────────────┐ │
                    │  │   Redis Replica           │ │
                    │  │   (Sentinel)              │ │
                    │  └───────────────────────────┘ │
                    │                                 │
                    └─────────────────────────────────┘
```

### 8.2 Configuration Réplication PostgreSQL

```sql
-- Configuration Primary (postgresql.conf)
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
synchronous_commit = on
synchronous_standby_names = 'FIRST 1 (replica1, replica2)'

-- Créer les slots de réplication
SELECT pg_create_physical_replication_slot('replica1_slot');
SELECT pg_create_physical_replication_slot('replica2_slot');

-- Créer l'utilisateur de réplication
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secure_password';
```

```bash
# Configuration Replica (recovery.conf / postgresql.auto.conf)
primary_conninfo = 'host=primary.db.internal port=5432 user=replicator password=secure_password application_name=replica1'
primary_slot_name = 'replica1_slot'
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_timeline = 'latest'
```

```ini
# pg_hba.conf - Autoriser la réplication
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    replication     replicator      10.0.0.0/8              scram-sha-256
```

### 8.3 Configuration Redis Sentinel

```conf
# /etc/redis/sentinel.conf

# Sentinel configuration
port 26379
daemonize yes
pidfile /var/run/redis/redis-sentinel.pid
logfile /var/log/redis/sentinel.log

# Monitor configuration
sentinel monitor taxcollector-redis primary.redis.internal 6379 2
sentinel auth-pass taxcollector-redis your_redis_password
sentinel down-after-milliseconds taxcollector-redis 5000
sentinel parallel-syncs taxcollector-redis 1
sentinel failover-timeout taxcollector-redis 60000

# Notification script
sentinel notification-script taxcollector-redis /opt/scripts/redis-failover-notify.sh
sentinel client-reconfig-script taxcollector-redis /opt/scripts/redis-failover-reconfig.sh
```

```python
# Django Redis configuration with Sentinel
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://taxcollector-redis/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.SentinelClient',
            'SENTINELS': [
                ('sentinel1.internal', 26379),
                ('sentinel2.internal', 26379),
                ('sentinel3.internal', 26379),
            ],
            'PASSWORD': 'your_redis_password',
            'SENTINEL_KWARGS': {
                'password': 'sentinel_password',
            },
        },
    }
}
```

### 8.4 Failover Automatique

```python
# /opt/scripts/database_failover.py
import subprocess
import boto3
import time
from datetime import datetime

class DatabaseFailover:
    def __init__(self):
        self.primary_host = 'primary.db.internal'
        self.replica_hosts = ['replica1.db.internal', 'replica2.db.internal']
        self.sns_topic = 'arn:aws:sns:region:account:db-alerts'
        
    def check_primary_health(self):
        """Vérifier la santé du primary"""
        try:
            result = subprocess.run(
                ['pg_isready', '-h', self.primary_host, '-p', '5432'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def promote_replica(self, replica_host):
        """Promouvoir un replica en primary"""
        print(f"Promoting {replica_host} to primary...")
        
        # Promouvoir le replica
        subprocess.run([
            'psql', '-h', replica_host, '-U', 'postgres', '-c',
            'SELECT pg_promote();'
        ])
        
        # Mettre à jour le DNS
        self.update_dns(replica_host)
        
        # Notifier
        self.send_notification(f"Database failover: {replica_host} promoted to primary")
        
    def update_dns(self, new_primary):
        """Mettre à jour le DNS pour pointer vers le nouveau primary"""
        route53 = boto3.client('route53')
        route53.change_resource_record_sets(
            HostedZoneId='ZONE_ID',
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'primary.db.internal',
                        'Type': 'CNAME',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': new_primary}]
                    }
                }]
            }
        )
    
    def send_notification(self, message):
        """Envoyer une notification SNS"""
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=self.sns_topic,
            Subject='Database Failover Alert',
            Message=message
        )
    
    def run_failover_check(self):
        """Boucle principale de vérification"""
        consecutive_failures = 0
        max_failures = 3
        
        while True:
            if not self.check_primary_health():
                consecutive_failures += 1
                print(f"Primary health check failed ({consecutive_failures}/{max_failures})")
                
                if consecutive_failures >= max_failures:
                    # Trouver le replica le plus à jour
                    best_replica = self.find_best_replica()
                    if best_replica:
                        self.promote_replica(best_replica)
                        consecutive_failures = 0
            else:
                consecutive_failures = 0
            
            time.sleep(10)
    
    def find_best_replica(self):
        """Trouver le replica avec le moins de lag"""
        best_replica = None
        min_lag = float('inf')
        
        for replica in self.replica_hosts:
            try:
                result = subprocess.run([
                    'psql', '-h', replica, '-U', 'postgres', '-t', '-c',
                    "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));"
                ], capture_output=True, text=True, timeout=5)
                
                lag = float(result.stdout.strip())
                if lag < min_lag:
                    min_lag = lag
                    best_replica = replica
            except Exception:
                continue
        
        return best_replica

if __name__ == '__main__':
    failover = DatabaseFailover()
    failover.run_failover_check()
```

---

## 9. Performance et Scalabilité

### 9.1 Métriques de Performance Cibles

| Métrique | Cible | Critique |
|----------|-------|----------|
| Temps de réponse P50 | < 100ms | > 500ms |
| Temps de réponse P95 | < 500ms | > 2s |
| Temps de réponse P99 | < 1s | > 5s |
| Taux d'erreur | < 0.1% | > 1% |
| Disponibilité | 99.9% | < 99% |
| Requêtes/seconde | 2000-4000 | < 1000 |
| Connexions DB | < 400 | > 450 |
| Utilisation CPU | < 70% | > 85% |
| Utilisation Mémoire | < 80% | > 90% |

### 9.2 Stratégie de Cache

```python
# cache_strategy.py
from django.core.cache import cache
from functools import wraps
import hashlib

class CacheStrategy:
    """Stratégie de cache multi-niveaux"""
    
    # TTL par type de données
    TTL_CONFIG = {
        'user_profile': 300,        # 5 minutes
        'vehicle_list': 180,        # 3 minutes
        'vehicle_detail': 300,      # 5 minutes
        'tax_calculation': 3600,    # 1 heure
        'tariff_grid': 86400,       # 24 heures
        'statistics': 600,          # 10 minutes
        'api_response': 60,         # 1 minute
    }
    
    @classmethod
    def cache_key(cls, prefix: str, *args, **kwargs) -> str:
        """Générer une clé de cache unique"""
        key_data = f"{prefix}:{':'.join(str(a) for a in args)}"
        if kwargs:
            key_data += f":{hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()[:8]}"
        return key_data
    
    @classmethod
    def get_or_set(cls, key: str, func, ttl_type: str = 'api_response'):
        """Récupérer du cache ou calculer et stocker"""
        result = cache.get(key)
        if result is None:
            result = func()
            ttl = cls.TTL_CONFIG.get(ttl_type, 60)
            cache.set(key, result, ttl)
        return result
    
    @classmethod
    def invalidate_pattern(cls, pattern: str):
        """Invalider toutes les clés correspondant au pattern"""
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"*{pattern}*")
        if keys:
            redis_conn.delete(*keys)


def cached_view(ttl_type='api_response', key_func=None):
    """Décorateur pour cacher les vues"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Générer la clé de cache
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = CacheStrategy.cache_key(
                    view_func.__name__,
                    request.user.id if request.user.is_authenticated else 'anon',
                    request.path,
                    request.GET.urlencode()
                )
            
            # Vérifier le cache
            response = cache.get(cache_key)
            if response is not None:
                return response
            
            # Exécuter la vue
            response = view_func(request, *args, **kwargs)
            
            # Stocker en cache si succès
            if response.status_code == 200:
                ttl = CacheStrategy.TTL_CONFIG.get(ttl_type, 60)
                cache.set(cache_key, response, ttl)
            
            return response
        return wrapper
    return decorator
```

### 9.3 Configuration Auto-Scaling

```yaml
# aws-autoscaling.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: TaxCollector Auto Scaling Configuration

Resources:
  WebServerAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: taxcollector-web-asg
      LaunchTemplate:
        LaunchTemplateId: !Ref WebServerLaunchTemplate
        Version: !GetAtt WebServerLaunchTemplate.LatestVersionNumber
      MinSize: 6
      MaxSize: 16
      DesiredCapacity: 8
      VPCZoneIdentifier:
        - !Ref PrivateSubnetA
        - !Ref PrivateSubnetB
      TargetGroupARNs:
        - !Ref WebTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: taxcollector-web
          PropagateAtLaunch: true

  # Scale Up Policy
  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref WebServerAutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70.0
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  # Scale based on Request Count
  RequestCountScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref WebServerAutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ALBRequestCountPerTarget
          ResourceLabel: !Sub "${LoadBalancer.LoadBalancerFullName}/${WebTargetGroup.TargetGroupFullName}"
        TargetValue: 1000.0

  # Celery Workers Auto Scaling
  CeleryAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: taxcollector-celery-asg
      LaunchTemplate:
        LaunchTemplateId: !Ref CeleryLaunchTemplate
        Version: !GetAtt CeleryLaunchTemplate.LatestVersionNumber
      MinSize: 4
      MaxSize: 12
      DesiredCapacity: 6
      VPCZoneIdentifier:
        - !Ref PrivateSubnetA
        - !Ref PrivateSubnetB

  # Scale Celery based on Queue Length
  CeleryQueueScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref CeleryAutoScalingGroup
      PolicyType: StepScaling
      AdjustmentType: ChangeInCapacity
      StepAdjustments:
        - MetricIntervalLowerBound: 0
          MetricIntervalUpperBound: 500
          ScalingAdjustment: 1
        - MetricIntervalLowerBound: 500
          MetricIntervalUpperBound: 1000
          ScalingAdjustment: 2
        - MetricIntervalLowerBound: 1000
          ScalingAdjustment: 4
```

### 9.4 Optimisation des Requêtes

```python
# query_optimization.py
from django.db.models import Prefetch, Count, Sum, F, Q
from django.db.models.functions import Coalesce

class VehicleQueryOptimizer:
    """Optimisations des requêtes véhicules"""
    
    @staticmethod
    def get_vehicles_with_related(user, filters=None):
        """Récupérer les véhicules avec données liées optimisées"""
        queryset = Vehicule.objects.select_related(
            'type_vehicule',
            'proprietaire'
        ).prefetch_related(
            Prefetch(
                'documents',
                queryset=VehicleDocument.objects.filter(est_verifie=True)
            ),
            Prefetch(
                'payments',
                queryset=Payment.objects.filter(
                    annee_fiscale=timezone.now().year
                ).order_by('-date_paiement')[:1]
            )
        ).annotate(
            total_payments=Coalesce(Sum('payments__montant'), 0),
            documents_count=Count('documents')
        )
        
        if filters:
            queryset = queryset.filter(**filters)
        
        return queryset.filter(proprietaire=user)
    
    @staticmethod
    def get_dashboard_stats(user):
        """Statistiques dashboard optimisées (une seule requête)"""
        return Vehicule.objects.filter(
            proprietaire=user
        ).aggregate(
            total_vehicles=Count('id'),
            vehicles_paid=Count('id', filter=Q(statut_paiement='PAYE')),
            vehicles_unpaid=Count('id', filter=Q(statut_paiement='IMPAYE')),
            total_tax_due=Coalesce(
                Sum('montant_taxe', filter=Q(statut_paiement='IMPAYE')),
                0
            ),
            terrestrial_count=Count('id', filter=Q(categorie_vehicule='TERRESTRE')),
            aerial_count=Count('id', filter=Q(categorie_vehicule='AERIEN')),
            maritime_count=Count('id', filter=Q(categorie_vehicule='MARITIME')),
        )
    
    @staticmethod
    def bulk_update_payment_status(vehicle_ids, new_status):
        """Mise à jour en masse du statut de paiement"""
        return Vehicule.objects.filter(
            id__in=vehicle_ids
        ).update(
            statut_paiement=new_status,
            date_modification=timezone.now()
        )
```

---

## 10. Procédures Opérationnelles

### 10.1 Checklist de Déploiement

```markdown
## Checklist Pré-Déploiement

### 1. Préparation
- [ ] Code review approuvé
- [ ] Tests unitaires passés (>90% coverage)
- [ ] Tests d'intégration passés
- [ ] Tests de performance validés
- [ ] Documentation mise à jour
- [ ] Changelog mis à jour

### 2. Base de Données
- [ ] Migrations testées en staging
- [ ] Backup de la base de production effectué
- [ ] Plan de rollback des migrations préparé
- [ ] Temps d'arrêt estimé communiqué

### 3. Infrastructure
- [ ] Images Docker construites et testées
- [ ] Configuration des secrets vérifiée
- [ ] Capacité des serveurs vérifiée
- [ ] Alertes monitoring configurées

### 4. Communication
- [ ] Équipe notifiée du déploiement
- [ ] Fenêtre de maintenance communiquée
- [ ] Support client informé
- [ ] Page de statut mise à jour

## Procédure de Déploiement

1. Activer le mode maintenance
2. Créer un snapshot de la base de données
3. Appliquer les migrations
4. Déployer les nouveaux conteneurs (rolling update)
5. Vérifier les health checks
6. Exécuter les smoke tests
7. Désactiver le mode maintenance
8. Monitorer les métriques pendant 30 minutes

## Checklist Post-Déploiement

- [ ] Toutes les instances healthy
- [ ] Pas d'erreurs dans les logs
- [ ] Métriques de performance normales
- [ ] Tests de fumée passés
- [ ] Notification de succès envoyée
```

### 10.2 Procédure de Rollback

```bash
#!/bin/bash
# /opt/scripts/rollback.sh

set -e

PREVIOUS_VERSION=$1
CURRENT_VERSION=$(docker inspect taxcollector-web --format='{{.Config.Image}}' | cut -d: -f2)

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: $0 <previous_version>"
    echo "Current version: ${CURRENT_VERSION}"
    exit 1
fi

echo "Rolling back from ${CURRENT_VERSION} to ${PREVIOUS_VERSION}..."

# 1. Activer le mode maintenance
echo "Enabling maintenance mode..."
redis-cli SET maintenance_mode "true"

# 2. Rollback des migrations si nécessaire
echo "Checking for migration rollback..."
MIGRATION_ROLLBACK=$(cat /opt/deployments/${PREVIOUS_VERSION}/migration_rollback.txt 2>/dev/null || echo "")
if [ -n "$MIGRATION_ROLLBACK" ]; then
    echo "Rolling back migrations: ${MIGRATION_ROLLBACK}"
    docker exec taxcollector-web python manage.py migrate ${MIGRATION_ROLLBACK}
fi

# 3. Déployer l'ancienne version
echo "Deploying previous version..."
docker service update \
    --image taxcollector:${PREVIOUS_VERSION} \
    --update-parallelism 2 \
    --update-delay 30s \
    taxcollector-web

# 4. Attendre que tous les conteneurs soient healthy
echo "Waiting for containers to be healthy..."
sleep 60

# 5. Vérifier la santé
HEALTHY=$(docker service ps taxcollector-web --filter "desired-state=running" --format "{{.CurrentState}}" | grep -c "Running" || echo "0")
TOTAL=$(docker service ps taxcollector-web --filter "desired-state=running" --format "{{.ID}}" | wc -l)

if [ "$HEALTHY" -eq "$TOTAL" ]; then
    echo "Rollback successful!"
    redis-cli DEL maintenance_mode
else
    echo "WARNING: Not all containers are healthy!"
    echo "Healthy: ${HEALTHY}/${TOTAL}"
fi

# 6. Notifier
curl -X POST "${SLACK_WEBHOOK}" \
    -H 'Content-type: application/json' \
    -d "{\"text\":\"⚠️ Rollback completed: ${CURRENT_VERSION} → ${PREVIOUS_VERSION}\"}"
```

### 10.3 Runbook Incidents

```markdown
## Runbook: Haute Latence API

### Symptômes
- Temps de réponse P95 > 2 secondes
- Alertes Prometheus: HighLatencyP95

### Diagnostic
1. Vérifier les métriques Grafana
   - Dashboard: TaxCollector > API Performance
   
2. Identifier les endpoints lents
   ```bash
   # Top 10 endpoints les plus lents
   curl -s "http://prometheus:9090/api/v1/query?query=topk(10,histogram_quantile(0.95,rate(django_http_request_duration_seconds_bucket[5m])))"
   ```

3. Vérifier les connexions DB
   ```sql
   SELECT count(*), state FROM pg_stat_activity GROUP BY state;
   ```

4. Vérifier les requêtes lentes
   ```sql
   SELECT query, calls, mean_time, total_time 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC LIMIT 10;
   ```

### Actions
1. **Si connexions DB saturées:**
   - Augmenter pool_size PgBouncer
   - Redémarrer les workers Django

2. **Si requêtes lentes:**
   - Identifier et optimiser la requête
   - Ajouter des index si nécessaire
   - Activer le cache pour les données concernées

3. **Si CPU élevé:**
   - Déclencher le scale-up manuel
   - Identifier les processus consommateurs

### Escalade
- Si non résolu en 15 minutes: Contacter l'équipe DBA
- Si non résolu en 30 minutes: Activer le mode dégradé
```

```markdown
## Runbook: Base de Données Indisponible

### Symptômes
- Erreurs "Connection refused" dans les logs
- Alertes: DatabaseDown

### Diagnostic
1. Vérifier l'état du primary
   ```bash
   pg_isready -h primary.db.internal -p 5432
   ```

2. Vérifier l'état des replicas
   ```bash
   pg_isready -h replica1.db.internal -p 5432
   pg_isready -h replica2.db.internal -p 5432
   ```

3. Vérifier les logs PostgreSQL
   ```bash
   tail -100 /var/log/postgresql/postgresql-16-main.log
   ```

### Actions
1. **Si primary down, replicas OK:**
   - Promouvoir le replica le plus à jour
   ```bash
   /opt/scripts/promote_replica.sh replica1.db.internal
   ```

2. **Si tous les serveurs down:**
   - Vérifier la connectivité réseau
   - Vérifier l'espace disque
   - Redémarrer PostgreSQL si nécessaire

3. **Si corruption de données:**
   - NE PAS redémarrer
   - Contacter immédiatement l'équipe DBA
   - Préparer la restauration depuis backup

### Escalade
- Immédiate: Contacter l'équipe DBA
- Si non résolu en 10 minutes: Activer le DR plan
```

### 10.4 Contacts et Escalade

```yaml
# contacts.yml
teams:
  platform:
    name: "Équipe Plateforme"
    primary:
      name: "[CONTACT_NAME]"
      phone: "[PHONE_NUMBER]"
      email: "[EMAIL]"
    secondary:
      name: "[CONTACT_NAME]"
      phone: "[PHONE_NUMBER]"
      email: "[EMAIL]"
    slack: "#platform-oncall"
    
  dba:
    name: "Équipe DBA"
    primary:
      name: "[CONTACT_NAME]"
      phone: "[PHONE_NUMBER]"
      email: "[EMAIL]"
    slack: "#dba-oncall"
    
  security:
    name: "Équipe Sécurité"
    primary:
      name: "[CONTACT_NAME]"
      phone: "[PHONE_NUMBER]"
      email: "[EMAIL]"
    slack: "#security-incidents"

escalation_matrix:
  severity_1:  # Service complètement down
    response_time: "15 minutes"
    contacts: ["platform.primary", "dba.primary"]
    
  severity_2:  # Dégradation majeure
    response_time: "30 minutes"
    contacts: ["platform.primary"]
    
  severity_3:  # Dégradation mineure
    response_time: "2 heures"
    contacts: ["platform.secondary"]
    
  severity_4:  # Problème non urgent
    response_time: "24 heures"
    contacts: ["platform.secondary"]
```

---

## Annexes

### A. Variables d'Environnement

```bash
# .env.production
# Application
DJANGO_SETTINGS_MODULE=taxcollector_project.settings_prod
SECRET_KEY=<generated_secret>
DEBUG=False
ALLOWED_HOSTS=taxcollector.mg,www.taxcollector.mg

# Database
DATABASE_URL=postgres://user:pass@primary.db.internal:5432/taxcollector
DATABASE_REPLICA_URL=postgres://user:pass@replica1.db.internal:5432/taxcollector

# Redis
REDIS_URL=redis://:password@redis.internal:6379/0
REDIS_CACHE_URL=redis://:password@redis.internal:6379/1
REDIS_SESSION_URL=redis://:password@redis.internal:6379/2

# Celery
CELERY_BROKER_URL=redis://:password@redis.internal:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis.internal:6379/0

# Storage
AWS_ACCESS_KEY_ID=<access_key>
AWS_SECRET_ACCESS_KEY=<secret_key>
AWS_STORAGE_BUCKET_NAME=taxcollector-media
AWS_S3_REGION_NAME=eu-west-1

# Email
EMAIL_HOST=smtp.provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=<email_user>
EMAIL_HOST_PASSWORD=<email_password>
EMAIL_USE_TLS=True

# Payment Gateways
MVOLA_BASE_URL=https://api.mvola.mg
MVOLA_CONSUMER_KEY=<consumer_key>
MVOLA_CONSUMER_SECRET=<consumer_secret>
STRIPE_SECRET_KEY=<stripe_key>

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
NEW_RELIC_LICENSE_KEY=<license_key>
```

### B. Commandes Utiles

```bash
# Vérifier l'état du cluster
docker service ls
docker node ls

# Logs en temps réel
docker service logs -f taxcollector-web

# Scaling manuel
docker service scale taxcollector-web=12

# Vérifier les connexions DB
psql -h primary.db.internal -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Vérifier le lag de réplication
psql -h replica1.db.internal -U postgres -c "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));"

# Vider le cache Redis
redis-cli -h redis.internal FLUSHDB

# Vérifier la file Celery
celery -A taxcollector_project inspect active
celery -A taxcollector_project inspect reserved

# Forcer un backup
/opt/scripts/backup_database.sh

# Vérifier les métriques Prometheus
curl -s "http://prometheus:9090/api/v1/query?query=up"
```

---

**Document maintenu par:** Équipe Plateforme TaxCollector  
**Dernière mise à jour:** Novembre 2025  
**Version:** 2.0
