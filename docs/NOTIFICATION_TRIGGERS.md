# Notification Triggers - Complete Reference

This document provides a complete reference of all notification triggers in the Tax Collection Platform.

## 📋 Trigger Summary

| # | Action | Event | Notification Type | File Location | Method |
|---|--------|-------|-------------------|---------------|--------|
| 1 | User Registration | User created | Welcome | `core/views.py` | `RegisterView.form_valid()` |
| 2 | User Registration | User created (signal) | Welcome | `notifications/signals.py` | `create_welcome_notification()` |
| 3 | User Login | User logged in | Login Success | `notifications/signals.py` | `create_login_notification()` |
| 4 | User Logout | User logged out | Logout | `notifications/signals.py` | `create_logout_notification()` |
| 5 | Profile Update | Profile modified | Profile Updated | `core/views.py` | `ProfileEditView.form_valid()` |
| 6 | Password Change | Password modified | Security Alert | Manual trigger | `create_password_changed_notification()` |
| 7 | Vehicle Added | Vehicle created | Vehicle Added | `vehicles/views.py` | `VehiculeCreateView.form_valid()` |
| 8 | Vehicle Updated | Vehicle modified | Vehicle Updated | `vehicles/views.py` | `VehiculeUpdateView.form_valid()` |
| 9 | Vehicle Deleted | Vehicle removed | Vehicle Deleted | `vehicles/views.py` | `VehiculeDeleteView.delete()` |
| 10 | Payment Success | Payment completed | Payment Confirmed | `payments/views.py` | `CheckPaymentStatusView.post()` |
| 11 | Payment Failed | Payment failed | Payment Failed | `payments/views.py` | `CheckPaymentStatusView.post()` |
| 12 | Payment Cancelled | Payment cancelled | Payment Cancelled | Manual trigger | `create_payment_cancelled_notification()` |
| 13 | QR Code Generated | QR created | QR Generated | `payments/views.py` | `GenerateQRCodeView.post()` |
| 14 | Account Deactivated | Admin action | Account Deactivated | `administration/views.py` | `toggle_user_status()` |
| 15 | Account Reactivated | Admin action | Account Reactivated | `administration/views.py` | `toggle_user_status()` |
| 16 | Tax Reminder | Scheduled task | Tax Reminder | Scheduled | `create_tax_reminder_notification()` |
| 17 | Admin Action | Admin action | Admin Action | Manual trigger | `create_admin_action_notification()` |

## 🔍 Detailed Trigger Information

### 1. User Registration
**Trigger:** New user account created  
**When:** User completes registration form  
**File:** `core/views.py` - `RegisterView.form_valid()`  
**Also:** `notifications/signals.py` - `post_save` signal on User model

**Code:**
```python
NotificationService.create_welcome_notification(
    user=self.object,
    langue='fr'
)
```

**Notification Content (French):**
- **Title:** "Bienvenue sur la plateforme!"
- **Content:** "Bienvenue [Name]! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme."

**Notification Content (Malagasy):**
- **Title:** "Tonga soa eto amin'ny sehatra!"
- **Content:** "Tonga soa [Name]! Ny kaontinao dia voaforona soa aman-tsara. Afaka manomboka mampiasa ny sehatra ianao izao."

---

### 2. User Login
**Trigger:** User successfully logs in  
**When:** User submits login form with valid credentials  
**File:** `notifications/signals.py` - `user_logged_in` signal

