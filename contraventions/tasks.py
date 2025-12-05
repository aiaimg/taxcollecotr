from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from celery import shared_task

from contraventions.models import Contestation, Contravention, DossierFourriere
from notifications.models import Notification


@shared_task
def send_payment_reminder(contravention_id, reminder_type="approaching_due"):
    """
    Send payment reminder for a specific contravention
    """
    try:
        contravention = Contravention.objects.get(id=contravention_id)

        # Get contact information
        email = None
        phone = None
        recipient_name = ""

        if contravention.conducteur:
            email = contravention.conducteur.email
            phone = contravention.conducteur.telephone
            recipient_name = f"{contravention.conducteur.prenom} {contravention.conducteur.nom}"
        elif contravention.vehicule and contravention.vehicule.proprietaire:
            email = contravention.vehicule.proprietaire.email
            phone = contravention.vehicule.proprietaire.telephone
            recipient_name = contravention.vehicule.proprietaire.get_full_name()

        if not email and not phone:
            return False

        # Determine message based on reminder type
        if reminder_type == "approaching_due":
            subject = f"Rappel: Paiement de contravention {contravention.numero_pv}"
            message = f"""
Bonjour {recipient_name},

Nous vous rappelons que la contravention {contravention.numero_pv} 
doit être payée avant le {contravention.date_limite_paiement.strftime("%d/%m/%Y")}.

Montant: {contravention.get_montant_total():,} Ar

Pour payer: {settings.SITE_URL}/contraventions/public/{contravention.numero_pv}/pay/

Cordialement,
Service des Contraventions
"""

        elif reminder_type == "past_due":
            subject = f"URGENT: Contravention impayée {contravention.numero_pv}"
            message = f"""
Bonjour {recipient_name},

Votre contravention {contravention.numero_pv} est maintenant en retard.
La date limite de paiement ({contravention.date_limite_paiement.strftime("%d/%m/%Y")}) est dépassée.

Montant: {contravention.get_montant_total():,} Ar
Frais de retard peuvent s'appliquer.

Payez immédiatement: {settings.SITE_URL}/contraventions/public/{contravention.numero_pv}/pay/

Cordialement,
Service des Contraventions
"""

        elif reminder_type == "very_overdue":
            subject = f"AVERTISSEMENT: Contravention très en retard {contravention.numero_pv}"
            message = f"""
Bonjour {recipient_name},

Votre contravention {contravention.numero_pv} est très en retard 
(plus de 30 jours depuis la date limite).

Montant: {contravention.get_montant_total():,} Ar

Des poursuites judiciaires peuvent être engagées.

Payez immédiatement: {settings.SITE_URL}/contraventions/public/{contravention.numero_pv}/pay/

Pour toute question: {settings.CONTACT_PHONE}

Cordialement,
Service des Contraventions
"""

        # Send email if available
        if email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email to {email}: {str(e)}")

        # Create notification record
        Notification.objects.create(
            recipient_email=email,
            recipient_phone=phone,
            subject=subject,
            message=message,
            notification_type="payment_reminder",
            related_object_id=contravention.id,
            related_object_type="contravention",
        )

        return True

    except Contravention.DoesNotExist:
        return False


@shared_task
def process_expired_fourriere():
    """
    Process expired fourrière cases
    """
    expired_fourrieres = DossierFourriere.objects.filter(
        statut="EN_FOURRIERE", date_mise_fourriere__lte=timezone.now() - timedelta(days=30)  # 30 days max duration
    )

    processed_count = 0

    for fourriere in expired_fourrieres:
        days_elapsed = (timezone.now() - fourriere.date_mise_fourriere).days

        if days_elapsed >= fourriere.duree_maximale_jours:
            # Mark for sale notification
            fourriere.observations += f'\n\n[SYSTEM] Dossier expiré le {timezone.now().strftime("%d/%m/%Y")}. '
            fourriere.observations += "Notification de vente envoyée."
            fourriere.save()

            # Send notification to vehicle owner
            if fourriere.contravention.vehicule and fourriere.contravention.vehicule.proprietaire:
                owner = fourriere.contravention.vehicule.proprietaire
                subject = f"Notification de vente - Véhicule {fourriere.contravention.vehicule.plaque_immatriculation}"
                message = f"""
Bonjour {owner.get_full_name()},

Votre véhicule immatriculé {fourriere.contravention.vehicule.plaque_immatriculation} 
est en fourrière depuis plus de {days_elapsed} jours.

Le délai légal étant dépassé, votre véhicule sera mis en vente.

Pour plus d'informations, contactez: {settings.CONTACT_PHONE}

Cordialement,
Service de la Fourrière
"""

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[owner.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Failed to send fourrière notification to {owner.email}: {str(e)}")

            processed_count += 1

    return processed_count


@shared_task
def process_contestation_reminders():
    """
    Send reminders for contestations that need processing
    """
    # Find contestations that have been pending for more than 7 days
    old_contestations = Contestation.objects.filter(
        statut="EN_ATTENTE", date_soumission__lte=timezone.now() - timedelta(days=7)
    )

    reminder_count = 0

    for contestation in old_contestations:
        # Send reminder to administrators
        subject = f"Reminder: Contestation en attente - {contestation.contravention.numero_pv}"
        message = f"""
Une contestation pour la contravention {contestation.contravention.numero_pv} 
est en attente de traitement depuis plus de 7 jours.

Contestataire: {contestation.nom_demandeur}
Date de contestation: {contestation.date_soumission.strftime("%d/%m/%Y")}
Motif: {contestation.motif[:100]}...

Pour traiter: {settings.SITE_URL}/admin/contraventions/contestation/{contestation.id}/change/
"""

        # Get admin emails
        admin_emails = settings.ADMIN_EMAILS if hasattr(settings, "ADMIN_EMAILS") else []

        if admin_emails:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=False,
                )
                reminder_count += 1
            except Exception as e:
                print(f"Failed to send contestation reminder: {str(e)}")

    return reminder_count


@shared_task
def generate_daily_reports():
    """
    Generate daily reports for contraventions
    """
    from datetime import datetime, timedelta

    yesterday = timezone.now() - timedelta(days=1)

    # Daily statistics
    stats = {
        "new_contraventions": Contravention.objects.filter(date_creation__date=yesterday.date()).count(),
        "paid_contraventions": Contravention.objects.filter(date_paiement__date=yesterday.date()).count(),
        "contested_contraventions": Contravention.objects.filter(
            statut="contested", date_modification__date=yesterday.date()
        ).count(),
        "total_revenue": Contravention.objects.filter(date_paiement__date=yesterday.date()).aggregate(
            total=Sum("montant_total_ariary")
        )["total"]
        or 0,
    }

    # Create report record
    from contraventions.models import RapportJournalier

    RapportJournalier.objects.create(
        date=yesterday.date(),
        nombre_nouvelles_contraventions=stats["new_contraventions"],
        nombre_contraventions_payees=stats["paid_contraventions"],
        nombre_contestations=stats["contested_contraventions"],
        montant_total_percu=stats["total_revenue"],
    )

    return stats
