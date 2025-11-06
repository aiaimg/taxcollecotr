from django.contrib import admin
from .models import StripeConfig, StripeWebhookEvent, PaiementTaxe, QRCode


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


@admin.register(PaiementTaxe)
class PaiementTaxeAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'vehicule_plaque',
        'annee_fiscale',
        'montant_du_ariary',
        'montant_paye_ariary',
        'statut',
        'methode_paiement',
        'date_paiement'
    )
    list_filter = ('statut', 'methode_paiement', 'annee_fiscale', 'created_at')
    search_fields = (
        'transaction_id',
        'vehicule_plaque__plaque_immatriculation',
        'vehicule_plaque__proprietaire__username',
        'stripe_payment_intent_id',
        'billing_email'
    )
    readonly_fields = ('id', 'transaction_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('id', 'vehicule_plaque', 'annee_fiscale', 'transaction_id')
        }),
        ('Montants', {
            'fields': ('montant_du_ariary', 'montant_paye_ariary', 'currency_stripe')
        }),
        ('Paiement', {
            'fields': ('statut', 'methode_paiement', 'date_paiement', 'details_paiement')
        }),
        ('Stripe - Payment Intent', {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_status',
                'stripe_payment_method',
                'stripe_charge_id',
                'stripe_customer_id',
                'stripe_receipt_url',
                'stripe_created',
                'amount_stripe'
            ),
            'classes': ('collapse',)
        }),
        ('Stripe - Metadata', {
            'fields': ('stripe_metadata',),
            'classes': ('collapse',)
        }),
        ('Facturation', {
            'fields': ('billing_name', 'billing_email'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of paid transactions
        if obj and obj.statut in ['PAYE', 'EXONERE']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vehicule_plaque',
        'annee_fiscale',
        'est_actif',
        'nombre_scans',
        'date_generation',
        'date_expiration',
        'derniere_verification'
    )
    list_filter = ('est_actif', 'annee_fiscale', 'date_generation', 'date_expiration')
    search_fields = (
        'token',
        'vehicule_plaque__plaque_immatriculation',
        'vehicule_plaque__proprietaire__username'
    )
    readonly_fields = ('id', 'token', 'date_generation', 'nombre_scans', 'derniere_verification')
    ordering = ('-date_generation',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('id', 'vehicule_plaque', 'annee_fiscale', 'est_actif')
        }),
        ('Token et sécurité', {
            'fields': ('token', 'date_generation', 'date_expiration')
        }),
        ('Statistiques', {
            'fields': ('nombre_scans', 'derniere_verification')
        }),
    )
