"""
API Admin Interface

Django admin configuration for API models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    APIKey,
    APIKeyPermission,
    APIKeyEvent,
    APIAuditLog,
    DataChangeLog,
    WebhookSubscription,
    WebhookDelivery,
)
from api.utils.webhooks import dispatch_webhook_event
from django.http import HttpResponse
import csv
import json


class APIKeyPermissionInline(admin.TabularInline):
    """Inline admin for API key permissions"""
    model = APIKeyPermission
    extra = 1
    fields = ('resource', 'scope', 'granted_by', 'granted_at')
    readonly_fields = ('granted_at',)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Auto-fill granted_by with current user
        formset.form.base_fields['granted_by'].initial = request.user
        return formset


class APIKeyEventInline(admin.TabularInline):
    """Inline admin for API key events"""
    model = APIKeyEvent
    extra = 0
    fields = ('event_type', 'performed_by', 'timestamp', 'details')
    readonly_fields = ('event_type', 'performed_by', 'timestamp', 'details')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for API keys"""
    
    list_display = (
        'name',
        'organization',
        'status_badge',
        'last_used_display',
        'rate_limit_display',
        'created_at',
    )
    list_filter = (
        'is_active',
        'created_at',
        'last_used_at',
    )
    search_fields = (
        'name',
        'organization',
        'contact_email',
        'key',
    )
    readonly_fields = (
        'key',
        'created_at',
        'created_by',
        'last_used_at',
        'key_display',
    )
    fieldsets = (
        (_('Identification'), {
            'fields': ('name', 'organization', 'contact_email', 'description')
        }),
        (_('API Key'), {
            'fields': ('key_display', 'key'),
            'description': _('The API key will be generated automatically when you save.')
        }),
        (_('Status'), {
            'fields': ('is_active', 'expires_at', 'last_used_at')
        }),
        (_('Rate Limiting'), {
            'fields': ('rate_limit_per_hour', 'rate_limit_per_day')
        }),
        (_('Security'), {
            'fields': ('ip_whitelist',),
            'description': _('Leave empty to allow all IP addresses.')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    inlines = [APIKeyPermissionInline, APIKeyEventInline]
    
    def save_model(self, request, obj, form, change):
        """Generate API key on creation and log event"""
        if not change:  # New object
            obj.key = APIKey.generate_key()
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # Log creation event
        if not change:
            APIKeyEvent.objects.create(
                api_key=obj,
                event_type='CREATED',
                performed_by=request.user,
                details={
                    'organization': obj.organization,
                    'contact_email': obj.contact_email,
                }
            )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        if not obj.is_active:
            return format_html(
                '<span style="color: red; font-weight: bold;">⛔ Revoked</span>'
            )
        elif obj.is_expired():
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
    status_badge.short_description = _('Status')
    
    def last_used_display(self, obj):
        """Display last used time in human-readable format"""
        if not obj.last_used_at:
            return _('Never')
        
        delta = timezone.now() - obj.last_used_at
        if delta.days > 30:
            return format_html(
                '<span style="color: orange;">{} days ago</span>',
                delta.days
            )
        elif delta.days > 0:
            return f'{delta.days} days ago'
        elif delta.seconds > 3600:
            return f'{delta.seconds // 3600} hours ago'
        else:
            return f'{delta.seconds // 60} minutes ago'
    last_used_display.short_description = _('Last Used')
    
    def rate_limit_display(self, obj):
        """Display rate limits"""
        return f'{obj.rate_limit_per_hour}/hour, {obj.rate_limit_per_day}/day'
    rate_limit_display.short_description = _('Rate Limits')
    
    def key_display(self, obj):
        """Display API key with copy button"""
        if obj.key:
            return format_html(
                '<code style="background: #f5f5f5; padding: 5px; display: block; '
                'word-break: break-all;">{}</code>',
                obj.key
            )
        return _('Will be generated on save')
    key_display.short_description = _('API Key')
    
    actions = ['revoke_keys', 'activate_keys']
    
    def revoke_keys(self, request, queryset):
        """Revoke selected API keys"""
        count = 0
        for api_key in queryset:
            if api_key.is_active:
                api_key.revoke(revoked_by=request.user)
                count += 1
        
        self.message_user(
            request,
            _(f'{count} API key(s) revoked successfully.')
        )
    revoke_keys.short_description = _('Revoke selected API keys')
    
    def activate_keys(self, request, queryset):
        """Activate selected API keys"""
        count = queryset.filter(is_active=False).update(is_active=True)
        
        # Log activation events
        for api_key in queryset.filter(is_active=True):
            APIKeyEvent.objects.create(
                api_key=api_key,
                event_type='RENEWED',
                performed_by=request.user,
                details={'activated_at': timezone.now().isoformat()}
            )
        
        self.message_user(
            request,
            _(f'{count} API key(s) activated successfully.')
        )
    activate_keys.short_description = _('Activate selected API keys')


@admin.register(APIKeyPermission)
class APIKeyPermissionAdmin(admin.ModelAdmin):
    """Admin interface for API key permissions"""
    
    list_display = (
        'api_key',
        'resource',
        'scope',
        'granted_by',
        'granted_at',
    )
    list_filter = (
        'resource',
        'scope',
        'granted_at',
    )
    search_fields = (
        'api_key__name',
        'api_key__organization',
        'resource',
    )
    readonly_fields = ('granted_at',)


@admin.register(APIKeyEvent)
class APIKeyEventAdmin(admin.ModelAdmin):
    """Admin interface for API key events"""
    
    list_display = (
        'api_key',
        'event_type',
        'performed_by',
        'timestamp',
    )
    list_filter = (
        'event_type',
        'timestamp',
    )
    search_fields = (
        'api_key__name',
        'api_key__organization',
    )
    readonly_fields = (
        'api_key',
        'event_type',
        'performed_by',
        'timestamp',
        'details',
    )
    
    def has_add_permission(self, request):
        """Events are created automatically, not manually"""
        return False


@admin.register(APIAuditLog)
class APIAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'method', 'endpoint', 'status_code', 'correlation_id', 'api_key', 'user'
    )
    list_filter = (
        'method', 'status_code', 'timestamp', 'api_key'
    )
    search_fields = (
        'correlation_id', 'endpoint', 'user__username', 'api_key__name'
    )
    readonly_fields = (
        'timestamp', 'correlation_id', 'endpoint', 'method', 'status_code', 'duration_ms', 'client_ip',
        'api_key', 'user', 'request_headers', 'request_body', 'response_body', 'error_type', 'error_message'
    )
    actions = ['export_selected_csv', 'export_selected_json']

    def export_selected_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="api_audit_logs.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'timestamp', 'correlation_id', 'method', 'endpoint', 'status_code', 'duration_ms', 'client_ip', 'api_key', 'user'
        ])
        for log in queryset:
            writer.writerow([
                log.timestamp.isoformat(), log.correlation_id, log.method, log.endpoint, log.status_code,
                log.duration_ms, log.client_ip, getattr(log.api_key, 'name', ''), getattr(log.user, 'username', '')
            ])
        return response
    export_selected_csv.short_description = _('Export selected logs to CSV')

    def export_selected_json(self, request, queryset):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="api_audit_logs.json"'
        data = []
        for log in queryset:
            data.append({
                'timestamp': log.timestamp.isoformat(),
                'correlation_id': log.correlation_id,
                'method': log.method,
                'endpoint': log.endpoint,
                'status_code': log.status_code,
                'duration_ms': log.duration_ms,
                'client_ip': log.client_ip,
                'api_key': getattr(log.api_key, 'name', None),
                'user': getattr(log.user, 'username', None),
            })
        response.write(json.dumps(data))
        return response
    export_selected_json.short_description = _('Export selected logs to JSON')


