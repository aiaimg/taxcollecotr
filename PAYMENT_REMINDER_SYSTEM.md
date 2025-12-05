# Payment Reminder System

## Overview

The payment reminder system automatically tracks vehicle tax payments and notifies users about:
- **Unpaid taxes** - Vehicles without payment for the current year
- **Expiring taxes** - Payments expiring within 30 days
- **Expired taxes** - Payments that have already expired

## Tax Validation Period

**Vehicle taxes are valid for ONE YEAR from the payment date.**

Example:
- Payment made: January 15, 2024
- Valid until: January 15, 2025
- Expiring soon warning: December 16, 2024 (30 days before)
- Expired: January 16, 2025

## Features

### 1. Dashboard Widget

Users see a prominent warning widget on their dashboard showing:
- 🔴 **Expired taxes** - Red alert with days overdue
- 🟡 **Expiring soon** - Yellow warning with days remaining
- 🔵 **Unpaid taxes** - Blue info for current year unpaid taxes

Each item has a direct "Pay Now" button.

### 2. Vehicle List Badges

Each vehicle card shows a status badge:
- ✅ **Payé** (Paid) - Green badge for valid payments
- ⏰ **Expire dans Xj** - Yellow badge showing days until expiry
- ❌ **Expiré** - Red badge for expired payments
- ⚠️ **Taxe à payer** - Yellow badge for unpaid taxes
- 🛡️ **Exonéré** - Blue badge for exempt vehicles

### 3. Automated Notifications

The system creates notifications for:
- Unpaid taxes
- Taxes expiring within 30 days
- Expired taxes

### 4. Management Command

Run the reminder system manually or via cron:

```bash
# Dry run (see what would be sent)
python manage.py send_payment_reminders --dry-run

# Actually send reminders
python manage.py send_payment_reminders
```

## Setup Automated Reminders

### Option 1: Cron Job (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_payment_reminders

# Run weekly on Monday at 9 AM
0 9 * * 1 cd /path/to/project && /path/to/venv/bin/python manage.py send_payment_reminders
```

### Option 2: Django-Cron

Install django-cron:
```bash
pip install django-cron
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'django_cron',
]
```

Create `core/cron.py`:
```python
from django_cron import CronJobBase, Schedule

class SendPaymentRemindersCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # Run once per day
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.send_payment_reminders'
    
    def do(self):
        from django.core.management import call_command
        call_command('send_payment_reminders')
```

Run cron jobs:
```bash
python manage.py runcrons
```

### Option 3: Celery (Recommended for Production)

Install celery:
```bash
pip install celery redis
```

Create `core/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def send_payment_reminders():
    call_command('send_payment_reminders')
```

Add to celery beat schedule:
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-payment-reminders-daily': {
        'task': 'core.tasks.send_payment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

## API Methods

### Vehicle Model Methods

```python
# Get payment status for a vehicle
status_info = vehicle.get_current_payment_status()
# Returns: {
#     'status': 'valid|unpaid|expiring_soon|expired|exempt',
#     'payment': PaiementTaxe object or None,
#     'days_until_expiry': int or None,
#     'is_expired': bool,
#     'expiry_date': date or None
# }

# Check if vehicle needs reminder
needs_reminder = vehicle.needs_payment_reminder()  # Returns bool

# Get HTML badge for status
badge_html = vehicle.get_payment_status_badge()
```

### Notification Service Methods

```python
from notifications.services import NotificationService

# Send payment reminder
NotificationService.create_payment_reminder_notification(
    user=user,
    vehicle=vehicle,
    reminder_type='unpaid',  # or 'expiring' or 'expired'
    days_remaining=15,  # for 'expiring' type
    expiry_date=date(2025, 1, 15),
    langue='fr'  # or 'mg'
)
```

## Reminder Types

### 1. Unpaid Tax
- **When**: No payment for current year
- **Message (FR)**: "La taxe pour votre véhicule {plaque} n'a pas encore été payée."
- **Message (MG)**: "Tsy mbola voaloa ny hetra ho an'ny fiara {plaque}."

### 2. Expiring Soon
- **When**: Payment expires within 30 days
- **Message (FR)**: "La taxe pour votre véhicule {plaque} expire dans {X} jours."
- **Message (MG)**: "Ny hetra ho an'ny fiara {plaque} dia ho lany andro afaka {X} andro."

### 3. Expired
- **When**: Payment has expired
- **Message (FR)**: "La taxe pour votre véhicule {plaque} a expiré."
- **Message (MG)**: "Ny hetra ho an'ny fiara {plaque} dia efa lany andro."

## Testing

### Test the reminder system:

```bash
# Create test vehicles with different payment statuses
python manage.py shell

from vehicles.models import Vehicule
from payments.models import PaiementTaxe
from datetime import date, timedelta

# Get a vehicle
vehicle = Vehicule.objects.first()

# Check its status
status = vehicle.get_current_payment_status()
print(f"Status: {status['status']}")
print(f"Days until expiry: {status['days_until_expiry']}")

# Test reminder command
python manage.py send_payment_reminders --dry-run
```

## Dashboard Integration

The payment reminders widget is automatically shown on the dashboard for regular users (not admins).

Location: `templates/partials/payment_reminders_widget.html`

The widget shows:
- Count of vehicles in each status
- List of vehicles with direct payment links
- Color-coded alerts (red for expired, yellow for expiring, blue for unpaid)

## Customization

### Change Expiry Warning Period

Edit `vehicles/models.py`:

```python
# Change from 30 days to 60 days
elif days_until_expiry <= 60:  # Was 30
    status = 'expiring_soon'
```

### Change Notification Messages

Edit `notifications/services.py` in the `create_payment_reminder_notification` method.

### Customize Dashboard Widget

Edit `templates/partials/payment_reminders_widget.html` to change:
- Colors
- Layout
- Button text
- Alert styling

## Monitoring

Check reminder statistics:

```bash
# Run with dry-run to see counts
python manage.py send_payment_reminders --dry-run
```

Output shows:
- Total vehicles checked
- Unpaid taxes count
- Expiring soon count
- Expired count

## Best Practices

1. **Run reminders daily** - Ensures users get timely notifications
2. **Test before deploying** - Use --dry-run flag first
3. **Monitor logs** - Check for any errors in notification creation
4. **Adjust timing** - Run reminders at a time when users are likely to see them
5. **Multilingual** - System supports French (fr) and Malagasy (mg)

## Troubleshooting

### Reminders not showing on dashboard?
- Check that user is not an admin (admins don't see reminders)
- Verify vehicles exist for the user
- Check payment status with `vehicle.get_current_payment_status()`

### Command not sending notifications?
- Run with --dry-run to see what would be sent
- Check notification service is working
- Verify user has preferred language set

### Wrong expiry dates?
- Verify payment dates are correct
- Check timezone settings
- Ensure payment status is 'PAYE' (paid)

## Future Enhancements

- [ ] Email notifications for reminders
- [ ] SMS notifications via Twilio/similar
- [ ] Push notifications for mobile app
- [ ] Configurable reminder schedules per user
- [ ] Grace period before penalties
- [ ] Automatic payment renewal option
