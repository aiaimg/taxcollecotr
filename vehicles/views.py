from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from decimal import Decimal

from .models import Vehicule, GrilleTarifaire
from .forms import VehiculeForm, VehiculeSearchForm


class VehiculeListView(LoginRequiredMixin, ListView):
    """List user's vehicles with search functionality"""
    model = Vehicule
    template_name = 'vehicles/vehicule_list.html'
    context_object_name = 'vehicules'
    paginate_by = 10
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        """Filter vehicles by current user and search criteria"""
        queryset = Vehicule.objects.filter(
            proprietaire=self.request.user,
            est_actif=True
        ).order_by('-created_at')
        
        # Apply search filters
        form = VehiculeSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(
                    plaque_immatriculation__icontains=search
                )
            
            source_energie = form.cleaned_data.get('source_energie')
            if source_energie:
                queryset = queryset.filter(source_energie=source_energie)
            
            categorie_vehicule = form.cleaned_data.get('categorie_vehicule')
            if categorie_vehicule:
                queryset = queryset.filter(categorie_vehicule=categorie_vehicule)
            
            type_vehicule = form.cleaned_data.get('type_vehicule')
            if type_vehicule:
                queryset = queryset.filter(type_vehicule=type_vehicule)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = VehiculeSearchForm(self.request.GET)
        context['page_title'] = _('Mes Véhicules')
        return context


class VehiculeDetailView(LoginRequiredMixin, DetailView):
    """Vehicle detail view with tax calculation"""
    model = Vehicule
    template_name = 'vehicles/vehicule_detail.html'
    context_object_name = 'vehicule'
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        """Only show user's own vehicles"""
        return Vehicule.objects.filter(proprietaire=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = self.get_object()
        
        # Calculate current year tax
        current_year = timezone.now().year
        tax_amount = self.calculate_tax(vehicule, current_year)
        
        context.update({
            'page_title': f'{_("Véhicule")} {vehicule.plaque_immatriculation}',
            'current_year': current_year,
            'tax_amount': tax_amount,
            'is_exempt': vehicule.est_exonere(),
        })
        
        return context
    
    def calculate_tax(self, vehicule, year):
        """Calculate tax amount for a vehicle"""
        if vehicule.est_exonere():
            return Decimal('0.00')
        
        try:
            tax_grid = GrilleTarifaire.objects.filter(
                annee_fiscale=year,
                est_active=True
            )
            
            for rate in tax_grid:
                if rate.est_applicable(vehicule):
                    return rate.montant_ariary
            
            # No applicable rate found
            return None
            
        except Exception:
            return None


class VehiculeCreateView(LoginRequiredMixin, CreateView):
    """Create new vehicle"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicles/vehicule_form.html'
    login_url = reverse_lazy('core:login')
    
    def form_valid(self, form):
        """Set the current user as owner"""
        form.instance.proprietaire = self.request.user
        response = super().form_valid(form)
        
        # Create notification for vehicle added
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(self.request.user, 'profile'):
            langue = self.request.user.profile.langue_preferee
        
        NotificationService.create_vehicle_added_notification(
            user=self.request.user,
            vehicle=form.instance,
            langue=langue
        )
        
        messages.success(
            self.request, 
            _('Véhicule %(plaque)s ajouté avec succès!') % {
                'plaque': form.instance.plaque_immatriculation
            }
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('vehicles:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Ajouter un Véhicule')
        context['form_action'] = _('Ajouter')
        return context


class VehiculeUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing vehicle"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicles/vehicule_form.html'
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        """Only allow editing user's own vehicles"""
        return Vehicule.objects.filter(proprietaire=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create notification for vehicle updated
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(self.request.user, 'profile'):
            langue = self.request.user.profile.langue_preferee
        
        NotificationService.create_vehicle_updated_notification(
            user=self.request.user,
            vehicle=form.instance,
            langue=langue
        )
        
        messages.success(
            self.request, 
            _('Véhicule %(plaque)s modifié avec succès!') % {
                'plaque': form.instance.plaque_immatriculation
            }
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('vehicles:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Modifier le Véhicule')
        context['form_action'] = _('Modifier')
        return context


class VehiculeDeleteView(LoginRequiredMixin, DeleteView):
    """Soft delete vehicle (set est_actif=False)"""
    model = Vehicule
    template_name = 'vehicles/vehicule_confirm_delete.html'
    success_url = reverse_lazy('vehicles:list')
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        """Only allow deleting user's own vehicles"""
        return Vehicule.objects.filter(proprietaire=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Soft delete - set est_actif=False instead of actual deletion"""
        self.object = self.get_object()
        vehicle_plaque = self.object.numero_plaque
        self.object.est_actif = False
        self.object.save()
        
        # Create notification for vehicle deleted
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(request.user, 'profile'):
            langue = request.user.profile.langue_preferee
        
        NotificationService.create_vehicle_deleted_notification(
            user=request.user,
            vehicle_plaque=vehicle_plaque,
            langue=langue
        )
        
        messages.success(
            request, 
            _('Véhicule %(plaque)s supprimé avec succès!') % {
                'plaque': self.object.plaque_immatriculation
            }
        )
        
        return redirect(self.success_url)


def calculate_tax_ajax(request):
    """AJAX endpoint for real-time tax calculation"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            puissance_fiscale_cv = int(request.POST.get('puissance_fiscale_cv', 0))
            source_energie = request.POST.get('source_energie', '')
            date_premiere_circulation = request.POST.get('date_premiere_circulation', '')
            categorie_vehicule = request.POST.get('categorie_vehicule', 'Personnel')
            
            if not all([puissance_fiscale_cv, source_energie, date_premiere_circulation]):
                return JsonResponse({
                    'success': False,
                    'message': _('Données incomplètes')
                })
            
            # Parse date
            from datetime import datetime
            try:
                date_circulation = datetime.strptime(date_premiere_circulation, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': _('Format de date invalide')
                })
            
            # Check if exempt
            if categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']:
                return JsonResponse({
                    'success': True,
                    'tax_amount': '0.00',
                    'is_exempt': True,
                    'message': _('Véhicule exonéré de taxe')
                })
            
            # Calculate age
            current_year = timezone.now().year
            age = current_year - date_circulation.year
            
            # Find applicable tax rate
            tax_rates = GrilleTarifaire.objects.filter(
                annee_fiscale=current_year,
                est_active=True,
                source_energie=source_energie,
                puissance_min_cv__lte=puissance_fiscale_cv,
                age_min_annees__lte=age
            ).filter(
                Q(puissance_max_cv__isnull=True) | Q(puissance_max_cv__gte=puissance_fiscale_cv)
            ).filter(
                Q(age_max_annees__isnull=True) | Q(age_max_annees__gte=age)
            ).first()
            
            if tax_rates:
                return JsonResponse({
                    'success': True,
                    'tax_amount': str(tax_rates.montant_ariary),
                    'is_exempt': False,
                    'message': _('Taxe calculée avec succès')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': _('Aucun tarif trouvé pour ce véhicule')
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': _('Erreur lors du calcul')
            })
    
    return JsonResponse({
        'success': False,
        'message': _('Méthode non autorisée')
    })