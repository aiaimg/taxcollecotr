# Notification System Rules and Guidelines

## Overview
This document defines the rules and guidelines for the notification system in the Tax Collection Platform.

## Core Principles

### 1. **User-Friendly Notifications**
- Every significant action should trigger a notification
- Notifications should be clear, concise, and actionable
- Use the user's preferred language (French or Malagasy)
- Include relevant details without overwhelming the user

### 2. **Notification Triggers**
All CRUD operations and important events trigger notifications:

#### **CREATE Operations**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| User Registration | New user account created | Welcome notification |
| Vehicle Added | New vehicle added to account | Vehicle added notification |
| Payment Initiated | Payment process started | Payment initiated notification |
| QR Code Generated | QR code created for vehicle | QR code generated notification |

#### **READ Operations**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| First Login | User logs in for first time | Welcome back notification |
| QR Code Verified | QR code scanned by agent | Verification notification |

#### **UPDATE Operations**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| Vehicle Updated | Vehicle information modified | Vehicle updated notification |
| Profile Updated | User profile information changed | Profile updated notification |
| Payment Updated | Payment status or details changed | Payment updated notification |
| Password Changed | User password modified | Security notification |

#### **DELETE Operations**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| Vehicle Deleted | Vehicle removed from account | Vehicle deleted notification |
| Payment Cancelled | Payment cancelled by user/admin | Payment cancelled notification |

#### **ADMIN Actions**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| Account Activated | Admin activates user account | Account reactivated notification |
| Account Deactivated | Admin deactivates user account | Account deactivated notification |
| Admin Action | Any admin action on user account | Admin action notification |

#### **SYSTEM Events**
| Action | Trigger | Notification Type |
|--------|---------|-------------------|
| Payment Success | Payment completed successfully | Payment confirmation notification |
| Payment Failed | Payment processing failed | Payment failed notification |
| Tax Deadline | Approaching tax payment deadline | Tax reminder notification |

## Implementation Rules

### Rule 1: Automatic Notification Creation
```python
# Every significant action MUST create a notification
# Use NotificationService methods for consistency

from notifications.services import NotificationService

# Example: After creating a vehicle
NotificationService.create_vehicle_added_notification(
    user=request.user,
    vehicle=vehicle_instance,
    langue=user_language
)
```

### Rule 2: Language Support
```python
# Always respect user's language preference
langue = 'fr'  # Default to French
if hasattr(user, 'profile'):
    langue = user.profile.langue_preferee

# Pass language to notification service
NotificationService.create_notification(..., langue=langue)
```

### Rule 3: Metadata Inclusion
```python
# Include relevant metadata for tracking and debugging
metadata = {
    'event': 'vehicle_added',
    'vehicle_id': str(vehicle.id),
    'timestamp': timezone.now().isoformat(),
    'action_by': request.user.username
}
```

### Rule 4: Security Notifications
```python
# Security-related actions MUST trigger immediate notifications
# Examples: password change, account deactivation, suspicious activity

NotificationService.create_password_changed_notification(
    user=user,
    langue=langue
)
```

### Rule 5: Notification Types
Use appropriate notification types:
- `system` - Platform notifications (default)
- `email` - Email notifications (future)
- `sms` - SMS notifications (future)
- `push` - Push notifications (future)

### Rule 6: Error Handling
```python
# Notification creation should not break the main flow
try:
    NotificationService.create_notification(...)
except Exception as e:
    logger.error(f"Failed to create notification: {e}")
    # Continue with main operation
```

## Notification Content Guidelines

### Title (Titre)
- Keep it short (max 50 characters)
- Use action verbs
- Be specific
- Examples:
  - ✅ "Véhicule ajouté"
  - ✅ "Paiement confirmé"
  - ❌ "Notification"
  - ❌ "Information importante"

### Content (Contenu)
- Be clear and concise
- Include relevant details (vehicle plate, amount, date)
- Provide context
- Use friendly tone
- Examples:
  - ✅ "Le véhicule ABC-123 a été ajouté avec succès à votre compte."
  - ✅ "Votre paiement de 50,000 Ar pour le véhicule ABC-123 a été confirmé."
  - ❌ "Opération effectuée."
  - ❌ "Voir les détails dans votre compte."

### Bilingual Support
Every notification must support both French and Malagasy:

```python
if langue == 'mg':
    titre = "Fiara nampidirina"
    contenu = f"Ny fiara {vehicle.numero_plaque} dia nampidirina soa aman-tsara."
else:
    titre = "Véhicule ajouté"
    contenu = f"Le véhicule {vehicle.numero_plaque} a été ajouté avec succès."
```

## Integration Points

