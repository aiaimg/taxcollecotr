from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count
from vehicles.models import GrilleTarifaire, Vehicule
from payments.models import QRCode, PaiementTaxe
from .models import EntrepriseProfile
from django.utils import timezone
import json
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import xlsxwriter

class HomeView(TemplateView):
    """Homepage with tax grid display and public information"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current year tax grid
        current_year = timezone.now().year
        tax_grid = GrilleTarifaire.objects.filter(
            annee_fiscale=current_year,
            est_active=True
        ).order_by('puissance_min_cv', 'source_energie')
        
        context.update({
            'tax_grid': tax_grid,
            'current_year': current_year,
            'page_title': _('Plateforme de Collecte de Taxe Véhicules - Madagascar'),
            'page_description': _('Plateforme numérique pour la déclaration et le paiement des taxes véhicules à Madagascar'),
        })
        
        return context

class QRVerificationView(TemplateView):
    """Public QR code verification page"""
    template_name = 'core/qr_verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Vérification QR Code'),
            'page_description': _('Vérifiez la validité d\'un QR code de paiement de taxe véhicule'),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle QR code verification via AJAX"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            qr_code = request.POST.get('qr_code', '').strip()
            
            if not qr_code:
                return JsonResponse({
                    'success': False,
                    'message': _('Veuillez saisir un code QR')
                })
            
            try:
                qr_obj = get_object_or_404(QRCode, code=qr_code)
                
                # Check if QR code is valid
                if not qr_obj.est_actif:
                    return JsonResponse({
                        'success': False,
                        'message': _('Ce QR code n\'est plus actif')
                    })
                
                if qr_obj.date_expiration and qr_obj.date_expiration < timezone.now():
                    return JsonResponse({
                        'success': False,
                        'message': _('Ce QR code a expiré')
                    })
                
                # QR code is valid
                return JsonResponse({
                    'success': True,
                    'message': _('QR code valide'),
                    'data': {
                        'vehicule_plaque': qr_obj.vehicule_plaque,
                        'annee_fiscale': qr_obj.annee_fiscale,
                        'montant_paye': str(qr_obj.paiement.montant_ariary),
                        'date_paiement': qr_obj.paiement.date_paiement.strftime('%d/%m/%Y %H:%M'),
                        'statut_paiement': qr_obj.paiement.get_statut_display(),
                        'date_expiration': qr_obj.date_expiration.strftime('%d/%m/%Y %H:%M') if qr_obj.date_expiration else None,
                    }
                })
                
            except QRCode.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': _('QR code non trouvé')
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': _('Erreur lors de la vérification')
                })
        
        # If not AJAX, redirect to GET
        return self.get(request, *args, **kwargs)

class AboutView(TemplateView):
    """About page"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('À propos'),
            'page_description': _('Informations sur la plateforme de collecte de taxe véhicules'),
        })
        return context

class ContactView(TemplateView):
    """Contact page"""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Contact'),
            'page_description': _('Contactez-nous pour toute question ou assistance'),
        })
        return context


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('core:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Inscription'),
            'page_description': _('Créez votre compte pour accéder à la plateforme'),
        })
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after successful registration
        login(self.request, self.object)
        
        # Create welcome notification (also handled by signal, but this ensures it's created)
        from notifications.services import NotificationService
        NotificationService.create_welcome_notification(
            user=self.object,
            langue='fr'
        )
        
        messages.success(self.request, _('Votre compte a été créé avec succès! Consultez vos notifications.'))
        return response
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to home
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'registration/profile.html'
    login_url = reverse_lazy('core:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Mon Profil'),
            'page_description': _('Gérez vos informations personnelles'),
        })
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """User profile edit view"""
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration/profile_edit.html'
    success_url = reverse_lazy('core:profile')
    login_url = reverse_lazy('core:login')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Modifier le Profil'),
            'page_description': _('Modifiez vos informations personnelles'),
        })
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create notification for profile updated
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(self.request.user, 'profile'):
            langue = self.request.user.profile.langue_preferee
        
        NotificationService.create_profile_updated_notification(
            user=self.request.user,
            langue=langue
        )
        
        messages.success(self.request, _('Votre profil a été mis à jour avec succès!'))
        return response


