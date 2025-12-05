import base64
import io
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView, TemplateView

import qrcode
import stripe
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from vehicles.models import Vehicule
from vehicles.services import TaxCalculationService

from .forms import PaiementTaxeForm
from .models import PaiementTaxe, QRCode, StripeConfig
from .services import PaymentServiceFactory

logger = logging.getLogger(__name__)


class PaymentListView(LoginRequiredMixin, ListView):
    """List user's payments"""

    model = PaiementTaxe
    template_name = "payments/payment_list.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        return (
            PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=self.request.user)
            .select_related("vehicule_plaque")
            .order_by("-created_at")
        )


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """Payment detail view"""

    model = PaiementTaxe
    template_name = "payments/payment_detail.html"
    context_object_name = "payment"

    def get_queryset(self):
        return PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=self.request.user).select_related(
            "vehicule_plaque"
        )


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Create payment for a vehicle"""

    model = PaiementTaxe
    form_class = PaiementTaxeForm
    template_name = "payments/payment_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plaque = self.kwargs["plaque"]
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=plaque, proprietaire=self.request.user)

        # Calculate tax
        tax_service = TaxCalculationService()
        current_year = timezone.now().year
        tax_info = tax_service.calculate_tax(vehicule, current_year)

        # Calculate MVola fee breakdown if tax amount is available
        mvola_fee_info = None
        if tax_info.get("amount"):
            from .services.mvola.fee_calculator import MvolaFeeCalculator

            mvola_fee_info = MvolaFeeCalculator.calculate_total_amount(tax_info["amount"])

        context.update(
            {
                "vehicule": vehicule,
                "tax_info": tax_info,
                "current_year": current_year,
                "mvola_fee_info": mvola_fee_info,
            }
        )
        return context

    def form_valid(self, form):
        plaque = self.kwargs["plaque"]
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=plaque, proprietaire=self.request.user)

        # Calculate tax
        tax_service = TaxCalculationService()
        current_year = timezone.now().year
        tax_info = tax_service.calculate_tax(vehicule, current_year)

        if tax_info["is_exempt"]:
            messages.error(self.request, _("Ce véhicule est exempté de taxe."))
            return redirect("vehicles:detail", plaque=plaque)

        if not tax_info["amount"]:
            messages.error(self.request, _("Impossible de calculer la taxe pour ce véhicule."))
            return redirect("vehicles:detail", plaque=plaque)

        # Check if payment already exists for this year (exclude ANNULE)
        existing_payment = (
            PaiementTaxe.objects.filter(vehicule_plaque=plaque, annee_fiscale=current_year)
            .exclude(statut="ANNULE")
            .first()
        )

        if existing_payment:
            if existing_payment.statut == "EN_ATTENTE":
                if existing_payment.methode_paiement == "cash":
                    messages.info(
                        self.request,
                        _("Un paiement en espèces est en attente d'approbation pour ce véhicule cette année."),
                    )
                else:
                    messages.info(self.request, _("Un paiement est en cours pour ce véhicule cette année."))
            else:
                messages.warning(self.request, _("Un paiement existe déjà pour ce véhicule cette année."))
            return redirect("payments:detail", pk=existing_payment.pk)

        # Get payment method and phone number
        methode_paiement = form.cleaned_data["methode_paiement"]
        numero_telephone = form.cleaned_data.get("numero_telephone")

        # Handle MVola payment initiation
        if methode_paiement == "mvola" and numero_telephone:
            try:
                from .services.mvola.api_client import MvolaAPIClient
                from .services.mvola.exceptions import MvolaAPIError, MvolaAuthenticationError, MvolaValidationError
                from .services.mvola.fee_calculator import MvolaFeeCalculator
                from .services.mvola.validators import validate_msisdn

                # Validate MSISDN format
                try:
                    customer_msisdn = validate_msisdn(numero_telephone)
                except MvolaValidationError as e:
                    messages.error(self.request, str(e))
                    return self.form_invalid(form)

                # Calculate total amount with 3% fee
                base_tax_amount = tax_info["amount"]
                fee_calculation = MvolaFeeCalculator.calculate_total_amount(base_tax_amount)
                total_amount = fee_calculation["total_amount"]
                platform_fee = fee_calculation["platform_fee"]

                # Prepare payment description
                description = f"Taxe véhicule {plaque} - {current_year}"

                # Initialize MVola API client and initiate payment
                mvola_client = MvolaAPIClient()
                payment_result = mvola_client.initiate_payment(
                    amount=total_amount,
                    customer_msisdn=customer_msisdn,
                    description=description,
                    vehicle_plate=plaque,
                    tax_year=current_year,
                )

                if not payment_result["success"]:
                    error_message = payment_result.get("error", "Erreur lors de l'initiation du paiement MVola.")
                    messages.error(self.request, error_message)
                    return self.form_invalid(form)

                # Extract MVola response data
                x_correlation_id = payment_result["x_correlation_id"]
                server_correlation_id = payment_result["server_correlation_id"]
                mvola_status = payment_result.get("status", "pending")

                # Create PaiementTaxe record with MVola fields populated
                with transaction.atomic():
                    payment = PaiementTaxe.objects.create(
                        vehicule_plaque=vehicule,
                        annee_fiscale=current_year,
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

                messages.success(
                    self.request, _("Paiement MVola initié. Veuillez confirmer sur votre téléphone MVola.")
                )

                # Redirect to payment status page
                return redirect("payments:detail", pk=payment.pk)

            except MvolaAuthenticationError as e:
                logger.error(f"MVola authentication error: {str(e)}")
                messages.error(self.request, _("Erreur d'authentification MVola. Veuillez réessayer plus tard."))
                return self.form_invalid(form)

            except MvolaAPIError as e:
                logger.error(f"MVola API error: {str(e)}")
                messages.error(self.request, _("Erreur lors de la communication avec MVola. Veuillez réessayer."))
                return self.form_invalid(form)

            except Exception as e:
                logger.exception(f"Unexpected error during MVola payment initiation: {str(e)}")
                messages.error(self.request, _("Une erreur inattendue s'est produite. Veuillez réessayer."))
                return self.form_invalid(form)

        # Handle other Mobile Money payments (Orange Money, Airtel Money)
        elif methode_paiement in ["orange_money", "airtel_money"] and numero_telephone:
            try:
                # Initiate Mobile Money payment using PaymentServiceFactory
                payment_result = PaymentServiceFactory.initiate_payment(
                    payment_method=methode_paiement,
                    amount=float(tax_info["amount"]),
                    phone=numero_telephone,
                    reference=plaque,
                    description=f"Taxe véhicule {plaque} - {current_year}",
                )

                if payment_result["success"]:
                    # Create payment record
                    payment = form.save(commit=False)
                    payment.vehicule_plaque = plaque
                    payment.annee_fiscale = current_year
                    payment.montant_du = tax_info["amount"]
                    payment.montant_paye = 0
                    payment.statut = "EN_ATTENTE"
                    payment.transaction_id = payment_result["transaction_id"]
                    payment.details_supplementaires = f"Mobile Money initié: {payment_result.get('message', '')}"
                    payment.save()

                    messages.success(self.request, payment_result["message"])

                    # If there's a payment URL, redirect to it
                    if payment_result.get("payment_url"):
                        return redirect(payment_result["payment_url"])

                    return redirect("payments:detail", pk=payment.pk)
                else:
                    messages.error(self.request, payment_result["error"])
                    return self.form_invalid(form)

            except Exception as e:
                logger.exception(f"Error initiating {methode_paiement} payment: {str(e)}")
                messages.error(self.request, _("Erreur lors de l'initiation du paiement Mobile Money."))
                return self.form_invalid(form)

        # Handle other payment methods (cash, bank card, etc.)
        else:
            payment = form.save(commit=False)
            payment.vehicule_plaque = plaque
            payment.annee_fiscale = current_year
            payment.montant_du = tax_info["amount"]
            payment.montant_paye = 0
            payment.statut = "EN_ATTENTE"
            payment.save()

            messages.success(self.request, _("Paiement créé avec succès."))
            return redirect("payments:detail", pk=payment.pk)


class GenerateQRCodeView(LoginRequiredMixin, View):
    """Generate QR code for a paid tax"""

    def post(self, request, payment_id):
        payment = get_object_or_404(PaiementTaxe, pk=payment_id, vehicule_plaque__proprietaire=request.user)

        if not payment.est_paye():
            return JsonResponse(
                {"success": False, "message": _("Le paiement doit être effectué avant de générer le QR code.")}
            )

        # Create or get existing QR code
        qr_code, created = QRCode.objects.get_or_create(
            vehicule_plaque=payment.vehicule_plaque,
            annee_fiscale=payment.annee_fiscale,
            defaults={"date_expiration": timezone.now() + timedelta(days=365), "est_actif": True},
        )

        if not created and not qr_code.est_valide():
            # Reactivate expired QR code
            qr_code.est_actif = True
            qr_code.date_expiration = timezone.now() + timedelta(days=365)
            qr_code.save()

        # Create notification for QR code generation
        if created:
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(request.user, "profile"):
                langue = request.user.profile.langue_preferee

            NotificationService.create_qr_generated_notification(user=request.user, qr_code=qr_code, langue=langue)

        # Get QR code verification URL using unified service
        from .services.payment_success_service import PaymentSuccessService

        qr_verification_url = PaymentSuccessService.get_qr_verification_url(qr_code, request=request)

        return JsonResponse(
            {
                "success": True,
                "qr_token": qr_code.token,
                "qr_url": qr_verification_url,
                "message": _("QR code généré avec succès. Ce code peut être vérifié à /app/qr-verification/"),
            }
        )


class DownloadQRCodeView(LoginRequiredMixin, View):
    """Download QR code as image"""

    def get(self, request, pk):
        payment = get_object_or_404(PaiementTaxe, pk=pk, vehicule_plaque__proprietaire=request.user)

        if not payment.est_paye():
            messages.error(request, _("Le paiement doit être effectué avant de télécharger le QR code."))
            return redirect("payments:detail", pk=pk)

        # Get or create QR code (should already exist if payment is paid)
        qr_code, created = QRCode.objects.get_or_create(
            vehicule_plaque=payment.vehicule_plaque,
            annee_fiscale=payment.annee_fiscale,
            defaults={"date_expiration": timezone.now() + timedelta(days=365), "est_actif": True},
        )

        # Generate QR code image with verification URL
        # The QR code contains a URL to /app/qr-verification/?code={token}
        # This is the same verification endpoint used by all payment methods
        from .services.payment_success_service import PaymentSuccessService

        qr_url = PaymentSuccessService.get_qr_verification_url(qr_code, request=request)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Create a larger image with vehicle info
        img_width, img_height = 800, 1000
        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)

        # Try to load a font
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            info_font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Add title
        title = "TAXE VÉHICULE PAYÉE"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 50), title, fill="black", font=title_font)

        # Add vehicle info
        y_pos = 120
        payment_date = payment.date_paiement.strftime("%d/%m/%Y") if payment.date_paiement else "N/A"
        # Format amount: remove decimals, add space as thousands separator
        try:
            amount = int(float(payment.montant_paye_ariary or 0))
            amount_formatted = f"{amount:,}".replace(",", " ")
        except (ValueError, TypeError):
            amount_formatted = str(payment.montant_paye_ariary or 0)
        vehicle_info = [
            f"Plaque: {payment.vehicule_plaque.plaque_immatriculation}",
            f"Année fiscale: {payment.annee_fiscale}",
            f"Montant payé: {amount_formatted} Ar",
            f"Date de paiement: {payment_date}",
        ]

        for info in vehicle_info:
            info_bbox = draw.textbbox((0, 0), info, font=info_font)
            info_width = info_bbox[2] - info_bbox[0]
            draw.text(((img_width - info_width) // 2, y_pos), info, fill="black", font=info_font)
            y_pos += 40

        # Add QR code
        qr_size = 400
        qr_img_resized = qr_img.resize((qr_size, qr_size))
        qr_x = (img_width - qr_size) // 2
        qr_y = y_pos + 20
        img.paste(qr_img_resized, (qr_x, qr_y))

        # Add instructions
        instructions = [
            "Scannez ce QR code pour vérifier",
            "le paiement de la taxe véhicule",
            f"Valide jusqu'au: {qr_code.date_expiration.strftime('%d/%m/%Y')}",
        ]

        y_pos = qr_y + qr_size + 30
        for instruction in instructions:
            inst_bbox = draw.textbbox((0, 0), instruction, font=small_font)
            inst_width = inst_bbox[2] - inst_bbox[0]
            draw.text(((img_width - inst_width) // 2, y_pos), instruction, fill="gray", font=small_font)
            y_pos += 25

        # Save to BytesIO
        img_io = io.BytesIO()
        img.save(img_io, format="PNG", quality=95)
        img_io.seek(0)

        response = HttpResponse(img_io.getvalue(), content_type="image/png")
        response["Content-Disposition"] = (
            f'attachment; filename="qr_code_{payment.vehicule_plaque.plaque_immatriculation}_{payment.annee_fiscale}.png"'
        )

        return response


class QRCodeGenerateView(LoginRequiredMixin, DetailView):
    """Generate QR code for a payment"""

    model = PaiementTaxe
    template_name = "payments/qr_code_generate.html"
    context_object_name = "payment"

    def get_object(self):
        payment = super().get_object()
        # Ensure user owns the vehicle
        if payment.vehicule_plaque.proprietaire != self.request.user:
            raise Http404
        return payment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()

        # Generate QR code if not exists or expired
        qr_service = QRCodeService()
        qr_code = qr_service.generate_qr_code(payment)

        context["qr_code"] = qr_code
        return context


class PaymentStatusCheckView(LoginRequiredMixin, View):
    """Check Mobile Money payment status"""

    def post(self, request, pk):
        payment = get_object_or_404(PaiementTaxe, pk=pk)

        # Ensure user owns the vehicle
        vehicule = get_object_or_404(
            Vehicule, plaque_immatriculation=payment.vehicule_plaque, proprietaire=request.user
        )

        if not payment.transaction_id:
            return JsonResponse({"error": "Aucun ID de transaction trouvé"}, status=400)

        try:
            # Check payment status
            status_result = PaymentServiceFactory.check_payment_status(
                payment_method=payment.methode_paiement, transaction_id=payment.transaction_id
            )

            if status_result["success"]:
                # Update payment status if changed
                if status_result["status"] == "COMPLETED" and payment.statut != "PAYE":
                    payment.statut = "PAYE"
                    payment.montant_paye = payment.montant_du
                    payment.date_paiement = timezone.now()
                    payment.save()

                    # Create notification for successful payment
                    from notifications.services import NotificationService

                    vehicule = Vehicule.objects.get(plaque_immatriculation=payment.vehicule_plaque)
                    langue = "fr"
                    if hasattr(vehicule.proprietaire, "profile"):
                        langue = vehicule.proprietaire.profile.langue_preferee

                    NotificationService.create_payment_confirmation_notification(
                        user=vehicule.proprietaire, payment=payment, langue=langue
                    )

                    return JsonResponse(
                        {"success": True, "status": "PAYE", "message": "Paiement confirmé avec succès!"}
                    )
                elif status_result["status"] == "FAILED":
                    payment.statut = "ECHEC"
                    payment.save()

                    # Create notification for failed payment
                    from notifications.services import NotificationService

                    vehicule = Vehicule.objects.get(plaque_immatriculation=payment.vehicule_plaque)
                    langue = "fr"
                    if hasattr(vehicule.proprietaire, "profile"):
                        langue = vehicule.proprietaire.profile.langue_preferee

                    NotificationService.create_payment_failed_notification(
                        user=vehicule.proprietaire, vehicle_plaque=payment.vehicule_plaque, langue=langue
                    )

                    return JsonResponse({"success": True, "status": "ECHEC", "message": "Le paiement a échoué."})
                else:
                    return JsonResponse(
                        {
                            "success": True,
                            "status": payment.statut,
                            "message": status_result.get("message", "Paiement en cours..."),
                        }
                    )
            else:
                return JsonResponse({"error": status_result["error"]}, status=400)

        except Exception as e:
            return JsonResponse({"error": "Erreur lors de la vérification du statut"}, status=500)


class DownloadReceiptView(LoginRequiredMixin, View):
    """Download payment receipt as PDF"""

    def get(self, request, pk):
        payment = get_object_or_404(
            PaiementTaxe.objects.select_related("vehicule_plaque", "vehicule_plaque__type_vehicule"),
            pk=pk,
            vehicule_plaque__proprietaire=request.user,
        )

        if not payment.est_paye():
            messages.error(request, _("Le paiement doit être effectué avant de télécharger le reçu."))
            return redirect("payments:detail", pk=pk)

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
        )
        story.append(Paragraph("REÇU DE PAIEMENT TAXE VÉHICULE", title_style))
        story.append(Spacer(1, 20))

        # Format amount: remove decimals, add space as thousands separator
        try:
            amount = int(float(payment.montant_paye_ariary or 0))
            amount_formatted = f"{amount:,}".replace(",", " ")
        except (ValueError, TypeError):
            amount_formatted = str(payment.montant_paye_ariary or 0)

        # Format payment date
        payment_date_str = payment.date_paiement.strftime("%d/%m/%Y %H:%M") if payment.date_paiement else "N/A"

        # Payment info table
        data = [
            ["Plaque d'immatriculation:", payment.vehicule_plaque.plaque_immatriculation],
            ["Année fiscale:", str(payment.annee_fiscale)],
            ["Montant payé:", f"{amount_formatted} Ar"],
            ["Date de paiement:", payment_date_str],
            ["Méthode de paiement:", payment.get_methode_paiement_display() or "N/A"],
            ["Référence transaction:", payment.transaction_id or "N/A"],
            ["Statut:", payment.get_statut_display()],
        ]

        table = Table(data, colWidths=[150, 200])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (1, 0), (1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 30))

        # Vehicle info
        story.append(Paragraph("INFORMATIONS DU VÉHICULE", styles["Heading2"]))
        story.append(Spacer(1, 10))

        # Get vehicle type name (ForeignKey, not choices field)
        type_vehicule_name = (
            payment.vehicule_plaque.type_vehicule.nom if payment.vehicule_plaque.type_vehicule else "N/A"
        )

        vehicle_data = [
            ["Puissance fiscale:", f"{payment.vehicule_plaque.puissance_fiscale_cv} CV"],
            [
                "Cylindrée:",
                f"{payment.vehicule_plaque.cylindree_cm3} cm³" if payment.vehicule_plaque.cylindree_cm3 else "N/A",
            ],
            ["Source d'énergie:", payment.vehicule_plaque.get_source_energie_display()],
            ["Catégorie:", payment.vehicule_plaque.get_categorie_vehicule_display()],
            ["Type:", type_vehicule_name],
            ["Date de circulation:", payment.vehicule_plaque.date_premiere_circulation.strftime("%d/%m/%Y")],
        ]

        vehicle_table = Table(vehicle_data, colWidths=[150, 200])
        vehicle_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (1, 0), (1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(vehicle_table)
        story.append(Spacer(1, 30))

        # Footer
        footer_text = f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="recu_{payment.vehicule_plaque.plaque_immatriculation}_{payment.annee_fiscale}.pdf"'
        )

        return response


# --- Stripe Integration Views ---


class StripePaymentInitView(LoginRequiredMixin, View):
    """Initialize Stripe payment and render payment page"""

    template_name = "payments/stripe_payment.html"

    def get(self, request, plaque):
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=plaque, proprietaire=request.user)
        current_year = timezone.now().year
        tax_service = TaxCalculationService()
        tax_info = tax_service.calculate_tax(vehicule, current_year)

        if tax_info["is_exempt"]:
            messages.error(request, _("Ce véhicule est exempté de taxe."))
            return redirect("vehicles:vehicle_detail", pk=plaque)

        amount = tax_info["amount"]
        if not amount:
            messages.error(request, _("Impossible de calculer la taxe pour ce véhicule."))
            return redirect("vehicles:vehicle_detail", pk=plaque)

        client_secret = None
        payment_id = None
        # Resolve Stripe configuration from active StripeConfig or settings
        active_cfg = StripeConfig.get_active()
        publishable_key = (
            active_cfg.publishable_key if active_cfg and active_cfg.publishable_key else settings.STRIPE_PUBLISHABLE_KEY
        )
        secret_key = active_cfg.secret_key if active_cfg and active_cfg.secret_key else settings.STRIPE_SECRET_KEY
        currency = (active_cfg.currency if active_cfg and active_cfg.currency else settings.STRIPE_CURRENCY).lower()
        success_url = active_cfg.success_url if active_cfg and active_cfg.success_url else settings.STRIPE_SUCCESS_URL

        try:
            if secret_key:
                stripe.api_key = secret_key
                amount_stripe = int(amount * 100)

                # Create or retrieve customer (basic creation for dev)
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}",
                    metadata={"user_id": request.user.id},
                )

                intent = stripe.PaymentIntent.create(
                    amount=amount_stripe,
                    currency=currency,
                    customer=customer.id,
                    metadata={
                        "vehicle_id": vehicule.id,
                        "user_id": request.user.id,
                        "vehicle_plate": vehicule.plaque_immatriculation,
                    },
                    description=f"Taxe annuelle véhicule - {vehicule.plaque_immatriculation}",
                    receipt_email=request.user.email,
                )

                paiement = PaiementTaxe.objects.create(
                    vehicule_plaque=vehicule,
                    annee_fiscale=current_year,
                    montant_du_ariary=amount,
                    montant_paye_ariary=Decimal("0"),
                    methode_paiement="carte_bancaire",
                    statut="EN_ATTENTE",
                    stripe_payment_intent_id=intent.id,
                    stripe_customer_id=customer.id,
                    amount_stripe=amount_stripe,
                    billing_email=request.user.email,
                    billing_name=f"{request.user.first_name} {request.user.last_name}",
                    currency_stripe=currency.upper(),
                )

                client_secret = intent.client_secret
                payment_id = str(paiement.id)
            else:
                # Fallback for development without keys
                client_secret = "test_client_secret"
                payment_id = "00000000-0000-0000-0000-000000000000"
                logger.warning("Stripe keys not configured; rendering payment page in fallback mode.")

        except Exception as e:
            logger.error(f"Erreur création Payment Intent: {str(e)}")
            messages.error(request, _("Erreur lors de l'initialisation du paiement."))
            return redirect("vehicles:vehicle_detail", pk=plaque)

        context = {
            "vehicle": vehicule,
            "montant_taxe": amount,
            "client_secret": client_secret,
            "stripe_publishable_key": publishable_key,
            "stripe_success_url": success_url,
            "payment_id": payment_id,
        }
        return render(request, self.template_name, context)


class PaymentSuccessView(LoginRequiredMixin, View):
    """
    Payment success view for Stripe payments
    Note: QR code is automatically generated in the webhook handler
    This view just displays the success page
    """

    def get(self, request):
        payment_id = request.GET.get("payment_id")
        paiement = get_object_or_404(PaiementTaxe, id=payment_id, vehicule_plaque__proprietaire=request.user)

        if paiement.stripe_status == "succeeded" or paiement.est_paye():
            # QR code should already be generated by webhook, but ensure it exists
            # Use get_or_create to avoid duplicates (same workflow as other payment methods)
            qr_code, created = QRCode.objects.get_or_create(
                vehicule_plaque=paiement.vehicule_plaque,
                annee_fiscale=paiement.annee_fiscale,
                defaults={"date_expiration": timezone.now() + timedelta(days=365), "est_actif": True},
            )

            context = {"paiement": paiement, "success": True, "qr_code": qr_code}
        else:
            context = {"success": False, "error": _("Paiement non confirmé")}

        return render(request, "payments/payment_success.html", context)


class PaymentCancelView(LoginRequiredMixin, View):
    def get(self, request):
        payment_id = request.GET.get("payment_id")
        if payment_id:
            PaiementTaxe.objects.filter(id=payment_id, vehicule_plaque__proprietaire=request.user).update(
                stripe_status="canceled", statut="ANNULE"
            )
        return render(request, "payments/payment_cancel.html")


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    payload = request.body

    try:
        active_cfg = StripeConfig.get_active()
        webhook_secret = (
            active_cfg.webhook_secret if active_cfg and active_cfg.webhook_secret else settings.STRIPE_WEBHOOK_SECRET
        )
        if not webhook_secret:
            logger.error("Stripe webhook secret not configured")
            return HttpResponse(status=400)

        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

        from .models import StripeWebhookEvent

        webhook_event = StripeWebhookEvent.objects.create(
            stripe_event_id=event["id"], type=event["type"], data=event["data"]
        )

        obj = event["data"]["object"]
        if event["type"] == "payment_intent.succeeded":
            _handle_payment_intent_succeeded(obj)
        elif event["type"] == "payment_intent.payment_failed":
            _handle_payment_intent_failed(obj)

        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return HttpResponse(status=400)


def _handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful Stripe payment - update payment status and generate QR code
    This ensures the same workflow as cash and MVola payments
    """
    try:
        paiement = PaiementTaxe.objects.get(stripe_payment_intent_id=payment_intent["id"])
        paiement.stripe_status = "succeeded"
        paiement.statut = "PAYE"
        paiement.date_paiement = timezone.now()
        paiement.montant_paye_ariary = paiement.montant_du_ariary
        charges = payment_intent.get("charges", {}).get("data", [])
        if charges:
            charge = charges[0]
            paiement.stripe_charge_id = charge.get("id")
            paiement.stripe_receipt_url = charge.get("receipt_url")
        paiement.save()

        # Use unified payment success service (same workflow as cash and MVola)
        from .services.payment_success_service import PaymentSuccessService

        qr_code, error = PaymentSuccessService.handle_payment_success(payment=paiement, send_notification=True)

        if error:
            logger.error(f"Error in payment success handler: {error}")
        elif qr_code:
            logger.info(f"Stripe payment success handled: payment_id={paiement.id}, qr_code_token={qr_code.token}")

    except PaiementTaxe.DoesNotExist:
        logger.error(f"Paiement non trouvé pour intent: {payment_intent['id']}")
    except Exception as e:
        logger.error(f"Error handling Stripe payment success: {str(e)}")


