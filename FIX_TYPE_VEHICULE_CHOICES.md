# Correction de l'erreur TYPE_VEHICULE_CHOICES

## Problème

**Erreur:** `AttributeError: type object 'Vehicule' has no attribute 'TYPE_VEHICULE_CHOICES'`

**Cause:** Le modèle `Vehicule` utilise maintenant un `ForeignKey` vers `VehicleType` au lieu d'un champ avec des choix fixes. La constante `TYPE_VEHICULE_CHOICES` n'existe plus.

## Solution

### 1. Mise à jour de `core/views.py` - FleetVehicleListView

**Avant:**
```python
'type_choices': Vehicule.TYPE_VEHICULE_CHOICES,
```

**Après:**
```python
from vehicles.models import VehicleType

# Get active vehicle types as choices (id, nom)
type_choices = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]

'type_choices': type_choices,
```

**Filtrage:**
```python
# Filter by vehicle type
vehicle_type = self.request.GET.get('type')
if vehicle_type:
    try:
        # Convert to integer if it's an ID
        vehicle_type_id = int(vehicle_type)
        queryset = queryset.filter(type_vehicule_id=vehicle_type_id)
    except (ValueError, TypeError):
        # If it's not a valid ID, try to filter by name
        queryset = queryset.filter(type_vehicule__nom__icontains=vehicle_type)
```

### 2. Mise à jour de `administration/views.py` - VehicleManagementView

**Avant:**
```python
context['vehicle_types'] = Vehicule.TYPE_VEHICULE_CHOICES
```

**Après:**
```python
from vehicles.models import VehicleType

# Get active vehicle types as choices (id, nom)
context['vehicle_types'] = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]
```

**Filtrage:** Même logique que pour `FleetVehicleListView`

### 3. Conversion de selected_type pour la comparaison dans les templates

**Problème:** `selected_type` vient de `request.GET.get('type', '')` qui est une chaîne, mais les IDs sont des entiers.

**Solution:**
```python
# Get selected type and convert to integer if possible for comparison
selected_type = self.request.GET.get('type', '')
try:
    selected_type_int = int(selected_type) if selected_type else ''
except (ValueError, TypeError):
    selected_type_int = selected_type

context['selected_type'] = selected_type_int
```

## Fichiers Modifiés

1. ✅ `core/views.py` - `FleetVehicleListView.get_context_data()`
2. ✅ `core/views.py` - `FleetVehicleListView.get_queryset()`
3. ✅ `administration/views.py` - `VehicleManagementView.get_context_data()`
4. ✅ `administration/views.py` - `VehicleManagementView.get_queryset()`

## Tests

### Vérification que VehicleType fonctionne
```python
from vehicles.models import VehicleType

types = VehicleType.get_active_types()
print(f'Types actifs: {types.count()}')
for vt in types:
    print(f'  - {vt.id}: {vt.nom}')
```

### Vérification que Vehicule n'a pas TYPE_VEHICULE_CHOICES
```python
from vehicles.models import Vehicule

# Cette ligne doit lever une AttributeError
# Vehicule.TYPE_VEHICULE_CHOICES  # ❌ N'existe plus

# Utiliser à la place:
from vehicles.models import VehicleType
choices = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]
```

## Format des Choices

**Ancien format (n'existe plus):**
```python
TYPE_VEHICULE_CHOICES = [
    ('voiture', 'Voiture'),
    ('moto', 'Moto'),
    # ...
]
```

**Nouveau format:**
```python
# Liste de tuples (id, nom) depuis VehicleType
choices = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]
# Exemple: [(1, 'Voiture'), (2, 'Moto'), ...]
```

## Utilisation dans les Templates

Les templates utilisent maintenant le format `(id, nom)`:
```django
{% for value, label in vehicle_types %}
    <option value="{{ value }}" {% if selected_type == value %}selected{% endif %}>
        {{ label }}
    </option>
{% endfor %}
```

Où:
- `value` = ID du VehicleType (entier)
- `label` = Nom du VehicleType (chaîne)
- `selected_type` = ID sélectionné (converti en entier dans la vue)

## Avantages de la Nouvelle Approche

1. **Flexibilité:** Les types de véhicules peuvent être ajoutés/modifiés via l'interface admin
2. **Activation/Désactivation:** Les types peuvent être activés ou désactivés sans modification du code
3. **Ordre d'affichage:** Les types peuvent être ordonnés via `ordre_affichage`
4. **Description:** Chaque type peut avoir une description

## Notes Importantes

- Les IDs de `VehicleType` sont des entiers, pas des chaînes
- Le filtrage doit utiliser `type_vehicule_id` ou `type_vehicule__nom`
- La comparaison dans les templates nécessite la conversion de `selected_type` en entier
- Les types inactifs (`est_actif=False`) ne sont pas inclus dans `get_active_types()`

## Résultat

✅ **Erreur corrigée:** `TYPE_VEHICULE_CHOICES` n'est plus utilisé
✅ **Filtrage fonctionnel:** Les véhicules peuvent être filtrés par type
✅ **Templates compatibles:** Les templates utilisent correctement le nouveau format
✅ **Tests passés:** Aucune erreur détectée

