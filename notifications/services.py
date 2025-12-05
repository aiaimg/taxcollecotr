"""
Notification service for creating and managing notifications
"""

import logging

from django.contrib.auth.models import User
from django.utils import timezone

from .models import Notification, NotificationTemplate

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and managing notifications"""

    @staticmethod
    def create_notification(user, type_notification, titre, contenu, langue="fr", metadata=None, send_email=False):
        """
        Create a notification for a user

        Args:
            user: User object
            type_notification: Type of notification (email, sms, push, system)
            titre: Notification title
            contenu: Notification content
            langue: Language (fr or mg)
            metadata: Additional metadata dict
            send_email: If True, also send email notification

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
            metadata=metadata,
        )

        # Send email if requested and user has email
        if send_email and user.email:
            try:
                from administration.email_utils import send_email as send_smtp_email

                success, message, logs = send_smtp_email(
                    subject=titre,
                    message=contenu,
                    recipient_list=[user.email],
                    email_type="notification",
                    related_object_type="Notification",
                    related_object_id=notification.id,
                    fail_silently=True,
                )

                if success:
                    logger.info(f"Email notification sent to {user.email}: {titre}")
                else:
                    logger.warning(f"Failed to send email notification to {user.email}: {message}")

            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")

        return notification

    @staticmethod
    def create_from_template(user, template_type, context=None, langue="fr"):
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
            template = NotificationTemplate.objects.get(type_template=template_type, langue=langue, est_actif=True)

            rendered = template.render(context)

            notification = Notification.objects.create(
                user=user,
                type_notification="system",
                titre=rendered["sujet"],
                contenu=rendered["contenu_texte"],
                langue=langue,
                metadata={"template_type": template_type, "context": context},
            )

            return notification

        except NotificationTemplate.DoesNotExist:
            # Fallback to default notification
            return None

    @staticmethod
    def create_welcome_notification(user, langue="fr"):
        """Create welcome notification for new user"""
        if langue == "mg":
            titre = "Tonga soa eto amin'ny sehatra!"
            contenu = f"Tonga soa {user.get_full_name() or user.username}! Ny kaontinao dia voaforona soa aman-tsara. Afaka manomboka mampiasa ny sehatra ianao izao."
        else:
            titre = "Bienvenue sur la plateforme!"
            contenu = f"Bienvenue {user.get_full_name() or user.username}! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "user_registration"},
        )

    @staticmethod
    def create_vehicle_added_notification(user, vehicle, langue="fr"):
        """
        Create notification when vehicle is added

        Args:
            user: User object
            vehicle: Vehicule instance
            langue: Language (fr or mg)

        Returns:
            Notification object
        """
        # Detect vehicle category
        vehicle_category = getattr(vehicle, "vehicle_category", "TERRESTRE")

        # Get vehicle identifier based on category
        if vehicle_category == "AERIEN":
            vehicle_id = vehicle.immatriculation_aerienne or vehicle.plaque_immatriculation
        elif vehicle_category == "MARITIME":
            vehicle_id = vehicle.nom_navire or vehicle.numero_francisation or vehicle.plaque_immatriculation
        else:
            vehicle_id = vehicle.plaque_immatriculation

        # Calculate tax amount
        tax_amount = None
        try:
            from vehicles.services import TaxCalculationService

            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicle)
            if tax_info and not tax_info.get("error"):
                tax_amount = tax_info.get("amount")
        except Exception as e:
            logger.warning(f"Could not calculate tax for vehicle notification: {e}")

        # Build notification content based on category
        if vehicle_category == "AERIEN":
            if langue == "mg":
                titre = "Fiaramanidina vaovao nampidirina"
                contenu = f"Ny fiaramanidina {vehicle_id} dia nampidirina soa aman-tsara amin'ny kaontinao."
                if tax_amount:
                    contenu += f"\n\nHetra azo ampiharina: {tax_amount:,.0f} Ar/taona."
            else:
                titre = "Aéronef ajouté"
                contenu = f"L'aéronef {vehicle_id} a été ajouté avec succès à votre compte."
                if tax_amount:
                    contenu += f"\n\nTaxe applicable: {tax_amount:,.0f} Ar/an."

        elif vehicle_category == "MARITIME":
            # Get maritime classification if available
            maritime_classification = None
            if hasattr(vehicle, "specifications_techniques") and vehicle.specifications_techniques:
                maritime_classification = vehicle.specifications_techniques.get("maritime_classification")

            if langue == "mg":
                titre = "Sambo vaovao nampidirina"
                contenu = f"Ny sambo {vehicle_id} dia nampidirina soa aman-tsara amin'ny kaontinao."

                if maritime_classification:
                    classification_names = {
                        "NAVIRE_PLAISANCE": "Sambo fialam-boly (≥7m na ≥22CV/90kW)",
                        "JETSKI": "Jet-ski/Moto an-dranomasina (≥90kW)",
                        "AUTRES_ENGINS": "Fitaovana hafa an-dranomasina misy motera",
                    }
                    classification_display = classification_names.get(maritime_classification, maritime_classification)
                    contenu += f"\n\nFanasokajiana: {classification_display}"

                if tax_amount:
                    contenu += f"\nHetra azo ampiharina: {tax_amount:,.0f} Ar/taona."
            else:
                titre = "Navire ajouté"
                contenu = f"Le navire {vehicle_id} a été ajouté avec succès à votre compte."

                if maritime_classification:
                    classification_names = {
                        "NAVIRE_PLAISANCE": "Navire de plaisance (≥7m ou ≥22CV/90kW)",
                        "JETSKI": "Jet-ski/Moto nautique (≥90kW)",
                        "AUTRES_ENGINS": "Autres engins maritimes motorisés",
                    }
                    classification_display = classification_names.get(maritime_classification, maritime_classification)
                    contenu += f"\n\nClassification: {classification_display}"

                if tax_amount:
                    contenu += f"\nTaxe applicable: {tax_amount:,.0f} Ar/an."

        else:  # TERRESTRE
            if langue == "mg":
                titre = "Fiara vaovao nampidirina"
                contenu = f"Ny fiara {vehicle_id} dia nampidirina soa aman-tsara amin'ny kaontinao."
                if tax_amount:
                    contenu += f"\n\nHetra azo ampiharina: {tax_amount:,.0f} Ar/taona."
            else:
                titre = "Véhicule ajouté"
                contenu = f"Le véhicule {vehicle_id} a été ajouté avec succès à votre compte."
                if tax_amount:
                    contenu += f"\n\nTaxe applicable: {tax_amount:,.0f} Ar/an."

        # Build metadata
        metadata = {
            "event": "vehicle_added",
            "vehicle_id": str(vehicle.pk),
            "vehicle_category": vehicle_category,
            "vehicle_identifier": vehicle_id,
        }

        if tax_amount:
            metadata["tax_amount"] = str(tax_amount)

        if vehicle_category == "MARITIME" and maritime_classification:
            metadata["maritime_classification"] = maritime_classification

        # Create the notification
        notification = NotificationService.create_notification(
            user=user, type_notification="system", titre=titre, contenu=contenu, langue=langue, metadata=metadata
        )

        # Send email with appropriate template
        if user.email:
            try:
                from django.conf import settings
                from django.template.loader import render_to_string

                from administration.email_utils import send_email as send_smtp_email

                # Determine template based on category
                if vehicle_category == "AERIEN":
                    html_template = "emails/vehicle_added_aerial.html"
                    text_template = "emails/vehicle_added_aerial.txt"
                    subject_template = "emails/vehicle_added_aerial_subject.txt"
                elif vehicle_category == "MARITIME":
                    html_template = "emails/vehicle_added_maritime.html"
                    text_template = "emails/vehicle_added_maritime.txt"
                    subject_template = "emails/vehicle_added_maritime_subject.txt"
                else:
                    # For terrestrial vehicles, use simple email
                    html_template = None
                    text_template = None
                    subject_template = None

                # Render email if templates exist
                if html_template:
                    context = {
                        "user": user,
                        "vehicle": vehicle,
                        "tax_amount": tax_amount,
                        "site_url": getattr(settings, "SITE_URL", "http://localhost:8000"),
                    }

                    # Add maritime-specific context
                    if vehicle_category == "MARITIME" and maritime_classification:
                        classification_names = {
                            "NAVIRE_PLAISANCE": "Navire de plaisance (≥7m ou ≥22CV/90kW)",
                            "JETSKI": "Jet-ski/Moto nautique (≥90kW)",
                            "AUTRES_ENGINS": "Autres engins maritimes motorisés",
                        }
                        context["maritime_classification"] = maritime_classification
                        context["maritime_classification_display"] = classification_names.get(
                            maritime_classification, maritime_classification
                        )

                    subject = render_to_string(subject_template, context).strip()
                    html_message = render_to_string(html_template, context)
                    text_message = render_to_string(text_template, context)

                    success, message, logs = send_smtp_email(
                        subject=subject,
                        message=text_message,
                        recipient_list=[user.email],
                        html_message=html_message,
                        email_type="notification",
                        related_object_type="Notification",
                        related_object_id=notification.id,
                        fail_silently=True,
                    )

                    if success:
                        logger.info(f"Vehicle added email sent to {user.email}: {subject}")
                    else:
                        logger.warning(f"Failed to send vehicle added email to {user.email}: {message}")
                else:
                    # Fallback to simple email for terrestrial vehicles
                    success, message, logs = send_smtp_email(
                        subject=titre,
                        message=contenu,
                        recipient_list=[user.email],
                        email_type="notification",
                        related_object_type="Notification",
                        related_object_id=notification.id,
                        fail_silently=True,
                    )

            except Exception as e:
                logger.error(f"Error sending vehicle added email: {str(e)}")

        return notification

    @staticmethod
    def create_payment_confirmation_notification(user, payment, langue="fr"):
        """Create notification for payment confirmation"""
        if langue == "mg":
            titre = "Fandoavam-bola vita soa aman-tsara"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {payment.vehicule.numero_plaque} dia vita soa aman-tsara. Vola naloa: {payment.montant_paye_ariary:,.0f} Ar"
        else:
            titre = "Paiement confirmé"
            contenu = f"Votre paiement pour le véhicule {payment.vehicule.numero_plaque} a été confirmé. Montant payé: {payment.montant_paye_ariary:,.0f} Ar"

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "payment_confirmed",
                "payment_id": str(payment.id),
                "amount": str(payment.montant_paye_ariary),
            },
        )

    @staticmethod
    def create_payment_failed_notification(user, vehicle_plaque, langue="fr"):
        """Create notification for failed payment"""
        if langue == "mg":
            titre = "Tsy nahomby ny fandoavam-bola"
            contenu = f"Tsy nahomby ny fandoavam-bola ho an'ny fiara {vehicle_plaque}. Andramo indray azafady."
        else:
            titre = "Échec du paiement"
            contenu = f"Le paiement pour le véhicule {vehicle_plaque} a échoué. Veuillez réessayer."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "payment_failed", "vehicle_plaque": vehicle_plaque},
        )

    @staticmethod
    def create_qr_generated_notification(user, qr_code, langue="fr"):
        """Create notification when QR code is generated"""
        if langue == "mg":
            titre = "QR code noforonina"
            contenu = f"Ny QR code ho an'ny fiara {qr_code.vehicule_plaque} dia noforonina soa aman-tsara."
        else:
            titre = "QR code généré"
            contenu = f"Le QR code pour le véhicule {qr_code.vehicule_plaque} a été généré avec succès."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "qr_generated", "qr_code": qr_code.code, "vehicle_plaque": qr_code.vehicule_plaque},
        )

    @staticmethod
    def create_vehicle_updated_notification(user, vehicle, langue="fr"):
        """Create notification when vehicle is updated"""
        if langue == "mg":
            titre = "Fiara nohavaozina"
            contenu = f"Ny fiara {vehicle.numero_plaque} dia nohavaozina soa aman-tsara."
        else:
            titre = "Véhicule modifié"
            contenu = f"Les informations du véhicule {vehicle.numero_plaque} ont été mises à jour avec succès."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "vehicle_updated", "vehicle_id": str(vehicle.id)},
        )

    @staticmethod
    def create_vehicle_deleted_notification(user, vehicle_plaque, langue="fr"):
        """Create notification when vehicle is deleted"""
        if langue == "mg":
            titre = "Fiara nesorina"
            contenu = f"Ny fiara {vehicle_plaque} dia nesorina tamin'ny kaontinao."
        else:
            titre = "Véhicule supprimé"
            contenu = f"Le véhicule {vehicle_plaque} a été supprimé de votre compte."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "vehicle_deleted", "vehicle_plaque": vehicle_plaque},
        )

    @staticmethod
    def create_payment_updated_notification(user, payment, langue="fr"):
        """Create notification when payment is updated"""
        if langue == "mg":
            titre = "Fandoavam-bola nohavaozina"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {payment.vehicule_plaque} dia nohavaozina."
        else:
            titre = "Paiement mis à jour"
            contenu = f"Le paiement pour le véhicule {payment.vehicule_plaque} a été mis à jour."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "payment_updated", "payment_id": str(payment.id)},
        )

    @staticmethod
    def create_payment_cancelled_notification(user, vehicle_plaque, langue="fr"):
        """Create notification when payment is cancelled"""
        if langue == "mg":
            titre = "Fandoavam-bola nofoanana"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {vehicle_plaque} dia nofoanana."
        else:
            titre = "Paiement annulé"
            contenu = f"Le paiement pour le véhicule {vehicle_plaque} a été annulé."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "payment_cancelled", "vehicle_plaque": vehicle_plaque},
        )

    @staticmethod
    def create_payment_reminder_notification(
        user, vehicle, reminder_type="unpaid", days_remaining=None, expiry_date=None, langue="fr"
    ):
        """
        Create payment reminder notification

        Args:
            user: User object
            vehicle: Vehicle object
            reminder_type: 'unpaid', 'expiring', or 'expired'
            days_remaining: Days until expiry (for 'expiring' type)
            expiry_date: Date when payment expires
            langue: Language (fr or mg)
        """
        plaque = vehicle.plaque_immatriculation

        if reminder_type == "unpaid":
            if langue == "mg":
                titre = f"Hetra tsy voaloa - {plaque}"
                contenu = f"Tsy mbola voaloa ny hetra ho an'ny fiara {plaque}. Alefaso izao mba hialana amin'ny sazy."
            else:
                titre = f"Taxe impayée - {plaque}"
                contenu = f"La taxe pour votre véhicule {plaque} n'a pas encore été payée. Veuillez effectuer le paiement pour éviter les pénalités."

        elif reminder_type == "expiring":
            if langue == "mg":
                titre = f"Hetra ho lany andro - {plaque}"
                contenu = (
                    f"Ny hetra ho an'ny fiara {plaque} dia ho lany andro afaka {days_remaining} andro. Alefaso izao."
                )
            else:
                titre = f"Taxe expire bientôt - {plaque}"
                contenu = f"La taxe pour votre véhicule {plaque} expire dans {days_remaining} jours. Renouvelez votre paiement dès maintenant."

        elif reminder_type == "expired":
            if langue == "mg":
                titre = f"Hetra lany andro - {plaque}"
                contenu = (
                    f"Ny hetra ho an'ny fiara {plaque} dia efa lany andro. Alefaso haingana mba hialana amin'ny sazy."
                )
            else:
                titre = f"Taxe expirée - {plaque}"
                contenu = f"La taxe pour votre véhicule {plaque} a expiré. Veuillez renouveler votre paiement immédiatement pour éviter les pénalités."

        metadata = {
            "event": "payment_reminder",
            "reminder_type": reminder_type,
            "vehicle_plaque": plaque,
            "vehicle_id": str(vehicle.pk),
        }

        if days_remaining is not None:
            metadata["days_remaining"] = days_remaining

        if expiry_date:
            metadata["expiry_date"] = expiry_date.isoformat()

        return NotificationService.create_notification(
            user=user, type_notification="system", titre=titre, contenu=contenu, langue=langue, metadata=metadata
        )

    @staticmethod
    def create_profile_updated_notification(user, langue="fr"):
        """Create notification when user profile is updated"""
        if langue == "mg":
            titre = "Mombamomba anao nohavaozina"
            contenu = "Ny mombamomba anao dia nohavaozina soa aman-tsara."
        else:
            titre = "Profil mis à jour"
            contenu = "Votre profil a été mis à jour avec succès."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "profile_updated"},
        )

    @staticmethod
    def create_password_changed_notification(user, langue="fr"):
        """Create notification when password is changed"""
        if langue == "mg":
            titre = "Teny miafina novaina"
            contenu = "Ny teny miafinao dia novaina soa aman-tsara. Raha tsy ianao no nanao izany, mifandraisa amin'ny mpitantana avy hatrany."
        else:
            titre = "Mot de passe modifié"
            contenu = "Votre mot de passe a été modifié avec succès. Si ce n'était pas vous, contactez immédiatement l'administrateur."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "password_changed", "security": True},
        )

    @staticmethod
    def create_account_deactivated_notification(user, langue="fr"):
        """Create notification when account is deactivated"""
        if langue == "mg":
            titre = "Kaonty najanona"
            contenu = "Ny kaontinao dia najanona. Mifandraisa amin'ny mpitantana raha mila fanazavana."
        else:
            titre = "Compte désactivé"
            contenu = "Votre compte a été désactivé. Contactez l'administrateur pour plus d'informations."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "account_deactivated", "security": True},
        )

    @staticmethod
    def create_account_reactivated_notification(user, langue="fr"):
        """Create notification when account is reactivated"""
        if langue == "mg":
            titre = "Kaonty navaoina"
            contenu = "Ny kaontinao dia navaoina. Afaka mampiasa ny sehatra indray ianao."
        else:
            titre = "Compte réactivé"
            contenu = "Votre compte a été réactivé. Vous pouvez à nouveau utiliser la plateforme."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "account_reactivated"},
        )

    @staticmethod
    def create_tax_reminder_notification(user, vehicle, days_remaining, langue="fr"):
        """Create reminder notification for tax deadline"""
        if langue == "mg":
            titre = "Fampahatsiahivana hetra"
            contenu = f"Misy {days_remaining} andro sisa alohan'ny ho tapitra ny fe-potoana handoavana ny hetra ho an'ny fiara {vehicle.numero_plaque}."
        else:
            titre = "Rappel de taxe"
            contenu = f"Il reste {days_remaining} jours avant l'échéance de paiement de la taxe pour le véhicule {vehicle.numero_plaque}."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "tax_reminder", "vehicle_id": str(vehicle.id), "days_remaining": days_remaining},
        )

    @staticmethod
    def create_login_notification(user, langue="fr"):
        """Create notification when user logs in"""
        from django.utils import timezone

        now = timezone.now()

        if langue == "mg":
            titre = "Niditra soa aman-tsara"
            contenu = f"Niditra tamin'ny kaontinao ianao tamin'ny {now.strftime('%d/%m/%Y')} tamin'ny {now.strftime('%H:%M')}."
        else:
            titre = "Connexion réussie"
            contenu = f"Vous vous êtes connecté avec succès le {now.strftime('%d/%m/%Y')} à {now.strftime('%H:%M')}."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "user_login", "login_time": now.isoformat()},
        )

    @staticmethod
    def create_logout_notification(user, langue="fr"):
        """Create notification when user logs out"""
        from django.utils import timezone

        now = timezone.now()

        if langue == "mg":
            titre = "Nivoaka"
            contenu = f"Nivoaka tamin'ny kaontinao ianao tamin'ny {now.strftime('%d/%m/%Y')} tamin'ny {now.strftime('%H:%M')}."
        else:
            titre = "Déconnexion"
            contenu = f"Vous vous êtes déconnecté le {now.strftime('%d/%m/%Y')} à {now.strftime('%H:%M')}."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "user_logout", "logout_time": now.isoformat()},
        )

    @staticmethod
    def create_admin_action_notification(user, action, details, langue="fr"):
        """Create notification for admin actions on user account"""
        if langue == "mg":
            titre = f"Hetsika avy amin'ny mpitantana: {action}"
            contenu = f"Nisy hetsika natao tamin'ny kaontinao: {details}"
        else:
            titre = f"Action administrateur: {action}"
            contenu = f"Une action a été effectuée sur votre compte: {details}"

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={"event": "admin_action", "action": action, "details": details},
        )

    # ============================================================================
    # CASH PAYMENT SYSTEM NOTIFICATIONS
    # ============================================================================

    @staticmethod
    def create_cash_payment_notification(user, payment, collector, langue="fr"):
        """Create notification when cash payment is completed"""
        vehicle_plate = (
            payment.vehicule_plaque.plaque_immatriculation
            if hasattr(payment.vehicule_plaque, "plaque_immatriculation")
            else str(payment.vehicule_plaque)
        )

        if langue == "mg":
            titre = "Fandoavam-bola amin'ny vola maivana vita"
            contenu = f"Ny fandoavam-bola ho an'ny fiara {vehicle_plate} dia vita soa aman-tsara. Vola naloa: {payment.montant_paye_ariary:,.0f} Ar. Nangonina tamin'ny alalan'i {collector.full_name}."
        else:
            titre = "Paiement en espèces confirmé"
            contenu = f"Votre paiement en espèces pour le véhicule {vehicle_plate} a été confirmé. Montant payé: {payment.montant_paye_ariary:,.0f} Ar. Collecté par {collector.full_name}."

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_payment_completed",
                "payment_id": str(payment.id),
                "amount": str(payment.montant_paye_ariary),
                "collector_id": collector.agent_id,
                "collector_name": collector.full_name,
            },
            send_email=True,
        )

    @staticmethod
    def create_cash_approval_required_notification(admin_user, transaction, langue="fr"):
        """Create notification when cash transaction requires approval"""
        if langue == "mg":
            titre = "Fankatoavana takiana ho an'ny fandoavam-bola"
            contenu = f"Mila fankatoavana ny fandoavam-bola {transaction.transaction_number} ho an'ny {transaction.customer_name}. Vola: {transaction.tax_amount:,.0f} Ar."
        else:
            titre = "Approbation requise pour paiement"
            contenu = f"Le paiement {transaction.transaction_number} pour {transaction.customer_name} nécessite votre approbation. Montant: {transaction.tax_amount:,.0f} Ar."

        return NotificationService.create_notification(
            user=admin_user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_approval_required",
                "transaction_id": str(transaction.id),
                "transaction_number": transaction.transaction_number,
                "amount": str(transaction.tax_amount),
                "customer_name": transaction.customer_name,
                "collector_id": transaction.collector.agent_id,
            },
            send_email=True,
        )

    @staticmethod
    def create_cash_session_closed_notification(collector_user, session, langue="fr"):
        """Create notification when cash session is closed"""
        if langue == "mg":
            titre = "Fotoana fanangonana vola nakatona"
            contenu = f"Ny fotoana fanangonana {session.session_number} dia nakatona. Vola nangonina: {session.expected_balance:,.0f} Ar. Komisiona: {session.total_commission:,.0f} Ar."
        else:
            titre = "Session de collecte fermée"
            contenu = f"La session {session.session_number} a été fermée. Montant collecté: {session.expected_balance:,.0f} Ar. Commission: {session.total_commission:,.0f} Ar."

        # Add discrepancy warning if exists
        if session.discrepancy_amount and abs(session.discrepancy_amount) > 0:
            if langue == "mg":
                contenu += f" Misy tsy fitoviana: {session.discrepancy_amount:,.0f} Ar."
            else:
                contenu += f" Écart constaté: {session.discrepancy_amount:,.0f} Ar."

        return NotificationService.create_notification(
            user=collector_user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_session_closed",
                "session_id": str(session.id),
                "session_number": session.session_number,
                "expected_balance": str(session.expected_balance),
                "closing_balance": str(session.closing_balance) if session.closing_balance else None,
                "discrepancy": str(session.discrepancy_amount),
                "commission": str(session.total_commission),
            },
        )

    @staticmethod
    def create_cash_transaction_approved_notification(collector_user, transaction, langue="fr"):
        """Create notification when transaction is approved"""
        if langue == "mg":
            titre = "Fandoavam-bola nekena"
            contenu = f"Ny fandoavam-bola {transaction.transaction_number} dia nekena. Afaka manomboka ny fandoavam-bola ianao."
        else:
            titre = "Transaction approuvée"
            contenu = (
                f"La transaction {transaction.transaction_number} a été approuvée. Vous pouvez procéder au paiement."
            )

        return NotificationService.create_notification(
            user=collector_user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_transaction_approved",
                "transaction_id": str(transaction.id),
                "transaction_number": transaction.transaction_number,
                "amount": str(transaction.tax_amount),
            },
        )

    @staticmethod
    def create_cash_transaction_rejected_notification(collector_user, transaction, reason, langue="fr"):
        """Create notification when transaction is rejected"""
        if langue == "mg":
            titre = "Fandoavam-bola nolavina"
            contenu = f"Ny fandoavam-bola {transaction.transaction_number} dia nolavina. Antony: {reason}"
        else:
            titre = "Transaction rejetée"
            contenu = f"La transaction {transaction.transaction_number} a été rejetée. Raison: {reason}"

        return NotificationService.create_notification(
            user=collector_user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_transaction_rejected",
                "transaction_id": str(transaction.id),
                "transaction_number": transaction.transaction_number,
                "reason": reason,
            },
        )

    @staticmethod
    def create_cash_discrepancy_alert_notification(admin_user, session, langue="fr"):
        """Create notification for admin when session has discrepancy"""
        if langue == "mg":
            titre = "Fampitandremana: Tsy fitoviana amin'ny vola"
            contenu = f"Misy tsy fitoviana amin'ny fotoana {session.session_number} avy amin'i {session.collector.full_name}. Tsy fitoviana: {session.discrepancy_amount:,.0f} Ar."
        else:
            titre = "Alerte: Écart de caisse"
            contenu = f"Un écart a été détecté dans la session {session.session_number} de {session.collector.full_name}. Écart: {session.discrepancy_amount:,.0f} Ar."

        return NotificationService.create_notification(
            user=admin_user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "cash_discrepancy_alert",
                "session_id": str(session.id),
                "session_number": session.session_number,
                "collector_id": session.collector.agent_id,
                "collector_name": session.collector.full_name,
                "discrepancy": str(session.discrepancy_amount),
                "expected": str(session.expected_balance),
                "actual": str(session.closing_balance) if session.closing_balance else None,
            },
            send_email=True,
        )

    # ============================================================================
    # CONTRAVENTION SYSTEM NOTIFICATIONS
    # ============================================================================

    @staticmethod
    def creer_notification(utilisateur, titre, message, type_notification="system", lien=None, metadata=None):
        """
        Créer une notification pour un utilisateur.

        Args:
            utilisateur: User object
            titre: str, titre de la notification
            message: str, contenu de la notification
            type_notification: str, type de notification (default: 'system')
            lien: str, lien optionnel
            metadata: dict, métadonnées additionnelles

        Returns:
            Notification object
        """
        if metadata is None:
            metadata = {}

        # Déterminer la langue de l'utilisateur (par défaut français)
        langue = "fr"
        if hasattr(utilisateur, "profile") and hasattr(utilisateur.profile, "langue_preferee"):
            langue = utilisateur.profile.langue_preferee

        notification = Notification.objects.create(
            user=utilisateur,
            type_notification=type_notification,
            titre=titre,
            contenu=message,
            langue=langue,
            metadata=metadata,
        )

        return notification

    @staticmethod
    def create_contravention_notification(user, contravention, langue="fr"):
        """Create notification when contravention is issued"""
        if langue == "mg":
            titre = "Famaizana vaovao"
            contenu = (
                f"Nisy famaizana natao tamin'ny fiara {contravention.get_vehicle_display()}. "
                f"Vola: {contravention.montant_amende_ariary:,.0f} Ar. "
                f"Laharana PV: {contravention.numero_pv}"
            )
        else:
            titre = "Nouvelle contravention"
            contenu = (
                f"Une contravention a été émise pour votre véhicule {contravention.get_vehicle_display()}. "
                f"Montant: {contravention.montant_amende_ariary:,.0f} Ar. "
                f"Numéro PV: {contravention.numero_pv}"
            )

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "contravention_issued",
                "contravention_id": str(contravention.id),
                "numero_pv": contravention.numero_pv,
                "montant": str(contravention.montant_amende_ariary),
                "type_infraction": contravention.type_infraction.nom if contravention.type_infraction else "",
            },
            send_email=True,
        )

    @staticmethod
    def create_contravention_payment_notification(user, contravention, langue="fr"):
        """Create notification when contravention is paid"""
        if langue == "mg":
            titre = "Famaizana voaloa"
            contenu = (
                f"Ny famaizana {contravention.numero_pv} dia voaloa soa aman-tsara. "
                f"Vola naloa: {contravention.montant_amende_ariary:,.0f} Ar."
            )
        else:
            titre = "Contravention payée"
            contenu = (
                f"La contravention {contravention.numero_pv} a été payée avec succès. "
                f"Montant payé: {contravention.montant_amende_ariary:,.0f} Ar."
            )

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "contravention_paid",
                "contravention_id": str(contravention.id),
                "numero_pv": contravention.numero_pv,
                "montant": str(contravention.montant_amende_ariary),
            },
            send_email=True,
        )

    @staticmethod
    def create_contravention_cancelled_notification(user, contravention, motif, langue="fr"):
        """Create notification when contravention is cancelled"""
        if langue == "mg":
            titre = "Famaizana nofoanana"
            contenu = f"Ny famaizana {contravention.numero_pv} dia nofoanana. " f"Antony: {motif}"
        else:
            titre = "Contravention annulée"
            contenu = f"La contravention {contravention.numero_pv} a été annulée. " f"Motif: {motif}"

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "contravention_cancelled",
                "contravention_id": str(contravention.id),
                "numero_pv": contravention.numero_pv,
                "motif": motif,
            },
            send_email=True,
        )

    @staticmethod
    def create_contravention_reminder_notification(user, contravention, days_remaining, langue="fr"):
        """Create reminder notification for contravention payment"""
        if langue == "mg":
            titre = "Fampahatsiahivana famaizana"
            contenu = (
                f"Misy {days_remaining} andro sisa alohan'ny ho tapitra ny fe-potoana handoavana "
                f"ny famaizana {contravention.numero_pv}. "
                f"Vola: {contravention.get_montant_total():,.0f} Ar."
            )
        else:
            titre = "Rappel de contravention"
            contenu = (
                f"Il reste {days_remaining} jours avant l'échéance de paiement "
                f"de la contravention {contravention.numero_pv}. "
                f"Montant: {contravention.get_montant_total():,.0f} Ar."
            )

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "contravention_reminder",
                "contravention_id": str(contravention.id),
                "numero_pv": contravention.numero_pv,
                "days_remaining": days_remaining,
                "montant": str(contravention.get_montant_total()),
            },
            send_email=True,
        )

    @staticmethod
    def create_maritime_classification_notification(user, vehicle, classification, tax_amount, langue="fr"):
        """
        Create notification for maritime vehicle classification

        Args:
            user: User object
            vehicle: Vehicule instance (maritime)
            classification: Maritime category (NAVIRE_PLAISANCE, JETSKI, AUTRES_ENGINS)
            tax_amount: Applicable tax amount in Ariary
            langue: Language (fr or mg)

        Returns:
            Notification object
        """
        # Classification display names
        classification_names = {
            "NAVIRE_PLAISANCE": {
                "fr": "Navire de plaisance (≥7m ou ≥22CV/90kW)",
                "mg": "Sambo fialam-boly (≥7m na ≥22CV/90kW)",
            },
            "JETSKI": {"fr": "Jet-ski/Moto nautique (≥90kW)", "mg": "Jet-ski/Moto an-dranomasina (≥90kW)"},
            "AUTRES_ENGINS": {
                "fr": "Autres engins maritimes motorisés",
                "mg": "Fitaovana hafa an-dranomasina misy motera",
            },
        }

        classification_display = classification_names.get(classification, {}).get(langue, classification)
        vehicle_name = vehicle.nom_navire or vehicle.numero_francisation or "votre navire"

        if langue == "mg":
            titre = "Fanasokajiana sambo"
            contenu = (
                f"Ny sambo {vehicle_name} dia nosokajiana ho: {classification_display}.\n\n"
                f"Hetra azo ampiharina: {tax_amount:,.0f} Ar/taona.\n\n"
                f"Raha tsy mifanaraka amin'ny fanasokajiana ianao, afaka manao fangatahana fanitsiana ianao "
                f"amin'ny alalan'ny fifandraisana amin'ny mpitantana."
            )
        else:
            titre = "Classification maritime"
            contenu = (
                f"Votre navire {vehicle_name} a été classifié comme: {classification_display}.\n\n"
                f"Taxe applicable: {tax_amount:,.0f} Ar/an.\n\n"
                f"Si vous contestez cette classification, vous pouvez soumettre une demande de révision "
                f"en contactant l'administration."
            )

        return NotificationService.create_notification(
            user=user,
            type_notification="system",
            titre=titre,
            contenu=contenu,
            langue=langue,
            metadata={
                "event": "maritime_classification",
                "vehicle_id": str(vehicle.pk),
                "vehicle_name": vehicle_name,
                "numero_francisation": vehicle.numero_francisation,
                "classification": classification,
                "classification_display": classification_display,
                "tax_amount": str(tax_amount),
                "longueur_metres": str(vehicle.longueur_metres) if vehicle.longueur_metres else None,
                "puissance_cv": str(vehicle.puissance_fiscale_cv) if vehicle.puissance_fiscale_cv else None,
                "puissance_kw": str(vehicle.puissance_moteur_kw) if vehicle.puissance_moteur_kw else None,
                "allow_contestation": True,
            },
            send_email=True,
        )

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        unread_notifications = Notification.objects.filter(user=user, est_lue=False)

        for notification in unread_notifications:
            notification.marquer_comme_lue()

        return unread_notifications.count()

    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(user=user, est_lue=False).count()

    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for a user"""
        return Notification.objects.filter(user=user).order_by("-date_envoi")[:limit]
