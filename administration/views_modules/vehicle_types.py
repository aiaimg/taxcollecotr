"""
Vehicle Types Management Views for Admin Console
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from vehicles.models import Vehicule
from administration.views import AdminRequiredMixin
import csv
import json


class VehicleTypeListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """
    Enhanced list view for vehicle types with pagination, search, and filters
    """
    model = Vehicule
    template_name = 'administration/vehicle_types/list.html'
    context_object_name = 'vehicles'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Vehicule.objects.select_related('proprietaire').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search) |
                Q(proprietaire__username__icontains=search) |
                Q(proprietaire__first_name__icontains=search) |
                Q(proprietaire__last_name__icontains=search) |
                Q(proprietaire__email__icontains=search)
            )
        
        # Filter by vehicle type
        vehicle_type = self.request.GET.get('type_vehicule', '').strip()
        if vehicle_type:
            queryset = queryset.filter(type_vehicule=vehicle_type)
        
        # Filter by category
        category = self.request.GET.get('categorie_vehicule', '').strip()
        if category:
            queryset = queryset.filter(categorie_vehicule=category)
        
        # Filter by energy source
        energy_source = self.request.GET.get('source_energie', '').strip()
        if energy_source:
            queryset = queryset.filter(source_energie=energy_source)
        
        # Filter by active status
        status = self.request.GET.get('status', '').strip()
        if status == 'active':
            queryset = queryset.filter(est_actif=True)
        elif status == 'inactive':
            queryset = queryset.filter(est_actif=False)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['plaque_immatriculation', '-plaque_immatriculation', 
                      'created_at', '-created_at', 'type_vehicule', '-type_vehicule']
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter choices
        context['vehicle_types'] = Vehicule.TYPE_VEHICULE_CHOICES
        context['categories'] = Vehicule.CATEGORIE_CHOICES
        context['energy_sources'] = Vehicule.SOURCE_ENERGIE_CHOICES
        
        # Preserve filter values
        context['search'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('type_vehicule', '')
        context['selected_category'] = self.request.GET.get('categorie_vehicule', '')
        context['selected_energy'] = self.request.GET.get('source_energie', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        # Statistics
        context['total_count'] = self.get_queryset().count()
        context['active_count'] = Vehicule.objects.filter(est_actif=True).count()
        context['inactive_count'] = Vehicule.objects.filter(est_actif=False).count()
        
        return context


class VehicleTypeDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """
    Detail view for individual vehicle record
    """
    model = Vehicule
    template_name = 'administration/vehicle_types/detail.html'
    context_object_name = 'vehicle'
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object
        
        # Get related payments
        from payments.models import PaiementTaxe
        context['payments'] = PaiementTaxe.objects.filter(
            vehicule=vehicle
        ).order_by('-created_at')[:10]
        
        # Calculate statistics
        context['total_payments'] = PaiementTaxe.objects.filter(vehicule=vehicle).count()
        context['vehicle_age'] = vehicle.get_age_annees()
        context['is_exempt'] = vehicle.est_exonere()
        
        return context


class VehicleTypeCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """
    Create view for adding new vehicle records
    """
    model = Vehicule
    template_name = 'administration/vehicle_types/form.html'
    fields = [
        'plaque_immatriculation', 'proprietaire', 'puissance_fiscale_cv',
        'cylindree_cm3', 'source_energie', 'date_premiere_circulation',
        'categorie_vehicule', 'type_vehicule', 'specifications_techniques',
        'est_actif'
    ]
    success_url = reverse_lazy('administration:vehicle_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Véhicule {form.instance.plaque_immatriculation} créé avec succès.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la création du véhicule. Veuillez vérifier les champs.")
        return super().form_invalid(form)


class VehicleTypeUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """
    Update view for editing existing vehicle records
    """
    model = Vehicule
    template_name = 'administration/vehicle_types/form.html'
    fields = [
        'proprietaire', 'puissance_fiscale_cv', 'cylindree_cm3',
        'source_energie', 'date_premiere_circulation', 'categorie_vehicule',
        'type_vehicule', 'specifications_techniques', 'est_actif'
    ]
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def get_success_url(self):
        return reverse_lazy('administration:vehicle_type_detail', kwargs={'plaque': self.object.plaque_immatriculation})
    
    def form_valid(self, form):
        messages.success(self.request, f"Véhicule {form.instance.plaque_immatriculation} modifié avec succès.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la modification du véhicule. Veuillez vérifier les champs.")
        return super().form_invalid(form)


class VehicleTypeDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """
    Delete view for removing vehicle records
    """
    model = Vehicule
    template_name = 'administration/vehicle_types/confirm_delete.html'
    success_url = reverse_lazy('administration:vehicle_type_list')
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def delete(self, request, *args, **kwargs):
        vehicle = self.get_object()
        messages.success(request, f"Véhicule {vehicle.plaque_immatriculation} supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


def vehicle_type_export(request):
    """
    Export vehicle data to CSV or JSON format
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    format_type = request.GET.get('format', 'csv')
    
    # Get filtered queryset (reuse same filters as list view)
    queryset = Vehicule.objects.select_related('proprietaire').order_by('-created_at')
    
    # Apply filters
    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(plaque_immatriculation__icontains=search) |
            Q(proprietaire__username__icontains=search) |
            Q(proprietaire__first_name__icontains=search) |
            Q(proprietaire__last_name__icontains=search)
        )
    
    vehicle_type = request.GET.get('type_vehicule', '').strip()
    if vehicle_type:
        queryset = queryset.filter(type_vehicule=vehicle_type)
    
    category = request.GET.get('categorie_vehicule', '').strip()
    if category:
        queryset = queryset.filter(categorie_vehicule=category)
    
    energy_source = request.GET.get('source_energie', '').strip()
    if energy_source:
        queryset = queryset.filter(source_energie=energy_source)
    
    status = request.GET.get('status', '').strip()
    if status == 'active':
        queryset = queryset.filter(est_actif=True)
    elif status == 'inactive':
        queryset = queryset.filter(est_actif=False)
    
    # Limit to 10,000 records
    queryset = queryset[:10000]
    
    if format_type == 'json':
        # JSON export
        data = []
        for vehicle in queryset:
            data.append({
                'plaque_immatriculation': vehicle.plaque_immatriculation,
                'proprietaire': vehicle.proprietaire.username,
                'proprietaire_nom': vehicle.proprietaire.get_full_name(),
                'proprietaire_email': vehicle.proprietaire.email,
                'puissance_fiscale_cv': vehicle.puissance_fiscale_cv,
                'cylindree_cm3': vehicle.cylindree_cm3,
                'source_energie': vehicle.source_energie,
                'date_premiere_circulation': vehicle.date_premiere_circulation.isoformat(),
                'categorie_vehicule': vehicle.categorie_vehicule,
                'type_vehicule': vehicle.type_vehicule,
                'est_actif': vehicle.est_actif,
                'created_at': vehicle.created_at.isoformat(),
            })
        
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="vehicles_export.json"'
        return response
    
    else:
        # CSV export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vehicles_export.csv"'
        
        writer = csv.writer(response)
        # Write header
        writer.writerow([
            'Plaque', 'Propriétaire', 'Nom Complet', 'Email',
            'Puissance (CV)', 'Cylindrée (cm3)', 'Source Énergie',
            'Date 1ère Circulation', 'Catégorie', 'Type', 'Actif', 'Date Création'
        ])
        
        # Write data
        for vehicle in queryset:
            writer.writerow([
                vehicle.plaque_immatriculation,
                vehicle.proprietaire.username,
                vehicle.proprietaire.get_full_name(),
                vehicle.proprietaire.email,
                vehicle.puissance_fiscale_cv,
                vehicle.cylindree_cm3,
                vehicle.source_energie,
                vehicle.date_premiere_circulation.strftime('%Y-%m-%d'),
                vehicle.categorie_vehicule,
                vehicle.type_vehicule,
                'Oui' if vehicle.est_actif else 'Non',
                vehicle.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response


def vehicle_type_bulk_update(request):
    """
    AJAX endpoint for bulk operations on vehicle records
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        items = data.get('items', [])
        
        if not action or not items:
            return JsonResponse({'success': False, 'message': 'Missing action or items'}, status=400)
        
        # Get vehicles
        vehicles = Vehicule.objects.filter(plaque_immatriculation__in=items)
        count = vehicles.count()
        
        if action == 'activate':
            vehicles.update(est_actif=True)
            message = f'{count} véhicule(s) activé(s) avec succès'
        elif action == 'deactivate':
            vehicles.update(est_actif=False)
            message = f'{count} véhicule(s) désactivé(s) avec succès'
        elif action == 'delete':
            vehicles.delete()
            message = f'{count} véhicule(s) supprimé(s) avec succès'
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
        
        return JsonResponse({'success': True, 'count': count, 'message': message})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
