from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from .models import (
    AgentPartenaireProfile,
    CashAuditLog,
    CashReceipt,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    CommissionRecord,
    MvolaConfiguration,
    PaiementTaxe,
    QRCode,
    StripeConfig,
    StripeWebhookEvent,
)


@admin.register(StripeConfig)
class StripeConfigAdmin(admin.ModelAdmin):
    list_display = (
        "environment",
        "is_active",
        "currency",
        "created_at",
        "updated_at",
    )
    list_filter = ("environment", "is_active")
    search_fields = ("environment", "publishable_key", "secret_key", "webhook_secret")
    readonly_fields = ("created_at", "updated_at")


@admin.register(MvolaConfiguration)
class MvolaConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "environment_badge",
        "merchant_msisdn",
        "status_badge",
        "verification_badge",
        "success_rate_display",
        "total_transactions",
        "last_test_date",
        "action_buttons",
    ]
    list_filter = ["is_active", "is_enabled", "is_verified", "environment", "created_at"]
    search_fields = ["name", "merchant_msisdn", "merchant_name", "consumer_key"]
    readonly_fields = [
        "is_verified",
        "last_test_date",
        "last_test_result",
        "total_transactions",
        "successful_transactions",
        "failed_transactions",
        "total_amount_processed",
        "created_at",
        "updated_at",
        "created_by",
        "modified_by",
        "success_rate_display",
    ]

    fieldsets = (
        ("Informations générales", {"fields": ("name", "environment", "description")}),
        (
            "Identifiants API MVola",
            {
                "fields": ("consumer_key", "consumer_secret"),
                "description": "Identifiants fournis par MVola pour l'authentification API",
            },
        ),
        (
            "Informations du marchand",
            {"fields": ("merchant_msisdn", "merchant_name"), "description": "Informations du compte marchand MVola"},
        ),
        (
            "Configuration API",
            {
                "fields": ("base_url", "callback_url"),
                "classes": ("collapse",),
                "description": "URLs de l'API (laissez vide pour utiliser les valeurs par défaut)",
            },
        ),
        (
            "Limites de paiement",
            {
                "fields": ("min_amount", "max_amount", "platform_fee_percentage"),
                "description": "Montants minimum et maximum autorisés, et frais de plateforme",
            },
        ),
        (
            "Personnalisation",
            {
                "fields": ("logo",),
                "classes": ("collapse",),
            },
        ),
        (
            "Statut",
            {
                "fields": ("is_active", "is_enabled", "is_verified", "last_test_date", "last_test_result"),
            },
        ),
        (
            "Statistiques",
            {
                "fields": (
                    "total_transactions",
                    "successful_transactions",
                    "failed_transactions",
                    "total_amount_processed",
                    "success_rate_display",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Métadonnées",
            {
                "fields": ("created_by", "modified_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:config_id>/test/",
                self.admin_site.admin_view(self.test_connection_view),
                name="mvola-config-test",
            ),
            path(
                "<int:config_id>/activate/",
                self.admin_site.admin_view(self.activate_config_view),
                name="mvola-config-activate",
            ),
        ]
        return custom_urls + urls

    def environment_badge(self, obj):
        if obj.environment == "production":
            color = "red"
            icon = "🔴"
            text = "PRODUCTION"
        else:
            color = "orange"
            icon = "🟡"
            text = "SANDBOX"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            text,
        )

    environment_badge.short_description = "Environnement"

    def status_badge(self, obj):
        if obj.is_active and obj.is_enabled:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        elif obj.is_enabled:
            return format_html('<span style="color: orange;">○ Inactive</span>')
        else:
            return format_html('<span style="color: red;">✗ Désactivée</span>')

    status_badge.short_description = "Statut"

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Vérifiée</span>')
        else:
            return format_html('<span style="color: gray;">○ Non vérifiée</span>')

    verification_badge.short_description = "Vérification"

    def success_rate_display(self, obj):
        rate = obj.get_success_rate()
        if rate >= 95:
            color = "green"
        elif rate >= 80:
            color = "orange"
        else:
            color = "red"

        # Format the rate as a string first
        rate_formatted = "{:.1f}%".format(rate)

        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, rate_formatted)

    success_rate_display.short_description = "Taux de réussite"

    def action_buttons(self, obj):
        if obj.pk:
            test_url = "/admin/payments/mvolaconfiguration/{}/test/".format(obj.pk)
            activate_url = "/admin/payments/mvolaconfiguration/{}/activate/".format(obj.pk)
            return format_html(
                '<a class="button" href="{}">Tester</a>&nbsp;' '<a class="button" href="{}">Activer</a>',
                test_url,
                activate_url,
            )
        return "-"

    action_buttons.short_description = "Actions"

    def test_connection_view(self, request, config_id):
        config = self.get_object(request, config_id)

        if config is None:
            messages.error(request, "Configuration introuvable")
            return redirect("admin:payments_mvolaconfiguration_changelist")

        success, message = config.test_connection()

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("admin:payments_mvolaconfiguration_change", config_id)

    def activate_config_view(self, request, config_id):
        config = self.get_object(request, config_id)

        if config is None:
            messages.error(request, "Configuration introuvable")
            return redirect("admin:payments_mvolaconfiguration_changelist")

        # Deactivate all other configurations
        MvolaConfiguration.objects.filter(is_active=True).update(is_active=False)

        # Activate this configuration
        config.is_active = True
        config.save()

        # Apply to Django settings
        config.apply_to_settings()

        messages.success(request, f"Configuration '{config.name}' activée avec succès")

        return redirect("admin:payments_mvolaconfiguration_changelist")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

        # If this config is active, apply it to settings
        if obj.is_active:
            obj.apply_to_settings()


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "stripe_event_id",
        "type",
        "processed",
        "created_at",
        "processed_at",
    )
    list_filter = ("type", "processed")
    search_fields = ("stripe_event_id", "type")
    readonly_fields = ("created_at", "processed_at", "data")


@admin.register(PaiementTaxe)
class PaiementTaxeAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "vehicule_plaque",
        "annee_fiscale",
        "montant_du_ariary",
        "montant_paye_ariary",
        "statut",
        "methode_paiement",
        "get_cash_collector",
        "date_paiement",
    )
    list_filter = ("statut", "methode_paiement", "annee_fiscale", "created_at", "collected_by")
    search_fields = (
        "transaction_id",
        "vehicule_plaque__plaque_immatriculation",
        "vehicule_plaque__proprietaire__username",
        "stripe_payment_intent_id",
        "billing_email",
        "collected_by__agent_id",
        "collected_by__full_name",
    )
    readonly_fields = ("id", "transaction_id", "created_at", "updated_at", "get_cash_transaction_link")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "vehicule_plaque", "annee_fiscale", "transaction_id")}),
        ("Montants", {"fields": ("montant_du_ariary", "montant_paye_ariary", "currency_stripe")}),
        ("Paiement", {"fields": ("statut", "methode_paiement", "date_paiement", "details_paiement")}),
        (
            "Paiement en espèces",
            {
                "fields": ("collected_by", "get_cash_transaction_link"),
                "classes": ("collapse",),
                "description": "Informations sur le paiement en espèces (si applicable)",
            },
        ),
        (
            "Stripe - Payment Intent",
            {
                "fields": (
                    "stripe_payment_intent_id",
                    "stripe_status",
                    "stripe_payment_method",
                    "stripe_charge_id",
                    "stripe_customer_id",
                    "stripe_receipt_url",
                    "stripe_created",
                    "amount_stripe",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Stripe - Metadata", {"fields": ("stripe_metadata",), "classes": ("collapse",)}),
        ("Facturation", {"fields": ("billing_name", "billing_email"), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_cash_collector(self, obj):
        """Display cash collector name if payment is cash"""
        if obj.methode_paiement == "cash" and obj.collected_by:
            return f"{obj.collected_by.full_name} ({obj.collected_by.agent_id})"
        return "-"

    get_cash_collector.short_description = "Collecté par"

    def get_cash_transaction_link(self, obj):
        """Display link to cash transaction if exists"""
        if hasattr(obj, "cash_transaction") and obj.cash_transaction:
            from django.urls import reverse
            from django.utils.html import format_html

            url = reverse("admin:payments_cashtransaction_change", args=[obj.cash_transaction.pk])
            return format_html(
                '<a href="{}" target="_blank">Transaction {} <i class="ri-external-link-line"></i></a>',
                url,
                obj.cash_transaction.transaction_number,
            )
        return "-"

    get_cash_transaction_link.short_description = "Transaction en espèces"

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of paid transactions
        if obj and obj.statut in ["PAYE", "EXONERE"]:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicule_plaque",
        "annee_fiscale",
        "est_actif",
        "nombre_scans",
        "date_generation",
        "date_expiration",
        "derniere_verification",
    )
    list_filter = ("est_actif", "annee_fiscale", "date_generation", "date_expiration")
    search_fields = ("token", "vehicule_plaque__plaque_immatriculation", "vehicule_plaque__proprietaire__username")
    readonly_fields = ("id", "token", "date_generation", "nombre_scans", "derniere_verification")
    ordering = ("-date_generation",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "vehicule_plaque", "annee_fiscale", "est_actif")}),
        ("Token et sécurité", {"fields": ("token", "date_generation", "date_expiration")}),
        ("Statistiques", {"fields": ("nombre_scans", "derniere_verification")}),
    )


# ============================================================================
# CASH PAYMENT SYSTEM ADMIN
# ============================================================================


@admin.register(CashSystemConfig)
class CashSystemConfigAdmin(admin.ModelAdmin):
    list_display = (
        "default_commission_rate",
        "dual_verification_threshold",
        "reconciliation_tolerance",
        "session_timeout_hours",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Taux de commission", {"fields": ("default_commission_rate",)}),
        (
            "Seuils et limites",
            {
                "fields": (
                    "dual_verification_threshold",
                    "reconciliation_tolerance",
                    "session_timeout_hours",
                    "void_time_limit_minutes",
                )
            },
        ),
        ("Configuration des reçus", {"fields": ("receipt_footer_text",)}),
        ("Métadonnées", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        # Only allow one configuration instance
        return not CashSystemConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of configuration
        return False


@admin.register(AgentPartenaireProfile)
class AgentPartenaireProfileAdmin(admin.ModelAdmin):
    list_display = ("agent_id", "full_name", "collection_location", "get_commission_rate", "is_active", "created_at")
    list_filter = ("is_active", "collection_location", "created_at")
    search_fields = ("agent_id", "full_name", "phone_number", "user__username", "user__email")
    readonly_fields = ("id", "created_at", "updated_at", "created_by")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "user", "agent_id", "full_name", "phone_number")}),
        ("Lieu de collecte", {"fields": ("collection_location",)}),
        ("Commission", {"fields": ("use_default_commission", "commission_rate")}),
        ("Statut", {"fields": ("is_active",)}),
        ("Métadonnées", {"fields": ("created_by", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CashSession)
class CashSessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_number",
        "collector",
        "status",
        "opening_balance",
        "closing_balance",
        "discrepancy_amount",
        "total_commission",
        "opening_time",
        "closing_time",
    )
    list_filter = ("status", "opening_time", "closing_time")
    search_fields = ("session_number", "collector__agent_id", "collector__full_name")
    readonly_fields = ("id", "session_number", "opening_time", "created_at")
    ordering = ("-opening_time",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "session_number", "collector", "status")}),
        (
            "Soldes",
            {
                "fields": (
                    "opening_balance",
                    "closing_balance",
                    "expected_balance",
                    "discrepancy_amount",
                    "total_commission",
                )
            },
        ),
        ("Horaires", {"fields": ("opening_time", "closing_time")}),
        ("Écarts et notes", {"fields": ("discrepancy_notes", "approved_by"), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of closed or reconciled sessions
        if obj and obj.status in ["closed", "reconciled"]:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_number",
        "customer_name",
        "vehicle_plate",
        "tax_amount",
        "amount_tendered",
        "change_given",
        "commission_amount",
        "collector",
        "requires_approval",
        "is_voided",
        "transaction_time",
    )
    list_filter = ("requires_approval", "is_voided", "receipt_printed", "transaction_time")
    search_fields = (
        "transaction_number",
        "customer_name",
        "vehicle_plate",
        "collector__agent_id",
        "collector__full_name",
    )
    readonly_fields = (
        "id",
        "transaction_number",
        "transaction_time",
        "approval_time",
        "receipt_print_time",
        "void_time",
    )
    ordering = ("-transaction_time",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "transaction_number", "session", "payment", "collector")}),
        ("Client et véhicule", {"fields": ("customer_name", "vehicle_plate")}),
        ("Montants", {"fields": ("tax_amount", "amount_tendered", "change_given", "commission_amount")}),
        ("Approbation", {"fields": ("requires_approval", "approved_by", "approval_time"), "classes": ("collapse",)}),
        ("Reçu", {"fields": ("receipt_printed", "receipt_print_time"), "classes": ("collapse",)}),
        ("Annulation", {"fields": ("is_voided", "voided_by", "void_time"), "classes": ("collapse",)}),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("transaction_time",), "classes": ("collapse",)}),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of transactions
        return False


