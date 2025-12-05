# Navigation Integration - Système de Contravention

## Vue d'ensemble

Le module de contraventions a été intégré dans la navigation de la plateforme TaxCollector avec des sidebars spécifiques pour différents types d'utilisateurs et des widgets de tableau de bord.

## Sidebars

### 1. Sidebar Agent Contrôleur (Police/Gendarmerie)

**Fichier:** `templates/velzon/partials/sidebar_agent_government.html`

**Sections ajoutées:**
- **Contraventions**
  - Liste des Contraventions (`contraventions:list`)
  - Créer une Contravention (`contraventions:create`)
  - Fourrière (`contraventions:fourriere_list`)

**Utilisateurs concernés:** Agents de police et gendarmerie avec profil `AgentControleurProfile`

**Détection:** Via le template tag `is_agent_government_user` dans `base_velzon.html`

### 2. Sidebar Administration

**Fichier:** `templates/velzon/partials/sidebar_administration.html`

**Sections ajoutées:**
- **Gestion des Contraventions**
  - Liste des Contraventions
  - Créer une Contravention
  - Contestations
  - Types d'Infractions
  - Rapports et Statistiques
  - Configuration

- **Gestion de la Fourrière**
  - Dossiers en Fourrière
  - Créer un Dossier

**Utilisateurs concernés:** Administrateurs et superviseurs (`is_staff` ou `is_superuser`)

## Widgets de Tableau de Bord

### 1. Widget Statistiques Contraventions

**Fichier:** `templates/partials/contraventions_stats_widget.html`

**Métriques affichées:**
- Contraventions du mois (avec croissance)
- Amendes collectées
- Taux de paiement
- Contestations en attente

**Intégration:** Inclus dans `templates/administration/dashboard.html`

**Données:** Fournies par `administration/views.py` dans `dashboard_view()`

### 2. Widget Contraventions Récentes

**Fichier:** `templates/partials/contraventions_widget.html`

**Affichage:**
- Liste des 5 dernières contraventions
- Numéro PV avec badge de statut
- Type d'infraction
- Véhicule et montant
- Temps écoulé

**Intégration:** Inclus dans `templates/administration/dashboard.html`

## URLs Configurées

### URLs Agents
- `/contraventions/` - Liste des contraventions
- `/contraventions/create/` - Créer une contravention
- `/contraventions/<id>/` - Détails d'une contravention
- `/contraventions/<id>/cancel/` - Annuler une contravention

### URLs Fourrière
- `/contraventions/fourriere/` - Liste des dossiers
- `/contraventions/fourriere/create/<contravention_id>/` - Créer un dossier
- `/contraventions/fourriere/<id>/` - Détails d'un dossier

### URLs Administration
- `/contraventions/admin/infractions/` - Gestion des types d'infractions
- `/contraventions/admin/reports/` - Rapports et statistiques
- `/contraventions/admin/contestations/` - Liste des contestations
- `/contraventions/admin/contestations/<id>/` - Détails d'une contestation
- `/contraventions/admin/configuration/` - Configuration du système

### URLs Publiques
- `/contraventions/public/<numero_pv>/` - Consultation publique
- `/contraventions/public/<numero_pv>/contest/` - Soumettre une contestation

### URLs AJAX
- `/contraventions/ajax/search-vehicle/` - Recherche véhicule
- `/contraventions/ajax/search-conducteur/` - Recherche conducteur
- `/contraventions/ajax/get-infraction-details/` - Détails infraction
- `/contraventions/ajax/check-recidive/` - Vérifier récidive

## Permissions

### Agent Contrôleur
- Créer des contraventions
- Consulter ses propres contraventions
- Créer des dossiers de fourrière
- Annuler ses contraventions (dans les 24h)

### Administrateur
- Toutes les permissions des agents
- Gérer les types d'infractions
- Consulter tous les rapports
- Examiner les contestations
- Configurer le système

### Public (sans authentification)
- Consulter une contravention via numéro PV
- Soumettre une contestation
- Payer une amende

## Statistiques du Tableau de Bord

Les statistiques suivantes sont calculées dans `administration/views.py`:

```python
contravention_stats = {
    'monthly_count': int,           # Nombre de contraventions ce mois
    'monthly_growth': float,        # Croissance par rapport au mois précédent (%)
    'monthly_revenue': Decimal,     # Revenus des amendes ce mois
    'payment_rate': float,          # Taux de paiement (%)
    'pending_contestations': int,   # Contestations en attente
}

recent_contraventions = [...]       # 5 dernières contraventions
```

## Vues Ajoutées

### Nouvelles vues créées pour la navigation:

1. **DossierFourriereListView** - Liste des dossiers de fourrière
   - Template: `contraventions/fourriere_list.html`
   - Filtres: statut
   - Pagination: 50 items

2. **ContestationDetailView** - Détails d'une contestation
   - Template: `contraventions/admin/contestation_detail.html`
   - Accès: Administrateurs uniquement

## Intégration avec le Système Existant

### Context Processors
Le système utilise `core/context_processors.py` pour détecter le type d'utilisateur:
- `is_agent_government` - Pour les agents contrôleurs
- `is_admin_user` - Pour les administrateurs

### Base Template
`templates/base_velzon.html` sélectionne automatiquement le bon sidebar selon le type d'utilisateur.

## Tests de Navigation

Pour tester l'intégration:

1. **En tant qu'Agent Contrôleur:**
   - Se connecter avec un compte ayant `AgentControleurProfile`
   - Vérifier que le sidebar affiche les sections Contraventions et Fourrière
   - Tester la navigation vers chaque page

2. **En tant qu'Administrateur:**
   - Se connecter avec un compte `is_staff=True`
   - Vérifier que le sidebar administration affiche toutes les sections
   - Vérifier que les widgets apparaissent sur le dashboard
   - Tester tous les liens de navigation

3. **Widgets du Dashboard:**
   - Vérifier que les statistiques s'affichent correctement
   - Vérifier que les contraventions récentes apparaissent
   - Tester les liens vers les pages détaillées

## Prochaines Étapes

1. Créer les templates HTML manquants (Tâche 11)
2. Ajouter les tests d'intégration
3. Documenter l'API pour l'application mobile
4. Créer les management commands manquantes

## Notes Importantes

- Les URLs ont été réorganisées pour une meilleure structure
- Les vues manquantes ont été ajoutées (DossierFourriereListView, ContestationDetailView)
- Les widgets sont conditionnels et ne s'affichent que si des données existent
- La navigation est responsive et fonctionne sur mobile
