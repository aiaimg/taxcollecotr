"""
Notification service for creating and managing notifications
"""
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Notification, NotificationTemplate


class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def create_notification(user, type_notification, titre, contenu, langue='fr', metadata=None):
        """
        Create a notification for a user
        
        Args:
            user: User object
            type_notification: Type of notification (email, sms, push, system)
            titre: Notification title
            contenu: Notification content
            langue: Language (fr or mg)
            metadata: Additional metadata dict
        
        Returns:
            Notification object
        """
        if metadata is None:
            metadata = {}
        
        notification = Notification.objects.create(
            user=user,
            type_notification=type_notification,
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata=metadata
        )
        
        return notification
    
    @staticmethod
    def create_from_template(user, template_type, context=None, langue='fr'):
        """
        Create notification from template
        
        Args:
            user: User object
            template_type: Type of template (bienvenue, confirmation_paiement, etc.)
            context: Context variables for template rendering
            langue: Language (fr or mg)
        
        Returns:
            Notification object or None if template not found
        """
        if context is None:
            context = {}
        
        try:
            template = NotificationTemplate.objects.get(
                type_template=template_type,
                langue=langue,
                est_actif=True
            )
            
            rendered = template.render(context)
            
            notification = Notification.objects.create(
                user=user,
                type_notification='system',
                titre=rendered['sujet'],
                contenu=rendered['contenu_texte'],
                langue=langue,
                metadata={'template_type': template_type, 'context': context}
            )
            
            return notification
            
        except NotificationTemplate.DoesNotExist:
            # Fallback to default notification
            return None
    
    @staticmethod
    def create_welcome_notification(user, langue='fr'):
        """Create welcome notification for new user"""
        if langue == 'mg':
            titre = "Tonga soa eto amin'ny sehatra!"
            contenu = f"Tonga soa {user.get_full_name() or user.username}! Ny kaontinao dia voaforona soa aman-tsara. Afaka manomboka mampiasa ny sehatra ianao izao."
        else:
            titre = "Bienvenue sur la plateforme!"
            contenu = f"Bienvenue {user.get_full_name() or user.username}! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'user_registration'}
        )
    
    @staticmethod
    def create_vehicle_added_notification(user, vehicle, langue='fr'):
        """Create notification when vehicle is added"""
        if langue == 'mg':
            titre = "Fiara vaovao nampidirina"
            contenu = f"Ny fiara {vehicle.numero_plaque} dia nampidirina soa aman-tsara."
        else:
            titre = "Véhicule ajouté"
            contenu = f"Le véhicule {vehicle.numero_plaque} a été ajouté avec succès à votre compte."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'vehicle_added', 'vehicle_id': str(vehicle.id)}
        )
    
    @staticmethod
    def create_payment_confirmation_notification(user, payment, langue='fr'):
        """Create notification for payment confirmation"""
        if langue == 'mg':
            titre = "Fandoavam-bola vita soa aman-tsara"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {payment.vehicule.numero_plaque} dia vita soa aman-tsara. Vola naloa: {payment.montant_paye_ariary:,.0f} Ar"
        else:
            titre = "Paiement confirmé"
            contenu = f"Votre paiement pour le véhicule {payment.vehicule.numero_plaque} a été confirmé. Montant payé: {payment.montant_paye_ariary:,.0f} Ar"
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                'event': 'payment_confirmed',
                'payment_id': str(payment.id),
                'amount': str(payment.montant_paye_ariary)
            }
        )
    
    @staticmethod
    def create_payment_failed_notification(user, vehicle_plaque, langue='fr'):
        """Create notification for failed payment"""
        if langue == 'mg':
            titre = "Tsy nahomby ny fandoavam-bola"
            contenu = f"Tsy nahomby ny fandoavam-bola ho an'ny fiara {vehicle_plaque}. Andramo indray azafady."
        else:
            titre = "Échec du paiement"
            contenu = f"Le paiement pour le véhicule {vehicle_plaque} a échoué. Veuillez réessayer."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'payment_failed', 'vehicle_plaque': vehicle_plaque}
        )
    
    @staticmethod
    def create_qr_generated_notification(user, qr_code, langue='fr'):
        """Create notification when QR code is generated"""
        if langue == 'mg':
            titre = "QR code noforonina"
            contenu = f"Ny QR code ho an'ny fiara {qr_code.vehicule_plaque} dia noforonina soa aman-tsara."
        else:
            titre = "QR code généré"
            contenu = f"Le QR code pour le véhicule {qr_code.vehicule_plaque} a été généré avec succès."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                'event': 'qr_generated',
                'qr_code': qr_code.code,
                'vehicle_plaque': qr_code.vehicule_plaque
            }
        )
    
    @staticmethod
    def create_vehicle_updated_notification(user, vehicle, langue='fr'):
        """Create notification when vehicle is updated"""
        if langue == 'mg':
            titre = "Fiara nohavaozina"
            contenu = f"Ny fiara {vehicle.numero_plaque} dia nohavaozina soa aman-tsara."
        else:
            titre = "Véhicule modifié"
            contenu = f"Les informations du véhicule {vehicle.numero_plaque} ont été mises à jour avec succès."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'vehicle_updated', 'vehicle_id': str(vehicle.id)}
        )
    
    @staticmethod
    def create_vehicle_deleted_notification(user, vehicle_plaque, langue='fr'):
        """Create notification when vehicle is deleted"""
        if langue == 'mg':
            titre = "Fiara nesorina"
            contenu = f"Ny fiara {vehicle_plaque} dia nesorina tamin'ny kaontinao."
        else:
            titre = "Véhicule supprimé"
            contenu = f"Le véhicule {vehicle_plaque} a été supprimé de votre compte."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'vehicle_deleted', 'vehicle_plaque': vehicle_plaque}
        )
    
    @staticmethod
    def create_payment_updated_notification(user, payment, langue='fr'):
        """Create notification when payment is updated"""
        if langue == 'mg':
            titre = "Fandoavam-bola nohavaozina"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {payment.vehicule_plaque} dia nohavaozina."
        else:
            titre = "Paiement mis à jour"
            contenu = f"Le paiement pour le véhicule {payment.vehicule_plaque} a été mis à jour."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'payment_updated', 'payment_id': str(payment.id)}
        )
    
    @staticmethod
    def create_payment_cancelled_notification(user, vehicle_plaque, langue='fr'):
        """Create notification when payment is cancelled"""
        if langue == 'mg':
            titre = "Fandoavam-bola nofoanana"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {vehicle_plaque} dia nofoanana."
        else:
            titre = "Paiement annulé"
            contenu = f"Le paiement pour le véhicule {vehicle_plaque} a été annulé."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'payment_cancelled', 'vehicle_plaque': vehicle_plaque}
        )
    
    @staticmethod
    def create_profile_updated_notification(user, langue='fr'):
        """Create notification when user profile is updated"""
        if langue == 'mg':
            titre = "Mombamomba anao nohavaozina"
            contenu = "Ny mombamomba anao dia nohavaozina soa aman-tsara."
        else:
            titre = "Profil mis à jour"
            contenu = "Votre profil a été mis à jour avec succès."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'profile_updated'}
        )
    
    @staticmethod
    def create_password_changed_notification(user, langue='fr'):
        """Create notification when password is changed"""
        if langue == 'mg':
            titre = "Teny miafina novaina"
            contenu = "Ny teny miafinao dia novaina soa aman-tsara. Raha tsy ianao no nanao izany, mifandraisa amin'ny mpitantana avy hatrany."
        else:
            titre = "Mot de passe modifié"
            contenu = "Votre mot de passe a été modifié avec succès. Si ce n'était pas vous, contactez immédiatement l'administrateur."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'password_changed', 'security': True}
        )
    
    @staticmethod
    def create_account_deactivated_notification(user, langue='fr'):
        """Create notification when account is deactivated"""
        if langue == 'mg':
            titre = "Kaonty najanona"
            contenu = "Ny kaontinao dia najanona. Mifandraisa amin'ny mpitantana raha mila fanazavana."
        else:
            titre = "Compte désactivé"
            contenu = "Votre compte a été désactivé. Contactez l'administrateur pour plus d'informations."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'account_deactivated', 'security': True}
        )
    
    @staticmethod
    def create_account_reactivated_notification(user, langue='fr'):
        """Create notification when account is reactivated"""
        if langue == 'mg':
            titre = "Kaonty navaoina"
            contenu = "Ny kaontinao dia navaoina. Afaka mampiasa ny sehatra indray ianao."
        else:
            titre = "Compte réactivé"
            contenu = "Votre compte a été réactivé. Vous pouvez à nouveau utiliser la plateforme."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'account_reactivated'}
        )
    
    @staticmethod
    def create_tax_reminder_notification(user, vehicle, days_remaining, langue='fr'):
        """Create reminder notification for tax deadline"""
        if langue == 'mg':
            titre = "Fampahatsiahivana hetra"
            contenu = f"Misy {days_remaining} andro sisa alohan'ny ho tapitra ny fe-potoana handoavana ny hetra ho an'ny fiara {vehicle.numero_plaque}."
        else:
            titre = "Rappel de taxe"
            contenu = f"Il reste {days_remaining} jours avant l'échéance de paiement de la taxe pour le véhicule {vehicle.numero_plaque}."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                'event': 'tax_reminder',
                'vehicle_id': str(vehicle.id),
                'days_remaining': days_remaining
            }
        )
    
    @staticmethod
    def create_login_notification(user, langue='fr'):
        """Create notification when user logs in"""
        from django.utils import timezone
        now = timezone.now()
        
        if langue == 'mg':
            titre = "Niditra soa aman-tsara"
            contenu = f"Niditra tamin'ny kaontinao ianao tamin'ny {now.strftime('%d/%m/%Y')} tamin'ny {now.strftime('%H:%M')}."
        else:
            titre = "Connexion réussie"
            contenu = f"Vous vous êtes connecté avec succès le {now.strftime('%d/%m/%Y')} à {now.strftime('%H:%M')}."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'user_login', 'login_time': now.isoformat()}
        )
    
    @staticmethod
    def create_logout_notification(user, langue='fr'):
        """Create notification when user logs out"""
        from django.utils import timezone
        now = timezone.now()
        
        if langue == 'mg':
            titre = "Nivoaka"
            contenu = f"Nivoaka tamin'ny kaontinao ianao tamin'ny {now.strftime('%d/%m/%Y')} tamin'ny {now.strftime('%H:%M')}."
        else:
            titre = "Déconnexion"
            contenu = f"Vous vous êtes déconnecté le {now.strftime('%d/%m/%Y')} à {now.strftime('%H:%M')}."
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'user_logout', 'logout_time': now.isoformat()}
        )
    
    @staticmethod
    def create_admin_action_notification(user, action, details, langue='fr'):
        """Create notification for admin actions on user account"""
        if langue == 'mg':
            titre = f"Hetsika avy amin'ny mpitantana: {action}"
            contenu = f"Nisy hetsika natao tamin'ny kaontinao: {details}"
        else:
            titre = f"Action administrateur: {action}"
            contenu = f"Une action a été effectuée sur votre compte: {details}"
        
        return NotificationService.create_notification(
            user=user,
            type_notification='system',
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={'event': 'admin_action', 'action': action, 'details': details}
        )
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        unread_notifications = Notification.objects.filter(
            user=user,
            est_lue=False
        )
        
        for notification in unread_notifications:
            notification.marquer_comme_lue()
        
        return unread_notifications.count()
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(
            user=user,
            est_lue=False
        ).count()
    
    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for a user"""
        return Notification.objects.filter(
            user=user
        ).order_by('-date_envoi')[:limit]