# Fleet Manager Views
class FleetManagerMixin(LoginRequiredMixin):
    """Mixin to ensure user has fleet manager access"""
    login_url = reverse_lazy('core:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'entreprise_profile'):
            messages.error(request, _('Accès réservé aux gestionnaires de flotte'))
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class FleetDashboardView(FleetManagerMixin, TemplateView):
    """Fleet Manager Dashboard"""
    template_name = 'fleet/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = timezone.now().year
        
        # Get all vehicles for this company
        vehicles = Vehicule.objects.filter(proprietaire=user)
        
        # Calculate statistics
        total_vehicles = vehicles.count()
        paid_vehicles = vehicles.filter(
            paiements__annee_fiscale=current_year,
            paiements__statut='PAID'
        ).distinct().count()
        
        pending_payments = vehicles.exclude(
            paiements__annee_fiscale=current_year,
            paiements__statut='PAID'
        ).count()
        
        total_amount_due = 0
        total_amount_paid = 0
        
        for vehicle in vehicles:
            # Calculate tax for each vehicle
            from vehicles.services import TaxCalculationService
            tax_service = TaxCalculationService()
            tax_info = tax_service.calculate_tax(vehicle, current_year)
            
            if not tax_info['is_exempt'] and tax_info['amount']:
                total_amount_due += tax_info['amount']
                
                # Check if paid
                payment = PaiementTaxe.objects.filter(
                    vehicule_plaque=vehicle,
                    annee_fiscale=current_year,
                    statut='PAID'
                ).first()
                
                if payment:
                    total_amount_paid += payment.montant_paye
        
        context.update({
            'total_vehicles': total_vehicles,
            'paid_vehicles': paid_vehicles,
            'pending_payments': pending_payments,
            'total_amount_due': total_amount_due,
            'total_amount_paid': total_amount_paid,
            'current_year': current_year,
            'page_title': _('Tableau de Bord Flotte'),
        })
        
        return context


class FleetVehicleListView(FleetManagerMixin, ListView):
    """Fleet vehicle list with batch operations"""
    model = Vehicule
    template_name = 'fleet/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vehicule.objects.filter(
            proprietaire=self.request.user
        ).order_by('plaque_immatriculation')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search) |
                Q(type_vehicule__icontains=search) |
                Q(source_energie__icontains=search)
            )
        
        # Filter by energy source
        energy = self.request.GET.get('energy')
        if energy:
            queryset = queryset.filter(source_energie=energy)
        
        # Filter by vehicle type
        vehicle_type = self.request.GET.get('type')
        if vehicle_type:
            queryset = queryset.filter(type_vehicule=vehicle_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search': self.request.GET.get('search', ''),
            'selected_energy': self.request.GET.get('energy', ''),
            'selected_type': self.request.GET.get('type', ''),
            'energy_choices': Vehicule.SOURCE_ENERGIE_CHOICES,
            'type_choices': Vehicule.TYPE_VEHICULE_CHOICES,
            'page_title': _('Gestion de Flotte'),
        })
        return context


class FleetBatchPaymentView(FleetManagerMixin, TemplateView):
    """Batch payment processing for multiple vehicles"""
    template_name = 'fleet/batch_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = timezone.now().year
        
        # Get vehicles that need payment
        vehicles = Vehicule.objects.filter(proprietaire=user).exclude(
            paiements__annee_fiscale=current_year,
            paiements__statut='PAID'
        )
        
        # Calculate tax for each vehicle
        vehicle_taxes = []
        total_amount = 0
        
        from vehicles.services import TaxCalculationService
        tax_service = TaxCalculationService()
        
        for vehicle in vehicles:
            tax_info = tax_service.calculate_tax(vehicle, current_year)
            if not tax_info['is_exempt'] and tax_info['amount']:
                vehicle_taxes.append({
                    'vehicle': vehicle,
                    'tax_amount': tax_info['amount'],
                    'is_exempt': False
                })
                total_amount += tax_info['amount']
            else:
                vehicle_taxes.append({
                    'vehicle': vehicle,
                    'tax_amount': 0,
                    'is_exempt': True
                })
        
        context.update({
            'vehicle_taxes': vehicle_taxes,
            'total_amount': total_amount,
            'current_year': current_year,
            'page_title': _('Paiement en Lot'),
        })
        
        return context


class FleetExportView(FleetManagerMixin, TemplateView):
    """Export fleet data and accounting reports"""
    template_name = 'fleet/export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Export Comptable'),
        })
        return context


