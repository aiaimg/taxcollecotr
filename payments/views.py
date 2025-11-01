from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import qrcode
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from vehicles.models import Vehicule
from vehicles.services import TaxCalculationService
from .models import PaiementTaxe, QRCode
from .forms import PaiementTaxeForm
from .services import PaymentServiceFactory


class PaymentListView(LoginRequiredMixin, ListView):
    """List user's payments"""
    model = PaiementTaxe
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        return PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=self.request.user
        ).select_related('vehicule_plaque').order_by('-created_at')


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """Payment detail view"""
    model = PaiementTaxe
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        return PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=self.request.user
        ).select_related('vehicule_plaque')


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Create payment for a vehicle"""
    model = PaiementTaxe
    form_class = PaiementTaxeForm
    template_name = 'payments/payment_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plaque = self.kwargs['plaque']
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=plaque, proprietaire=self.request.user)
        
        # Calculate tax
        tax_service = TaxCalculationService()
        current_year = timezone.now().year
        tax_info = tax_service.calculate_tax(vehicule, current_year)
        
        context.update({
            'vehicule': vehicule,
            'tax_info': tax_info,
            'current_year': current_year
        })
        return context
    
    def form_valid(self, form):
        plaque = self.kwargs['plaque']
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=plaque, proprietaire=self.request.user)
        
        # Calculate tax
        tax_service = TaxCalculationService()
        current_year = timezone.now().year
        tax_info = tax_service.calculate_tax(vehicule, current_year)
        
        if tax_info['is_exempt']:
            messages.error(self.request, _('Ce véhicule est exempté de taxe.'))
            return redirect('vehicles:detail', plaque=plaque)
        
        if not tax_info['amount']:
            messages.error(self.request, _('Impossible de calculer la taxe pour ce véhicule.'))
            return redirect('vehicles:detail', plaque=plaque)
        
        # Check if payment already exists for this year
        existing_payment = PaiementTaxe.objects.filter(
            vehicule_plaque=plaque,
            annee_fiscale=current_year,
            statut__in=['PAYE', 'EN_ATTENTE']
        ).first()
        
        if existing_payment:
            messages.warning(self.request, _('Un paiement existe déjà pour ce véhicule cette année.'))
            return redirect('payments:detail', pk=existing_payment.pk)
        
        # Create payment
        payment = form.save(commit=False)
        payment.vehicule_plaque = plaque
        payment.annee_fiscale = current_year
        payment.montant_du = tax_info['amount']
        payment.montant_paye = 0
        payment.statut = 'EN_ATTENTE'
        
        # Handle Mobile Money payments
        methode_paiement = form.cleaned_data['methode_paiement']
        numero_telephone = form.cleaned_data.get('numero_telephone')
        
        mobile_money_methods = ['mvola', 'orange_money', 'airtel_money']
        
        if methode_paiement in mobile_money_methods and numero_telephone:
            try:
                # Initiate Mobile Money payment
                payment_result = PaymentServiceFactory.initiate_payment(
                    payment_method=methode_paiement,
                    amount=float(tax_info['amount']),
                    phone=numero_telephone,
                    reference=plaque,
                    description=f'Taxe véhicule {plaque} - {current_year}'
                )
                
                if payment_result['success']:
                    payment.transaction_id = payment_result['transaction_id']
                    payment.details_supplementaires = f"Mobile Money initié: {payment_result.get('message', '')}"
                    messages.success(self.request, payment_result['message'])
                    
                    # If there's a payment URL, redirect to it
                    if payment_result.get('payment_url'):
                        payment.save()
                        return redirect(payment_result['payment_url'])
                else:
                    messages.error(self.request, payment_result['error'])
                    return self.form_invalid(form)
                    
            except Exception as e:
                messages.error(self.request, _('Erreur lors de l\'initiation du paiement Mobile Money.'))
                return self.form_invalid(form)
        
        payment.save()
        messages.success(self.request, _('Paiement créé avec succès.'))
        return redirect('payments:detail', pk=payment.pk)


class GenerateQRCodeView(LoginRequiredMixin, View):
    """Generate QR code for a paid tax"""
    
    def post(self, request, payment_id):
        payment = get_object_or_404(
            PaiementTaxe,
            pk=payment_id,
            vehicule_plaque__proprietaire=request.user
        )
        
        if not payment.est_paye():
            return JsonResponse({
                'success': False,
                'message': _('Le paiement doit être effectué avant de générer le QR code.')
            })
        
        # Create or get existing QR code
        qr_code, created = QRCode.objects.get_or_create(
            vehicule_plaque=payment.vehicule_plaque,
            annee_fiscale=payment.annee_fiscale,
            defaults={
                'date_expiration': timezone.now() + timedelta(days=365),
                'est_actif': True
            }
        )
        
        if not created and not qr_code.est_valide():
            # Reactivate expired QR code
            qr_code.est_actif = True
            qr_code.date_expiration = timezone.now() + timedelta(days=365)
            qr_code.save()
        
        # Create notification for QR code generation
        if created:
            from notifications.services import NotificationService
            langue = 'fr'
            if hasattr(request.user, 'profile'):
                langue = request.user.profile.langue_preferee
            
            NotificationService.create_qr_generated_notification(
                user=request.user,
                qr_code=qr_code,
                langue=langue
            )
        
        return JsonResponse({
            'success': True,
            'qr_token': qr_code.token,
            'qr_url': request.build_absolute_uri(
                reverse('core:qr_verification') + f'?code={qr_code.token}'
            )
        })


class DownloadQRCodeView(LoginRequiredMixin, View):
    """Download QR code as image"""
    
    def get(self, request, payment_id):
        payment = get_object_or_404(
            PaiementTaxe,
            pk=payment_id,
            vehicule_plaque__proprietaire=request.user
        )
        
        if not payment.est_paye():
            messages.error(request, _('Le paiement doit être effectué avant de télécharger le QR code.'))
            return redirect('payments:detail', pk=payment_id)
        
        qr_code = get_object_or_404(
            QRCode,
            vehicule_plaque=payment.vehicule_plaque,
            annee_fiscale=payment.annee_fiscale
        )
        
        # Generate QR code image
        qr_url = request.build_absolute_uri(
            reverse('core:qr_verification') + f'?code={qr_code.token}'
        )
        
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
        img = Image.new('RGB', (img_width, img_height), 'white')
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
        draw.text(((img_width - title_width) // 2, 50), title, fill='black', font=title_font)
        
        # Add vehicle info
        y_pos = 120
        vehicle_info = [
            f"Plaque: {payment.vehicule_plaque.plaque_immatriculation}",
            f"Année fiscale: {payment.annee_fiscale}",
            f"Montant payé: {payment.montant_paye_ariary} Ar",
            f"Date de paiement: {payment.date_paiement.strftime('%d/%m/%Y')}",
        ]
        
        for info in vehicle_info:
            info_bbox = draw.textbbox((0, 0), info, font=info_font)
            info_width = info_bbox[2] - info_bbox[0]
            draw.text(((img_width - info_width) // 2, y_pos), info, fill='black', font=info_font)
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
            f"Valide jusqu'au: {qr_code.date_expiration.strftime('%d/%m/%Y')}"
        ]
        
        y_pos = qr_y + qr_size + 30
        for instruction in instructions:
            inst_bbox = draw.textbbox((0, 0), instruction, font=small_font)
            inst_width = inst_bbox[2] - inst_bbox[0]
            draw.text(((img_width - inst_width) // 2, y_pos), instruction, fill='gray', font=small_font)
            y_pos += 25
        
        # Save to BytesIO
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        response = HttpResponse(img_io.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="qr_code_{payment.vehicule_plaque.plaque_immatriculation}_{payment.annee_fiscale}.png"'
        
        return response


class QRCodeGenerateView(LoginRequiredMixin, DetailView):
    """Generate QR code for a payment"""
    model = PaiementTaxe
    template_name = 'payments/qr_code_generate.html'
    context_object_name = 'payment'
    
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
        
        context['qr_code'] = qr_code
        return context


class PaymentStatusCheckView(LoginRequiredMixin, View):
    """Check Mobile Money payment status"""
    
    def post(self, request, pk):
        payment = get_object_or_404(PaiementTaxe, pk=pk)
        
        # Ensure user owns the vehicle
        vehicule = get_object_or_404(Vehicule, plaque_immatriculation=payment.vehicule_plaque, proprietaire=request.user)
        
        if not payment.transaction_id:
            return JsonResponse({'error': 'Aucun ID de transaction trouvé'}, status=400)
        
        try:
            # Check payment status
            status_result = PaymentServiceFactory.check_payment_status(
                payment_method=payment.methode_paiement,
                transaction_id=payment.transaction_id
            )
            
            if status_result['success']:
                # Update payment status if changed
                if status_result['status'] == 'COMPLETED' and payment.statut != 'PAYE':
                    payment.statut = 'PAYE'
                    payment.montant_paye = payment.montant_du
                    payment.date_paiement = timezone.now()
                    payment.save()
                    
                    # Create notification for successful payment
                    from notifications.services import NotificationService
                    vehicule = Vehicule.objects.get(plaque_immatriculation=payment.vehicule_plaque)
                    langue = 'fr'
                    if hasattr(vehicule.proprietaire, 'profile'):
                        langue = vehicule.proprietaire.profile.langue_preferee
                    
                    NotificationService.create_payment_confirmation_notification(
                        user=vehicule.proprietaire,
                        payment=payment,
                        langue=langue
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'status': 'PAYE',
                        'message': 'Paiement confirmé avec succès!'
                    })
                elif status_result['status'] == 'FAILED':
                    payment.statut = 'ECHEC'
                    payment.save()
                    
                    # Create notification for failed payment
                    from notifications.services import NotificationService
                    vehicule = Vehicule.objects.get(plaque_immatriculation=payment.vehicule_plaque)
                    langue = 'fr'
                    if hasattr(vehicule.proprietaire, 'profile'):
                        langue = vehicule.proprietaire.profile.langue_preferee
                    
                    NotificationService.create_payment_failed_notification(
                        user=vehicule.proprietaire,
                        vehicle_plaque=payment.vehicule_plaque,
                        langue=langue
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'status': 'ECHEC',
                        'message': 'Le paiement a échoué.'
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'status': payment.statut,
                        'message': status_result.get('message', 'Paiement en cours...')
                    })
            else:
                return JsonResponse({'error': status_result['error']}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': 'Erreur lors de la vérification du statut'}, status=500)


class DownloadReceiptView(LoginRequiredMixin, View):
    """Download payment receipt as PDF"""
    
    def get(self, request, payment_id):
        payment = get_object_or_404(
            PaiementTaxe,
            pk=payment_id,
            vehicule_plaque__proprietaire=request.user
        )
        
        if not payment.est_paye():
            messages.error(request, _('Le paiement doit être effectué avant de télécharger le reçu.'))
            return redirect('payments:detail', pk=payment_id)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        story.append(Paragraph("REÇU DE PAIEMENT TAXE VÉHICULE", title_style))
        story.append(Spacer(1, 20))
        
        # Payment info table
        data = [
            ['Plaque d\'immatriculation:', payment.vehicule_plaque.plaque_immatriculation],
            ['Année fiscale:', str(payment.annee_fiscale)],
            ['Montant payé:', f"{payment.montant_paye_ariary} Ariary"],
            ['Date de paiement:', payment.date_paiement.strftime('%d/%m/%Y %H:%M')],
            ['Méthode de paiement:', payment.get_methode_paiement_display() or 'N/A'],
            ['Référence transaction:', payment.transaction_id],
            ['Statut:', payment.get_statut_display()],
        ]
        
        table = Table(data, colWidths=[150, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Vehicle info
        story.append(Paragraph("INFORMATIONS DU VÉHICULE", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        vehicle_data = [
            ['Puissance fiscale:', f"{payment.vehicule_plaque.puissance_fiscale_cv} CV"],
            ['Cylindrée:', f"{payment.vehicule_plaque.cylindree_cm3} cm³" if payment.vehicule_plaque.cylindree_cm3 else 'N/A'],
            ['Source d\'énergie:', payment.vehicule_plaque.get_source_energie_display()],
            ['Catégorie:', payment.vehicule_plaque.get_categorie_vehicule_display()],
            ['Type:', payment.vehicule_plaque.get_type_vehicule_display()],
            ['Date de circulation:', payment.vehicule_plaque.date_premiere_circulation.strftime('%d/%m/%Y')],
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[150, 200])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(vehicle_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recu_{payment.vehicule_plaque.plaque_immatriculation}_{payment.annee_fiscale}.pdf"'
        
        return response
