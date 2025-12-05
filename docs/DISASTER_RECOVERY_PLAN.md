# Plan de Reprise d'Activité (PRA) - TaxCollector

**Version:** 1.0  
**Date:** Novembre 2025  
**Classification:** Confidentiel

---

## 1. Objectifs de Reprise

### 1.1 Définitions SLA

| Métrique | Définition | Objectif |
|----------|------------|----------|
| **RTO** (Recovery Time Objective) | Temps maximum d'interruption acceptable | 4 heures |
| **RPO** (Recovery Point Objective) | Perte de données maximum acceptable | 1 heure |
| **MTTR** (Mean Time To Recovery) | Temps moyen de récupération | 2 heures |
| **Disponibilité** | Uptime annuel | 99.9% (8.76h downtime/an) |

### 1.2 Classification des Incidents

| Niveau | Description | RTO | Exemples |
|--------|-------------|-----|----------|
| **P1 - Critique** | Service complètement indisponible | 1h | DB down, datacenter failure |
| **P2 - Majeur** | Fonctionnalités critiques impactées | 4h | Paiements impossibles |
| **P3 - Modéré** | Dégradation de performance | 8h | Latence élevée |
| **P4 - Mineur** | Impact limité | 24h | Fonctionnalité secondaire |

---

## 2. Architecture de Reprise

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE DISASTER RECOVERY                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│      RÉGION PRINCIPALE          │     │      RÉGION DR (STANDBY)        │
│      (Production Active)        │     │      (Warm Standby)             │
│                                 │     │                                 │
│  ┌───────────────────────────┐ │     │  ┌───────────────────────────┐ │
│  │   Application Servers     │ │     │  │   Application Servers     │ │
│  │   (8-16 instances)        │ │     │  │   (2 instances standby)   │ │
│  └───────────────────────────┘ │     │  └───────────────────────────┘ │
│                                 │     │                                 │
│  ┌───────────────────────────┐ │     │  ┌───────────────────────────┐ │
│  │   PostgreSQL Primary      │ │────→│  │   PostgreSQL Replica      │ │
│  │   + 2 Replicas locaux     │ │ WAL │  │   (Async replication)     │ │
│  └───────────────────────────┘ │     │  └───────────────────────────┘ │
│                                 │     │                                 │
│  ┌───────────────────────────┐ │     │  ┌───────────────────────────┐ │
│  │   Redis Cluster           │ │────→│  │   Redis Replica           │ │
│  │   (3 nodes)               │ │     │  │   (1 node)                │ │
│  └───────────────────────────┘ │     │  └───────────────────────────┘ │
│                                 │     │                                 │
└─────────────────────────────────┘     └─────────────────────────────────┘
                │                                       │
                └───────────────┬───────────────────────┘
                                │
                                ↓
                ┌───────────────────────────────────────┐
                │           AWS S3 (Cross-Region)       │
                │   • Backups répliqués                 │
                │   • Documents véhicules               │
                │   • Versioning activé                 │
                └───────────────────────────────────────┘
```

---

## 3. Scénarios de Reprise

### 3.1 Scénario 1: Panne Serveur Application

**Impact:** Partiel - Autres serveurs prennent le relais  
**RTO:** < 5 minutes (automatique)

```bash
# Détection automatique via health checks
# Load balancer retire le serveur défaillant
# Auto-scaling lance une nouvelle instance

# Vérification manuelle si nécessaire
docker service ps taxcollector-web
docker service scale taxcollector-web=8
```

### 3.2 Scénario 2: Panne Base de Données Primary

**Impact:** Critique - Écriture impossible  
**RTO:** 5-15 minutes

```bash
#!/bin/bash
# /opt/scripts/db_failover.sh

