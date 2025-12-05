# Guide de Configuration SMTP

Ce guide explique comment configurer et utiliser le système d'envoi d'emails via SMTP dans l'administration Django.

## Accès à la Configuration

1. Connectez-vous à l'interface d'administration Django: `/admin/`
2. Naviguez vers **Administration** → **Configurations SMTP**

## Créer une Nouvelle Configuration SMTP

### 1. Informations Générales

- **Nom**: Un nom descriptif pour identifier cette configuration (ex: "Gmail Production", "Office365 Dev")
- **Description**: Notes ou description optionnelle
- **Configuration active**: Cochez pour activer cette configuration (une seule peut être active à la fois)

### 2. Configuration du Serveur SMTP

#### Exemples de Configurations Populaires

**Gmail:**
- Serveur SMTP: `smtp.gmail.com`
- Port: `587`
- Chiffrement: `TLS`
- Note: Utilisez un "Mot de passe d'application" au lieu de votre mot de passe Gmail

**Office 365 / Outlook:**
- Serveur SMTP: `smtp.office365.com`
- Port: `587`
- Chiffrement: `TLS`

**SendGrid:**
- Serveur SMTP: `smtp.sendgrid.net`
- Port: `587`
- Chiffrement: `TLS`
- Nom d'utilisateur: `apikey`
- Mot de passe: Votre clé API SendGrid

**Mailgun:**
- Serveur SMTP: `smtp.mailgun.org`
- Port: `587`
- Chiffrement: `TLS`

### 3. Authentification

- **Nom d'utilisateur**: Votre adresse email ou nom d'utilisateur SMTP
- **Mot de passe**: Votre mot de passe ou mot de passe d'application

### 4. Paramètres d'Expédition

- **Email expéditeur**: L'adresse email qui apparaîtra comme expéditeur
- **Nom de l'expéditeur**: Le nom qui apparaîtra (ex: "Tax Collector")
- **Email de réponse**: Adresse email pour les réponses (optionnel)

### 5. Limites et Quotas

- **Limite quotidienne d'emails**: Nombre maximum d'emails par jour (0 = illimité)
- Le compteur se réinitialise automatiquement chaque jour

## Tester la Configuration

1. Après avoir créé/modifié une configuration, cliquez sur le bouton **"Tester"**
2. Vous pouvez:
   - **Tester la connexion**: Vérifie que les paramètres SMTP sont corrects
   - **Envoyer un email de test**: Entrez une adresse email pour recevoir un email de test

## Utilisation dans le Code

### Méthode 1: Envoi Simple

```python
from administration.email_utils import send_email

success, message, logs = send_email(
    subject="Sujet de l'email",
    message="Corps du message en texte brut",
    recipient_list=["destinataire@example.com"],
    html_message="<h1>Corps HTML optionnel</h1>",
    email_type="notification",
    fail_silently=False
)

if success:
    print(f"Email envoyé: {message}")
else:
    print(f"Erreur: {message}")
```

### Méthode 2: Utilisation de Templates

```python
from administration.email_utils import send_template_email

success, message, logs = send_template_email(
    template_name='payment_reminder',  # Sans extension
    context={
        'user': user,
        'vehicle': vehicle,
        'payment': payment,
    },
    recipient_list=[user.email],
    email_type='payment_reminder',
    related_object_type='PaiementTaxe',
    related_object_id=payment.id,
    fail_silently=True
)
```

### Méthode 3: Fonctions Spécialisées

```python
from administration.email_utils import send_payment_reminder, send_notification_email

# Envoyer un rappel de paiement
success, message, logs = send_payment_reminder(payment)

# Envoyer une notification
success, message, logs = send_notification_email(notification)
```

## Structure des Templates d'Email

Les templates d'email doivent être placés dans `templates/emails/` avec la structure suivante:

```
templates/emails/
├── payment_reminder_subject.txt  # Sujet de l'email
├── payment_reminder.txt          # Version texte
└── payment_reminder.html         # Version HTML (optionnel)
```

### Exemple de Template Sujet (`payment_reminder_subject.txt`):
```
Rappel de paiement - Taxe véhicule {{ vehicle.plaque_immatriculation }}
```

### Exemple de Template Texte (`payment_reminder.txt`):
```
Bonjour {{ user.get_full_name }},

Ceci est un rappel concernant le paiement de la taxe pour votre véhicule:
Plaque: {{ vehicle.plaque_immatriculation }}
Montant: {{ payment.montant_paye_ariary }} Ar

Cordialement,
L'équipe Tax Collector
```

## Journal des Emails

Tous les emails envoyés sont enregistrés dans **Administration** → **Journaux d'emails**.

Vous pouvez consulter:
- Le statut de chaque email (En attente, Envoyé, Échoué, Rejeté)
- Le destinataire et le sujet
- Le type d'email
- La date d'envoi
- Les messages d'erreur éventuels

## Sécurité

### Mots de Passe d'Application

Pour Gmail et d'autres services, utilisez des "mots de passe d'application" au lieu de votre mot de passe principal:

**Gmail:**
1. Activez la validation en deux étapes sur votre compte Google
2. Allez dans Paramètres → Sécurité → Mots de passe d'application
3. Générez un nouveau mot de passe d'application
4. Utilisez ce mot de passe dans la configuration SMTP

### Bonnes Pratiques

1. **Ne partagez jamais** vos identifiants SMTP
2. **Utilisez des mots de passe d'application** plutôt que vos mots de passe principaux
3. **Testez toujours** une nouvelle configuration avant de l'activer
4. **Surveillez les limites** quotidiennes pour éviter d'être bloqué
5. **Vérifiez les logs** régulièrement pour détecter les problèmes

## Dépannage

### Erreur d'authentification
- Vérifiez le nom d'utilisateur et le mot de passe
- Pour Gmail, assurez-vous d'utiliser un mot de passe d'application
- Vérifiez que la validation en deux étapes est activée (si nécessaire)

### Impossible de se connecter au serveur
- Vérifiez l'hôte et le port SMTP
- Vérifiez le type de chiffrement (TLS/SSL)
- Assurez-vous que votre pare-feu autorise les connexions sortantes

### Emails non reçus
- Vérifiez le dossier spam/courrier indésirable
- Consultez les journaux d'emails pour voir le statut
- Vérifiez que l'adresse email du destinataire est correcte

### Limite quotidienne atteinte
- Attendez le lendemain pour que le compteur se réinitialise
- Augmentez la limite quotidienne dans la configuration
- Utilisez un service SMTP avec des limites plus élevées

## Intégration avec les Rappels de Paiement

Le système de rappels de paiement utilise automatiquement la configuration SMTP active.

Pour envoyer des rappels:

```bash
python manage.py send_payment_reminders
```

Cette commande:
1. Identifie les paiements en retard
2. Utilise la configuration SMTP active
3. Envoie des emails de rappel
4. Enregistre tous les envois dans les journaux

## Support

Pour toute question ou problème, consultez:
- La documentation Django sur l'envoi d'emails
- Les logs d'application dans `logs/`
- Les journaux d'emails dans l'administration

## Prochaines Étapes

- [ ] Configuration SMS (à venir)
- [ ] Webhooks pour les événements d'email
- [ ] Templates d'email personnalisables via l'interface
- [ ] Statistiques d'envoi avancées
