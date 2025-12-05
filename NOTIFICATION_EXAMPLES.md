# Exemples Pratiques d'Utilisation des Notifications

## 🎯 Exemples Django + JavaScript

### 1. Formulaire AJAX avec Notifications

#### Vue Django (views.py)
```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

@login_required
@require_POST
def save_vehicle(request):
    try:
        data = json.loads(request.body)
        
        # Validation
        if not data.get('plate_number'):
            return JsonResponse({
                'success': False,
                'message': 'Le numéro de plaque est requis'
            }, status=400)
        
        # Save vehicle
        vehicle = Vehicule.objects.create(
            plaque=data['plate_number'],
            proprietaire=request.user,
            # ... autres champs
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Véhicule enregistré avec succès!',
            'vehicle_id': vehicle.id,
            'redirect_url': reverse('vehicles:vehicle_detail', args=[vehicle.id])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)
```

#### Template HTML + JavaScript
```html
<form id="vehicleForm">
    {% csrf_token %}
    <div class="mb-3">
        <label>Numéro de plaque</label>
        <input type="text" name="plate_number" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Enregistrer</button>
</form>

<script>
document.getElementById('vehicleForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        plate_number: this.plate_number.value
    };
    
    // Show loading
    Notifications.loading('Enregistrement en cours...');
    
    fetch('/api/vehicles/save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        Notifications.close();
        
        if (data.success) {
            Notifications.alertSuccess('Succès!', data.message).then(() => {
                window.location.href = data.redirect_url;
            });
        } else {
            Notifications.alertError('Erreur', data.message);
        }
    })
    .catch(error => {
        Notifications.close();
        Notifications.error('Erreur réseau');
    });
});
</script>
```

### 2. Suppression avec Confirmation

#### Vue Django
```python
@login_required
@require_POST
def delete_vehicle(request, vehicle_id):
    try:
        vehicle = get_object_or_404(Vehicule, id=vehicle_id, proprietaire=request.user)
        plate_number = vehicle.plaque
        vehicle.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Véhicule {plate_number} supprimé avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
```

#### Template
```html
<button class="btn btn-danger" onclick="deleteVehicle({{ vehicle.id }}, '{{ vehicle.plaque }}')">
    <i class="ri-delete-bin-line"></i> Supprimer
</button>

<script>
function deleteVehicle(vehicleId, plateNumber) {
    Notifications.confirmDelete(
        'Supprimer ce véhicule?',
        `Êtes-vous sûr de vouloir supprimer le véhicule ${plateNumber}? Cette action est irréversible.`
    ).then((result) => {
        if (result.isConfirmed) {
            Notifications.loading('Suppression en cours...');
            
            fetch(`/api/vehicles/${vehicleId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
            .then(response => response.json())
            .then(data => {
                Notifications.close();
                
                if (data.success) {
                    Notifications.success(data.message);
                    // Remove row from table or reload
                    setTimeout(() => location.reload(), 1500);
                } else {
                    Notifications.error(data.message);
                }
            })
            .catch(error => {
                Notifications.close();
                Notifications.error('Erreur lors de la suppression');
            });
        }
    });
}
</script>
```

### 3. Validation en Temps Réel

```html
<form id="paymentForm">
    <div class="mb-3">
        <label>Montant (Ar)</label>
        <input type="number" id="amount" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Payer</button>
</form>

<script>
document.getElementById('amount').addEventListener('blur', function() {
    const amount = parseFloat(this.value);
    
    if (amount < 1000) {
        Notifications.warning('Le montant minimum est de 1000 Ar');
        this.focus();
    } else if (amount > 1000000) {
        Notifications.warning('Le montant maximum est de 1,000,000 Ar');
        this.focus();
    }
});

document.getElementById('paymentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const amount = parseFloat(document.getElementById('amount').value);
    
    if (amount < 1000 || amount > 1000000) {
        Notifications.alertError('Montant invalide', 'Veuillez entrer un montant valide');
        return;
    }
    
    // Process payment...
    Notifications.loading('Traitement du paiement...');
    
    // Simulate payment processing
    setTimeout(() => {
        Notifications.close();
        Notifications.alertSuccess('Paiement réussi!', `Montant: ${amount.toLocaleString()} Ar`);
    }, 2000);
});
</script>
```

### 4. Messages Django Automatiques

#### Vue Django
```python
from django.contrib import messages
from django.shortcuts import redirect

