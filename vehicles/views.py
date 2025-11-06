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
from .forms import VehiculeForm, VehiculeSearchForm, VehicleDocumentUploadForm
from .models import DocumentVehicule


class VehiculeListView(LoginRequiredMixin, ListView):
    """List user's vehicles with search functionality"""
    model = Vehicule
    template_name = 'vehicles/vehicule_list_velzon.html'
    context_object_name = 'vehicules'
    paginate_by = 10
    login_url = reverse_lazy('core:login')
    
    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user
        if is_admin_user(self.request.user):
            return ['administration/vehicles/vehicule_list.html']
        # Regular users (including company users) should use regular templates
        return [self.template_name]
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle list"""
        from administration.mixins import is_admin_user
        if is_admin_user(request.user):
            return redirect('administration:admin_vehicle_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter vehicles by current user and search criteria"""
        # All users (including company users) should only see their own vehicles
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
    
    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user
        if is_admin_user(self.request.user):
            return ['administration/vehicles/vehicule_detail.html']
        # Regular users (including company users) should use regular templates
        return [self.template_name]
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle detail"""
        from administration.mixins import is_admin_user
        if is_admin_user(request.user):
            return redirect('administration:admin_vehicle_detail', pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
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
            'documents': DocumentVehicule.objects.filter(vehicule=vehicule).order_by('-created_at'),
            'document_form': VehicleDocumentUploadForm(),
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


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
@login_required
@require_POST
def upload_vehicle_document(request, pk):
    """Upload a document for a specific vehicle (owner or admin)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)

    # Permissions: owner or admin users
    from administration.mixins import is_admin_user
    if not (vehicule.proprietaire == request.user or is_admin_user(request.user)):
        messages.error(request, _('Permission refusée pour télécharger un document pour ce véhicule.'))
        return redirect('vehicles:vehicle_detail', pk=pk)

    form = VehicleDocumentUploadForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.vehicule = vehicule
        doc.uploaded_by = request.user
        doc.save()

        # Send notification to owner
        try:
            from notifications.services import NotificationService
            langue = 'fr'
            if hasattr(vehicule.proprietaire, 'profile'):
                langue = vehicule.proprietaire.profile.langue_preferee
            NotificationService.create_notification(
                user=vehicule.proprietaire,
                type_notification='document_uploaded',
                titre=_('Nouveau document pour votre véhicule'),
                contenu=_('Le document %(doc)s a été ajouté pour le véhicule %(plaque)s.') % {
                    'doc': doc.get_document_type_display(),
                    'plaque': vehicule.plaque_immatriculation
                },
                langue=langue,
                metadata={'vehicule': vehicule.plaque_immatriculation, 'document_id': str(doc.id)}
            )
        except Exception:
            # Do not block on notification errors
            pass

        messages.success(request, _('Document téléchargé avec succès.'))
    else:
        messages.error(request, _('Échec du téléchargement du document. Veuillez vérifier les informations.'))

    return redirect('vehicles:vehicle_detail', pk=pk)


