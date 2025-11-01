# Notification System Documentation

## Overview
The notification system automatically notifies users about important events in the tax collection platform. Every significant action (Create, Read, Update, Delete) triggers appropriate notifications to keep users informed.

## Related Documentation
- **[Notification Rules](NOTIFICATION_RULES.md)** - Complete rules and guidelines
- **[Notification API](NOTIFICATION_API.md)** - API endpoints and integration examples

## Features Implemented

### 1. **Automatic Notifications**
Notifications are automatically created for the following events:

- ✅ **User Registration** - Welcome notification when a new user registers
- ✅ **Vehicle Added** - Notification when a vehicle is added to the account
- ✅ **Payment Confirmed** - Notification when payment is successfully completed
- ✅ **Payment Failed** - Notification when payment fails
- ✅ **QR Code Generated** - Notification when QR code is created

### 2. **Notification Service**
Location: `notifications/services.py`

The `NotificationService` class provides methods to:
- Create notifications manually
- Create notifications from templates
- Create specific event notifications (welcome, payment, vehicle, etc.)
- Mark notifications as read
- Get unread notification count
- Get recent notifications

### 3. **Signal Handlers**
Location: `notifications/signals.py`

Automatic notification creation using Django signals:
- `post_save` signal on User model creates welcome notification

### 4. **Views and URLs**
Location: `notifications/views.py` and `notifications/urls.py`

Available endpoints:
- `/notifications/` - List all notifications
- `/notifications/<id>/` - View notification detail (marks as read)
- `/notifications/<id>/mark-read/` - Mark specific notification as read
- `/notifications/mark-all-read/` - Mark all notifications as read
- `/notifications/api/unread-count/` - Get unread count (JSON)
- `/notifications/api/recent/` - Get recent notifications (JSON)

## Integration Points

### User Registration
File: `core/views.py` - `RegisterView.form_valid()`
```python
NotificationService.create_welcome_notification(user=self.object, langue='fr')
```

### Vehicle Creation
File: `vehicles/views.py` - `VehiculeCreateView.form_valid()`
```python
NotificationService.create_vehicle_added_notification(
    user=self.request.user,
    vehicle=form.instance,
    langue=langue
)
```

### Payment Confirmation
File: `payments/views.py` - `CheckPaymentStatusView.post()`
```python
NotificationService.create_payment_confirmation_notification(
    user=vehicule.proprietaire,
    payment=payment,
    langue=langue
)
```

### Payment Failed
File: `payments/views.py` - `CheckPaymentStatusView.post()`
```python
NotificationService.create_payment_failed_notification(
    user=vehicule.proprietaire,
    vehicle_plaque=payment.vehicule_plaque,
    langue=langue
)
```

### QR Code Generation
File: `payments/views.py` - `GenerateQRCodeView.post()`
```python
NotificationService.create_qr_generated_notification(
    user=request.user,
    qr_code=qr_code,
    langue=langue
)
```

## Testing

### Test Command
Run the test command to verify the notification system:
```bash
python manage.py test_notifications --username=<username>
```

This will:
1. Create sample notifications for the specified user
2. Display unread notification count
3. List recent notifications

### Manual Testing Steps

1. **Test User Registration:**
   - Register a new user at `/register/`
   - Check notifications at `/notifications/`
   - Should see welcome notification

2. **Test Vehicle Addition:**
   - Login and add a vehicle at `/vehicles/add/`
   - Check notifications
   - Should see vehicle added notification

3. **Test Payment:**
   - Create a payment for a vehicle
   - Complete the payment
   - Check notifications
   - Should see payment confirmation notification

4. **Test QR Code:**
   - Generate QR code for a paid vehicle
   - Check notifications
   - Should see QR code generated notification

## API Usage

### Get Unread Count (AJAX)
```javascript
fetch('/notifications/api/unread-count/')
  .then(response => response.json())
  .then(data => console.log('Unread:', data.count));
```

### Get Recent Notifications (AJAX)
```javascript
fetch('/notifications/api/recent/?limit=10')
  .then(response => response.json())
  .then(data => {
    console.log('Notifications:', data.notifications);
    console.log('Unread count:', data.unread_count);
  });
```

### Mark as Read (AJAX)
```javascript
fetch('/notifications/<notification_id>/mark-read/', {
  method: 'POST',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRFToken': getCookie('csrftoken')
  }
})
.then(response => response.json())
.then(data => console.log(data.message));
```

## Database Models

### Notification Model
- `id` - UUID primary key
- `user` - ForeignKey to User
- `type_notification` - Type (email, sms, push, system)
- `titre` - Title
- `contenu` - Content
- `langue` - Language (fr/mg)
- `est_lue` - Read status
- `date_envoi` - Send date
- `date_lecture` - Read date
- `metadata` - Additional data (JSON)

### NotificationTemplate Model
- Template-based notifications for consistency
- Supports multiple languages
- Variable substitution

## Multi-language Support

The system supports both French (fr) and Malagasy (mg) languages. Notifications are created in the user's preferred language if available in their profile.

## Future Enhancements

Potential improvements:
- Email notifications
- SMS notifications via API
- Push notifications for mobile apps
- Notification preferences/settings
- Batch notifications for fleet managers
- Tax deadline reminders (scheduled task)
- Notification templates management UI

## Notes

- All notifications are stored in the database
- Notifications are user-specific and secure
- Signal handlers ensure automatic notification creation
- The system is extensible for new notification types
- Supports both French and Malagasy languages
