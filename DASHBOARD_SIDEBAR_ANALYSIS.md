# Analyse des Dashboards et Sidebars par Type d'Utilisateur

## État Actuel

### Sidebars Existants
1. ✅ `sidebar_client.html` - Pour `individual` (par défaut)
2. ✅ `sidebar_company.html` - Pour `company`
3. ✅ `sidebar_administration.html` - Pour `admin/staff`
4. ✅ `sidebar_agent_government.html` - Pour agents gouvernement
5. ✅ `sidebar_agent_partenaire.html` - Pour agents partenaires

### Dashboards Existants
1. ✅ `dashboard.html` - Dashboard général (VelzonDashboardView) - Pour tous les utilisateurs non-admin
2. ✅ `fleet/dashboard.html` - Dashboard flotte (FleetDashboardView) - Pour `company` uniquement
3. ✅ `administration/dashboard.html` - Dashboard admin

## Problèmes Identifiés

### ❌ Problème 1: Sidebar pour public_institution et international_organization
- **Situation:** Les utilisateurs `public_institution` et `international_organization` utilisent actuellement le `sidebar_client` (par défaut)
- **Impact:** Ils n'ont pas accès aux fonctionnalités de gestion de flotte dans le sidebar
- **Solution:** Créer des sidebars spécifiques ou faire en sorte qu'ils utilisent le sidebar_company

### ❌ Problème 2: FleetManagerMixin restreint à company uniquement
- **Fichier:** `core/views.py` ligne 667
- **Code actuel:** `if not (hasattr(request.user, 'profile') and request.user.profile.user_type == 'company'):`
- **Impact:** Les utilisateurs `public_institution` et `international_organization` ne peuvent pas accéder au dashboard flotte
- **Solution:** Mettre à jour le mixin pour inclure les nouveaux types

### ❌ Problème 3: Logique de sidebar dans base_velzon.html
- **Fichier:** `templates/base_velzon.html` lignes 40-58
- **Problème:** Pas de cas spécifique pour `public_institution` et `international_organization`
- **Solution:** Ajouter des conditions pour ces types

## Solutions Recommandées

### Option 1: Utiliser le sidebar_company pour public_institution et international_organization
- **Avantage:** Réutilise le code existant
- **Justification:** Ces types gèrent aussi des flottes de véhicules
- **Implémentation:** Modifier `base_velzon.html` pour inclure ces types

### Option 2: Créer des sidebars spécifiques
- **Avantage:** Plus de flexibilité pour personnaliser
- **Inconvénient:** Duplication de code
- **Recommandation:** Utiliser Option 1 pour l'instant

## Plan d'Action

1. ✅ Mettre à jour `FleetManagerMixin` pour inclure `public_institution` et `international_organization`
2. ✅ Mettre à jour `base_velzon.html` pour afficher le sidebar_company pour ces types
3. ✅ Vérifier que le dashboard flotte fonctionne pour ces types
4. ✅ Tester l'accès aux fonctionnalités de flotte

