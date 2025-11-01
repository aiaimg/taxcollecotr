# Tax Collection Platform - Documentation

Welcome to the Tax Collection Platform documentation. This folder contains all technical documentation for the system.

## 📚 Documentation Index

### Notification System
The notification system keeps users informed about all important actions and events.

1. **[NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md)**
   - Overview and features
   - Integration points
   - Testing procedures
   - Database models
   - Multi-language support

2. **[NOTIFICATION_RULES.md](NOTIFICATION_RULES.md)**
   - Core principles and rules
   - Notification triggers (CRUD operations)
   - Implementation guidelines
   - Content guidelines
   - Security rules
   - Performance considerations
   - Testing requirements

3. **[NOTIFICATION_API.md](NOTIFICATION_API.md)**
   - API endpoints documentation
   - Request/response formats
   - Integration examples (React, Vue, jQuery, Vanilla JS)
   - Error handling
   - Security considerations

4. **[NOTIFICATION_TRIGGERS.md](NOTIFICATION_TRIGGERS.md)**
   - Complete trigger reference
   - Detailed trigger information
   - Code examples for each trigger
   - Automatic vs manual triggers
   - Testing procedures

## 🚀 Quick Start

### For Developers

#### Understanding the Notification System
1. Read [NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md) for overview
2. Review [NOTIFICATION_RULES.md](NOTIFICATION_RULES.md) for implementation rules
3. Check [NOTIFICATION_API.md](NOTIFICATION_API.md) for API integration

#### Adding New Notifications
```python
from notifications.services import NotificationService

# Create a notification
NotificationService.create_notification(
    user=user,
    type_notification='system',
    titre='Your Title',
    contenu='Your message',
    langue='fr',
    metadata={'event': 'your_event'}
)
```

#### Testing Notifications
```bash
# Run test command
python manage.py test_notifications --username=admin

# Check notifications in browser
http://localhost:8000/notifications/
```

### For Frontend Developers

#### Get Unread Count
```javascript
fetch('/notifications/api/unread-count/')
  .then(response => response.json())
  .then(data => console.log('Unread:', data.count));
```

#### Display Recent Notifications
```javascript
fetch('/notifications/api/recent/?limit=10')
  .then(response => response.json())
  .then(data => {
    data.notifications.forEach(notif => {
      console.log(notif.titre, notif.contenu);
    });
  });
```

## 📋 Notification Triggers

### User Actions
- ✅ User Registration → Welcome notification
- ✅ User Login → Login notification
- ✅ User Logout → Logout notification
- ✅ Profile Update → Profile updated notification
- ✅ Password Change → Security notification

### Vehicle Management
- ✅ Vehicle Added → Vehicle added notification
- ✅ Vehicle Updated → Vehicle updated notification
- ✅ Vehicle Deleted → Vehicle deleted notification

### Payment Operations
- ✅ Payment Initiated → Payment initiated notification
- ✅ Payment Success → Payment confirmation notification
- ✅ Payment Failed → Payment failed notification
- ✅ Payment Cancelled → Payment cancelled notification

### QR Code Operations
- ✅ QR Code Generated → QR generated notification
- ✅ QR Code Verified → Verification notification

### Admin Actions
- ✅ Account Activated → Account reactivated notification
- ✅ Account Deactivated → Account deactivated notification
- ✅ Admin Action → Admin action notification

## 🔧 Configuration

### Settings
Notification settings are configured in `settings.py`:
```python
# Notification settings
NOTIFICATION_RETENTION_DAYS = 90  # Days to keep read notifications
NOTIFICATION_POLL_INTERVAL = 30000  # Milliseconds (30 seconds)
```

### Language Support
The system supports:
- French (fr) - Default
- Malagasy (mg)

User's preferred language is stored in their profile.

## 🧪 Testing

### Manual Testing
1. Register a new user
2. Add a vehicle
3. Make a payment
4. Check notifications at `/notifications/`