@admin.register(CashReceipt)
class CashReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "vehicle_registration",
        "vehicle_owner",
        "tax_year",
        "tax_amount",
        "collector_name",
        "is_duplicate",
        "payment_date",
        "created_at",
    )
    list_filter = ("is_duplicate", "tax_year", "payment_date", "created_at")
    search_fields = ("receipt_number", "vehicle_registration", "vehicle_owner", "collector_name", "collector_id")
    readonly_fields = ("id", "receipt_number", "qr_code_data", "created_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "receipt_number", "transaction", "qr_code")}),
        ("Véhicule", {"fields": ("vehicle_registration", "vehicle_owner", "tax_year")}),
        ("Montants", {"fields": ("tax_amount", "amount_paid", "change_given")}),
        ("Collecteur", {"fields": ("collector_name", "collector_id")}),
        ("QR Code", {"fields": ("qr_code_data",), "classes": ("collapse",)}),
        ("Duplicata", {"fields": ("is_duplicate", "original_receipt"), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("payment_date", "created_at"), "classes": ("collapse",)}),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of receipts
        return False


@admin.register(CommissionRecord)
class CommissionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "collector",
        "tax_amount",
        "commission_rate",
        "commission_amount",
        "payment_status",
        "paid_date",
        "created_at",
    )
    list_filter = ("payment_status", "paid_date", "created_at")
    search_fields = ("collector__agent_id", "collector__full_name", "transaction__transaction_number")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "collector", "session", "transaction")}),
        ("Montants", {"fields": ("tax_amount", "commission_rate", "commission_amount")}),
        ("Paiement", {"fields": ("payment_status", "paid_date", "paid_by")}),
        ("Métadonnées", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(CashAuditLog)
class CashAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action_type", "user", "session", "transaction", "timestamp", "ip_address")
    list_filter = ("action_type", "timestamp")
    search_fields = ("user__username", "session__session_number", "transaction__transaction_number", "ip_address")
    readonly_fields = (
        "id",
        "action_type",
        "user",
        "session",
        "transaction",
        "action_data",
        "ip_address",
        "user_agent",
        "previous_hash",
        "current_hash",
        "timestamp",
    )
    ordering = ("-timestamp",)

    fieldsets = (
        ("Informations de base", {"fields": ("id", "action_type", "user", "timestamp")}),
        ("Références", {"fields": ("session", "transaction")}),
        ("Données", {"fields": ("action_data",), "classes": ("collapse",)}),
        ("Contexte", {"fields": ("ip_address", "user_agent"), "classes": ("collapse",)}),
        ("Chaîne de hachage", {"fields": ("previous_hash", "current_hash"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent modification of audit logs
        return False