def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Erreur lors de la mise à jour du profil')
    
    return render(request, 'profile_edit.html', {'form': form})
```

Les messages Django sont automatiquement convertis en toast notifications!

### 5. Upload de Fichier avec Progression

```html
<form id="uploadForm" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="document" id="fileInput" accept=".pdf,.jpg,.png">
    <button type="submit" class="btn btn-primary">Upload</button>
</form>

<script>
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        Notifications.warning('Veuillez sélectionner un fichier');
        return;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        Notifications.alertError('Fichier trop volumineux', 'La taille maximale est de 5 MB');
        return;
    }
    
    const formData = new FormData(this);
    
    Notifications.loading('Upload en cours...', 'Veuillez patienter');
    
    fetch('/api/documents/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        Notifications.close();
        
        if (data.success) {
            Notifications.alertSuccess('Upload réussi!', data.message);
            fileInput.value = '';
        } else {
            Notifications.alertError('Erreur d\'upload', data.message);
        }
    })
    .catch(error => {
        Notifications.close();
        Notifications.error('Erreur lors de l\'upload');
    });
});
</script>
```

### 6. Recherche en Temps Réel

```html
<input type="text" id="searchInput" class="form-control" placeholder="Rechercher...">
<div id="searchResults"></div>

<script>
let searchTimeout;

document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value.trim();
    
    if (query.length < 2) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length === 0) {
                    Notifications.info('Aucun résultat trouvé', {
                        duration: 2000
                    });
                }
                // Display results...
            })
            .catch(error => {
                Notifications.error('Erreur de recherche');
            });
    }, 500);
});
</script>
```

### 7. Batch Operations

```html
<button class="btn btn-primary" onclick="processBatchPayment()">
    Payer la sélection
</button>

<script>
function processBatchPayment() {
    const selectedVehicles = getSelectedVehicles(); // Your function
    
    if (selectedVehicles.length === 0) {
        Notifications.warning('Veuillez sélectionner au moins un véhicule');
        return;
    }
    
    Notifications.confirm(
        'Paiement groupé',
        `Payer pour ${selectedVehicles.length} véhicule(s)?`
    ).then((result) => {
        if (result.isConfirmed) {
            Notifications.loading('Traitement des paiements...');
            
            fetch('/api/payments/batch/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    vehicle_ids: selectedVehicles
                })
            })
            .then(response => response.json())
            .then(data => {
                Notifications.close();
                
                if (data.success) {
                    Notifications.alertSuccess(
                        'Paiements effectués!',
                        `${data.processed} paiement(s) traité(s) avec succès`
                    ).then(() => {
                        location.reload();
                    });
                } else {
                    Notifications.alertError('Erreur', data.message);
                }
            })
            .catch(error => {
                Notifications.close();
                Notifications.error('Erreur lors du traitement');
            });
        }
    });
}
</script>
```

### 8. Export avec Feedback

```html
<button class="btn btn-success" onclick="exportData('excel')">
    <i class="ri-file-excel-line"></i> Exporter Excel
</button>

<script>
function exportData(format) {
    Notifications.loading('Génération du fichier...', 'Cela peut prendre quelques secondes');
    
    fetch(`/api/export/${format}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Export failed');
        return response.blob();
    })
    .then(blob => {
        Notifications.close();
        
        // Download file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        Notifications.success('Fichier téléchargé avec succès!');
    })
    .catch(error => {
        Notifications.close();
        Notifications.error('Erreur lors de l\'export');
    });
}
</script>
```

## 🎨 Bonnes Pratiques

1. **Utilisez les toasts pour les actions rapides**
   - Sauvegarde réussie
   - Élément supprimé
   - Validation simple

2. **Utilisez les alertes modales pour les actions importantes**
   - Confirmations de suppression
   - Erreurs critiques
   - Informations détaillées

3. **Toujours fermer les loading states**
   ```javascript
   Notifications.loading('...');
   try {
       await someOperation();
   } finally {
       Notifications.close(); // Important!
   }
   ```

4. **Gérez les erreurs réseau**
   ```javascript
   .catch(error => {
       Notifications.close();
       Notifications.error('Erreur de connexion');
   });
   ```

5. **Utilisez des messages clairs et en français**
   - ✅ "Véhicule enregistré avec succès"
   - ❌ "Success"

## 🔗 Liens Utiles

- Documentation complète: `NOTIFICATION_SYSTEM.md`
- Page de démonstration: `/app/notifications/demo/`
- Code source: `static/js/notifications.js`