### Automated Testing
```bash
# Run notification tests
python manage.py test notifications

# Test notification creation
python manage.py test_notifications --username=testuser
```

### API Testing
```bash
# Get unread count
curl http://localhost:8000/notifications/api/unread-count/

# Get recent notifications
curl http://localhost:8000/notifications/api/recent/?limit=5
```

## 📊 Database Schema

### Notification Model
```
notifications_notification
├── id (UUID, PK)
├── user_id (FK to auth_user)
├── type_notification (VARCHAR)
├── titre (VARCHAR)
├── contenu (TEXT)
├── langue (VARCHAR)
├── est_lue (BOOLEAN)
├── date_envoi (DATETIME)
├── date_lecture (DATETIME, nullable)
└── metadata (JSON)
```

### NotificationTemplate Model
```
notifications_notificationtemplate
├── id (INT, PK)
├── nom (VARCHAR)
├── type_template (VARCHAR)
├── langue (VARCHAR)
├── sujet (VARCHAR)
├── contenu_html (TEXT)
├── contenu_texte (TEXT)
├── variables_disponibles (JSON)
├── est_actif (BOOLEAN)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

## 🔐 Security

### Authentication
- All notification endpoints require authentication
- Users can only access their own notifications

### Authorization
- Proper queryset filtering: `Notification.objects.filter(user=request.user)`
- UUID-based notification IDs prevent enumeration

### Data Protection
- No sensitive data in notifications
- XSS protection via template escaping
- CSRF protection on all POST requests

## 🎯 Best Practices

### For Backend Developers
1. Always create notifications after successful operations
2. Use appropriate notification types
3. Include relevant metadata
4. Handle errors gracefully
5. Respect user's language preference

### For Frontend Developers
1. Poll unread count every 30-60 seconds
2. Use AJAX for mark-as-read operations
3. Display notifications in a dropdown/modal
4. Show unread count badge
5. Handle errors gracefully

### For Content Writers
1. Keep titles short and clear
2. Include relevant details in content
3. Use friendly, professional tone
4. Provide both French and Malagasy versions
5. Test readability

## 🐛 Troubleshooting

### Notifications Not Appearing
1. Check if signal handlers are registered
2. Verify user has correct permissions
3. Check database for notification records
4. Review application logs

### Wrong Language
1. Check user profile language setting
2. Verify language code (fr/mg)
3. Ensure translations exist

### Duplicate Notifications
1. Check for multiple signal handlers
2. Review view code for duplicate calls
3. Check for race conditions

## 📞 Support

### Getting Help
- Check documentation first
- Review code examples
- Test with management command
- Check application logs

### Reporting Issues
When reporting issues, include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages
- Screenshots (if applicable)

## 🔄 Future Enhancements

### Planned Features
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Push notifications
- [ ] WebSocket real-time updates
- [ ] Notification preferences UI
- [ ] Notification templates management
- [ ] Batch notifications for fleet managers
- [ ] Scheduled tax reminders
- [ ] Rich notifications with actions
- [ ] Notification analytics dashboard

### Roadmap
- **Phase 1** (Current): System notifications
- **Phase 2**: Email integration
- **Phase 3**: SMS integration
- **Phase 4**: Push notifications
- **Phase 5**: Advanced features

## 📝 Contributing

### Adding New Notification Types
1. Add method to `NotificationService` class
2. Update documentation
3. Add tests
4. Update this README

### Modifying Existing Notifications
1. Update service method
2. Update documentation
3. Update tests
4. Test both languages

## 📄 License

This documentation is part of the Tax Collection Platform project.

---

**Last Updated:** November 1, 2025  
**Version:** 1.0  
**Maintained By:** Development Team

## Quick Links
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - **Start here!**
- [Main Documentation](NOTIFICATION_SYSTEM.md)
- [Rules & Guidelines](NOTIFICATION_RULES.md)
- [API Documentation](NOTIFICATION_API.md)
- [Trigger Reference](NOTIFICATION_TRIGGERS.md)
