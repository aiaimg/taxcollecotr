# 🚀 Quick Reference - Système de Notification

## Toast Notifications (Rapides)

```javascript
// Success
Notifications.success('Message de succès');

// Error
Notifications.error('Message d\'erreur');

// Warning
Notifications.warning('Message d\'avertissement');

// Info
Notifications.info('Message d\'information');
```

## Modal Alerts (Importantes)

```javascript
// Success Alert
Notifications.alertSuccess('Titre', 'Description');

// Error Alert
Notifications.alertError('Titre', 'Description');

// Warning Alert
Notifications.alertWarning('Titre', 'Description');

// Info Alert
Notifications.alertInfo('Titre', 'Description');
```

## Confirmations

```javascript
// Confirmation simple
Notifications.confirm('Titre', 'Message').then((result) => {
    if (result.isConfirmed) {
        // Action confirmée
    }
});

// Confirmation de suppression
Notifications.confirmDelete('Titre', 'Message').then((result) => {
    if (result.isConfirmed) {
        // Supprimer
    }
});
```

## Loading & Autres

```javascript
// Loading
Notifications.loading('Chargement...');
Notifications.close(); // Fermer

// Timer (auto-close)
Notifications.timerAlert('Titre', 'Message', 2000, 'success');

// Input Prompt
Notifications.prompt('Question', 'text').then((result) => {
    if (result.isConfirmed) {
        console.log(result.value);
    }
});
```

## Pattern AJAX Complet

```javascript
// Show loading
Notifications.loading('Traitement...');

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token }}'
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    Notifications.close();
    if (data.success) {
        Notifications.success(data.message);
    } else {
        Notifications.error(data.message);
    }
})
.catch(error => {
    Notifications.close();
    Notifications.error('Erreur réseau');
});
```

## Django Messages (Automatique)

```python
from django.contrib import messages

messages.success(request, 'Message de succès')
messages.error(request, 'Message d\'erreur')
messages.warning(request, 'Message d\'avertissement')
messages.info(request, 'Message d\'information')
```

## 🎯 Quand utiliser quoi?

| Type | Usage |
|------|-------|
| **Toast Success** | Sauvegarde, création, mise à jour réussie |
| **Toast Error** | Erreur simple, validation échouée |
| **Toast Warning** | Avertissement, attention requise |
| **Toast Info** | Information générale |
| **Alert Success** | Confirmation d'action importante |
| **Alert Error** | Erreur critique nécessitant attention |
| **Confirm** | Demander confirmation avant action |
| **Confirm Delete** | Confirmation de suppression |
| **Loading** | Opération asynchrone en cours |
| **Prompt** | Demander une saisie utilisateur |

## 📍 Accès Rapide

- **Demo**: `/app/notifications/demo/`
- **Docs**: `NOTIFICATION_SYSTEM.md`
- **Exemples**: `NOTIFICATION_EXAMPLES.md`
- **Code**: `static/js/notifications.js`
