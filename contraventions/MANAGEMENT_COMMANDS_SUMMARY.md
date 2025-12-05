# Management Commands - Système de Contravention

Ce document décrit les commandes de gestion (management commands) disponibles pour le système de contravention numérique.

## Vue d'ensemble

Le système de contravention dispose de **6 management commands** pour l'administration et l'automatisation:

1. ✅ `setup_contravention_permissions` - Configuration des permissions et groupes
2. ✅ `import_infractions` - Import des 24 types d'infractions de la loi
3. ✅ `calculate_penalties` - Calcul quotidien des pénalités de retard
4. ✅ `generate_daily_report` - Génération de rapports quotidiens
5. ✅ `create_test_contraventions` - Création de données de test
6. ✅ `process_expired_fourriere` - Traitement des dossiers de fourrière expirés
7. ✅ `send_payment_reminders` - Envoi de rappels de paiement

---

## 1. setup_contravention_permissions

**Description:** Configure les groupes et permissions pour le système de contraventions.

**Usage:**
```bash
python manage.py setup_contravention_permissions
```

**Fonctionnalités:**
- Crée 3 groupes d'utilisateurs:
  - **Agent Contrôleur**: Agents de police/gendarmerie autorisés à créer des contraventions
  - **Superviseur Police**: Superviseurs pouvant valider les annulations et contestations
  - **Administrateur Contraventions**: Administrateurs avec accès complet au système

- Assigne les permissions appropriées à chaque groupe:
  - Agent Contrôleur: add/view/change pour Contravention, PhotoContravention, DossierFourriere, Conducteur
  - Superviseur Police: Toutes les permissions Agent + delete Contravention + manage Contestation
  - Administrateur: Toutes les permissions sur tous les modèles

**Quand l'utiliser:**
- Lors de l'installation initiale du système
- Après une migration de base de données
- Pour réinitialiser les permissions

**Exemple de sortie:**
```
Configuration des permissions de contraventions...
Création des groupes...
  ✓ Groupe créé: Agent Contrôleur
  ✓ Groupe créé: Superviseur Police
  ✓ Groupe créé: Administrateur Contraventions

Configuration des permissions Agent Contrôleur...
  ✓ 11 permissions assignées au groupe Agent Contrôleur

Configuration des permissions Superviseur Police...
  ✓ 14 permissions assignées au groupe Superviseur Police

Configuration des permissions Administrateur Contraventions...
  ✓ 36 permissions assignées au groupe Administrateur Contraventions

✓ Configuration des permissions terminée avec succès!
```

---

## 2. calculate_penalties

**Description:** Calcule et applique les pénalités de retard pour les contraventions impayées dont la date limite de paiement est dépassée.

**Usage:**
```bash
# Mode normal (applique les pénalités)
python manage.py calculate_penalties

# Mode dry-run (affiche sans appliquer)
python manage.py calculate_penalties --dry-run

# Avec envoi de notifications
python manage.py calculate_penalties --send-notifications
```

**Options:**
- `--dry-run`: Affiche les actions sans les exécuter (recommandé pour tester)
- `--send-notifications`: Envoie des notifications par email aux conducteurs

**Fonctionnalités:**
- Parcourt toutes les contraventions avec statut `IMPAYEE` et `date_limite_paiement` dépassée
- Calcule la pénalité selon `ConfigurationSysteme.penalite_retard_pct` (défaut: 10%)
- Applique la pénalité au montant de l'amende
- Enregistre chaque pénalité dans `ContraventionAuditLog` pour traçabilité
- Envoie des notifications aux conducteurs (si `--send-notifications`)

**Exemple de sortie:**
```
Calcul des pénalités de retard...
Contraventions en retard trouvées: 15

✓ PV-20251101-ABC123: Pénalité appliquée: 40,000.00 Ar (400,000.00 → 440,000.00 Ar)
✓ PV-20251102-DEF456: Pénalité appliquée: 20,000.00 Ar (200,000.00 → 220,000.00 Ar)
...

============================================================
✓ 15 pénalités appliquées avec succès
Montant total des pénalités: 450,000.00 Ar
============================================================
```

**Automatisation avec Celery:**
Cette commande peut être automatisée avec Celery Beat pour exécution quotidienne:
```python
# Dans settings.py
CELERY_BEAT_SCHEDULE = {
    'calculate-penalties-daily': {
        'task': 'contraventions.tasks.calculate_penalties_task',
        'schedule': crontab(hour=0, minute=0),  # Minuit chaque jour
    },
}
```