def _handle_payment_intent_failed(payment_intent):
    try:
        paiement = PaiementTaxe.objects.get(stripe_payment_intent_id=payment_intent["id"])
        paiement.stripe_status = "failed"
        paiement.statut = "IMPAYE"
        paiement.save()
    except PaiementTaxe.DoesNotExist:
        logger.error(f"Paiement non trouvé pour intent: {payment_intent['id']}")


# --- QR Code Verification Views ---


class QRCodeVerifyView(View):
    """Verify QR code - accessible to verification agents"""

    template_name = "payments/qr_verify.html"

    def get(self, request, code):
        """Display QR code verification page"""
        try:
            # Use token field for lookup (code parameter is the token)
            qr_code = QRCode.objects.select_related(
                "vehicule_plaque", "vehicule_plaque__proprietaire", "vehicule_plaque__type_vehicule"
            ).get(token=code)

            # Increment scan count
            qr_code.nombre_scans += 1
            qr_code.derniere_verification = timezone.now()
            qr_code.save(update_fields=["nombre_scans", "derniere_verification"])

            # Determine status
            now = timezone.now()
            is_valid = qr_code.est_actif and qr_code.date_expiration >= now.date()

            # Get payment status - query payment by vehicle and year
            payment_status = None
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=qr_code.vehicule_plaque, annee_fiscale=qr_code.annee_fiscale
            ).first()
            if payment:
                payment_status = payment.statut

            context = {
                "qr_code": qr_code,
                "payment": payment,
                "is_valid": is_valid,
                "payment_status": payment_status,
                "verification_time": now,
            }

            # Log verification if user is an agent
            if request.user.is_authenticated and hasattr(request.user, "agent_verification"):
                from administration.models import VerificationQR

                # Determine verification status
                if not qr_code.est_actif:
                    statut = "invalide"
                elif qr_code.date_expiration < now.date():
                    statut = "expire"
                else:
                    statut = "valide"

                VerificationQR.objects.create(
                    agent=request.user.agent_verification,
                    qr_code=qr_code,
                    statut_verification=statut,
                    notes=f"Vérification via interface web",
                )

            return render(request, self.template_name, context)

        except QRCode.DoesNotExist:
            context = {"error": "QR Code invalide ou introuvable", "token": code}
            return render(request, self.template_name, context, status=404)


