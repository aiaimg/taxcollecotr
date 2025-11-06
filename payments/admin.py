from django.contrib import admin
from .models import StripeConfig, StripeWebhookEvent


@admin.register(StripeConfig)
class StripeConfigAdmin(admin.ModelAdmin):
    list_display = (
        'environment',
        'is_active',
        'currency',
        'created_at',
        'updated_at',
    )
    list_filter = ('environment', 'is_active')
    search_fields = ('environment', 'publishable_key', 'secret_key', 'webhook_secret')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        'stripe_event_id',
        'type',
        'processed',
        'created_at',
        'processed_at',
    )
    list_filter = ('type', 'processed')
    search_fields = ('stripe_event_id', 'type')
    readonly_fields = ('created_at', 'processed_at', 'data')

# Register your models here.