---

## 3. generate_daily_report

**Description:** Génère un rapport quotidien complet des contraventions avec statistiques détaillées.

**Usage:**
```bash
# Rapport pour hier (par défaut)
python manage.py generate_daily_report

# Rapport pour une date spécifique
python manage.py generate_daily_report --date 2025-11-15

# Format JSON
python manage.py generate_daily_report --format json

# Format HTML
python manage.py generate_daily_report --format html

# Envoyer par email aux administrateurs
python manage.py generate_daily_report --send-email
```

**Options:**
- `--date DATE`: Date du rapport (format: YYYY-MM-DD). Par défaut: hier
- `--format {text,json,html}`: Format du rapport (text, json, html)
- `--send-email`: Envoie le rapport par email aux administrateurs

**Statistiques incluses:**

### Statistiques du jour:
- Nombre de contraventions créées
- Répartition par statut (payées, impayées, contestées, annulées)
- Taux de paiement
- Montant total émis et collecté
- Statistiques de fourrière (mises en fourrière, restitutions)
- Statistiques de contestations (nouvelles, acceptées, rejetées)
- Top 10 infractions les plus fréquentes
- Top 10 agents contrôleurs les plus actifs

### Statistiques cumulées:
- Total de contraventions (tous temps)
- Total payées et impayées
- Montant total émis et collecté

**Exemple de sortie (format text):**
```
================================================================================
RAPPORT QUOTIDIEN DES CONTRAVENTIONS - 15/11/2025
================================================================================

📊 STATISTIQUES DU JOUR
--------------------------------------------------------------------------------
Contraventions créées:        125
  - Payées:                    45 ( 36.0%)
  - Impayées:                  70
  - Contestées:                 8
  - Annulées:                   2

💰 MONTANTS
Montant total émis:        45,000,000.00 Ar
Montant collecté:          16,200,000.00 Ar

🚗 FOURRIÈRE
Véhicules mis en fourrière:    12
Véhicules restitués:            5

⚖️  CONTESTATIONS
Nouvelles contestations:        8
Contestations acceptées:        2
Contestations rejetées:         3

🚨 TOP 10 INFRACTIONS
--------------------------------------------------------------------------------
 1. L7.2-5      Excès de vitesse                          35 (  14,000,000 Ar)
 2. L7.3-2      Stationnement interdit                    22 (   4,400,000 Ar)
 3. L7.1-1      Conduite en état d'ivresse                15 (  15,000,000 Ar)
...

👮 TOP 10 AGENTS CONTRÔLEURS
--------------------------------------------------------------------------------
 1. POL-2024-001  Jean RAKOTO              Brigade Centrale      18 PV
 2. GEN-2024-015  Marie RASOLOFO           Gendarmerie RN7       15 PV
...

📈 STATISTIQUES CUMULÉES (TOTAL)
--------------------------------------------------------------------------------
Total contraventions:          5,234
  - Payées:                    3,156
  - Impayées:                  1,890
Montant total émis:        1,890,000,000.00 Ar
Montant total collecté:    1,134,000,000.00 Ar

================================================================================
```

**Format JSON:**
Retourne un objet JSON structuré avec toutes les statistiques, idéal pour intégration avec d'autres systèmes.

**Format HTML:**
Génère un rapport HTML formaté avec tableaux et styles CSS, idéal pour envoi par email.

**Automatisation avec Celery:**
```python
# Dans settings.py
CELERY_BEAT_SCHEDULE = {
    'generate-daily-report': {
        'task': 'contraventions.tasks.generate_daily_reports',
        'schedule': crontab(hour=23, minute=0),  # 23h chaque jour
    },
}
```

---

## 4. import_infractions

**Description:** Importe les 24 types d'infractions définis dans la Loi n°2017-002 du Code de la Route Malagasy.

**Usage:**
```bash
python manage.py import_infractions
```

**Fonctionnalités:**
- Importe les 24 types d'infractions organisés en 4 catégories:
  - Délits routiers graves (7 types)
  - Infractions de circulation (7 types)
  - Infractions documentaires (6 types)
  - Infractions de sécurité (4 types)