class QRCodeImageView(View):
    """Generate QR code image"""

    def get(self, request, code):
        """Generate and return QR code image"""
        try:
            # Use token field for lookup (code parameter is the token)
            qr_code_obj = QRCode.objects.get(token=code)

            # Generate verification URL
            verify_url = request.build_absolute_uri(reverse("payments:qr_verify", kwargs={"code": code}))

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verify_url)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Save to BytesIO
            img_io = io.BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)

            return HttpResponse(img_io.getvalue(), content_type="image/png")

        except QRCode.DoesNotExist:
            return HttpResponse("QR Code not found", status=404)


class QRCodeVerifyAPIView(View):
    """API endpoint for QR code verification"""

    def get(self, request, code):
        """Verify QR code and return JSON response"""
        try:
            # Use token field for lookup (code parameter is the token)
            qr_code = QRCode.objects.select_related(
                "vehicule_plaque", "vehicule_plaque__proprietaire", "vehicule_plaque__type_vehicule"
            ).get(token=code)

            # Increment scan count
            qr_code.nombre_scans += 1
            qr_code.derniere_verification = timezone.now()
            qr_code.save(update_fields=["nombre_scans", "derniere_verification"])

            # Determine status
            now = timezone.now()
            is_valid = qr_code.est_actif and qr_code.date_expiration >= now.date()

            # Get payment by vehicle and year
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=qr_code.vehicule_plaque, annee_fiscale=qr_code.annee_fiscale
            ).first()

            # Prepare response data
            data = {
                "success": True,
                "valid": is_valid,
                "token": qr_code.token,
                "vehicle": {
                    "plate": qr_code.vehicule_plaque.plaque_immatriculation,
                    "type": (
                        qr_code.vehicule_plaque.type_vehicule.nom if qr_code.vehicule_plaque.type_vehicule else None
                    ),
                    "owner": qr_code.vehicule_plaque.proprietaire.get_full_name()
                    or qr_code.vehicule_plaque.proprietaire.username,
                },
                "expiration_date": qr_code.date_expiration.isoformat(),
                "scan_count": qr_code.nombre_scans,
                "verification_time": now.isoformat(),
            }

            if payment:
                data["payment"] = {
                    "amount": str(payment.montant_paye_ariary) if payment.montant_paye_ariary else None,
                    "status": payment.statut,
                    "date": payment.date_paiement.isoformat() if payment.date_paiement else None,
                }

            # Log verification if user is an agent
            if request.user.is_authenticated and hasattr(request.user, "agent_verification"):
                from administration.models import VerificationQR

                if not qr_code.est_actif:
                    statut = "invalide"
                elif qr_code.date_expiration < now.date():
                    statut = "expire"
                else:
                    statut = "valide"

                VerificationQR.objects.create(
                    agent=request.user.agent_verification,
                    qr_code=qr_code,
                    statut_verification=statut,
                    notes=f"Vérification via API",
                )

                data["agent_verification"] = True

            return JsonResponse(data)

        except QRCode.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "QR Code invalide ou introuvable", "token": code}, status=404
            )


class QRVerificationDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for government agents to verify QR codes"""

    template_name = "payments/qr_verification_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        """Check if user is an agent government"""
        if not request.user.is_authenticated:
            return redirect("administration:agent_government_login")

        if not hasattr(request.user, "agent_verification") or not request.user.agent_verification.est_actif:
            messages.error(request, _("Accès refusé. Vous devez être un Agent Gouvernement actif."))
            return redirect("administration:agent_government_login")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.request.user.agent_verification

        # Get recent verifications
        from administration.models import VerificationQR

        recent_verifications = (
            VerificationQR.objects.filter(agent=agent)
            .select_related(
                "qr_code",
                "qr_code__vehicule_plaque",
                "qr_code__vehicule_plaque__type_vehicule",
                "qr_code__vehicule_plaque__proprietaire",
            )
            .order_by("-date_verification")[:10]
        )

        # Get statistics for today
        today = timezone.now().date()
        today_verifications = VerificationQR.objects.filter(agent=agent, date_verification__date=today).count()

        # Get statistics for this week
        week_start = today - timedelta(days=today.weekday())
        week_verifications = VerificationQR.objects.filter(agent=agent, date_verification__date__gte=week_start).count()

        # Get verification status counts
        status_counts = list(
            VerificationQR.objects.filter(agent=agent, date_verification__date=today)
            .values("statut_verification")
            .annotate(count=Count("id"))
        )

        # Calculate invalid/expired count
        invalid_expired_count = sum(
            s["count"] for s in status_counts if s["statut_verification"] in ["invalide", "expire"]
        )

        # Get valid count
        valid_count = next((s["count"] for s in status_counts if s["statut_verification"] == "valide"), 0)

        context.update(
            {
                "agent": agent,
                "recent_verifications": recent_verifications,
                "today_verifications": today_verifications,
                "week_verifications": week_verifications,
                "status_counts": status_counts,
                "invalid_expired_count": invalid_expired_count,
                "valid_count": valid_count,
            }
        )
        return context


class MvolaStatusView(LoginRequiredMixin, DetailView):
    """
    Display MVola payment status page.

    This view renders a dedicated status page for MVola payments showing:
    - Payment status indicator (initiated, pending, completed, failed)
    - MVola transaction details (server_correlation_id, customer_msisdn)
    - Fee breakdown (base amount, platform fee, total)
    - Check status button with auto-refresh functionality
    - Payment instructions in French
    """

    model = PaiementTaxe
    template_name = "payments/mvola_status.html"
    context_object_name = "payment"

    def get_queryset(self):
        """Ensure user can only view their own payments"""
        return PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=self.request.user, methode_paiement="mvola"
        ).select_related("vehicule_plaque", "vehicule_plaque__proprietaire")

    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        payment = self.get_object()

        # Calculate total amount with fee if not already paid
        if payment.mvola_platform_fee:
            total_amount = payment.montant_du_ariary + payment.mvola_platform_fee
        else:
            from .services.mvola.fee_calculator import MvolaFeeCalculator

            fee_info = MvolaFeeCalculator.calculate_total_amount(payment.montant_du_ariary)
            total_amount = fee_info["total_amount"]

        context["total_amount"] = total_amount

        return context
