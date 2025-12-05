"""
Unified Payment Success Service
Handles QR code generation and notifications for all payment methods
Ensures consistent workflow across cash, MVola, and Stripe payments
"""

import logging
from datetime import timedelta
from typing import Optional, Tuple

from django.utils import timezone

from payments.models import PaiementTaxe, QRCode

logger = logging.getLogger(__name__)


class PaymentSuccessService:
    """
    Unified service for handling payment success across all payment methods
    Ensures consistent workflow: QR code generation, notifications, etc.
    """

    @staticmethod
    def handle_payment_success(
        payment: PaiementTaxe, send_notification: bool = True
    ) -> Tuple[Optional[QRCode], Optional[str]]:
        """
        Handle payment success - generate QR code and send notifications
        This is called by all payment methods (cash, MVola, Stripe) after payment is confirmed

        Args:
            payment: The PaiementTaxe instance that was successfully paid
            send_notification: Whether to send notification to user (default: True)

        Returns:
            Tuple of (QRCode instance, error_message)
        """
        try:
            # Ensure payment is marked as paid
            if payment.statut != "PAYE" and payment.statut != "EXONERE":
                payment.statut = "PAYE"
                if not payment.date_paiement:
                    payment.date_paiement = timezone.now()
                if not payment.montant_paye_ariary:
                    payment.montant_paye_ariary = payment.montant_du_ariary
                payment.save(update_fields=["statut", "date_paiement", "montant_paye_ariary"])

            # Generate QR code using get_or_create to avoid duplicates
            # This ensures the same QR code is used for the same vehicle and tax year
            # regardless of payment method (cash, MVola, Stripe)
            qr_code, created = QRCode.objects.get_or_create(
                vehicule_plaque=payment.vehicule_plaque,
                annee_fiscale=payment.annee_fiscale,
                defaults={"date_expiration": timezone.now() + timedelta(days=365), "est_actif": True},
            )

            # If QR code already existed but was expired, reactivate it
            if not created:
                if not qr_code.est_actif or (qr_code.date_expiration and qr_code.date_expiration < timezone.now()):
                    qr_code.est_actif = True
                    qr_code.date_expiration = timezone.now() + timedelta(days=365)
                    qr_code.save(update_fields=["est_actif", "date_expiration"])
                    logger.info(f"Reactivated expired QR code for payment: {payment.id}")

            if created:
                logger.info(
                    f"QR code generated for payment: payment_id={payment.id}, qr_code_id={qr_code.id}, token={qr_code.token}"
                )
            else:
                logger.info(
                    f"QR code already exists for payment: payment_id={payment.id}, qr_code_id={qr_code.id}, token={qr_code.token}"
                )

            # Send notification if requested
            if send_notification:
                PaymentSuccessService._send_payment_notification(payment, qr_code)

            return qr_code, None

        except Exception as e:
            error_msg = f"Error handling payment success: {str(e)}"
            logger.error(f"{error_msg} - payment_id={payment.id}")
            return None, error_msg

    @staticmethod
    def _send_payment_notification(payment: PaiementTaxe, qr_code: QRCode):
        """
        Send notification to user about successful payment
        """
        try:
            from notifications.services import NotificationService

            owner = payment.vehicule_plaque.proprietaire
            langue = "fr"
            if hasattr(owner, "profile"):
                langue = owner.profile.langue_preferee

            # Use appropriate notification based on payment method
            if payment.methode_paiement == "cash":
                NotificationService.create_cash_payment_notification(
                    user=owner, payment=payment, collector=payment.collected_by, langue=langue
                )
            elif payment.methode_paiement == "mvola":
                NotificationService.create_payment_confirmation_notification(user=owner, payment=payment, langue=langue)
            elif payment.methode_paiement == "carte_bancaire":
                NotificationService.create_payment_confirmation_notification(user=owner, payment=payment, langue=langue)
            else:
                # Generic payment confirmation
                NotificationService.create_payment_confirmation_notification(user=owner, payment=payment, langue=langue)

            logger.info(f"Payment notification sent: payment_id={payment.id}")

        except Exception as e:
            # Log error but don't fail the payment success handling
            logger.error(f"Error sending payment notification: {str(e)} - payment_id={payment.id}")

    @staticmethod
    def get_qr_verification_url(qr_code: QRCode, request=None) -> str:
        """
        Get the QR code verification URL
        This is the URL that should be encoded in the QR code for verification

        The verification URL format is: /app/qr-verification/?code={token}
        This is the SAME URL used for ALL payment methods (cash, MVola, Stripe)

        Args:
            qr_code: The QRCode instance
            request: HTTP request object (optional, for building absolute URL)

        Returns:
            Verification URL string (absolute if request provided, relative otherwise)
        """
        from django.urls import reverse

        # Build the verification URL with token parameter
        # Format: /app/qr-verification/?code={token}
        verification_path = f"/app/qr-verification/?code={qr_code.token}"

        if request:
            # Build absolute URL
            return request.build_absolute_uri(verification_path)
        else:
            # Return relative URL
            return verification_path