**Code:**
```python
NotificationService.create_login_notification(
    user=user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Connexion réussie"
- **Content:** "Vous vous êtes connecté avec succès le [DATE] à [TIME]."

**Notification Content (Malagasy):**
- **Title:** "Niditra soa aman-tsara"
- **Content:** "Niditra tamin'ny kaontinao ianao tamin'ny [DATE] tamin'ny [TIME]."

**Metadata:** `{'event': 'user_login', 'login_time': timestamp}`

**Security:** Helps users track account access

---

### 3. User Logout
**Trigger:** User logs out  
**When:** User clicks logout button  
**File:** `notifications/signals.py` - `user_logged_out` signal

**Code:**
```python
NotificationService.create_logout_notification(
    user=user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Déconnexion"
- **Content:** "Vous vous êtes déconnecté le [DATE] à [TIME]."

**Notification Content (Malagasy):**
- **Title:** "Nivoaka"
- **Content:** "Nivoaka tamin'ny kaontinao ianao tamin'ny [DATE] tamin'ny [TIME]."

**Metadata:** `{'event': 'user_logout', 'logout_time': timestamp}`

---

### 4. Profile Update
**Trigger:** User updates profile information  
**When:** User saves profile changes  
**File:** `core/views.py` - `ProfileEditView.form_valid()`

**Code:**
```python
NotificationService.create_profile_updated_notification(
    user=self.request.user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Profil mis à jour"
- **Content:** "Votre profil a été mis à jour avec succès."

**Notification Content (Malagasy):**
- **Title:** "Mombamomba anao nohavaozina"
- **Content:** "Ny mombamomba anao dia nohavaozina soa aman-tsara."

---

### 5. Password Change
**Trigger:** User changes password  
**When:** Password change form submitted  
**File:** Manual trigger (to be implemented in password change view)

**Code:**
```python
NotificationService.create_password_changed_notification(
    user=user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Mot de passe modifié"
- **Content:** "Votre mot de passe a été modifié avec succès. Si ce n'était pas vous, contactez immédiatement l'administrateur."

**Notification Content (Malagasy):**
- **Title:** "Teny miafina novaina"
- **Content:** "Ny teny miafinao dia novaina soa aman-tsara. Raha tsy ianao no nanao izany, mifandraisa amin'ny mpitantana avy hatrany."

**Security:** This is a security notification with `metadata={'security': True}`

---

### 6. Vehicle Added
**Trigger:** New vehicle added to account  
**When:** Vehicle creation form submitted  
**File:** `vehicles/views.py` - `VehiculeCreateView.form_valid()`

**Code:**
```python
NotificationService.create_vehicle_added_notification(
    user=self.request.user,
    vehicle=form.instance,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Véhicule ajouté"
- **Content:** "Le véhicule [PLAQUE] a été ajouté avec succès à votre compte."

**Notification Content (Malagasy):**
- **Title:** "Fiara vaovao nampidirina"
- **Content:** "Ny fiara [PLAQUE] dia nampidirina soa aman-tsara."

**Metadata:** `{'event': 'vehicle_added', 'vehicle_id': str(vehicle.id)}`

---

### 7. Vehicle Updated
**Trigger:** Vehicle information modified  
**When:** Vehicle update form submitted  
**File:** `vehicles/views.py` - `VehiculeUpdateView.form_valid()`

**Code:**
```python
NotificationService.create_vehicle_updated_notification(
    user=self.request.user,
    vehicle=form.instance,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Véhicule modifié"
- **Content:** "Les informations du véhicule [PLAQUE] ont été mises à jour avec succès."

**Notification Content (Malagasy):**
- **Title:** "Fiara nohavaozina"
- **Content:** "Ny fiara [PLAQUE] dia nohavaozina soa aman-tsara."

**Metadata:** `{'event': 'vehicle_updated', 'vehicle_id': str(vehicle.id)}`

---

### 8. Vehicle Deleted
**Trigger:** Vehicle removed from account  
**When:** Vehicle deletion confirmed  
**File:** `vehicles/views.py` - `VehiculeDeleteView.delete()`

**Code:**
```python
NotificationService.create_vehicle_deleted_notification(
    user=request.user,
    vehicle_plaque=vehicle_plaque,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Véhicule supprimé"
- **Content:** "Le véhicule [PLAQUE] a été supprimé de votre compte."

**Notification Content (Malagasy):**
- **Title:** "Fiara nesorina"
- **Content:** "Ny fiara [PLAQUE] dia nesorina tamin'ny kaontinao."

**Metadata:** `{'event': 'vehicle_deleted', 'vehicle_plaque': vehicle_plaque}`

**Note:** This is a soft delete (sets `est_actif=False`)

---

### 9. Payment Success
**Trigger:** Payment completed successfully  
**When:** Payment status changes to 'PAYE'  
**File:** `payments/views.py` - `CheckPaymentStatusView.post()`

**Code:**
```python
NotificationService.create_payment_confirmation_notification(
    user=vehicule.proprietaire,
    payment=payment,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Paiement confirmé"
- **Content:** "Votre paiement pour le véhicule [PLAQUE] a été confirmé. Montant payé: [AMOUNT] Ar"

**Notification Content (Malagasy):**
- **Title:** "Fandoavam-bola vita soa aman-tsara"
- **Content:** "Ny fandoavam-bola ho an'ny fiara [PLAQUE] dia vita soa aman-tsara. Vola naloa: [AMOUNT] Ar"

**Metadata:** `{'event': 'payment_confirmed', 'payment_id': str(payment.id), 'amount': str(payment.montant_paye_ariary)}`

---

### 10. Payment Failed
**Trigger:** Payment processing failed  
**When:** Payment status changes to 'ECHEC'  
**File:** `payments/views.py` - `CheckPaymentStatusView.post()`

**Code:**
```python
NotificationService.create_payment_failed_notification(
    user=vehicule.proprietaire,
    vehicle_plaque=payment.vehicule_plaque,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Échec du paiement"
- **Content:** "Le paiement pour le véhicule [PLAQUE] a échoué. Veuillez réessayer."

**Notification Content (Malagasy):**
- **Title:** "Tsy nahomby ny fandoavam-bola"
- **Content:** "Tsy nahomby ny fandoavam-bola ho an'ny fiara [PLAQUE]. Andramo indray azafady."

**Metadata:** `{'event': 'payment_failed', 'vehicle_plaque': vehicle_plaque}`

---

### 11. Payment Cancelled
**Trigger:** Payment cancelled by user or admin  
**When:** Payment cancellation confirmed  
**File:** Manual trigger (to be implemented)

**Code:**
```python
NotificationService.create_payment_cancelled_notification(
    user=user,
    vehicle_plaque=vehicle_plaque,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Paiement annulé"
- **Content:** "Le paiement pour le véhicule [PLAQUE] a été annulé."

**Notification Content (Malagasy):**
- **Title:** "Fandoavam-bola nofoanana"
- **Content:** "Ny fandoavam-bola ho an'ny fiara [PLAQUE] dia nofoanana."

**Metadata:** `{'event': 'payment_cancelled', 'vehicle_plaque': vehicle_plaque}`

---

### 12. QR Code Generated
**Trigger:** QR code created for vehicle  
**When:** QR code generation requested  
**File:** `payments/views.py` - `GenerateQRCodeView.post()`

**Code:**
```python
NotificationService.create_qr_generated_notification(
    user=request.user,
    qr_code=qr_code,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "QR code généré"
- **Content:** "Le QR code pour le véhicule [PLAQUE] a été généré avec succès."

**Notification Content (Malagasy):**
- **Title:** "QR code noforonina"
- **Content:** "Ny QR code ho an'ny fiara [PLAQUE] dia noforonina soa aman-tsara."

**Metadata:** `{'event': 'qr_generated', 'qr_code': qr_code.code, 'vehicle_plaque': qr_code.vehicule_plaque}`

**Note:** Only triggered when QR code is newly created (not reactivated)

---

### 13. Account Deactivated
**Trigger:** Admin deactivates user account  
**When:** Admin toggles user status to inactive  
**File:** `administration/views.py` - `toggle_user_status()`

**Code:**
```python
NotificationService.create_account_deactivated_notification(
    user=user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Compte désactivé"
- **Content:** "Votre compte a été désactivé. Contactez l'administrateur pour plus d'informations."

**Notification Content (Malagasy):**
- **Title:** "Kaonty najanona"
- **Content:** "Ny kaontinao dia najanona. Mifandraisa amin'ny mpitantana raha mila fanazavana."

**Metadata:** `{'event': 'account_deactivated', 'security': True}`

**Security:** This is a security notification

---

### 14. Account Reactivated
**Trigger:** Admin reactivates user account  
**When:** Admin toggles user status to active  
**File:** `administration/views.py` - `toggle_user_status()`

**Code:**
```python
NotificationService.create_account_reactivated_notification(
    user=user,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Compte réactivé"
- **Content:** "Votre compte a été réactivé. Vous pouvez à nouveau utiliser la plateforme."

**Notification Content (Malagasy):**
- **Title:** "Kaonty navaoina"
- **Content:** "Ny kaontinao dia navaoina. Afaka mampiasa ny sehatra indray ianao."

**Metadata:** `{'event': 'account_reactivated'}`

---

### 15. Tax Reminder
**Trigger:** Scheduled task for tax deadline reminders  
**When:** Cron job runs (to be implemented)  
**File:** Scheduled task (to be implemented)

**Code:**
```python
NotificationService.create_tax_reminder_notification(
    user=user,
    vehicle=vehicle,
    days_remaining=days_remaining,
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Rappel de taxe"
- **Content:** "Il reste [DAYS] jours avant l'échéance de paiement de la taxe pour le véhicule [PLAQUE]."

**Notification Content (Malagasy):**
- **Title:** "Fampahatsiahivana hetra"
- **Content:** "Misy [DAYS] andro sisa alohan'ny ho tapitra ny fe-potoana handoavana ny hetra ho an'ny fiara [PLAQUE]."

**Metadata:** `{'event': 'tax_reminder', 'vehicle_id': str(vehicle.id), 'days_remaining': days_remaining}`

**Implementation:** Requires Celery or cron job

---

### 16. Admin Action
**Trigger:** Admin performs action on user account  
**When:** Admin makes changes to user account  
**File:** Manual trigger (to be implemented in admin views)

**Code:**
```python
NotificationService.create_admin_action_notification(
    user=user,
    action='Action name',
    details='Action details',
    langue=langue
)
```

**Notification Content (French):**
- **Title:** "Action administrateur: [ACTION]"
- **Content:** "Une action a été effectuée sur votre compte: [DETAILS]"

**Notification Content (Malagasy):**
- **Title:** "Hetsika avy amin'ny mpitantana: [ACTION]"
- **Content:** "Nisy hetsika natao tamin'ny kaontinao: [DETAILS]"

**Metadata:** `{'event': 'admin_action', 'action': action, 'details': details}`

---

## 🔄 Automatic vs Manual Triggers

### Automatic Triggers (Implemented)
These are automatically triggered by the system:
- ✅ User Registration (signal + view)
- ✅ Profile Update
- ✅ Vehicle Added
- ✅ Vehicle Updated
- ✅ Vehicle Deleted
- ✅ Payment Success
- ✅ Payment Failed
- ✅ QR Code Generated
- ✅ Account Deactivated
- ✅ Account Reactivated

### Manual Triggers (To Be Implemented)
These require additional implementation:
- ⏳ Password Change (needs password change view integration)
- ⏳ Payment Cancelled (needs cancellation feature)
- ⏳ Tax Reminder (needs scheduled task)
- ⏳ Admin Action (needs admin action tracking)

## 📊 Notification Flow Diagram

```
User Action → View/Signal → NotificationService → Database → User Notification
     ↓              ↓                ↓                ↓              ↓
  Register    form_valid()    create_welcome()    INSERT      Display in UI
```

## 🧪 Testing Triggers

### Test Each Trigger
```bash
# 1. User Registration
python manage.py test_notifications --username=newuser

# 2. Vehicle Operations
# - Add vehicle via UI
# - Update vehicle via UI
# - Delete vehicle via UI

# 3. Payment Operations
# - Create payment
# - Complete payment
# - Check notifications

# 4. Admin Operations
# - Toggle user status
# - Check user notifications
```

### Verify Notifications
```python
# In Django shell
from django.contrib.auth.models import User
from notifications.models import Notification

user = User.objects.get(username='testuser')
notifications = Notification.objects.filter(user=user)

for notif in notifications:
    print(f"{notif.titre}: {notif.contenu}")
```

---

**Last Updated:** November 1, 2025  
**Version:** 1.0  
**Maintained By:** Development Team
