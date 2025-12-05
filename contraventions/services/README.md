# Services de Contraventions

Ce dossier contient les services métier pour la gestion des contraventions.

## Services disponibles

### InfractionService
Service pour gérer le catalogue des types d'infractions conformes à la Loi n°2017-002.

**Méthodes principales:**
- `importer_infractions_loi_2017()`: Importe les 24 types d'infractions de la loi
- `get_infractions_par_categorie()`: Retourne les infractions groupées par catégorie
- `get_montant_pour_autorite(type_infraction, autorite)`: Retourne le montant applicable selon l'autorité

### ContraventionService
Service pour gérer les contraventions (création, validation, annulation).

**Méthodes principales:**
- `creer_contravention()`: Crée une nouvelle contravention avec validation complète
- `detecter_recidive()`: Détecte si le conducteur a commis la même infraction récemment
- `calculer_montant_amende()`: Calcule le montant final avec aggravations
- `annuler_contravention()`: Annule une contravention avec validation des règles
- `get_contraventions_impayees()`: Récupère les contraventions impayées

### FourriereService
Service pour gérer les dossiers de fourrière.

**Méthodes principales:**
- `creer_dossier_fourriere()`: Crée un dossier de fourrière lié à une contravention
- `calculer_frais_fourriere()`: Calcule les frais totaux (transport + gardiennage)
- `peut_restituer_vehicule()`: Vérifie si le véhicule peut être restitué
- `generer_bon_sortie()`: Génère le bon de sortie avec QR code
- `get_dossiers_actifs()`: Récupère tous les dossiers actifs
- `get_statistiques_fourriere()`: Calcule les statistiques de la fourrière

### PaiementAmendeService
Service pour gérer les paiements d'amendes via MVola, Stripe et Cash.

**Méthodes principales:**
- `initier_paiement_mvola()`: Initie un paiement MVola pour une amende
- `initier_paiement_stripe()`: Initie un paiement Stripe pour une amende
- `enregistrer_paiement_cash()`: Enregistre un paiement en espèces via un agent partenaire
- `confirmer_paiement()`: Confirme le paiement et génère le reçu avec QR code
- `calculer_frais_plateforme()`: Calcule les frais de plateforme selon la méthode

### ContestationService
Service pour gérer les contestations de contraventions.

**Méthodes principales:**
- `soumettre_contestation()`: Soumet une nouvelle contestation avec documents
- `examiner_contestation()`: Examine une contestation (pour superviseurs)
- `accepter_contestation()`: Accepte une contestation et annule la contravention
- `rejeter_contestation()`: Rejette une contestation et réactive le délai
- `get_contestations_en_attente()`: Récupère les contestations en attente
- `get_statistiques_contestations()`: Calcule les statistiques des contestations

## Utilisation

### Créer une contravention

```python
from contraventions.services import ContraventionService

contravention = ContraventionService.creer_contravention(
    agent=agent_user,
    type_infraction_id=infraction_id,
    conducteur_data={
        'cin': '123456789012',
        'nom_complet': 'John Doe',
        'numero_permis': 'P123456',
        'telephone': '0341234567'
    },
    lieu_data={
        'lieu_infraction': 'Route Nationale 1, Km 25',
        'route_type': 'NATIONALE',
        'route_numero': 'RN1'
    },
    vehicule_plaque='1234 TAA',
    observations='Excès de vitesse constaté',
    a_accident_associe=False,
    coordonnees_gps={'lat': -18.8792, 'lon': 47.5079}
)
```

### Créer un dossier de fourrière

```python
from contraventions.services import FourriereService

dossier = FourriereService.creer_dossier_fourriere(
    contravention=contravention,
    lieu_fourriere='Fourrière Centrale Antananarivo',
    adresse_fourriere='Rue de la Fourrière, Antananarivo',
    type_vehicule='VOITURE',
    user=agent_user
)
```

### Initier un paiement MVola

```python
from contraventions.services import PaiementAmendeService

result = PaiementAmendeService.initier_paiement_mvola(
    contravention=contravention,
    customer_msisdn='261341234567',
    user=request.user
)

if result['success']:
    print(f"Paiement initié. Transaction ID: {result['transaction_id']}")
```

### Enregistrer un paiement cash

```python
from contraventions.services import PaiementAmendeService

result = PaiementAmendeService.enregistrer_paiement_cash(
    contravention=contravention,
    agent_partenaire=agent_profile,
    montant_remis=Decimal('500000'),
    cash_session=session,
    user=agent_user
)

if result['success']:
    print(f"Paiement enregistré. Monnaie: {result['monnaie']} Ariary")
```

### Soumettre une contestation

```python
from contraventions.services import ContestationService

contestation = ContestationService.soumettre_contestation(
    contravention=contravention,
    demandeur_data={
        'nom_demandeur': 'John Doe',
        'email_demandeur': 'john@example.com',
        'telephone_demandeur': '0341234567'
    },
    motif='Je conteste cette contravention car...',
    documents=[document1, document2],
    user=request.user
)
```

### Examiner une contestation

```python
from contraventions.services import ContestationService

success, message = ContestationService.examiner_contestation(
    contestation=contestation,
    examinateur=superviseur_user,
    decision='ACCEPTEE',  # ou 'REJETEE'
    motif_decision='Après examen des preuves...',
    user=superviseur_user
)
```

## Intégrations

### Avec le système de paiement existant
- Réutilise `MvolaAPIClient` pour les paiements MVola
- Réutilise l'intégration Stripe pour les paiements par carte
- Réutilise `CashSession` et `CashTransaction` pour les paiements en espèces
- Génère des `QRCode` pour la vérification des reçus

### Avec le système de véhicules
- Recherche automatique des véhicules par plaque
- Récupération des informations du propriétaire
- Lien bidirectionnel entre contraventions et véhicules

### Avec le système de notifications
- Notifications au propriétaire lors de la création d'une contravention
- Notifications de confirmation de paiement
- Notifications d'annulation
- Notifications de décision sur les contestations

## Audit et traçabilité

Tous les services enregistrent leurs actions dans `ContraventionAuditLog` pour garantir:
- La traçabilité complète de toutes les opérations
- L'immuabilité via chaînage cryptographique
- La conformité légale et réglementaire
