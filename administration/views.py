from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from vehicles.models import Vehicule, GrilleTarifaire
from payments.models import PaiementTaxe, QRCode
from .models import AgentVerification, VerificationQR, StatistiquesPlateforme, ConfigurationSysteme
from .mixins import AdminRequiredMixin, is_admin_user


@login_required
@user_passes_test(is_admin_user)
def dashboard_view(request):
    """Main administration dashboard"""
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic statistics
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_vehicles': Vehicule.objects.count(),
        'total_payments': PaiementTaxe.objects.count(),
        'total_revenue': PaiementTaxe.objects.filter(
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0,
        
        # Today's statistics
        'today_payments': PaiementTaxe.objects.filter(
            created_at__date=today
        ).count(),
        'today_revenue': PaiementTaxe.objects.filter(
            created_at__date=today,
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0,
        
        # This week
        'week_payments': PaiementTaxe.objects.filter(
            created_at__date__gte=week_ago
        ).count(),
        'week_revenue': PaiementTaxe.objects.filter(
            created_at__date__gte=week_ago,
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0,
        
        # QR Codes
        'total_qr_codes': QRCode.objects.count(),
        'active_qr_codes': QRCode.objects.filter(
            date_expiration__gt=timezone.now()
        ).count(),
    }
    
    # Payment method breakdown
    payment_methods = PaiementTaxe.objects.values('methode_paiement').annotate(
        count=Count('*'),
        total=Sum('montant_paye_ariary')
    ).order_by('-count')
    
    # Recent payments
    recent_payments = PaiementTaxe.objects.select_related(
        'vehicule_plaque'
    ).order_by('-created_at')[:10]
    
    # Vehicle type breakdown
    vehicle_types = Vehicule.objects.values('type_vehicule').annotate(
        count=Count('plaque_immatriculation')
    ).order_by('-count')[:5]
    
    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = PaiementTaxe.objects.filter(
            created_at__date__range=[month_start, month_end],
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    context = {
        'stats': stats,
        'payment_methods': payment_methods,
        'recent_payments': recent_payments,
        'vehicle_types': vehicle_types,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'dashboard_velzon.html', context)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin access"""
    
    def test_func(self):
        return is_admin_user(self.request.user)


class VehicleManagementView(AdminRequiredMixin, ListView):
    """Vehicle fleet management"""
    model = Vehicule
    template_name = 'administration/vehicle_management.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vehicule.objects.select_related('proprietaire').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search) |
                Q(proprietaire__first_name__icontains=search) |
                Q(proprietaire__last_name__icontains=search) |
                Q(proprietaire__email__icontains=search)
            )
        
        # Filter by vehicle type
        vehicle_type = self.request.GET.get('type')
        if vehicle_type:
            queryset = queryset.filter(type_vehicule=vehicle_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_types'] = Vehicule.TYPE_VEHICULE_CHOICES
        context['search'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('type', '')
        return context


class UserManagementView(AdminRequiredMixin, ListView):
    """User management"""
    model = User
    template_name = 'administration/user_management.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.order_by('-date_joined')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'staff':
            queryset = queryset.filter(is_staff=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class PaymentManagementView(AdminRequiredMixin, ListView):
    """Payment management"""
    model = PaiementTaxe
    template_name = 'administration/payment_management.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PaiementTaxe.objects.select_related(
            'vehicule_plaque'
        ).order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(vehicule__plaque_immatriculation__icontains=search) |
                Q(utilisateur__username__icontains=search) |
                Q(transaction_id__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(statut=status)
        
        # Filter by payment method
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(methode_paiement=method)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statut_choices'] = PaiementTaxe.STATUT_CHOICES
        context['method_choices'] = PaiementTaxe.METHODE_PAIEMENT_CHOICES
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_method'] = self.request.GET.get('method', '')
        return context


@login_required
@user_passes_test(is_admin_user)
def analytics_view(request):
    """Analytics and reporting"""
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Payment analytics
    payments_in_range = PaiementTaxe.objects.filter(
        created_at__date__range=[start_date, end_date]
    )
    
    analytics = {
        'total_payments': payments_in_range.count(),
        'successful_payments': payments_in_range.filter(statut='complete').count(),
        'pending_payments': payments_in_range.filter(statut='en_attente').count(),
        'failed_payments': payments_in_range.filter(statut='echec').count(),
        'total_revenue': payments_in_range.filter(
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0,
        'average_payment': payments_in_range.filter(
            statut='complete'
        ).aggregate(Avg('montant_paye_ariary'))['montant_paye_ariary__avg'] or 0,
    }
    
    # Daily breakdown
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        day_payments = payments_in_range.filter(created_at__date=current_date)
        daily_stats.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'payments': day_payments.count(),
            'revenue': day_payments.filter(
                statut='complete'
            ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0
        })
        current_date += timedelta(days=1)
    
    context = {
        'analytics': analytics,
        'daily_stats': daily_stats,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'administration/analytics.html', context)


@login_required
@user_passes_test(is_admin_user)
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        was_active = user.is_active
        user.is_active = not user.is_active
        user.save()
        
        # Create notification for user
        from notifications.services import NotificationService
        langue = 'fr'
        if hasattr(user, 'profile'):
            langue = user.profile.langue_preferee
        
        if user.is_active:
            NotificationService.create_account_reactivated_notification(
                user=user,
                langue=langue
            )
        else:
            NotificationService.create_account_deactivated_notification(
                user=user,
                langue=langue
            )
        
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"L'utilisateur {user.username} a été {status}.")
    
    return redirect('administration:user_management')


@login_required
@user_passes_test(is_admin_user)
def dashboard_api_stats(request):
    """API endpoint for dashboard statistics"""
    
    today = timezone.now().date()
    
    # Real-time stats
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_vehicles': Vehicule.objects.count(),
        'today_payments': PaiementTaxe.objects.filter(
            created_at__date=today
        ).count(),
        'today_revenue': float(PaiementTaxe.objects.filter(
            created_at__date=today,
            statut='complete'
        ).aggregate(Sum('montant_paye_ariary'))['montant_paye_ariary__sum'] or 0),
        'pending_payments': PaiementTaxe.objects.filter(
            statut='en_attente'
        ).count(),
    }
    
    return JsonResponse(stats)


@login_required
@user_passes_test(is_admin_user)
def test_components_view(request):
    """Test page for Material Design components"""
    return render(request, 'admin_console/test_components.html')
