"""
MVola Payment API Views

This module contains API views for MVola mobile money payment operations:
- Payment initiation
- Callback handling
- Status checking
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.services import NotificationService
from vehicles.models import Vehicule
from vehicles.services import TaxCalculationService

from .models import PaiementTaxe, QRCode
from .services.mvola.api_client import MvolaAPIClient
from .services.mvola.exceptions import MvolaAPIError, MvolaAuthenticationError, MvolaCallbackError, MvolaValidationError
from .services.mvola.fee_calculator import MvolaFeeCalculator
from .services.mvola.validators import validate_msisdn

# Configure logger
logger = logging.getLogger("payments.mvola")


class MvolaInitiatePaymentView(APIView):
    """
    POST /api/payments/mvola/initiate/

    Initiate a MVola payment transaction.

    This endpoint:
    1. Validates request data (vehicle_plate, tax_year, customer_msisdn)
    2. Retrieves vehicle and verifies ownership
    3. Calculates tax amount using TaxCalculationService
    4. Calculates total amount with 3% fee using MvolaFeeCalculator
    5. Validates MSISDN format
    6. Calls MvolaAPIClient.initiate_payment()
    7. Creates PaiementTaxe record with MVola fields populated
    8. Returns JSON response with payment details

    Request Body:
    {
        "vehicle_plate": "1234AB01",
        "tax_year": 2024,
        "customer_msisdn": "0340000000"
    }

    Response (Success - 200):
    {
        "success": true,
        "payment_id": "uuid",
        "server_correlation_id": "...",
        "total_amount": "103000.00",
        "base_amount": "100000.00",
        "platform_fee": "3000.00",
        "message": "Paiement initié. Veuillez confirmer sur votre téléphone MVola."
    }

    Response (Error - 400/404/500):
    {
        "success": false,
        "error": "Message d'erreur en français"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle MVola payment initiation request"""

        # Extract and validate request data
        vehicle_plate = request.data.get("vehicle_plate")
        tax_year = request.data.get("tax_year")
        customer_msisdn = request.data.get("customer_msisdn")

        # Validate required fields
        if not vehicle_plate:
            logger.warning(f"Payment initiation failed: missing vehicle_plate, " f"user={request.user.username}")
            return Response(
                {"success": False, "error": "Le numéro de plaque est requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not tax_year:
            logger.warning(
                f"Payment initiation failed: missing tax_year, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}"
            )
            return Response(
                {"success": False, "error": "L'année fiscale est requise."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not customer_msisdn:
            logger.warning(
                f"Payment initiation failed: missing customer_msisdn, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}"
            )
            return Response(
                {"success": False, "error": "Le numéro de téléphone MVola est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate tax year
        try:
            tax_year = int(tax_year)
            current_year = timezone.now().year
            if tax_year < 2020 or tax_year > current_year + 1:
                raise ValueError("Invalid year range")
        except (ValueError, TypeError):
            logger.warning(
                f"Payment initiation failed: invalid tax_year={tax_year}, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}"
            )
            return Response({"success": False, "error": "Année fiscale invalide."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate MSISDN format
        try:
            customer_msisdn = validate_msisdn(customer_msisdn)
        except MvolaValidationError as e:
            logger.warning(
                f"Payment initiation failed: invalid MSISDN, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"error={str(e)}"
            )
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve vehicle and verify ownership
        try:
            vehicule = Vehicule.objects.select_related("type_vehicule").get(plaque_immatriculation=vehicle_plate)
        except Vehicule.DoesNotExist:
            logger.warning(
                f"Payment initiation failed: vehicle not found, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}"
            )
            return Response({"success": False, "error": "Véhicule introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Verify ownership
        if vehicule.proprietaire != request.user:
            logger.warning(
                f"Payment initiation failed: ownership verification failed, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"owner={vehicule.proprietaire.username}"
            )
            return Response(
                {"success": False, "error": "Vous n'êtes pas autorisé à effectuer un paiement pour ce véhicule."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if vehicle is exempt
        if vehicule.est_exonere():
            logger.info(
                f"Payment initiation failed: vehicle is exempt, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"category={vehicule.categorie_vehicule}"
            )
            return Response(
                {"success": False, "error": "Ce véhicule est exonéré de taxe."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing payment for this year
        existing_payment = PaiementTaxe.objects.filter(
            vehicule_plaque=vehicule, annee_fiscale=tax_year, statut__in=["PAYE", "EN_ATTENTE"]
        ).first()

        if existing_payment:
            logger.info(
                f"Payment initiation failed: payment already exists, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"tax_year={tax_year}, "
                f"payment_id={existing_payment.id}, "
                f"status={existing_payment.statut}"
            )
            return Response(
                {"success": False, "error": f"Un paiement existe déjà pour ce véhicule pour l'année {tax_year}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate tax amount using TaxCalculationService
        tax_service = TaxCalculationService()
        tax_info = tax_service.calculate_tax(vehicule, tax_year)

        if not tax_info.get("amount"):
            error_message = tax_info.get("error", "Impossible de calculer la taxe pour ce véhicule.")
            logger.error(
                f"Payment initiation failed: tax calculation error, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"tax_year={tax_year}, "
                f"error={error_message}"
            )
            return Response({"success": False, "error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        base_tax_amount = tax_info["amount"]

        # Calculate total amount with 3% fee using MvolaFeeCalculator
        fee_calculation = MvolaFeeCalculator.calculate_total_amount(base_tax_amount)
        total_amount = fee_calculation["total_amount"]
        platform_fee = fee_calculation["platform_fee"]

        logger.info(
            f"Tax calculated: "
            f"user={request.user.username}, "
            f"vehicle_plate={vehicle_plate}, "
            f"tax_year={tax_year}, "
            f"base_amount={base_tax_amount}, "
            f"platform_fee={platform_fee}, "
            f"total_amount={total_amount}"
        )

        # Prepare payment description
        description = f"Taxe véhicule {vehicle_plate} - {tax_year}"

        # Initialize MVola API client and initiate payment
        try:
            mvola_client = MvolaAPIClient()

            # Call MVola API to initiate payment
            payment_result = mvola_client.initiate_payment(
                amount=total_amount,
                customer_msisdn=customer_msisdn,
                description=description,
                vehicle_plate=vehicle_plate,
                tax_year=tax_year,
            )

            if not payment_result["success"]:
                # Payment initiation failed
                error_message = payment_result.get("error", "Erreur lors de l'initiation du paiement MVola.")
                logger.error(
                    f"MVola payment initiation failed: "
                    f"user={request.user.username}, "
                    f"vehicle_plate={vehicle_plate}, "
                    f"error={error_message}"
                )
                return Response({"success": False, "error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            # Extract MVola response data
            x_correlation_id = payment_result["x_correlation_id"]
            server_correlation_id = payment_result["server_correlation_id"]
            mvola_status = payment_result.get("status", "pending")

            logger.info(
                f"MVola payment initiated successfully: "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"x_correlation_id={x_correlation_id}, "
                f"server_correlation_id={server_correlation_id}"
            )

            # Create PaiementTaxe record with MVola fields populated
            with transaction.atomic():
                payment = PaiementTaxe.objects.create(
                    vehicule_plaque=vehicule,
                    annee_fiscale=tax_year,
                    montant_du_ariary=base_tax_amount,
                    montant_paye_ariary=Decimal("0.00"),
                    statut="EN_ATTENTE",
                    methode_paiement="mvola",
                    # MVola-specific fields
                    mvola_x_correlation_id=x_correlation_id,
                    mvola_server_correlation_id=server_correlation_id,
                    mvola_customer_msisdn=customer_msisdn,
                    mvola_platform_fee=platform_fee,
                    mvola_status=mvola_status,
                    details_paiement={
                        "mvola_initiation_time": timezone.now().isoformat(),
                        "base_amount": str(base_tax_amount),
                        "platform_fee": str(platform_fee),
                        "total_amount": str(total_amount),
                    },
                )

            logger.info(
                f"Payment record created: "
                f"payment_id={payment.id}, "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"server_correlation_id={server_correlation_id}"
            )

            # Create payment initiated notification
            try:
                # Determine user language preference (default to French)
                user_language = "fr"
                if hasattr(request.user, "userprofile") and hasattr(request.user.userprofile, "langue_preferee"):
                    user_language = request.user.userprofile.langue_preferee or "fr"

                if user_language == "mg":
                    titre = "Fandoavam-bola MVola natomboka"
                    contenu = (
                        f"Ny fandoavam-bola MVola ho an'ny fiara {vehicle_plate} "
                        f"({tax_year}) dia natomboka soa aman-tsara. "
                        f"Vola tokony haloa: {total_amount:,.0f} Ar "
                        f"(Hetra: {base_tax_amount:,.0f} Ar + Sarany MVola: {platform_fee:,.0f} Ar). "
                        f"Hamarino amin'ny findainao MVola azafady. "
                        f"Référence: {server_correlation_id}"
                    )
                else:
                    titre = "Paiement MVola initié"
                    contenu = (
                        f"Votre paiement MVola pour le véhicule {vehicle_plate} "
                        f"({tax_year}) a été initié avec succès. "
                        f"Montant à payer: {total_amount:,.0f} Ar "
                        f"(Taxe: {base_tax_amount:,.0f} Ar + Frais MVola: {platform_fee:,.0f} Ar). "
                        f"Veuillez confirmer sur votre téléphone MVola. "
                        f"Référence: {server_correlation_id}"
                    )

                NotificationService.create_notification(
                    user=request.user,
                    type_notification="system",
                    titre=titre,
                    contenu=contenu,
                    langue=user_language,
                    metadata={
                        "event": "mvola_payment_initiated",
                        "payment_id": str(payment.id),
                        "base_amount": str(base_tax_amount),
                        "platform_fee": str(platform_fee),
                        "total_amount": str(total_amount),
                        "server_correlation_id": server_correlation_id,
                        "vehicle_plate": vehicle_plate,
                        "tax_year": tax_year,
                        "customer_msisdn": customer_msisdn,
                    },
                )

                logger.info(
                    f"Payment initiated notification created: "
                    f"payment_id={payment.id}, "
                    f"user={request.user.username}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to create payment initiated notification: " f"payment_id={payment.id}, " f"error={str(e)}"
                )

            # Return success response with payment details
            return Response(
                {
                    "success": True,
                    "payment_id": str(payment.id),
                    "server_correlation_id": server_correlation_id,
                    "total_amount": str(total_amount),
                    "base_amount": str(base_tax_amount),
                    "platform_fee": str(platform_fee),
                    "message": "Paiement initié. Veuillez confirmer sur votre téléphone MVola.",
                },
                status=status.HTTP_200_OK,
            )

        except MvolaAuthenticationError as e:
            logger.error(
                f"MVola authentication error: "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Erreur d'authentification MVola. Veuillez réessayer plus tard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except MvolaAPIError as e:
            logger.error(
                f"MVola API error: "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Erreur lors de la communication avec MVola. Veuillez réessayer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.exception(
                f"Unexpected error during payment initiation: "
                f"user={request.user.username}, "
                f"vehicle_plate={vehicle_plate}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Une erreur inattendue s'est produite. Veuillez réessayer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class MvolaCallbackView(APIView):
    """
    PUT /api/payments/mvola/callback/

    Receive transaction status updates from MVola.

    This endpoint:
    1. Receives callback from MVola with transaction status
    2. Extracts callback data (serverCorrelationId, transactionStatus, transactionReference, fees)
    3. Finds PaiementTaxe by mvola_server_correlation_id
    4. Updates payment status based on transactionStatus
    5. Extracts and stores gateway fees using MvolaFeeCalculator.extract_gateway_fees()
    6. Updates mvola_status, mvola_transaction_reference, and mvola_gateway_fees fields
    7. Sets statut to 'PAYE' and date_paiement when status is 'completed'
    8. Creates notification for user
    9. Generates QR code if payment completed
    10. Returns HTTP 200 with acknowledgment JSON

    Request Body (from MVola):
    {
        "serverCorrelationId": "...",
        "transactionStatus": "completed",
        "transactionReference": "...",
        "fees": [
            {
                "feeAmount": "500"
            }
        ]
    }

    Response (Success - 200):
    {
        "status": "received",
        "message": "Callback processed successfully"
    }

    Response (Error - 400/404/500):
    {
        "status": "error",
        "message": "Error message"
    }
    """

    # Disable authentication and permissions for MVola callback
    authentication_classes = []
    permission_classes = []

    def put(self, request):
        """Handle MVola callback notification"""

        try:
            # Extract callback data
            callback_data = request.data

            logger.info(f"MVola callback received: {callback_data}")

            # Validate required fields
            server_correlation_id = callback_data.get("serverCorrelationId")
            transaction_status = callback_data.get("transactionStatus")

            if not server_correlation_id:
                logger.error(f"Callback missing serverCorrelationId: {callback_data}")
                return Response(
                    {"status": "error", "message": "serverCorrelationId is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not transaction_status:
                logger.error(f"Callback missing transactionStatus: " f"server_correlation_id={server_correlation_id}")
                return Response(
                    {"status": "error", "message": "transactionStatus is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Find PaiementTaxe by mvola_server_correlation_id
            try:
                payment = PaiementTaxe.objects.select_related("vehicule_plaque", "vehicule_plaque__proprietaire").get(
                    mvola_server_correlation_id=server_correlation_id
                )
            except PaiementTaxe.DoesNotExist:
                logger.error(f"Payment not found for server_correlation_id: {server_correlation_id}")
                return Response({"status": "error", "message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

            logger.info(
                f"Processing callback for payment: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"transaction_status={transaction_status}, "
                f"current_status={payment.statut}"
            )

            # Extract optional fields
            transaction_reference = callback_data.get("transactionReference")

            # Extract gateway fees using MvolaFeeCalculator
            gateway_fees = MvolaFeeCalculator.extract_gateway_fees(callback_data)

            # Update payment record within transaction
            with transaction.atomic():
                # Update MVola-specific fields
                payment.mvola_transaction_reference = transaction_reference
                payment.mvola_gateway_fees = gateway_fees

                # Map MVola transaction status to our mvola_status field
                # MVola statuses: pending, completed, failed, cancelled
                if transaction_status.lower() in ["completed", "success", "successful"]:
                    payment.mvola_status = "completed"
                    payment.statut = "PAYE"
                    payment.date_paiement = timezone.now()
                    payment.montant_paye_ariary = payment.montant_du_ariary

                    logger.info(
                        f"Payment completed: "
                        f"payment_id={payment.id}, "
                        f"server_correlation_id={server_correlation_id}, "
                        f"amount={payment.montant_paye_ariary}, "
                        f"gateway_fees={gateway_fees}"
                    )

                elif transaction_status.lower() in ["failed", "error", "cancelled", "canceled"]:
                    payment.mvola_status = "failed"
                    payment.statut = "ANNULE"

                    logger.warning(
                        f"Payment failed: "
                        f"payment_id={payment.id}, "
                        f"server_correlation_id={server_correlation_id}, "
                        f"transaction_status={transaction_status}"
                    )

                else:
                    # Keep as pending for other statuses
                    payment.mvola_status = "pending"

                    logger.info(
                        f"Payment status updated to pending: "
                        f"payment_id={payment.id}, "
                        f"server_correlation_id={server_correlation_id}, "
                        f"transaction_status={transaction_status}"
                    )

                # Save payment
                payment.save()

            # Get user and vehicle info for notifications
            user = payment.vehicule_plaque.proprietaire
            vehicle_plate = payment.vehicule_plaque.plaque_immatriculation

            # Determine user language preference (default to French)
            user_language = "fr"
            if hasattr(user, "userprofile") and hasattr(user.userprofile, "langue_preferee"):
                user_language = user.userprofile.langue_preferee or "fr"

            # Create notification based on payment status
            if payment.mvola_status == "completed":
                # Create payment confirmation notification
                try:
                    if user_language == "mg":
                        titre = "Fandoavam-bola MVola vita soa aman-tsara"
                        contenu = (
                            f"Ny fandoavam-bola MVola ho an'ny fiara {vehicle_plate} "
                            f"dia vita soa aman-tsara. "
                            f"Vola naloa: {payment.montant_paye_ariary:,.0f} Ar. "
                            f"Référence: {transaction_reference or server_correlation_id}"
                        )
                    else:
                        titre = "Paiement MVola confirmé"
                        contenu = (
                            f"Votre paiement MVola pour le véhicule {vehicle_plate} "
                            f"a été confirmé avec succès. "
                            f"Montant payé: {payment.montant_paye_ariary:,.0f} Ar. "
                            f"Référence: {transaction_reference or server_correlation_id}"
                        )

                    NotificationService.create_notification(
                        user=user,
                        type_notification="system",
                        titre=titre,
                        contenu=contenu,
                        langue=user_language,
                        metadata={
                            "event": "mvola_payment_completed",
                            "payment_id": str(payment.id),
                            "amount": str(payment.montant_paye_ariary),
                            "server_correlation_id": server_correlation_id,
                            "transaction_reference": transaction_reference,
                            "gateway_fees": str(gateway_fees),
                        },
                        send_email=True,
                    )

                    logger.info(
                        f"Payment confirmation notification created: "
                        f"payment_id={payment.id}, "
                        f"user={user.username}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create payment confirmation notification: "
                        f"payment_id={payment.id}, "
                        f"error={str(e)}"
                    )

                # Generate QR code for completed payment
                try:
                    # Check if QR code already exists for this vehicle and year
                    qr_code, created = QRCode.objects.get_or_create(
                        vehicule_plaque=payment.vehicule_plaque,
                        annee_fiscale=payment.annee_fiscale,
                        defaults={"date_expiration": timezone.now() + timedelta(days=365), "est_actif": True},
                    )

                    if created:
                        logger.info(
                            f"QR code generated: "
                            f"payment_id={payment.id}, "
                            f"qr_code_id={qr_code.id}, "
                            f"vehicle_plate={vehicle_plate}, "
                            f"tax_year={payment.annee_fiscale}"
                        )

                        # Create QR code generation notification
                        try:
                            if user_language == "mg":
                                titre_qr = "QR code noforonina"
                                contenu_qr = (
                                    f"Ny QR code ho an'ny fiara {vehicle_plate} "
                                    f"({payment.annee_fiscale}) dia noforonina soa aman-tsara."
                                )
                            else:
                                titre_qr = "QR code généré"
                                contenu_qr = (
                                    f"Le QR code pour le véhicule {vehicle_plate} "
                                    f"({payment.annee_fiscale}) a été généré avec succès."
                                )

                            NotificationService.create_notification(
                                user=user,
                                type_notification="system",
                                titre=titre_qr,
                                contenu=contenu_qr,
                                langue=user_language,
                                metadata={
                                    "event": "qr_generated",
                                    "qr_code_id": str(qr_code.id),
                                    "vehicle_plaque": vehicle_plate,
                                    "tax_year": payment.annee_fiscale,
                                    "payment_id": str(payment.id),
                                },
                            )

                            logger.info(f"QR code notification created: " f"qr_code_id={qr_code.id}")

                        except Exception as e:
                            logger.error(
                                f"Failed to create QR code notification: "
                                f"qr_code_id={qr_code.id}, "
                                f"error={str(e)}"
                            )
                    else:
                        logger.info(f"QR code already exists: " f"payment_id={payment.id}, " f"qr_code_id={qr_code.id}")

                except Exception as e:
                    logger.error(f"Failed to generate QR code: " f"payment_id={payment.id}, " f"error={str(e)}")

            elif payment.mvola_status == "failed":
                # Create payment failed notification
                try:
                    if user_language == "mg":
                        titre = "Tsy nahomby ny fandoavam-bola MVola"
                        contenu = (
                            f"Tsy nahomby ny fandoavam-bola MVola ho an'ny fiara {vehicle_plate}. "
                            f"Andramo indray azafady. "
                            f"Référence: {transaction_reference or server_correlation_id}"
                        )
                    else:
                        titre = "Échec du paiement MVola"
                        contenu = (
                            f"Le paiement MVola pour le véhicule {vehicle_plate} a échoué. "
                            f"Veuillez réessayer. "
                            f"Référence: {transaction_reference or server_correlation_id}"
                        )

                    NotificationService.create_notification(
                        user=user,
                        type_notification="system",
                        titre=titre,
                        contenu=contenu,
                        langue=user_language,
                        metadata={
                            "event": "mvola_payment_failed",
                            "payment_id": str(payment.id),
                            "server_correlation_id": server_correlation_id,
                            "transaction_reference": transaction_reference,
                            "transaction_status": transaction_status,
                        },
                        send_email=True,
                    )

                    logger.info(
                        f"Payment failed notification created: " f"payment_id={payment.id}, " f"user={user.username}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create payment failed notification: " f"payment_id={payment.id}, " f"error={str(e)}"
                    )

            # Return success acknowledgment to MVola
            logger.info(
                f"Callback processed successfully: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"final_status={payment.statut}, "
                f"mvola_status={payment.mvola_status}"
            )

            return Response(
                {"status": "received", "message": "Callback processed successfully"}, status=status.HTTP_200_OK
            )

        except MvolaCallbackError as e:
            logger.error(f"MVola callback error: {str(e)}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception(f"Unexpected error processing MVola callback: {str(e)}")
            return Response(
                {"status": "error", "message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MvolaStatusCheckView(APIView):
    """
    GET /api/payments/mvola/status/<server_correlation_id>/

    Check transaction status manually.

    This endpoint:
    1. Retrieves PaiementTaxe by mvola_server_correlation_id
    2. Verifies user owns the payment (check vehicle ownership)
    3. Calls MvolaAPIClient.get_transaction_status()
    4. Updates PaiementTaxe status based on MVola response
    5. Returns JSON response with current status

    Response (Success - 200):
    {
        "success": true,
        "status": "completed",
        "transaction_reference": "...",
        "payment_status": "PAYE",
        "mvola_status": "completed",
        "amount": "100000.00",
        "payment_id": "uuid"
    }

    Response (Error - 400/403/404/500):
    {
        "success": false,
        "error": "Message d'erreur en français"
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, server_correlation_id):
        """Handle MVola status check request"""

        # Log status check attempt
        logger.info(
            f"Status check requested: "
            f"user={request.user.username}, "
            f"server_correlation_id={server_correlation_id}"
        )

        # Retrieve PaiementTaxe by mvola_server_correlation_id
        try:
            payment = PaiementTaxe.objects.select_related("vehicule_plaque", "vehicule_plaque__proprietaire").get(
                mvola_server_correlation_id=server_correlation_id
            )
        except PaiementTaxe.DoesNotExist:
            logger.warning(
                f"Status check failed: payment not found, "
                f"user={request.user.username}, "
                f"server_correlation_id={server_correlation_id}"
            )
            return Response({"success": False, "error": "Transaction introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Verify user owns the payment (check vehicle ownership)
        if payment.vehicule_plaque.proprietaire != request.user:
            logger.warning(
                f"Status check failed: ownership verification failed, "
                f"user={request.user.username}, "
                f"server_correlation_id={server_correlation_id}, "
                f"owner={payment.vehicule_plaque.proprietaire.username}, "
                f"payment_id={payment.id}"
            )
            return Response(
                {"success": False, "error": "Vous n'êtes pas autorisé à consulter cette transaction."},
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(
            f"Payment found and ownership verified: "
            f"payment_id={payment.id}, "
            f"user={request.user.username}, "
            f"current_status={payment.statut}, "
            f"mvola_status={payment.mvola_status}"
        )

        # Call MvolaAPIClient.get_transaction_status()
        try:
            mvola_client = MvolaAPIClient()

            # Get transaction status from MVola
            status_result = mvola_client.get_transaction_status(server_correlation_id)

            if not status_result["success"]:
                # Status check failed
                error_message = status_result.get("error", "Erreur lors de la vérification du statut.")
                logger.error(
                    f"MVola status check failed: "
                    f"payment_id={payment.id}, "
                    f"server_correlation_id={server_correlation_id}, "
                    f"error={error_message}"
                )
                return Response({"success": False, "error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            # Extract status information from MVola response
            mvola_transaction_status = status_result.get("status", "pending")
            transaction_reference = status_result.get("transaction_reference")

            logger.info(
                f"MVola status retrieved: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"mvola_status={mvola_transaction_status}, "
                f"transaction_reference={transaction_reference}"
            )

            # Update PaiementTaxe status based on MVola response
            with transaction.atomic():
                # Store transaction reference if available
                if transaction_reference and not payment.mvola_transaction_reference:
                    payment.mvola_transaction_reference = transaction_reference

                # Map MVola transaction status to our status fields
                if mvola_transaction_status.lower() in ["completed", "success", "successful"]:
                    # Payment completed
                    if payment.mvola_status != "completed":
                        payment.mvola_status = "completed"
                        payment.statut = "PAYE"
                        payment.date_paiement = timezone.now()
                        payment.montant_paye_ariary = payment.montant_du_ariary

                        logger.info(
                            f"Payment status updated to completed: "
                            f"payment_id={payment.id}, "
                            f"server_correlation_id={server_correlation_id}"
                        )

                        # Create notification for user
                        user = payment.vehicule_plaque.proprietaire
                        vehicle_plate = payment.vehicule_plaque.plaque_immatriculation

                        # Determine user language preference
                        user_language = "fr"
                        if hasattr(user, "userprofile") and hasattr(user.userprofile, "langue_preferee"):
                            user_language = user.userprofile.langue_preferee or "fr"

                        try:
                            if user_language == "mg":
                                titre = "Fandoavam-bola MVola vita soa aman-tsara"
                                contenu = (
                                    f"Ny fandoavam-bola MVola ho an'ny fiara {vehicle_plate} "
                                    f"dia vita soa aman-tsara. "
                                    f"Vola naloa: {payment.montant_paye_ariary:,.0f} Ar. "
                                    f"Référence: {transaction_reference or server_correlation_id}"
                                )
                            else:
                                titre = "Paiement MVola confirmé"
                                contenu = (
                                    f"Votre paiement MVola pour le véhicule {vehicle_plate} "
                                    f"a été confirmé avec succès. "
                                    f"Montant payé: {payment.montant_paye_ariary:,.0f} Ar. "
                                    f"Référence: {transaction_reference or server_correlation_id}"
                                )

                            NotificationService.create_notification(
                                user=user,
                                type_notification="system",
                                titre=titre,
                                contenu=contenu,
                                langue=user_language,
                                metadata={
                                    "event": "mvola_payment_completed",
                                    "payment_id": str(payment.id),
                                    "amount": str(payment.montant_paye_ariary),
                                    "server_correlation_id": server_correlation_id,
                                    "transaction_reference": transaction_reference,
                                },
                                send_email=True,
                            )

                            logger.info(f"Payment confirmation notification created: " f"payment_id={payment.id}")

                        except Exception as e:
                            logger.error(
                                f"Failed to create notification: " f"payment_id={payment.id}, " f"error={str(e)}"
                            )

                        # Use unified payment success service (same workflow as cash and Stripe)
                        try:
                            from payments.services.payment_success_service import PaymentSuccessService

                            qr_code, error = PaymentSuccessService.handle_payment_success(
                                payment=payment, send_notification=False  # Notification already sent above
                            )

                            if error:
                                logger.error(
                                    f"Error in payment success handler: " f"payment_id={payment.id}, " f"error={error}"
                                )
                            elif qr_code:
                                logger.info(
                                    f"MVola payment success handled: "
                                    f"payment_id={payment.id}, "
                                    f"qr_code_token={qr_code.token}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Failed to handle payment success: " f"payment_id={payment.id}, " f"error={str(e)}"
                            )

                elif mvola_transaction_status.lower() in ["failed", "error", "cancelled", "canceled"]:
                    # Payment failed
                    if payment.mvola_status != "failed":
                        payment.mvola_status = "failed"
                        payment.statut = "ANNULE"

                        logger.warning(
                            f"Payment status updated to failed: "
                            f"payment_id={payment.id}, "
                            f"server_correlation_id={server_correlation_id}"
                        )

                else:
                    # Keep as pending
                    payment.mvola_status = "pending"

                    logger.info(
                        f"Payment status remains pending: "
                        f"payment_id={payment.id}, "
                        f"server_correlation_id={server_correlation_id}, "
                        f"mvola_status={mvola_transaction_status}"
                    )

                # Save payment
                payment.save()

            # Return JSON response with current status
            return Response(
                {
                    "success": True,
                    "status": mvola_transaction_status,
                    "transaction_reference": transaction_reference,
                    "payment_status": payment.statut,
                    "mvola_status": payment.mvola_status,
                    "amount": str(payment.montant_du_ariary),
                    "payment_id": str(payment.id),
                    "vehicle_plate": payment.vehicule_plaque.plaque_immatriculation,
                    "tax_year": payment.annee_fiscale,
                },
                status=status.HTTP_200_OK,
            )

        except MvolaAuthenticationError as e:
            logger.error(
                f"MVola authentication error during status check: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Erreur d'authentification MVola. Veuillez réessayer plus tard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except MvolaAPIError as e:
            logger.error(
                f"MVola API error during status check: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Erreur lors de la communication avec MVola. Veuillez réessayer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.exception(
                f"Unexpected error during status check: "
                f"payment_id={payment.id}, "
                f"server_correlation_id={server_correlation_id}, "
                f"error={str(e)}"
            )
            return Response(
                {"success": False, "error": "Une erreur inattendue s'est produite. Veuillez réessayer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
