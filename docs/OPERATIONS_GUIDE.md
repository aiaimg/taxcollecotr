# Guide des Opérations - TaxCollector

**Version:** 1.0  
**Date:** Novembre 2025

---

## 1. Commandes Essentielles

### 1.1 Gestion des Services

```bash
# Vérifier l'état des services
docker service ls
docker service ps taxcollector-web

# Scaling
docker service scale taxcollector-web=10
docker service scale taxcollector-celery=6

# Redémarrage gracieux
docker service update --force taxcollector-web

# Logs en temps réel
docker service logs -f --tail 100 taxcollector-web

# Déploiement nouvelle version
docker service update --image taxcollector:v2.1.0 taxcollector-web
```

### 1.2 Base de Données

```bash
# Connexion PostgreSQL
psql -h primary.db.internal -U postgres -d taxcollector

# Vérifier les connexions actives
psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Vérifier le lag de réplication
psql -h replica1.db.internal -c "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));"

# Requêtes lentes (top 10)
psql -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Taille des tables
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;"

# Vacuum manuel
psql -c "VACUUM ANALYZE vehicles_vehicule;"
```

### 1.3 Redis

```bash
# Connexion Redis
redis-cli -h redis.internal

# Statistiques mémoire
redis-cli INFO memory

# Clés par pattern
redis-cli KEYS "taxcollector:cache:*" | wc -l

# Vider le cache (attention!)
redis-cli FLUSHDB

# Monitorer en temps réel
redis-cli MONITOR
```

### 1.4 Celery

```bash
# Vérifier les workers actifs
celery -A taxcollector_project inspect active

# Tâches en attente
celery -A taxcollector_project inspect reserved

# Statistiques
celery -A taxcollector_project inspect stats

# Purger la queue (attention!)
celery -A taxcollector_project purge

# Redémarrer un worker
docker service update --force taxcollector-celery
```

### 1.5 Django Management

```bash
# Accéder au shell Django
docker exec -it $(docker ps -q -f name=taxcollector-web) python manage.py shell

# Migrations
docker exec -it $(docker ps -q -f name=taxcollector-web) python manage.py migrate

# Collecter les fichiers statiques
docker exec -it $(docker ps -q -f name=taxcollector-web) python manage.py collectstatic --noinput

# Créer un superuser
docker exec -it $(docker ps -q -f name=taxcollector-web) python manage.py createsuperuser

# Vérifier la configuration
docker exec -it $(docker ps -q -f name=taxcollector-web) python manage.py check --deploy
```

---

## 2. Monitoring

### 2.1 URLs de Monitoring

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | https://grafana.taxcollector.mg | admin / [vault] |
| Prometheus | https://prometheus.taxcollector.mg | - |
| Kibana | https://kibana.taxcollector.mg | elastic / [vault] |
| PgAdmin | https://pgadmin.taxcollector.mg | admin / [vault] |
| Flower (Celery) | https://flower.taxcollector.mg | admin / [vault] |

### 2.2 Métriques Clés à Surveiller

```
# API Performance
- django_http_requests_total
- django_http_request_duration_seconds
- django_http_responses_total{status=~"5.."}

# Database
- pg_stat_activity_count
- pg_stat_replication_lag_seconds
- pg_database_size_bytes

# Redis
- redis_memory_used_bytes
- redis_connected_clients
- redis_commands_processed_total

# Celery
- celery_tasks_total
- celery_tasks_failed_total
- celery_queue_length

# System
- node_cpu_seconds_total
- node_memory_MemAvailable_bytes
- node_filesystem_avail_bytes
```

### 2.3 Requêtes Prometheus Utiles

```promql
# Taux d'erreur API (5 dernières minutes)
sum(rate(django_http_responses_total{status=~"5.."}[5m])) / sum(rate(django_http_responses_total[5m])) * 100

# Temps de réponse P95
histogram_quantile(0.95, sum by (le) (rate(django_http_request_duration_seconds_bucket[5m])))

# Requêtes par seconde
sum(rate(django_http_requests_total[1m]))

# Utilisation CPU moyenne
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Mémoire disponible
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
```

---

## 3. Tâches Planifiées

### 3.1 Tâches Quotidiennes

| Heure | Tâche | Script |
|-------|-------|--------|
| 02:00 | Backup DB | `/opt/scripts/backup_database.sh` |
| 03:00 | Backup Media | `/opt/scripts/backup_media.sh` |
| 04:00 | Nettoyage logs | `/opt/scripts/cleanup_logs.sh` |
| 05:00 | Rapport quotidien | Celery beat |
| 06:00 | Vacuum DB | `/opt/scripts/vacuum_db.sh` |

### 3.2 Tâches Hebdomadaires