class FleetExportCSVView(FleetManagerMixin, TemplateView):
    """Export fleet vehicles to CSV"""
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="flotte_vehicules.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Plaque', 'Type', 'Puissance (CV)', 'Source Énergie', 
            'Date Circulation', 'Catégorie', 'Statut Taxe'
        ])
        
        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year
        
        for vehicle in vehicles:
            # Check payment status
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle,
                annee_fiscale=current_year,
                statut='PAID'
            ).first()
            
            status = 'Payé' if payment else 'Non payé'
            
            writer.writerow([
                vehicle.plaque_immatriculation,
                vehicle.get_type_vehicule_display(),
                vehicle.puissance_fiscale_cv,
                vehicle.get_source_energie_display(),
                vehicle.date_premiere_circulation.strftime('%d/%m/%Y'),
                vehicle.get_categorie_vehicule_display(),
                status
            ])
        
        return response


class FleetExportExcelView(FleetManagerMixin, TemplateView):
    """Export fleet payments to Excel"""
    
    def get(self, request, *args, **kwargs):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Paiements Flotte')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '#,##0 "Ar"'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Headers
        headers = [
            'Plaque', 'Type Véhicule', 'Puissance (CV)', 'Source Énergie',
            'Montant Taxe', 'Date Paiement', 'Statut', 'Transaction ID'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year
        row = 1
        
        from vehicles.services import TaxCalculationService
        tax_service = TaxCalculationService()
        
        for vehicle in vehicles:
            tax_info = tax_service.calculate_tax(vehicle, current_year)
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle,
                annee_fiscale=current_year
            ).first()
            
            worksheet.write(row, 0, vehicle.plaque_immatriculation)
            worksheet.write(row, 1, vehicle.get_type_vehicule_display())
            worksheet.write(row, 2, vehicle.puissance_fiscale_cv)
            worksheet.write(row, 3, vehicle.get_source_energie_display())
            
            if tax_info['is_exempt']:
                worksheet.write(row, 4, 'Exonéré')
                worksheet.write(row, 6, 'Exonéré')
            else:
                worksheet.write(row, 4, float(tax_info['amount'] or 0), money_format)
                if payment:
                    worksheet.write(row, 5, payment.date_paiement, date_format)
                    worksheet.write(row, 6, payment.get_statut_display())
                    worksheet.write(row, 7, payment.transaction_id or '')
                else:
                    worksheet.write(row, 6, 'Non payé')
            
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 12)  # Plaque
        worksheet.set_column('B:B', 15)  # Type
        worksheet.set_column('C:C', 12)  # Puissance
        worksheet.set_column('D:D', 15)  # Source
        worksheet.set_column('E:E', 15)  # Montant
        worksheet.set_column('F:F', 12)  # Date
        worksheet.set_column('G:G', 12)  # Statut
        worksheet.set_column('H:H', 20)  # Transaction
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="paiements_flotte.xlsx"'
        
        return response


class FleetExportPDFView(FleetManagerMixin, TemplateView):
    """Export fleet summary to PDF"""
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_flotte.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Rapport de Flotte", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Company info
        if hasattr(request.user, 'entreprise_profile'):
            company = request.user.entreprise_profile
            company_info = Paragraph(f"""
                <b>Entreprise:</b> {company.nom_entreprise}<br/>
                <b>Numéro de contribuable:</b> {company.numero_contribuable}<br/>
                <b>Date du rapport:</b> {timezone.now().strftime('%d/%m/%Y')}
            """, styles['Normal'])
            story.append(company_info)
            story.append(Spacer(1, 12))
        
        # Summary statistics
        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year
        
        total_vehicles = vehicles.count()
        paid_count = vehicles.filter(
            paiements__annee_fiscale=current_year,
            paiements__statut='PAID'
        ).distinct().count()
        
        summary = Paragraph(f"""
            <b>Résumé:</b><br/>
            • Total véhicules: {total_vehicles}<br/>
            • Véhicules payés: {paid_count}<br/>
            • Véhicules en attente: {total_vehicles - paid_count}
        """, styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))
        
        # Vehicle details table
        data = [['Plaque', 'Type', 'Puissance', 'Énergie', 'Statut']]
        
        from vehicles.services import TaxCalculationService
        tax_service = TaxCalculationService()
        
        for vehicle in vehicles:
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle,
                annee_fiscale=current_year,
                statut='PAID'
            ).first()
            
            status = 'Payé' if payment else 'Non payé'
            
            data.append([
                vehicle.plaque_immatriculation,
                vehicle.get_type_vehicule_display(),
                f"{vehicle.puissance_fiscale_cv} CV",
                vehicle.get_source_energie_display(),
                status
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        doc.build(story)
        return response