- Chaque infraction inclut:
  - Article du Code de la Route (ex: L7.1-1)
  - Montants minimum et maximum
  - Sanctions administratives
  - Pénalités pour accident et récidive
  - Indicateur de fourrière obligatoire

**Quand l'utiliser:**
- Lors de l'installation initiale du système
- Pour réinitialiser le catalogue d'infractions

---

## 5. create_test_contraventions

**Description:** Crée des données de test pour le développement et les démonstrations.

**Usage:**
```bash
# Créer 10 contraventions de test
python manage.py create_test_contraventions --count 10

# Créer avec des statuts variés
python manage.py create_test_contraventions --count 20 --with-payments
```

**Fonctionnalités:**
- Crée des contraventions avec données réalistes
- Génère des conducteurs et véhicules de test
- Peut créer des paiements associés
- Utile pour tester l'interface et les rapports

---

## 6. process_expired_fourriere

**Description:** Traite les dossiers de fourrière arrivés à échéance (durée maximale dépassée).

**Usage:**
```bash
# Mode normal
python manage.py process_expired_fourriere

# Mode dry-run
python manage.py process_expired_fourriere --dry-run
```

**Fonctionnalités:**
- Identifie les véhicules en fourrière depuis plus de 30 jours
- Marque les dossiers pour vente aux enchères
- Envoie des notifications aux propriétaires

---

## 7. send_payment_reminders

**Description:** Envoie des rappels de paiement pour les contraventions impayées.

**Usage:**
```bash
# Mode normal
python manage.py send_payment_reminders

# Mode dry-run
python manage.py send_payment_reminders --dry-run

# Personnaliser les délais
python manage.py send_payment_reminders --days-before-due 7 --days-after-due 3
```

**Options:**
- `--days-before-due`: Jours avant échéance pour rappel (défaut: 7)
- `--days-after-due`: Jours après échéance pour rappel (défaut: 3)
- `--dry-run`: Affiche sans envoyer

**Types de rappels:**
1. **Approchant échéance**: 7 jours avant la date limite
2. **Dépassé échéance**: 3 jours après la date limite
3. **Très en retard**: Plus de 30 jours après la date limite

---

## Automatisation avec Celery Beat

Pour automatiser l'exécution de ces commandes, configurez Celery Beat dans `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Calcul des pénalités chaque jour à minuit
    'calculate-penalties-daily': {
        'task': 'contraventions.tasks.calculer_penalites_retard',
        'schedule': crontab(hour=0, minute=0),
    },
    
    # Rapport quotidien chaque jour à 23h
    'generate-daily-report': {
        'task': 'contraventions.tasks.generer_rapport_quotidien',
        'schedule': crontab(hour=23, minute=0),
    },
    
    # Rappels de paiement chaque jour à 9h
    'send-payment-reminders': {
        'task': 'contraventions.tasks.envoyer_rappels_paiement',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Traitement fourrière expirée chaque jour à minuit
    'process-expired-fourriere': {
        'task': 'contraventions.tasks.traiter_fourriere_expiree',
        'schedule': crontab(hour=0, minute=0),
    },
}
```

Démarrer Celery Beat:
```bash
celery -A taxcollector_project beat --loglevel=info
```

---

## Bonnes pratiques

1. **Toujours tester avec --dry-run** avant d'exécuter en production
2. **Automatiser avec Celery Beat** pour les tâches récurrentes
3. **Surveiller les logs** pour détecter les erreurs
4. **Sauvegarder la base de données** avant les opérations de masse
5. **Configurer les notifications email** pour les rapports automatiques

---

## Dépannage

### Erreur: "No module named 'contraventions'"
- Vérifier que l'application est dans `INSTALLED_APPS`
- Redémarrer le serveur Django

### Erreur: "Permission denied"
- Vérifier que l'utilisateur a les permissions nécessaires
- Exécuter `setup_contravention_permissions` si nécessaire

### Notifications non envoyées
- Vérifier la configuration SMTP dans `administration.models.SMTPConfiguration`
- Tester avec `python manage.py test_smtp`

### Celery Beat ne s'exécute pas
- Vérifier que Celery Beat est démarré: `celery -A taxcollector_project beat`
- Vérifier les logs Celery: `tail -f logs/celery.log`

---

## Support

Pour plus d'informations:
- Documentation complète: `docs/contraventions/`
- API REST: `docs/contraventions/API.md`
- Guide utilisateur: `docs/contraventions/USER_GUIDE.md`