| Jour | Tâche | Script |
|------|-------|--------|
| Dimanche 01:00 | Test restauration backup | `/opt/scripts/test_backup_restore.sh` |
| Dimanche 02:00 | Rotation des logs | logrotate |
| Lundi 08:00 | Rapport hebdomadaire | Celery beat |

### 3.3 Tâches Mensuelles

| Jour | Tâche | Script |
|------|-------|--------|
| 1er du mois | Archivage backups | `/opt/scripts/archive_backups.sh` |
| 1er du mois | Rapport mensuel | Celery beat |
| 15 du mois | Test failover DB | Manuel |

---

## 4. Procédures de Maintenance

### 4.1 Mise à Jour de l'Application

```bash
#!/bin/bash
# Procédure de déploiement

VERSION=$1

# 1. Vérifier la version
echo "Deploying version: ${VERSION}"

# 2. Pull de l'image
docker pull taxcollector:${VERSION}

# 3. Backup de la DB
/opt/scripts/backup_database.sh

# 4. Appliquer les migrations (si nécessaire)
docker run --rm taxcollector:${VERSION} python manage.py migrate --check
if [ $? -ne 0 ]; then
    echo "Migrations needed, applying..."
    docker run --rm --network taxcollector-net taxcollector:${VERSION} python manage.py migrate
fi

# 5. Déploiement rolling
docker service update \
    --image taxcollector:${VERSION} \
    --update-parallelism 2 \
    --update-delay 30s \
    --update-failure-action rollback \
    taxcollector-web

# 6. Vérification
sleep 60
curl -f https://taxcollector.mg/api/v1/health/ || exit 1

echo "Deployment successful!"
```

### 4.2 Maintenance Base de Données

```bash
#!/bin/bash
# Maintenance PostgreSQL

# 1. Vacuum et Analyze
psql -h primary.db.internal -U postgres -d taxcollector << EOF
VACUUM ANALYZE;
REINDEX DATABASE taxcollector;
EOF

# 2. Vérifier la fragmentation
psql -h primary.db.internal -U postgres -d taxcollector << EOF
SELECT 
    schemaname || '.' || relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    n_dead_tup as dead_tuples,
    n_live_tup as live_tuples,
    round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
EOF

# 3. Mettre à jour les statistiques
psql -h primary.db.internal -U postgres -d taxcollector -c "ANALYZE VERBOSE;"
```

### 4.3 Rotation des Certificats SSL

```bash
#!/bin/bash
# Renouvellement certificat Let's Encrypt

# 1. Renouveler le certificat
certbot renew --quiet

# 2. Copier vers le load balancer
scp /etc/letsencrypt/live/taxcollector.mg/fullchain.pem lb1:/etc/nginx/ssl/
scp /etc/letsencrypt/live/taxcollector.mg/privkey.pem lb1:/etc/nginx/ssl/

# 3. Recharger Nginx
ssh lb1 "nginx -t && systemctl reload nginx"
ssh lb2 "nginx -t && systemctl reload nginx"

# 4. Vérifier
curl -vI https://taxcollector.mg 2>&1 | grep "expire date"
```

---

## 5. Troubleshooting

### 5.1 Problèmes Courants

#### API Lente

```bash
# 1. Vérifier les métriques
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(django_http_request_duration_seconds_bucket[5m]))"

# 2. Vérifier les connexions DB
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# 3. Vérifier le cache Redis
redis-cli INFO stats | grep hits

# 4. Identifier les requêtes lentes
tail -f /var/log/taxcollector/slow_queries.log
```

#### Erreurs 500

```bash
# 1. Vérifier les logs
docker service logs --tail 100 taxcollector-web | grep ERROR

# 2. Vérifier Sentry
# https://sentry.io/organizations/taxcollector/issues/

# 3. Vérifier la DB
psql -c "SELECT 1;" || echo "DB connection failed"

# 4. Vérifier Redis
redis-cli PING || echo "Redis connection failed"
```

#### Queue Celery Saturée

```bash
# 1. Vérifier la taille de la queue
redis-cli LLEN celery

# 2. Vérifier les workers
celery -A taxcollector_project inspect active

# 3. Scaler les workers
docker service scale taxcollector-celery=8

# 4. Si nécessaire, purger les tâches anciennes
celery -A taxcollector_project purge --force
```

---

## 6. Contacts

| Rôle | Contact | Disponibilité |
|------|---------|---------------|
| On-Call Platform | [PHONE] | 24/7 |
| DBA | [PHONE] | 24/7 |
| Security | [PHONE] | 24/7 |
| Management | [PHONE] | Heures ouvrées |

---

**Document maintenu par:** Équipe Opérations  
**Dernière mise à jour:** Novembre 2025
