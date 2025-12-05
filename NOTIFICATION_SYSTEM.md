# Système de Notification Professionnel

Ce document décrit le système de notification intégré utilisant **SweetAlert2** et **Toastify.js** de Velzon.

## 🎯 Fonctionnalités

- ✅ **Toast Notifications** - Notifications légères et non-intrusives
- ✅ **Modal Alerts** - Alertes modales pour actions importantes
- ✅ **Confirmations** - Dialogues de confirmation avec callbacks
- ✅ **Loading States** - Indicateurs de chargement
- ✅ **Auto-dismiss** - Fermeture automatique des notifications
- ✅ **Django Integration** - Intégration automatique avec les messages Django

## 📦 Installation

Le système est déjà intégré dans les templates de base :
- `templates/base_velzon.html` (Dashboard Velzon)
- `templates/cms/base.html` (Site public)

## 🚀 Utilisation

### 1. Toast Notifications (Toastify)

#### Notifications simples

```javascript
// Success
Notifications.success('Opération réussie!');

// Error
Notifications.error('Une erreur est survenue');

// Warning
Notifications.warning('Attention, vérifiez vos données');

// Info
Notifications.info('Information importante');
```

#### Notifications personnalisées

```javascript
Notifications.toast('Message personnalisé', 'success', {
    duration: 5000,
    position: 'center',
    gravity: 'bottom',
    onClick: function() {
        console.log('Toast clicked!');
    }
});
```

### 2. Modal Alerts (SweetAlert2)

#### Alertes simples

```javascript
// Success Alert
Notifications.alertSuccess('Succès!', 'Votre action a été effectuée avec succès');

// Error Alert
Notifications.alertError('Erreur!', 'Une erreur est survenue lors du traitement');

// Warning Alert
Notifications.alertWarning('Attention!', 'Cette action nécessite votre attention');

// Info Alert
Notifications.alertInfo('Information', 'Voici une information importante');
```

#### Confirmation Dialog

```javascript
Notifications.confirm(
    'Êtes-vous sûr?',
    'Cette action ne peut pas être annulée'
).then((result) => {
    if (result.isConfirmed) {
        // User clicked "Oui"
        console.log('Confirmed!');
    } else {
        // User clicked "Non" or closed
        console.log('Cancelled!');
    }
});
```

#### Confirmation de suppression

```javascript
Notifications.confirmDelete(
    'Supprimer cet élément?',
    'Cette action est irréversible.'
).then((result) => {
    if (result.isConfirmed) {
        // Proceed with deletion
        deleteItem();
    }
});
```

### 3. Loading States

```javascript
// Show loading
Notifications.loading('Traitement en cours...', 'Veuillez patienter');

// Perform async operation
fetch('/api/endpoint')
    .then(response => response.json())
    .then(data => {
        // Close loading
        Notifications.close();
        // Show success
        Notifications.success('Données chargées!');
    })
    .catch(error => {
        Notifications.close();
        Notifications.error('Erreur de chargement');
    });
```

### 4. Input Prompt

```javascript
Notifications.prompt('Entrez votre nom', 'text', {
    inputPlaceholder: 'Votre nom complet',
    inputValidator: (value) => {
        if (!value || value.length < 3) {
            return 'Le nom doit contenir au moins 3 caractères';
        }
    }
}).then((result) => {
    if (result.isConfirmed) {
        console.log('User entered:', result.value);
    }
});
```

### 5. Timer Alert (Auto-close)

```javascript
Notifications.timerAlert(
    'Sauvegardé!',
    'Vos modifications ont été enregistrées',
    2000,
    'success'
);
```

## 🎨 Exemples d'Utilisation dans les Templates

### Exemple 1: Formulaire de suppression