# 1. Vérifier l'état du primary
pg_isready -h primary.db.internal -p 5432
if [ $? -ne 0 ]; then
    echo "Primary is down, initiating failover..."
    
    # 2. Identifier le replica le plus à jour
    BEST_REPLICA=$(psql -h replica1.db.internal -U postgres -t -c \
        "SELECT pg_last_wal_receive_lsn();" | tr -d ' ')
    
    # 3. Promouvoir le replica
    psql -h replica1.db.internal -U postgres -c "SELECT pg_promote();"
    
    # 4. Mettre à jour le DNS
    aws route53 change-resource-record-sets \
        --hosted-zone-id ZONE_ID \
        --change-batch '{
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "primary.db.internal",
                    "Type": "CNAME",
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "replica1.db.internal"}]
                }
            }]
        }'
    
    # 5. Redémarrer les connexions applicatives
    docker service update --force taxcollector-web
    
    # 6. Notifier
    /opt/scripts/notify_incident.sh "DB Failover completed"
fi
```

### 3.3 Scénario 3: Panne Région Complète

**Impact:** Critique - Service indisponible  
**RTO:** 30-60 minutes

```bash
#!/bin/bash
# /opt/scripts/region_failover.sh

echo "Initiating region failover to DR site..."

# 1. Activer la page de maintenance
aws s3 cp maintenance.html s3://taxcollector-static/maintenance.html
aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"

# 2. Promouvoir la DB DR
ssh dr-bastion "psql -h dr-db.internal -U postgres -c 'SELECT pg_promote();'"

# 3. Démarrer les serveurs applicatifs DR
ssh dr-bastion "docker service scale taxcollector-web=8"
ssh dr-bastion "docker service scale taxcollector-celery=4"

