# Support for Vehicles Without Registration Plates

## Overview
Added support for motorcycles and other vehicles that don't have official registration plates (plaques d'immatriculation).

## Changes Made

### 1. Vehicle Model Updates (`vehicles/models.py`)

#### New Field
- **`a_plaque_immatriculation`**: Boolean field (default: True)
  - Indicates whether the vehicle has an official registration plate
  - Uncheck for motorcycles or vehicles without plates

#### Updated Field
- **`plaque_immatriculation`**: 
  - Max length increased from 15 to 20 characters
  - Now accepts two formats:
    - Standard format: `1234 TAA` (official plates)
    - Temporary format: `TEMP-XXXXXXXX` (for vehicles without plates)
  - Updated regex validator to accept both formats

#### New Methods
- **`generate_temp_plate()`**: Static method to generate temporary plate IDs
  - Format: `TEMP-` followed by 8 random alphanumeric characters
  - Example: `TEMP-A7K9M2X1`

- **`get_display_plate()`**: Returns user-friendly plate display
  - For vehicles with plates: Returns the actual plate number
  - For vehicles without plates: Returns "Sans plaque (TEMP-XXXXXXXX)"

- **`__str__()`**: Updated to show vehicle status
  - With plate: `1234 TAA - John Doe`
  - Without plate: `Véhicule sans plaque (TEMP-A7K9M2X1) - John Doe`

### 2. Database Migration
- Migration file: `vehicles/migrations/0007_add_temp_plate_support.py`
- Adds the new `a_plaque_immatriculation` field
- Updates the `plaque_immatriculation` field constraints

### 3. Fixed Administration View
- **File**: `administration/views_modules/individual_vehicles.py`
- Fixed `Count('id')` references to `Count('plaque_immatriculation')`
- The Vehicule model uses `plaque_immatriculation` as primary key, not `id`

## Usage

### Creating a Vehicle Without a Plate

#### Option 1: In Django Admin or Forms
1. Generate a temporary ID:
   ```python
   from vehicles.models import Vehicule
   temp_plate = Vehicule.generate_temp_plate()
   # Returns something like: "TEMP-A7K9M2X1"
   ```

2. Create the vehicle:
   ```python
   vehicle = Vehicule.objects.create(
       plaque_immatriculation=temp_plate,
       a_plaque_immatriculation=False,  # Important!
       proprietaire=user,
       type_vehicule=moto_type,
       # ... other fields
   )
   ```

#### Option 2: Automatic Generation (Recommended)
Add this to your vehicle creation form/view:

```python
def save(self, commit=True):
    vehicle = super().save(commit=False)
    
    # If no plate checkbox is unchecked and plate is empty or temp
    if not vehicle.a_plaque_immatriculation:
        if not vehicle.plaque_immatriculation or not vehicle.plaque_immatriculation.startswith('TEMP-'):
            vehicle.plaque_immatriculation = Vehicule.generate_temp_plate()
    
    if commit:
        vehicle.save()
    return vehicle
```

### Displaying Vehicle Information

```python
# In templates
{{ vehicle.get_display_plate }}  # Shows "Sans plaque (TEMP-XXX)" or actual plate

# Check if vehicle has a plate
{% if vehicle.a_plaque_immatriculation %}
    <span class="badge bg-success">Plaque officielle</span>
{% else %}
    <span class="badge bg-warning">Sans plaque</span>
{% endif %}
```

### Filtering Vehicles

```python
# Get all vehicles with official plates
vehicles_with_plates = Vehicule.objects.filter(a_plaque_immatriculation=True)

# Get all vehicles without plates (temporary IDs)
vehicles_without_plates = Vehicule.objects.filter(a_plaque_immatriculation=False)

# Get all motorcycles without plates
motos_sans_plaque = Vehicule.objects.filter(
    type_vehicule__nom='Moto',
    a_plaque_immatriculation=False
)
```

## Form Updates Needed

Update your vehicle forms to include the new field:

```python
class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = [
            'plaque_immatriculation',
            'a_plaque_immatriculation',  # Add this
            'proprietaire',
            # ... other fields
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make plate optional if checkbox is unchecked
        self.fields['plaque_immatriculation'].required = False
        self.fields['plaque_immatriculation'].help_text = (
            "Laissez vide pour les véhicules sans plaque - "
            "un identifiant sera généré automatiquement"
        )
```

## Template Updates

Update vehicle list/detail templates:

```html
<!-- Vehicle List -->
<td>
    {% if vehicle.a_plaque_immatriculation %}
        <span class="badge bg-success">
            <i class="ri-car-line me-1"></i>
            {{ vehicle.plaque_immatriculation }}
        </span>
    {% else %}
        <span class="badge bg-warning text-dark">
            <i class="ri-alert-line me-1"></i>
            Sans plaque
        </span>
        <small class="text-muted d-block">{{ vehicle.plaque_immatriculation }}</small>
    {% endif %}
</td>

<!-- Vehicle Detail -->
<div class="card">
    <div class="card-body">
        <h5>Identification</h5>
        {% if vehicle.a_plaque_immatriculation %}
            <p><strong>Plaque:</strong> {{ vehicle.plaque_immatriculation }}</p>
        {% else %}
            <p>
                <strong>Statut:</strong> 
                <span class="badge bg-warning">Véhicule sans plaque d'immatriculation</span>
            </p>
            <p><strong>Identifiant temporaire:</strong> {{ vehicle.plaque_immatriculation }}</p>
        {% endif %}
    </div>
</div>
```

## Important Notes

1. **Uniqueness**: Each temporary ID is unique and serves as the primary key
2. **Tax Calculation**: Vehicles without plates are still subject to taxes
3. **QR Codes**: QR codes can still be generated using the temporary ID
4. **Payments**: Payment system works the same way with temporary IDs
5. **Search**: Update search functionality to handle both formats
6. **Export**: When exporting data, indicate which vehicles don't have official plates

## Migration Applied

The migration has been successfully applied. All existing vehicles now have `a_plaque_immatriculation=True` by default.

## Next Steps

1. Update vehicle creation forms to include the new checkbox
2. Add JavaScript to auto-generate temp IDs when checkbox is unchecked
3. Update vehicle list/detail templates to show plate status
4. Update search/filter functionality to handle temporary IDs
5. Add admin interface customization for better UX