### Views Integration
```python
# In form_valid() or post() methods
def form_valid(self, form):
    response = super().form_valid(form)
    
    # Create notification after successful operation
    NotificationService.create_xxx_notification(
        user=self.request.user,
        ...
    )
    
    return response
```

### Signal Handlers
```python
# Use signals for automatic notifications
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Model)
def create_notification(sender, instance, created, **kwargs):
    if created:
        NotificationService.create_xxx_notification(...)
```

### API Endpoints
```python
# After successful API operation
if operation_successful:
    NotificationService.create_notification(...)
    return Response({'success': True})
```

## Testing Requirements

### Unit Tests
Every notification type must have unit tests:
```python
def test_vehicle_added_notification():
    user = User.objects.create(username='test')
    vehicle = Vehicle.objects.create(...)
    
    notif = NotificationService.create_vehicle_added_notification(
        user=user,
        vehicle=vehicle,
        langue='fr'
    )
    
    assert notif is not None
    assert notif.user == user
    assert 'ajouté' in notif.titre.lower()
```

### Integration Tests
Test notification creation in views:
```python
def test_vehicle_create_view_creates_notification():
    # Create vehicle via view
    response = client.post('/vehicles/add/', data)
    
    # Check notification was created
    notifications = Notification.objects.filter(user=user)
    assert notifications.count() == 1
    assert 'véhicule' in notifications[0].titre.lower()
```

## Performance Considerations

### Rule 1: Async Processing (Future)
For high-volume notifications, use async processing:
```python
# Future implementation with Celery
@shared_task
def send_notification_async(user_id, notification_type, **kwargs):
    user = User.objects.get(id=user_id)
    NotificationService.create_notification(...)
```

### Rule 2: Batch Notifications
For fleet managers with many vehicles:
```python
# Create notifications in bulk
notifications = [
    Notification(user=user, titre=..., contenu=...)
    for vehicle in vehicles
]
Notification.objects.bulk_create(notifications)
```

### Rule 3: Cleanup Old Notifications
Implement periodic cleanup:
```python
# Delete read notifications older than 90 days
old_date = timezone.now() - timedelta(days=90)
Notification.objects.filter(
    est_lue=True,
    date_lecture__lt=old_date
).delete()
```

## Security Rules

### Rule 1: User Isolation
- Users can only see their own notifications
- Implement proper queryset filtering:
```python
notifications = Notification.objects.filter(user=request.user)
```

### Rule 2: Sensitive Information
- Never include passwords or tokens in notifications
- Mask sensitive data (e.g., phone numbers: +261 XX XXX XX XX)

### Rule 3: XSS Prevention
- Escape all user-generated content in notifications
- Use Django's template auto-escaping

## Monitoring and Analytics

### Metrics to Track
- Notification creation rate
- Read vs unread ratio
- Time to read notifications
- Notification types distribution
- User engagement with notifications

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Log notification creation
logger.info(f"Notification created: {notif.id} for user {user.username}")
```

## Future Enhancements

### Phase 1: Email Integration
- Send email for important notifications
- User preference for email notifications
- Email templates

### Phase 2: SMS Integration
- SMS for critical notifications
- Integration with local SMS providers (Orange, Telma, Airtel)

### Phase 3: Push Notifications
- Mobile app push notifications
- Web push notifications
- Real-time updates

### Phase 4: Notification Preferences
- User settings for notification types
- Frequency preferences
- Quiet hours

### Phase 5: Rich Notifications
- Action buttons in notifications
- Inline actions (mark as read, delete)
- Notification grouping

## Compliance and Privacy

### GDPR Compliance
- Users can delete their notifications
- Export notification data on request
- Clear data retention policies

### Data Retention
- Keep unread notifications indefinitely
- Delete read notifications after 90 days (configurable)
- Archive important notifications

## Documentation Requirements

### Code Documentation
Every notification method must include:
```python
def create_xxx_notification(user, ..., langue='fr'):
    """
    Create notification for XXX event
    
    Args:
        user: User object
        ...: Additional parameters
        langue: Language code (fr/mg)
    
    Returns:
        Notification object
    
    Example:
        >>> notif = NotificationService.create_xxx_notification(
        ...     user=user,
        ...     langue='fr'
        ... )
    """
```

### Change Log
Document all notification changes:
- New notification types
- Modified notification content
- Deprecated notifications

## Support and Maintenance

### Troubleshooting
Common issues and solutions:
1. Notifications not appearing → Check signal registration
2. Wrong language → Verify user profile language setting
3. Duplicate notifications → Check for multiple signal handlers

### Contact
For notification system issues:
- Technical Lead: [Contact Info]
- Documentation: `/docs/NOTIFICATION_SYSTEM.md`
- Issue Tracker: [Link]

---

**Last Updated:** November 1, 2025  
**Version:** 1.0  
**Maintained By:** Development Team