class VehiculeCreateView(LoginRequiredMixin, CreateView):
    """Create new vehicle"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicles/vehicule_form_velzon.html'
    login_url = reverse_lazy('core:login')
    
    def get_template_names(self):
        """Use appropriate template based on user type"""
        # Admin users should use admin templates
        from administration.mixins import is_admin_user
        if is_admin_user(self.request.user):
            return ['administration/vehicles/vehicule_form.html']
        # Regular users (including company users) should use regular templates
        return [self.template_name]
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle creation"""
        from administration.mixins import is_admin_user
        if is_admin_user(request.user):
            return redirect('administration:admin_vehicle_create')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Set the owner based on user permissions"""
        from administration.mixins import is_admin_user
        
        if is_admin_user(self.request.user):
            # Admin can assign vehicle to selected owner
            if form.cleaned_data.get('proprietaire'):
                form.instance.proprietaire = form.cleaned_data['proprietaire']
            else:
                # If no owner selected, assign to admin (fallback)
                form.instance.proprietaire = self.request.user
        else:
            # Non-admin users can only create vehicles for themselves
            form.instance.proprietaire = self.request.user
            
        response = super().form_valid(form)
        
        # Create notification for vehicle added
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(self.request.user, 'profile'):
            langue = self.request.user.profile.langue_preferee
        
        NotificationService.create_vehicle_added_notification(
            user=form.instance.proprietaire,  # Send notification to the actual owner
            vehicle=form.instance,
            langue=langue
        )
        
        # Success message varies based on who added the vehicle
        if is_admin_user(self.request.user) and form.instance.proprietaire != self.request.user:
            messages.success(
                self.request, 
                _('Véhicule %(plaque)s ajouté avec succès pour %(owner)s!') % {
                    'plaque': form.instance.plaque_immatriculation,
                    'owner': form.instance.proprietaire.get_full_name() or form.instance.proprietaire.username
                }
            )
        else:
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
        context['current_year'] = timezone.now().year
        return context


class VehiculeUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing vehicle"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicles/vehicule_form.html'
    login_url = reverse_lazy('core:login')
    
    def get_template_names(self):
        """Use Velzon template for fleet managers (non-individual users)"""
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type != 'individual':
            return ['administration/vehicles/vehicule_form.html']
        return [self.template_name]
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle edit"""
        from administration.mixins import is_admin_user
        if is_admin_user(request.user):
            return redirect('administration:admin_vehicle_edit', pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Only allow editing user's own vehicles, or all vehicles for fleet managers"""
        # For fleet management: users with non-individual profiles can edit any vehicle
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type != 'individual':
            return Vehicule.objects.all()
        else:
            # Individual users can only edit their own vehicles
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
    
    def get_template_names(self):
        """Use Velzon template for fleet managers (non-individual users)"""
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type != 'individual':
            return ['administration/vehicles/vehicule_confirm_delete.html']
        return [self.template_name]
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect admin users to admin vehicle delete"""
        from administration.mixins import is_admin_user
        if is_admin_user(request.user):
            return redirect('administration:admin_vehicle_delete', pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Only allow deleting user's own vehicles, or all vehicles for fleet managers"""
        # For fleet management: users with non-individual profiles can delete any vehicle
        if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type != 'individual':
            return Vehicule.objects.all()
        else:
            # Individual users can only delete their own vehicles
            return Vehicule.objects.filter(proprietaire=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Soft delete - set est_actif=False instead of actual deletion"""
        self.object = self.get_object()
        vehicle_plaque = self.object.plaque_immatriculation
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


# Admin-specific vehicle views
class AdminVehiculeListView(LoginRequiredMixin, ListView):
    """Admin view for listing all vehicles"""
    model = Vehicule
    template_name = 'administration/vehicles/vehicule_list.html'
    context_object_name = 'vehicules'
    paginate_by = 20
    login_url = reverse_lazy('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        from administration.mixins import is_admin_user
        if not is_admin_user(request.user):
            return redirect('administration:admin_login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Get all vehicles for admin view"""
        return Vehicule.objects.select_related('proprietaire').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Gestion des Véhicules - Administration')
        context['is_admin_view'] = True
        return context


class AdminVehiculeCreateView(LoginRequiredMixin, CreateView):
    """Admin view for creating vehicles"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'administration/vehicles/vehicule_form.html'
    login_url = reverse_lazy('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        from administration.mixins import is_admin_user
        if not is_admin_user(request.user):
            return redirect('administration:admin_login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Set the owner based on admin selection"""
        from administration.mixins import is_admin_user
        
        if is_admin_user(self.request.user):
            # Admin can assign vehicle to selected owner
            if form.cleaned_data.get('proprietaire'):
                form.instance.proprietaire = form.cleaned_data['proprietaire']
            else:
                # If no owner selected, assign to admin (fallback)
                form.instance.proprietaire = self.request.user
        else:
            # This shouldn't happen due to dispatch check, but safety fallback
            form.instance.proprietaire = self.request.user
            
        response = super().form_valid(form)
        
        # Create notification for vehicle added
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(form.instance.proprietaire, 'profile'):
            langue = form.instance.proprietaire.profile.langue_preferee
        
        NotificationService.create_vehicle_added_notification(
            user=form.instance.proprietaire,  # Send notification to the actual owner
            vehicle=form.instance,
            langue=langue
        )
        
        # Success message for admin
        messages.success(
            self.request, 
            _('Véhicule %(plaque)s ajouté avec succès pour %(owner)s!') % {
                'plaque': form.instance.plaque_immatriculation,
                'owner': form.instance.proprietaire.get_full_name() or form.instance.proprietaire.username
            }
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('administration:admin_vehicle_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Ajouter un Véhicule - Administration')
        context['form_action'] = _('Ajouter')
        context['is_admin_view'] = True
        return context


class AdminVehiculeDetailView(LoginRequiredMixin, DetailView):
    """Admin view for vehicle details"""
    model = Vehicule
    template_name = 'administration/vehicles/vehicule_detail.html'
    context_object_name = 'vehicule'
    login_url = reverse_lazy('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        from administration.mixins import is_admin_user
        if not is_admin_user(request.user):
            return redirect('administration:admin_login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Détails du Véhicule - Administration')
        context['is_admin_view'] = True
        
        # Calculate tax for display
        vehicule = self.get_object()
        context['calculated_tax'] = self._calculate_tax(vehicule)
        
        return context
    
    def _calculate_tax(self, vehicule):
        """Calculate tax for the vehicle"""
        try:
            from payments.models import GrilleTarifaire
            from django.utils import timezone
            
            # Get current year
            current_year = timezone.now().year
            
            # Check if exempt
            if vehicule.categorie_vehicule in ['Ambulance', 'Sapeurs-pompiers', 'Convention_internationale']:
                return 0
            
            # Calculate age
            age = current_year - vehicule.date_premiere_circulation.year
            
            # Find applicable tax rate
            tax_grid = GrilleTarifaire.objects.filter(
                annee_fiscale=current_year,
                est_active=True,
                source_energie=vehicule.source_energie,
                puissance_min_cv__lte=vehicule.puissance_fiscale_cv,
                age_min_annees__lte=age
            ).filter(
                models.Q(puissance_max_cv__gte=vehicule.puissance_fiscale_cv) | models.Q(puissance_max_cv__isnull=True)
            ).filter(
                models.Q(age_max_annees__gte=age) | models.Q(age_max_annees__isnull=True)
            ).order_by('-puissance_min_cv', '-age_min_annees')
            
            for rate in tax_grid:
                if rate.est_applicable(vehicule):
                    return rate.montant_ariary
            
            # No applicable rate found
            return None
            
        except Exception:
            return None


class AdminVehiculeUpdateView(LoginRequiredMixin, UpdateView):
    """Admin view for updating vehicles"""
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'administration/vehicles/vehicule_form.html'
    login_url = reverse_lazy('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        from administration.mixins import is_admin_user
        if not is_admin_user(request.user):
            return redirect('administration:admin_login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Handle admin vehicle update"""
        from administration.mixins import is_admin_user
        
        if is_admin_user(self.request.user):
            # Admin can change vehicle owner
            if form.cleaned_data.get('proprietaire'):
                form.instance.proprietaire = form.cleaned_data['proprietaire']
        
        response = super().form_valid(form)
        
        messages.success(
            self.request, 
            _('Véhicule %(plaque)s modifié avec succès!') % {
                'plaque': form.instance.plaque_immatriculation
            }
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('administration:admin_vehicle_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Modifier le Véhicule - Administration')
        context['form_action'] = _('Modifier')
        context['is_admin_view'] = True
        return context


class AdminVehiculeDeleteView(LoginRequiredMixin, DeleteView):
    """Admin view for deleting vehicles"""
    model = Vehicule
    template_name = 'administration/vehicles/vehicule_confirm_delete.html'
    success_url = reverse_lazy('administration:admin_vehicle_list')
    login_url = reverse_lazy('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        from administration.mixins import is_admin_user
        if not is_admin_user(request.user):
            return redirect('administration:admin_login')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Handle vehicle deletion with success message"""
        vehicule = self.get_object()
        plaque = vehicule.plaque_immatriculation
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            self.request,
            _('Véhicule %(plaque)s supprimé avec succès!') % {'plaque': plaque}
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Supprimer le Véhicule - Administration')
        context['is_admin_view'] = True
        return context