# 4. Vérifier la santé
sleep 60
HEALTH=$(curl -s https://dr.taxcollector.mg/api/v1/health/ | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
    echo "ERROR: DR site not healthy!"
    exit 1
fi

# 5. Basculer le DNS
aws route53 change-resource-record-sets \
    --hosted-zone-id ZONE_ID \
    --change-batch file://dr-dns-change.json

# 6. Désactiver la maintenance
aws s3 rm s3://taxcollector-static/maintenance.html

# 7. Notifier
/opt/scripts/notify_incident.sh "Region failover completed to DR site"
```

### 3.4 Scénario 4: Corruption de Données

**Impact:** Critique - Intégrité compromise  
**RTO:** 1-4 heures (selon étendue)

```bash
#!/bin/bash
# /opt/scripts/data_recovery.sh

RECOVERY_POINT=$1  # Format: '2025-11-25 14:30:00'

echo "Starting Point-in-Time Recovery to ${RECOVERY_POINT}..."

# 1. Arrêter l'application
docker service scale taxcollector-web=0
docker service scale taxcollector-celery=0

# 2. Créer un snapshot de l'état actuel (pour analyse)
pg_dump -h primary.db.internal -U postgres taxcollector > /backup/pre_recovery_$(date +%Y%m%d_%H%M%S).sql

# 3. Restaurer depuis le backup le plus récent avant la corruption
LATEST_BACKUP=$(aws s3 ls s3://taxcollector-backups/database/daily/ | sort | tail -1 | awk '{print $4}')
aws s3 cp s3://taxcollector-backups/database/daily/${LATEST_BACKUP} /tmp/

# 4. Restaurer la base
pg_restore -h primary.db.internal -U postgres -d taxcollector --clean /tmp/${LATEST_BACKUP}

# 5. Appliquer les WAL jusqu'au point de récupération
# (Configuration PITR dans postgresql.conf)

# 6. Vérifier l'intégrité
psql -h primary.db.internal -U postgres -d taxcollector -c "
    SELECT 'vehicles' as table_name, COUNT(*) as count FROM vehicles_vehicule
    UNION ALL
    SELECT 'payments', COUNT(*) FROM payments_payment
    UNION ALL
    SELECT 'users', COUNT(*) FROM auth_user;
"

# 7. Redémarrer l'application
docker service scale taxcollector-web=8
docker service scale taxcollector-celery=4

echo "Recovery completed. Please verify data integrity."
```

---

## 4. Tests de Reprise

### 4.1 Planning des Tests

| Test | Fréquence | Durée | Impact |
|------|-----------|-------|--------|
| Restauration backup | Hebdomadaire | 1h | Aucun |
| Failover DB | Mensuel | 30min | Minimal |
| Failover région | Trimestriel | 2h | Planifié |
| Test complet DR | Annuel | 4h | Planifié |

### 4.2 Procédure de Test Failover DB

```bash
#!/bin/bash
# /opt/scripts/test_db_failover.sh

echo "=== TEST FAILOVER DB ==="
echo "Date: $(date)"
echo "========================"

# 1. Vérifier l'état initial
echo "1. État initial..."
psql -h primary.db.internal -U postgres -c "SELECT pg_is_in_recovery();"
psql -h replica1.db.internal -U postgres -c "SELECT pg_is_in_recovery();"

# 2. Simuler la panne (arrêt contrôlé)
echo "2. Arrêt du primary..."
ssh primary.db.internal "sudo systemctl stop postgresql"

# 3. Mesurer le temps de détection
START_TIME=$(date +%s)

# 4. Attendre la promotion automatique
echo "3. Attente de la promotion..."
while true; do
    IS_RECOVERY=$(psql -h replica1.db.internal -U postgres -t -c "SELECT pg_is_in_recovery();" 2>/dev/null | tr -d ' ')
    if [ "$IS_RECOVERY" == "f" ]; then
        break
    fi
    sleep 1
done

END_TIME=$(date +%s)
FAILOVER_TIME=$((END_TIME - START_TIME))

echo "4. Failover complété en ${FAILOVER_TIME} secondes"

# 5. Vérifier que l'application fonctionne
echo "5. Test de l'application..."
curl -s https://taxcollector.mg/api/v1/health/ | jq .

# 6. Restaurer l'état initial
echo "6. Restauration de l'état initial..."
ssh primary.db.internal "sudo systemctl start postgresql"
# Reconfigurer comme replica...

echo "=== TEST TERMINÉ ==="
echo "Temps de failover: ${FAILOVER_TIME}s"
echo "Objectif RTO: 300s"
if [ $FAILOVER_TIME -lt 300 ]; then
    echo "RÉSULTAT: SUCCÈS ✓"
else
    echo "RÉSULTAT: ÉCHEC ✗"
fi
```

---

## 5. Communication d'Incident

### 5.1 Matrice d'Escalade

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MATRICE D'ESCALADE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Temps écoulé    P1 (Critique)         P2 (Majeur)           P3 (Modéré)
─────────────────────────────────────────────────────────────────────────────
0 min           Équipe On-Call        Équipe On-Call        Équipe On-Call
15 min          + Tech Lead           -                     -
30 min          + Engineering Manager + Tech Lead           -
1 heure         + CTO                 + Engineering Manager + Tech Lead
2 heures        + Direction Générale  + CTO                 -
4 heures        Communication externe + Direction           + Engineering Manager
```

### 5.2 Templates de Communication

```markdown
## Template: Notification Initiale (Interne)

**Sujet:** [P{NIVEAU}] Incident TaxCollector - {DESCRIPTION_COURTE}

**Statut:** En cours d'investigation
**Début:** {DATE_HEURE}
**Impact:** {DESCRIPTION_IMPACT}

**Équipe assignée:** {NOMS}
**Prochaine mise à jour:** Dans 30 minutes

---

## Template: Communication Externe (Utilisateurs)

**Sujet:** Interruption de service TaxCollector

Chers utilisateurs,

Nous rencontrons actuellement des difficultés techniques affectant {SERVICE_IMPACTÉ}.

**Impact:** {DESCRIPTION_SIMPLE}
**Début:** {DATE_HEURE}
**Estimation de résolution:** {ESTIMATION}

Nous travaillons activement à la résolution de ce problème.
Nous vous tiendrons informés de l'évolution de la situation.

Nous vous prions de nous excuser pour la gêne occasionnée.

L'équipe TaxCollector

---

## Template: Résolution

**Sujet:** [RÉSOLU] Incident TaxCollector - {DESCRIPTION_COURTE}

**Statut:** Résolu
**Début:** {DATE_HEURE_DEBUT}
**Fin:** {DATE_HEURE_FIN}
**Durée totale:** {DUREE}

**Cause:** {DESCRIPTION_CAUSE}
**Résolution:** {DESCRIPTION_RESOLUTION}

**Actions préventives:**
- {ACTION_1}
- {ACTION_2}

Un rapport d'incident détaillé sera disponible sous 48 heures.
```

---

## 6. Post-Mortem

### 6.1 Template Post-Mortem

```markdown
# Post-Mortem: {TITRE_INCIDENT}

**Date de l'incident:** {DATE}
**Durée:** {DUREE}
**Niveau de sévérité:** P{NIVEAU}
**Auteur:** {NOM}
**Date du rapport:** {DATE_RAPPORT}

## Résumé Exécutif
{RESUME_2_3_PHRASES}

## Impact
- Utilisateurs affectés: {NOMBRE}
- Transactions perdues: {NOMBRE}
- Revenus impactés: {MONTANT}

## Chronologie
| Heure | Événement |
|-------|-----------|
| HH:MM | Détection de l'incident |
| HH:MM | Première action |
| HH:MM | Escalade |
| HH:MM | Résolution |

## Cause Racine
{DESCRIPTION_DETAILLEE}

## Facteurs Contributifs
1. {FACTEUR_1}
2. {FACTEUR_2}

## Ce qui a bien fonctionné
- {POINT_POSITIF_1}
- {POINT_POSITIF_2}

## Ce qui peut être amélioré
- {AMELIORATION_1}
- {AMELIORATION_2}

## Actions Correctives
| Action | Responsable | Échéance | Statut |
|--------|-------------|----------|--------|
| {ACTION} | {NOM} | {DATE} | En cours |

## Leçons Apprises
{LECONS}
```

---

## 7. Inventaire des Ressources Critiques

### 7.1 Composants Critiques

| Composant | Criticité | Redondance | RTO |
|-----------|-----------|------------|-----|
| PostgreSQL Primary | Critique | 2 replicas sync | 5 min |
| Redis Cache | Haute | 3 nodes Sentinel | 2 min |
| Application Servers | Haute | 8-16 instances | 1 min |
| Load Balancer | Critique | Multi-AZ | 30 sec |
| S3 Storage | Haute | Cross-region | N/A |
| DNS (Route53) | Critique | Global | 60 sec |

### 7.2 Dépendances Externes

| Service | Criticité | Fallback | Contact |
|---------|-----------|----------|---------|
| MVola API | Haute | Mode offline | support@mvola.mg |
| Stripe API | Moyenne | MVola uniquement | support@stripe.com |
| SMTP (Email) | Basse | Queue + retry | - |
| CloudFlare | Haute | Direct access | - |

---

## 8. Checklist de Reprise

### 8.1 Checklist Failover DB

```markdown
- [ ] Confirmer que le primary est inaccessible
- [ ] Identifier le replica le plus à jour
- [ ] Vérifier le lag de réplication
- [ ] Promouvoir le replica
- [ ] Mettre à jour le DNS
- [ ] Vérifier les connexions applicatives
- [ ] Tester les opérations CRUD
- [ ] Notifier l'équipe
- [ ] Documenter l'incident
```

### 8.2 Checklist Failover Région

```markdown
- [ ] Activer la page de maintenance
- [ ] Vérifier l'état du site DR
- [ ] Promouvoir la DB DR
- [ ] Démarrer les serveurs applicatifs
- [ ] Vérifier les health checks
- [ ] Tester les fonctionnalités critiques
- [ ] Basculer le DNS
- [ ] Désactiver la maintenance
- [ ] Monitorer les métriques
- [ ] Communiquer aux utilisateurs
- [ ] Planifier le retour à la normale
```

---

**Document maintenu par:** Équipe Infrastructure  
**Dernière révision:** Novembre 2025  
**Prochaine révision:** Février 2026
