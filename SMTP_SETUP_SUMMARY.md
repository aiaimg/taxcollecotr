# SMTP Configuration - Setup Summary

## What Was Created

### 1. Database Models (`administration/models.py`)

**SMTPConfiguration Model:**
- Manages SMTP server settings (host, port, encryption, credentials)
- Supports multiple configurations (only one active at a time)
- Includes email limits and usage tracking
- Built-in connection testing
- Automatic daily counter reset

**EmailLog Model:**
- Tracks all emails sent through the system
- Records status (pending, sent, failed, bounced)
- Links to SMTP configuration used
- Stores error messages for debugging

### 2. Admin Interface (`administration/admin.py`)

**Features:**
- Full CRUD operations for SMTP configurations
- Visual status badges (Active/Inactive, Verified/Not Verified)
- Test button for each configuration
- Email log viewer with filtering
- Readonly fields for security

**Test Interface:**
- Connection testing
- Send test emails to any address
- Real-time feedback on success/failure

### 3. Email Utilities (`administration/email_utils.py`)

**Functions:**
- `send_email()` - Send simple emails
- `send_template_email()` - Send emails using Django templates
- `send_payment_reminder()` - Specialized payment reminder function
- `send_notification_email()` - Send notification emails
- `get_smtp_backend()` - Get configured SMTP settings

**Features:**
- Automatic SMTP configuration loading
- Daily limit enforcement
- Email logging
- Template rendering support
- Error handling

### 4. Email Templates

Created in `templates/emails/`:
- `payment_reminder_subject.txt` - Email subject
- `payment_reminder.txt` - Plain text version
- `payment_reminder.html` - HTML version (responsive design)

### 5. Management Command

**`python manage.py test_smtp <email>`**
- Test SMTP configuration from command line
- Send test emails
- Verify connection
- Useful for debugging

### 6. Integration with Notifications

Updated `notifications/services.py`:
- Added `send_email` parameter to `create_notification()`
- Automatic email sending when creating notifications
- Logging of email sending attempts

## Quick Start

### 1. Access Admin Panel

```
http://127.0.0.1:8000/admin/administration/smtpconfiguration/
```

### 2. Create SMTP Configuration

**For Gmail:**
```
Name: Gmail Production
Host: smtp.gmail.com
Port: 587
Encryption: TLS
Username: your-email@gmail.com
Password: your-app-password (not your Gmail password!)
From Email: your-email@gmail.com
From Name: Tax Collector
```

**Important for Gmail:**
1. Enable 2-Step Verification
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the app password in the configuration

### 3. Test Configuration

**Option 1: Admin Interface**
1. Click "Tester" button next to your configuration
2. Enter test email address
3. Click "Envoyer l'email de test"

**Option 2: Command Line**
```bash
python manage.py test_smtp your-email@example.com
```

### 4. Activate Configuration

1. Edit your SMTP configuration
2. Check "Configuration active"
3. Save

## Usage Examples

### Send Simple Email

```python
from administration.email_utils import send_email

success, message, logs = send_email(
    subject="Welcome to Tax Collector",
    message="Thank you for registering!",
    recipient_list=["user@example.com"],
    email_type="welcome"
)
```

### Send Template Email

```python
from administration.email_utils import send_template_email

success, message, logs = send_template_email(
    template_name='payment_reminder',
    context={
        'user': user,
        'vehicle': vehicle,
        'payment': payment,
    },
    recipient_list=[user.email],
    email_type='payment_reminder'
)
```

### Send Notification with Email

```python
from notifications.services import NotificationService

notification = NotificationService.create_notification(
    user=user,
    type_notification='system',
    titre='Payment Reminder',
    contenu='Your payment is due soon',
    send_email=True  # This will also send an email
)
```

### Use in Payment Reminders

```python
from administration.email_utils import send_payment_reminder

success, message, logs = send_payment_reminder(payment)
```

## Monitoring

### View Email Logs

```
http://127.0.0.1:8000/admin/administration/emaillog/
```

Filter by:
- Status (sent, failed, pending, bounced)
- Email type
- Date range
- Recipient

### Check SMTP Status

```
http://127.0.0.1:8000/admin/administration/smtpconfiguration/
```

Monitor:
- Emails sent today
- Daily limit
- Last test date
- Verification status

## Common SMTP Providers

### Gmail
- Host: `smtp.gmail.com`
- Port: `587` (TLS) or `465` (SSL)
- Requires App Password

### Office 365 / Outlook
- Host: `smtp.office365.com`
- Port: `587` (TLS)
- Use your Office 365 credentials

### SendGrid
- Host: `smtp.sendgrid.net`
- Port: `587` (TLS)
- Username: `apikey`
- Password: Your SendGrid API key

### Mailgun
- Host: `smtp.mailgun.org`
- Port: `587` (TLS)
- Find credentials in Mailgun dashboard

### Amazon SES
- Host: `email-smtp.region.amazonaws.com`
- Port: `587` (TLS)
- Use SMTP credentials from AWS console

## Troubleshooting

### "No active SMTP configuration found"
- Create an SMTP configuration in admin
- Check "Configuration active"
- Save the configuration

### "Authentication failed"
- Verify username and password
- For Gmail, use App Password
- Check if 2FA is required

### "Connection refused"
- Verify host and port
- Check firewall settings
- Try different encryption type

### "Daily limit reached"
- Wait until tomorrow (auto-resets)
- Increase daily limit in configuration
- Use different SMTP provider

### Emails not received
- Check spam folder
- Verify recipient email address
- Check email logs for errors
- Test with different email provider

## Security Best Practices

1. **Use App Passwords** - Never use your main account password
2. **Enable 2FA** - On your email account
3. **Limit Access** - Only admins should access SMTP settings
4. **Monitor Logs** - Regularly check email logs
5. **Set Limits** - Configure daily limits to prevent abuse
6. **Test Regularly** - Verify configuration works
7. **Backup Config** - Document your SMTP settings securely

## Next Steps

- [ ] Configure production SMTP provider
- [ ] Set up email templates for all notification types
- [ ] Configure SMS provider (coming soon)
- [ ] Set up email analytics
- [ ] Create scheduled email campaigns
- [ ] Implement email queue for bulk sending

## Support

For issues or questions:
1. Check `SMTP_CONFIGURATION_GUIDE.md` for detailed documentation
2. Review email logs in admin panel
3. Test configuration using management command
4. Check Django logs in `logs/` directory
