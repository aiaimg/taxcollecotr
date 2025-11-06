"""
Enhanced vehicle management views for admin console with role-based access
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator

from vehicles.models import Vehicule
from core.models import UserProfile
from ..mixins import AdminRequiredMixin, is_admin_user


class EnhancedVehicleManagementView(AdminRequiredMixin, ListView):
    """
    Enhanced vehicle management view with role-based filtering
    - Admin view: Show all vehicles organized by user accounts and company affiliations
    - User view: Show only vehicles assigned to the logged-in user
    """
    model = Vehicule
    template_name = 'administration/enhanced_vehicle_management.html'
    context_object_name = 'vehicles'
    paginate_by = 50

    def get_queryset(self):
        """Get vehicles based on user role"""
        user = self.request.user
        
        if is_admin_user(user):
            # Admin view: Get all vehicles with related user and profile data
            return Vehicule.objects.select_related(
                'proprietaire',
                'proprietaire__profile'
            ).prefetch_related(
                'proprietaire__groups'
            ).order_by(
                'proprietaire__profile__user_type',
                'proprietaire__username',
                'plaque_immatriculation'
            )
        else:
            # Regular user view: Only their own vehicles
            return Vehicule.objects.filter(
                proprietaire=user
            ).select_related('proprietaire').order_by('plaque_immatriculation')

    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['is_admin'] = is_admin_user(user)
        
        if is_admin_user(user):
            # For admin users, organize vehicles by company and user
            vehicles = self.get_queryset()
            
            # Group vehicles by user type and then by user
            grouped_vehicles = {}
            
            for vehicle in vehicles:
                owner = vehicle.proprietaire
                profile = getattr(owner, 'profile', None)
                user_type = profile.user_type if profile else 'individual'
                
                # Create user type group if it doesn't exist
                if user_type not in grouped_vehicles:
                    grouped_vehicles[user_type] = {}
                
                # Create user group if it doesn't exist
                if owner.id not in grouped_vehicles[user_type]:
                    grouped_vehicles[user_type][owner.id] = {
                        'user': owner,
                        'profile': profile,
                        'vehicles': []
                    }
                
                # Add vehicle to user's list
                grouped_vehicles[user_type][owner.id]['vehicles'].append(vehicle)
            
            context['grouped_vehicles'] = grouped_vehicles
            
            # Add statistics
            context['stats'] = {
                'total_vehicles': vehicles.count(),
                'total_users': User.objects.filter(vehicules__isnull=False).distinct().count(),
                'company_users': User.objects.filter(
                    profile__user_type='company',
                    vehicules__isnull=False
                ).distinct().count(),
                'individual_users': User.objects.filter(
                    profile__user_type='individual',
                    vehicules__isnull=False
                ).distinct().count(),
            }
        else:
            # For regular users, just provide their vehicle count
            context['stats'] = {
                'total_vehicles': self.get_queryset().count()
            }
        
        return context


@login_required
@user_passes_test(is_admin_user)
def vehicle_management_api(request):
    """
    API endpoint for vehicle management data
    Returns JSON data for AJAX requests
    """
    user = self.request.user
    
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    user_type_filter = request.GET.get('user_type', '')
    owner_filter = request.GET.get('owner', '')
    
    # Base queryset based on user role
    if is_admin_user(user):
        queryset = Vehicule.objects.select_related(
            'proprietaire',
            'proprietaire__profile'
        )
    else:
        queryset = Vehicule.objects.filter(proprietaire=user)
    
    # Apply filters
    if search_query:
        queryset = queryset.filter(
            Q(plaque_immatriculation__icontains=search_query) |
            Q(proprietaire__username__icontains=search_query) |
            Q(proprietaire__first_name__icontains=search_query) |
            Q(proprietaire__last_name__icontains=search_query)
        )
    
    if user_type_filter and is_admin_user(user):
        queryset = queryset.filter(proprietaire__profile__user_type=user_type_filter)
    
    if owner_filter and is_admin_user(user):
        queryset = queryset.filter(proprietaire__id=owner_filter)
    
    # Prepare response data
    vehicles_data = []
    for vehicle in queryset[:100]:  # Limit to 100 results for performance
        owner = vehicle.proprietaire
        profile = getattr(owner, 'profile', None)
        
        vehicle_data = {
            'id': vehicle.id,
            'plaque_immatriculation': vehicle.plaque_immatriculation,
            'puissance_fiscale_cv': vehicle.puissance_fiscale_cv,
            'cylindree_cm3': vehicle.cylindree_cm3,
            'source_energie': vehicle.source_energie,
            'owner': {
                'id': owner.id,
                'username': owner.username,
                'full_name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
                'user_type': profile.user_type if profile else 'individual'
            }
        }
        
        # Only include owner details for admin users
        if not is_admin_user(user):
            vehicle_data['owner'] = {
                'full_name': 'Vous'  # "You" in French
            }
        
        vehicles_data.append(vehicle_data)
    
    return JsonResponse({
        'vehicles': vehicles_data,
        'total_count': queryset.count(),
        'is_admin': is_admin_user(user)
    })


@login_required
@user_passes_test(is_admin_user)
def vehicle_owner_details(request, user_id):
    """
    Get detailed information about a vehicle owner (admin only)
    """
    owner = get_object_or_404(User, id=user_id)
    profile = getattr(owner, 'profile', None)
    
    # Get owner's vehicles
    vehicles = Vehicule.objects.filter(proprietaire=owner).order_by('plaque_immatriculation')
    
    owner_data = {
        'id': owner.id,
        'username': owner.username,
        'email': owner.email,
        'full_name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
        'user_type': profile.user_type if profile else 'individual',
        'is_active': owner.is_active,
        'date_joined': owner.date_joined.isoformat(),
        'vehicles': [
            {
                'id': v.id,
                'plaque_immatriculation': v.plaque_immatriculation,
                'puissance_fiscale_cv': v.puissance_fiscale_cv,
                'cylindree_cm3': v.cylindree_cm3,
                'source_energie': v.source_energie,
                'date_premiere_circulation': v.date_premiere_circulation.isoformat() if v.date_premiere_circulation else None,
            }
            for v in vehicles
        ]
    }
    
    return JsonResponse(owner_data)