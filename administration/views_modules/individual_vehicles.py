from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
import json

from vehicles.models import Vehicule
from core.models import User
from administration.mixins import AdminRequiredMixin


class IndividualVehicleListView(AdminRequiredMixin, ListView):
    """Enhanced list view for individual vehicles with advanced search and filtering"""
    model = Vehicule
    template_name = 'administration/individual_vehicles/list_velzon.html'
    context_object_name = 'vehicles'
    paginate_by = 25

    def get_queryset(self):
        """Get vehicles with search and filter capabilities"""
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
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(est_actif=True)
        elif status == 'inactive':
            queryset = queryset.filter(est_actif=False)
        
        # Filter by energy source
        energy_source = self.request.GET.get('energy_source')
        if energy_source:
            queryset = queryset.filter(source_energie=energy_source)
        
        # Filter by vehicle category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categorie_vehicule=category)
        
        # Filter by vehicle type
        vehicle_type = self.request.GET.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(type_vehicule=vehicle_type)
        
        # Filter by owner type
        owner_type = self.request.GET.get('owner_type')
        if owner_type:
            if owner_type == 'individual':
                queryset = queryset.filter(proprietaire__profile__user_type='individual')
            elif owner_type == 'company':
                queryset = queryset.filter(proprietaire__profile__user_type='company')
            elif owner_type == 'government':
                queryset = queryset.filter(proprietaire__profile__user_type='government')
        
        # Sort options
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = [
            'plaque_immatriculation', '-plaque_immatriculation',
            'proprietaire__username', '-proprietaire__username',
            'created_at', '-created_at',
            'puissance_fiscale_cv', '-puissance_fiscale_cv',
            'cylindree_cm3', '-cylindree_cm3'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        total_vehicles = Vehicule.objects.count()
        active_vehicles = Vehicule.objects.filter(est_actif=True).count()
        inactive_vehicles = total_vehicles - active_vehicles
        
        # Energy source distribution
        energy_sources = Vehicule.objects.values('source_energie').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Vehicle categories distribution
        categories = Vehicule.objects.values('categorie_vehicule').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Vehicle types distribution
        vehicle_types = Vehicule.objects.values('type_vehicule').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Owner types distribution
        owner_types = Vehicule.objects.select_related('proprietaire__profile').values(
            'proprietaire__profile__user_type'
        ).annotate(count=Count('id')).order_by('-count')
        
        context.update({
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'inactive_vehicles': inactive_vehicles,
            'energy_sources': energy_sources,
            'categories': categories,
            'vehicle_types': vehicle_types,
            'owner_types': owner_types,
            'search': self.request.GET.get('search', ''),
            'current_filters': {
                'status': self.request.GET.get('status', ''),
                'energy_source': self.request.GET.get('energy_source', ''),
                'category': self.request.GET.get('category', ''),
                'vehicle_type': self.request.GET.get('vehicle_type', ''),
                'owner_type': self.request.GET.get('owner_type', ''),
                'sort': self.request.GET.get('sort', '-created_at'),
            }
        })
        
        return context


class IndividualVehicleDetailView(AdminRequiredMixin, DetailView):
    """Detailed view for individual vehicle with comprehensive information"""
    model = Vehicule
    template_name = 'administration/individual_vehicles/detail_velzon.html'
    context_object_name = 'vehicle'
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        
        # Calculate current year tax
        current_year = timezone.now().year
        
        # Get related vehicles from same owner
        related_vehicles = Vehicule.objects.filter(
            proprietaire=vehicle.proprietaire
        ).exclude(plaque_immatriculation=vehicle.plaque_immatriculation)[:5]
        
        # Get payment history (if payments app is available)
        try:
            from payments.models import Payment
            payments = Payment.objects.filter(
                vehicle_plate=vehicle.plaque_immatriculation
            ).order_by('-created_at')[:10]
            context['payments'] = payments
        except ImportError:
            context['payments'] = []
        
        context.update({
            'current_year': current_year,
            'related_vehicles': related_vehicles,
            'owner_profile': getattr(vehicle.proprietaire, 'profile', None),
        })
        
        return context


class IndividualVehicleCreateView(AdminRequiredMixin, CreateView):
    """Create view for adding new individual vehicles"""
    model = Vehicule
    template_name = 'administration/individual_vehicles/form_velzon.html'
    fields = [
        'plaque_immatriculation', 'proprietaire', 'puissance_fiscale_cv',
        'cylindree_cm3', 'source_energie', 'date_premiere_circulation',
        'categorie_vehicule', 'type_vehicule', 'specifications_techniques',
        'est_actif'
    ]
    
    def get_success_url(self):
        return reverse_lazy('administration:individual_vehicle_detail', 
                          kwargs={'plaque': self.object.plaque_immatriculation})
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f"Véhicule {form.instance.plaque_immatriculation} créé avec succès."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            "Erreur lors de la création du véhicule. Veuillez vérifier les champs."
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Créer un Nouveau Véhicule'
        context['submit_text'] = 'Créer Véhicule'
        return context


class IndividualVehicleUpdateView(AdminRequiredMixin, UpdateView):
    """Update view for editing individual vehicles"""
    model = Vehicule
    template_name = 'administration/individual_vehicles/form_velzon.html'
    fields = [
        'proprietaire', 'puissance_fiscale_cv', 'cylindree_cm3',
        'source_energie', 'date_premiere_circulation', 'categorie_vehicule',
        'type_vehicule', 'specifications_techniques', 'est_actif'
    ]
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def get_success_url(self):
        return reverse_lazy('administration:individual_vehicle_detail', 
                          kwargs={'plaque': self.object.plaque_immatriculation})
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f"Véhicule {form.instance.plaque_immatriculation} modifié avec succès."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            "Erreur lors de la modification du véhicule. Veuillez vérifier les champs."
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Modifier le Véhicule {self.object.plaque_immatriculation}'
        context['submit_text'] = 'Mettre à Jour'
        return context


class IndividualVehicleDeleteView(AdminRequiredMixin, DeleteView):
    """Delete view for removing individual vehicles"""
    model = Vehicule
    template_name = 'administration/individual_vehicles/confirm_delete_velzon.html'
    success_url = reverse_lazy('administration:individual_vehicle_list')
    pk_url_kwarg = 'plaque'
    
    def get_object(self):
        return get_object_or_404(Vehicule, plaque_immatriculation=self.kwargs['plaque'])
    
    def delete(self, request, *args, **kwargs):
        vehicle = self.get_object()
        messages.success(
            request, 
            f"Véhicule {vehicle.plaque_immatriculation} supprimé avec succès."
        )
        return super().delete(request, *args, **kwargs)


def individual_vehicle_bulk_operations(request):
    """Handle bulk operations on individual vehicles"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        vehicle_ids = data.get('vehicle_ids', [])
        
        if not action or not vehicle_ids:
            return JsonResponse({'error': 'Missing action or vehicle IDs'}, status=400)
        
        vehicles = Vehicule.objects.filter(plaque_immatriculation__in=vehicle_ids)
        
        if action == 'activate':
            vehicles.update(est_actif=True)
            message = f"{vehicles.count()} véhicules activés avec succès."
        elif action == 'deactivate':
            vehicles.update(est_actif=False)
            message = f"{vehicles.count()} véhicules désactivés avec succès."
        elif action == 'delete':
            count = vehicles.count()
            vehicles.delete()
            message = f"{count} véhicules supprimés avec succès."
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'affected_count': vehicles.count() if action != 'delete' else count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def individual_vehicle_export(request):
    """Export individual vehicles data"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Get filtered queryset
    view = IndividualVehicleListView()
    view.request = request
    vehicles = view.get_queryset()
    
    # Limit export to prevent performance issues
    if vehicles.count() > 10000:
        vehicles = vehicles[:10000]
    
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="individual_vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Plaque d\'Immatriculation', 'Propriétaire', 'Email Propriétaire',
            'Puissance Fiscale (CV)', 'Cylindrée (cm³)', 'Source d\'Énergie',
            'Date Première Circulation', 'Catégorie Véhicule', 'Type Véhicule',
            'Statut', 'Date Création'
        ])
        
        for vehicle in vehicles:
            writer.writerow([
                vehicle.plaque_immatriculation,
                vehicle.proprietaire.get_full_name() or vehicle.proprietaire.username,
                vehicle.proprietaire.email,
                vehicle.puissance_fiscale_cv,
                vehicle.cylindree_cm3,
                vehicle.get_source_energie_display(),
                vehicle.date_premiere_circulation.strftime('%Y-%m-%d') if vehicle.date_premiere_circulation else '',
                vehicle.get_categorie_vehicule_display(),
                vehicle.get_type_vehicule_display(),
                'Actif' if vehicle.est_actif else 'Inactif',
                vehicle.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    elif format_type == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="individual_vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'plaque_immatriculation': vehicle.plaque_immatriculation,
                'proprietaire': {
                    'username': vehicle.proprietaire.username,
                    'full_name': vehicle.proprietaire.get_full_name(),
                    'email': vehicle.proprietaire.email,
                },
                'puissance_fiscale_cv': vehicle.puissance_fiscale_cv,
                'cylindree_cm3': vehicle.cylindree_cm3,
                'source_energie': vehicle.source_energie,
                'date_premiere_circulation': vehicle.date_premiere_circulation.isoformat() if vehicle.date_premiere_circulation else None,
                'categorie_vehicule': vehicle.categorie_vehicule,
                'type_vehicule': vehicle.type_vehicule,
                'est_actif': vehicle.est_actif,
                'created_at': vehicle.created_at.isoformat(),
                'specifications_techniques': vehicle.specifications_techniques,
            })
        
        import json
        response.write(json.dumps(vehicles_data, indent=2, ensure_ascii=False))
        return response
    
    else:
        return JsonResponse({'error': 'Unsupported format'}, status=400)