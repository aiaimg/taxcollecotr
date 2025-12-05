# Normalisation des Plaques d'Immatriculation

## Problème Résolu

Les plaques d'immatriculation étaient stockées avec des espaces (ex: `6160 TAB`), ce qui causait des problèmes d'URL et de routage Django.

## Solution Implémentée

### 1. Normalisation du Modèle Vehicule

**Fichier**: `vehicles/models.py`

- **Validation mise à jour**: Le regex n'accepte plus les espaces dans les plaques (ex: `1234TAA` au lieu de `1234 TAA`)
- **Méthode `normalize_plate()`**: Supprime automatiquement les espaces et convertit en majuscules
- **Méthode `get_display_plate()`**: Formate la plaque pour l'affichage avec un espace (ex: `1234TAA` → `1234 TAA`)
- **Override `save()` et `clean()`**: Normalise automatiquement les plaques avant sauvegarde

### 2. Template Tag pour l'Affichage

**Fichier**: `vehicles/templatetags/vehicle_extras.py`

Ajout du filtre `format_plate` pour formater les plaques dans les templates:

```django
{{ vehicle.plaque_immatriculation|format_plate }}
```

Ce filtre transforme `1234TAA` en `1234 TAA` pour l'affichage.

### 3. Script de Migration

**Fichier**: `vehicles/management/commands/normalize_vehicle_plates.py`

Commande Django pour normaliser les plaques existantes:

```bash
# Mode dry-run (aperçu sans modification)
python manage.py normalize_vehicle_plates --dry-run

# Exécution réelle
python manage.py normalize_vehicle_plates
```

Le script:
- Trouve toutes les plaques avec espaces
- Met à jour les tables liées (payments_qrcode, payments_paiementtaxe)
- Met à jour la table vehicles_vehicule
- Gère les contraintes de clé étrangère

### 4. Auto-Dismiss des Notifications

**Fichiers modifiés**:
- `templates/base_velzon.html`
- `templates/administration/base_admin.html`
- `templates/cms/base.html`
- `templates/base/base.html`

Les notifications (messages Django) disparaissent automatiquement après 5 secondes et peuvent être fermées manuellement avec le bouton ×.

### 5. Corrections des Templates

**Fichiers corrigés**:
- `templates/administration/payment_management.html`
- `templates/administration/users/detail.html`

Corrections:
- Utilisation de `payment.vehicule_plaque` au lieu de `payment.vehicule`
- Ajout du filtre `format_plate` pour l'affichage
- Gestion des cas où `vehicule_plaque` est `None`

## Résultats

✅ **4 véhicules normalisés**:
- `7280 TCD` → `7280TCD`
- `6160 TAB` → `6160TAB`
- `3482 TCD` → `3482TCD`
- `5172 TAB` → `5172TAB`

✅ **URLs fonctionnelles**: `/administration/individual-vehicles/6160TAB/` fonctionne correctement

✅ **Affichage lisible**: Les plaques s'affichent avec espace (`6160 TAB`) pour la lisibilité

✅ **Notifications améliorées**: Auto-dismiss après 5 secondes, bouton de fermeture fonctionnel

## Utilisation Future

### Pour les nouveaux véhicules

Les plaques peuvent être saisies avec ou sans espace - elles seront automatiquement normalisées:
- Saisie: `1234 TAA` ou `1234TAA`
- Stockage: `1234TAA` (sans espace)
- Affichage: `1234 TAA` (avec espace)

### Dans les templates

Toujours utiliser le filtre `format_plate` pour l'affichage:

```django
{% load vehicle_extras %}
{{ vehicle.plaque_immatriculation|format_plate }}
```

### Dans le code Python

Utiliser la méthode du modèle:

```python
# Affichage formaté
display_plate = vehicle.get_display_plate()

# Normalisation manuelle
normalized = Vehicule.normalize_plate("1234 TAA")  # → "1234TAA"
```