@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'operation', 'content_type', 'object_id', 'correlation_id', 'user', 'api_key'
    )
    list_filter = (
        'operation', 'timestamp', 'content_type'
    )
    search_fields = (
        'correlation_id', 'object_id', 'user__username', 'api_key__name'
    )
    readonly_fields = (
        'timestamp', 'correlation_id', 'operation', 'content_type', 'object_id', 'object_repr',
        'user', 'api_key', 'changed_fields', 'previous_data', 'new_data'
    )
    actions = ['export_selected_csv', 'export_selected_json']

    def export_selected_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_change_logs.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'timestamp', 'operation', 'content_type', 'object_id', 'correlation_id', 'user', 'api_key'
        ])
        for log in queryset:
            writer.writerow([
                log.timestamp.isoformat(), log.operation, str(log.content_type), log.object_id, log.correlation_id,
                getattr(log.user, 'username', ''), getattr(log.api_key, 'name', '')
            ])
        return response
    export_selected_csv.short_description = _('Export selected logs to CSV')

    def export_selected_json(self, request, queryset):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="data_change_logs.json"'
        data = []
        for log in queryset:
            data.append({
                'timestamp': log.timestamp.isoformat(),
                'operation': log.operation,
                'content_type': str(log.content_type),
                'object_id': log.object_id,
                'correlation_id': log.correlation_id,
                'user': getattr(log.user, 'username', None),
                'api_key': getattr(log.api_key, 'name', None),
            })
        response.write(json.dumps(data))
        return response
    export_selected_json.short_description = _('Export selected logs to JSON')
    
    def has_delete_permission(self, request, obj=None):
        """Events should not be deleted for audit purposes"""
        return False


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "target_url", "is_active", "created_at", "created_by")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "target_url")
    readonly_fields = ("created_at", "created_by")

    actions = ["send_test_event_action"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def send_test_event_action(self, request, queryset):
        for sub in queryset:
            dispatch_webhook_event("test.event", {"message": "Webhook test", "subscription": str(sub.id)})
        self.message_user(request, f"Scheduled test events for {queryset.count()} subscription(s)")
    send_test_event_action.short_description = "Send test webhook event"


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "subscription",
        "event_type",
        "status",
        "attempt_count",
        "response_code",
        "created_at",
    )
    list_filter = ("status", "event_type", "created_at")
    search_fields = ("subscription__name", "event_type")
    readonly_fields = (
        "subscription",
        "event_type",
        "payload",
        "signature",
        "status",
        "attempt_count",
        "next_attempt_at",
        "response_code",
        "response_body",
        "error_message",
        "created_at",
        "updated_at",
    )
