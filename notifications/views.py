from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from .models import Notification
from .services import NotificationService


class NotificationListView(LoginRequiredMixin, ListView):
    """List all notifications for the current user"""
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-date_envoi')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = NotificationService.get_unread_count(self.request.user)
        context['page_title'] = _('Mes Notifications')
        return context


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """View a single notification"""
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'
    login_url = reverse_lazy('core:login')
    
    def get_queryset(self):
        # Only allow users to view their own notifications
        return Notification.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark as read when viewed
        if not obj.est_lue:
            obj.marquer_comme_lue()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Notification')
        return context


@login_required
def mark_notification_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    
    notification.marquer_comme_lue()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': _('Notification marquée comme lue')
        })
    
    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        count = NotificationService.mark_all_as_read(request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _(f'{count} notifications marquées comme lues'),
                'count': count
            })
        
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """API endpoint to get unread notification count"""
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({
        'count': count
    })


@login_required
def get_recent_notifications(request):
    """API endpoint to get recent notifications"""
    limit = int(request.GET.get('limit', 10))
    notifications = NotificationService.get_recent_notifications(
        request.user,
        limit=limit
    )
    
    data = [{
        'id': str(notif.id),
        'titre': notif.titre,
        'contenu': notif.contenu[:100] + '...' if len(notif.contenu) > 100 else notif.contenu,
        'type': notif.type_notification,
        'est_lue': notif.est_lue,
        'date_envoi': notif.date_envoi.isoformat(),
    } for notif in notifications]
    
    return JsonResponse({
        'notifications': data,
        'unread_count': NotificationService.get_unread_count(request.user)
    })
