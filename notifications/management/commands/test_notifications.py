"""
Management command to test notification system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Test notification system by creating sample notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create notifications for',
            default='admin'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return
        
        # Create test notifications
        self.stdout.write('Creating test notifications...')
        
        # Welcome notification
        notif1 = NotificationService.create_welcome_notification(user, langue='fr')
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created welcome notification: {notif1.id}')
        )
        
        # System notification
        notif2 = NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre='Test de notification système',
            contenu='Ceci est un test de notification système. Tout fonctionne correctement!',
            langue='fr',
            metadata={'test': True}
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created system notification: {notif2.id}')
        )
        
        # Get unread count
        unread_count = NotificationService.get_unread_count(user)
        self.stdout.write(
            self.style.SUCCESS(f'\nUser has {unread_count} unread notifications')
        )
        
        # List recent notifications
        recent = NotificationService.get_recent_notifications(user, limit=5)
        self.stdout.write('\nRecent notifications:')
        for notif in recent:
            status = '✓ Read' if notif.est_lue else '✗ Unread'
            self.stdout.write(f'  [{status}] {notif.titre}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Notification system test completed successfully!')
        )