```html
<button type="button" class="btn btn-danger" onclick="confirmDelete({{ item.id }})">
    <i class="fas fa-trash"></i> Supprimer
</button>

<script>
function confirmDelete(itemId) {
    Notifications.confirmDelete(
        'Supprimer cet élément?',
        'Cette action est irréversible.'
    ).then((result) => {
        if (result.isConfirmed) {
            // Show loading
            Notifications.loading('Suppression en cours...');
            
            // Make AJAX request
            fetch(`/api/items/${itemId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                Notifications.close();
                if (response.ok) {
                    Notifications.success('Élément supprimé avec succès!');
                    // Reload or update UI
                    location.reload();
                } else {
                    Notifications.error('Erreur lors de la suppression');
                }
            })
            .catch(error => {
                Notifications.close();
                Notifications.error('Erreur réseau');
            });
        }
    });
}
</script>
```

### Exemple 2: Formulaire AJAX

```html
<form id="myForm">
    {% csrf_token %}
    <input type="text" name="name" class="form-control" required>
    <button type="submit" class="btn btn-primary">Enregistrer</button>
</form>

<script>
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    // Show loading
    Notifications.loading('Enregistrement en cours...');
    
    fetch('/api/save/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        Notifications.close();
        
        if (data.success) {
            Notifications.alertSuccess('Succès!', data.message).then(() => {
                // Redirect or update UI
                window.location.href = data.redirect_url;
            });
        } else {
            Notifications.alertError('Erreur', data.message);
        }
    })
    .catch(error => {
        Notifications.close();
        Notifications.error('Erreur lors de l\'enregistrement');
    });
});
</script>
```

### Exemple 3: Validation côté client

```javascript
function validateForm() {
    const email = document.getElementById('email').value;
    
    if (!email.includes('@')) {
        Notifications.warning('Email invalide', {
            duration: 4000
        });
        return false;
    }
    
    return true;
}
```

## 🔧 Intégration Django

### Dans les vues Django

```python
from django.contrib import messages
from django.shortcuts import redirect

def my_view(request):
    # Success message
    messages.success(request, 'Opération réussie!')
    
    # Error message
    messages.error(request, 'Une erreur est survenue')
    
    # Warning message
    messages.warning(request, 'Attention!')
    
    # Info message
    messages.info(request, 'Information')
    
    return redirect('some_view')
```

Les messages Django sont automatiquement convertis en toast notifications!

## 🎨 Personnalisation

### Modifier les styles de toast

Éditez `templates/partials/notifications.html` pour personnaliser les styles CSS.

### Modifier les options par défaut

Éditez `static/js/notifications.js` pour changer les configurations par défaut.

## 📱 Responsive

Le système est entièrement responsive et s'adapte à tous les écrans :
- Desktop: Position top-right
- Mobile: Position center ou top-center

## 🌐 Internationalisation

Les messages peuvent être traduits en utilisant Django i18n :

```javascript
Notifications.success("{% trans 'Opération réussie!' %}");
```

## 🔍 Débogage

Pour tester le système de notification :

```javascript
// Test all notification types
Notifications.success('Test Success');
Notifications.error('Test Error');
Notifications.warning('Test Warning');
Notifications.info('Test Info');

// Test alert
Notifications.alertSuccess('Test Alert', 'This is a test');

// Test confirmation
Notifications.confirm('Test?', 'Confirm this action').then(console.log);
```

## 📚 Documentation des bibliothèques

- **SweetAlert2**: https://sweetalert2.github.io/
- **Toastify.js**: https://apvarun.github.io/toastify-js/

## ✅ Checklist d'implémentation

- [x] Installation des bibliothèques (Velzon inclus)
- [x] Création du fichier notifications.js
- [x] Création du template partials/notifications.html
- [x] Intégration dans base_velzon.html
- [x] Intégration dans cms/base.html
- [x] Support des messages Django
- [x] Documentation complète

## 🎯 Prochaines étapes

Pour utiliser le système dans votre application :

1. Les notifications sont déjà intégrées dans tous les templates
2. Utilisez `Notifications.*` dans vos scripts JavaScript
3. Utilisez `messages.*` dans vos vues Django
4. Personnalisez les styles selon vos besoins

Profitez d'un système de notification professionnel et élégant! 🎉
