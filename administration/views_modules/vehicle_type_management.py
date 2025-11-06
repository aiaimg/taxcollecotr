"""
Vehicle Type Management Views for Admin Console
Manages VehicleType model records (not individual vehicles)
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
import csv
import json
from datetime import datetime

from vehicles.models import VehicleType
from ..mixins import AdminRequiredMixin


class VehicleTypeManagementListView(AdminRequiredMixin, ListView):
    """
    List view for managing VehicleType records
    """
    model = VehicleType
    template_name = 'administration/vehicle_type_management/list_velzon.html'
    context_object_name = 'vehicle_types'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = VehicleType.objects.annotate(
            vehicle_count=Count('vehicules')
        ).order_by('ordre_affichage', 'nom')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by active status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(est_actif=True)
        elif status == 'inactive':
            queryset = queryset.filter(est_actif=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['total_types'] = VehicleType.objects.count()
        context['active_types'] = VehicleType.objects.filter(est_actif=True).count()
        return context


class VehicleTypeManagementDetailView(AdminRequiredMixin, DetailView):
    """
    Detail view for VehicleType with associated vehicles
    """
    model = VehicleType
    template_name = 'administration/vehicle_type_management/detail_velzon.html'
    context_object_name = 'vehicle_type'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get vehicles using this type
        context['vehicles'] = self.object.vehicules.select_related('proprietaire').order_by('-created_at')[:10]
        context['vehicle_count'] = self.object.vehicules.count()
        return context


class VehicleTypeManagementCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for adding new VehicleType records
    """
    model = VehicleType
    template_name = 'administration/vehicle_type_management/form_velzon.html'
    fields = ['nom', 'description', 'est_actif', 'ordre_affichage']
    success_url = reverse_lazy('administration:vehicle_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Type de véhicule '{form.instance.nom}' créé avec succès.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la création du type de véhicule. Veuillez vérifier les champs.")
        return super().form_invalid(form)


class VehicleTypeManagementUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for editing VehicleType records
    """
    model = VehicleType
    template_name = 'administration/vehicle_type_management/form_velzon.html'
    fields = ['nom', 'description', 'est_actif', 'ordre_affichage']
    
    def get_success_url(self):
        return reverse_lazy('administration:vehicle_type_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f"Type de véhicule '{form.instance.nom}' modifié avec succès.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la modification du type de véhicule. Veuillez vérifier les champs.")
        return super().form_invalid(form)


class VehicleTypeManagementDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for removing VehicleType records
    """
    model = VehicleType
    template_name = 'administration/vehicle_type_management/confirm_delete_velzon.html'
    success_url = reverse_lazy('administration:vehicle_type_list')
    
    def delete(self, request, *args, **kwargs):
        vehicle_type = self.get_object()
        
        # Check if there are vehicles using this type
        vehicle_count = vehicle_type.vehicules.count()
        if vehicle_count > 0:
            messages.error(request, f"Impossible de supprimer le type '{vehicle_type.nom}' car {vehicle_count} véhicule(s) l'utilisent encore.")
            return self.get(request, *args, **kwargs)
        
        messages.success(request, f"Type de véhicule '{vehicle_type.nom}' supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


def vehicle_type_bulk_import(request):
    """
    Bulk import VehicleType records from CSV
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'GET':
        return render(request, 'administration/vehicle_type_management/bulk_import_velzon.html')
    
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Aucun fichier CSV fourni.')
            return render(request, 'administration/vehicle_type_management/bulk_import_velzon.html')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return render(request, 'administration/vehicle_type_management/bulk_import_velzon.html')
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    nom = row.get('Nom', '').strip()
                    if not nom:
                        errors.append(f"Ligne {row_num}: Le nom est requis")
                        continue
                    
                    description = row.get('Description', '').strip()
                    est_actif = row.get('Actif', '').strip().lower() in ['oui', 'yes', 'true', '1']
                    ordre_affichage = int(row.get('Ordre d\'affichage', 0) or 0)
                    
                    # Check if vehicle type already exists
                    vehicle_type, created = VehicleType.objects.get_or_create(
                        nom=nom,
                        defaults={
                            'description': description,
                            'est_actif': est_actif,
                            'ordre_affichage': ordre_affichage
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing record
                        vehicle_type.description = description
                        vehicle_type.est_actif = est_actif
                        vehicle_type.ordre_affichage = ordre_affichage
                        vehicle_type.save()
                        updated_count += 1
                        
                except ValueError as e:
                    errors.append(f"Ligne {row_num}: Erreur de format - {str(e)}")
                except Exception as e:
                    errors.append(f"Ligne {row_num}: {str(e)}")
            
            if errors:
                messages.warning(request, f"Import terminé avec {len(errors)} erreurs. {created_count} créés, {updated_count} mis à jour.")
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
            else:
                messages.success(request, f"Import réussi: {created_count} types de véhicules créés, {updated_count} mis à jour.")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la lecture du fichier CSV: {str(e)}")
        
        return render(request, 'administration/vehicle_type_management/bulk_import_velzon.html')