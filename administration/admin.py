from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AdminSession,
    AdminUserProfile,
    AgentVerification,
    ConfigurationSysteme,
    DataVersion,
    EmailLog,
    PermissionGroup,
    SMTPConfiguration,
    StatistiquesPlateforme,
    VerificationQR,
)


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "host",
        "port",
        "from_email",
        "status_badge",
        "verification_badge",
        "emails_sent_today",
        "daily_limit",
        "last_test_date",
        "action_buttons",
    ]
    list_filter = ["is_active", "is_verified", "encryption", "created_at"]
    search_fields = ["name", "host", "from_email", "username"]
    readonly_fields = [
        "is_verified",
        "last_test_date",
        "last_test_result",
        "emails_sent_today",
        "last_reset_date",
        "created_at",
        "updated_at",
        "created_by",
        "modified_by",
    ]

    fieldsets = (
        ("Informations générales", {"fields": ("name", "description", "is_active")}),
        ("Configuration du serveur SMTP", {"fields": ("host", "port", "encryption", "username", "password")}),
        ("Paramètres d'expédition", {"fields": ("from_email", "from_name", "reply_to_email")}),
        ("Limites et quotas", {"fields": ("daily_limit", "emails_sent_today", "last_reset_date")}),
        (
            "Statut de vérification",
            {"fields": ("is_verified", "last_test_date", "last_test_result"), "classes": ("collapse",)},
        ),
        (
            "Métadonnées",
            {"fields": ("created_by", "modified_by", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; '
            'border-radius: 3px;">Inactive</span>'
        )

    status_badge.short_description = "Statut"

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; '
                'border-radius: 3px;">✓ Vérifié</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
            'border-radius: 3px;">⚠ Non vérifié</span>'
        )

    verification_badge.short_description = "Vérification"

    def action_buttons(self, obj):
        test_url = "/admin/administration/smtpconfiguration/{}/test/".format(obj.pk)
        return format_html('<a class="button" href="{}">Tester</a>', test_url)

    action_buttons.short_description = "Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:pk>/test/", self.admin_site.admin_view(self.test_smtp_view), name="smtp-test"),
        ]
        return custom_urls + urls

    def test_smtp_view(self, request, pk):
        """Test SMTP configuration"""
        smtp_config = SMTPConfiguration.objects.get(pk=pk)

        if request.method == "POST":
            test_email = request.POST.get("test_email")

            if test_email:
                # Test connection and send test email
                success, message = smtp_config.test_connection()

                if success:
                    # Try to send a test email
                    try:
                        from django.conf import settings
                        from django.core.mail import send_mail

                        # Temporarily override email settings
                        original_backend = settings.EMAIL_BACKEND
                        settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
                        settings.EMAIL_HOST = smtp_config.host
                        settings.EMAIL_PORT = smtp_config.port
                        settings.EMAIL_HOST_USER = smtp_config.username
                        settings.EMAIL_HOST_PASSWORD = smtp_config.password
                        settings.EMAIL_USE_TLS = smtp_config.encryption == "tls"
                        settings.EMAIL_USE_SSL = smtp_config.encryption == "ssl"
                        settings.DEFAULT_FROM_EMAIL = f"{smtp_config.from_name} <{smtp_config.from_email}>"

                        send_mail(
                            subject="Test de configuration SMTP - Tax Collector",
                            message="Ceci est un email de test pour vérifier la configuration SMTP.",
                            from_email=smtp_config.from_email,
                            recipient_list=[test_email],
                            fail_silently=False,
                        )

                        # Restore original backend
                        settings.EMAIL_BACKEND = original_backend

                        messages.success(request, f"✓ Email de test envoyé avec succès à {test_email}")
                    except Exception as e:
                        messages.error(request, f"✗ Erreur lors de l'envoi de l'email de test: {str(e)}")
                else:
                    messages.error(request, message)
            else:
                # Just test connection
                success, message = smtp_config.test_connection()
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

            return redirect("admin:administration_smtpconfiguration_change", pk)

        context = {
            "smtp_config": smtp_config,
            "title": f"Tester la configuration SMTP: {smtp_config.name}",
            "opts": self.model._meta,
        }
        return render(request, "admin/smtp_test.html", context)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ["subject", "recipient", "email_type", "status_badge", "smtp_config", "created_at", "sent_at"]
    list_filter = ["status", "email_type", "created_at", "smtp_config"]
    search_fields = ["recipient", "subject", "body"]
    readonly_fields = ["created_at", "sent_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Détails de l'email", {"fields": ("recipient", "subject", "body", "html_body")}),
        ("Statut", {"fields": ("status", "error_message", "smtp_config")}),
        ("Métadonnées", {"fields": ("email_type", "related_object_type", "related_object_id")}),
        ("Horodatage", {"fields": ("created_at", "sent_at")}),
    )

    def status_badge(self, obj):
        colors = {"pending": "#ffc107", "sent": "#28a745", "failed": "#dc3545", "bounced": "#fd7e14"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; ' 'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Statut"

    def has_add_permission(self, request):
        # Email logs are created automatically, not manually
        return False


@admin.register(AgentVerification)
class AgentVerificationAdmin(admin.ModelAdmin):
    list_display = ["user", "numero_badge", "zone_affectation", "est_actif", "date_creation"]
    list_filter = ["est_actif", "zone_affectation", "date_creation"]
    search_fields = ["user__username", "user__email", "numero_badge", "zone_affectation"]
    readonly_fields = ["date_creation", "date_modification"]


@admin.register(VerificationQR)
class VerificationQRAdmin(admin.ModelAdmin):
    list_display = ["qr_code", "agent", "statut_verification", "date_verification"]
    list_filter = ["statut_verification", "date_verification"]
    search_fields = ["qr_code__code", "agent__user__username"]
    readonly_fields = ["date_verification"]
    date_hierarchy = "date_verification"


@admin.register(StatistiquesPlateforme)
class StatistiquesPlateformeAdmin(admin.ModelAdmin):
    list_display = ["type_statistique", "valeur", "date_statistique", "created_at"]
    list_filter = ["type_statistique", "date_statistique"]
    search_fields = ["type_statistique"]
    readonly_fields = ["created_at"]
    date_hierarchy = "date_statistique"


@admin.register(ConfigurationSysteme)
class ConfigurationSystemeAdmin(admin.ModelAdmin):
    list_display = ["cle", "type_config", "valeur", "est_actif", "date_modification"]
    list_filter = ["type_config", "est_actif", "date_modification"]
    search_fields = ["cle", "valeur", "description"]
    readonly_fields = ["date_creation", "date_modification"]


@admin.register(AdminUserProfile)
class AdminUserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "is_2fa_enabled", "is_ip_whitelist_enabled", "failed_login_attempts", "last_login_ip"]
    list_filter = ["is_2fa_enabled", "is_ip_whitelist_enabled", "theme_preference"]
    search_fields = ["user__username", "user__email", "last_login_ip"]
    readonly_fields = ["created_at", "updated_at", "last_password_change"]


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "created_at"]
    search_fields = ["name", "description"]
    filter_horizontal = ["users"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AdminSession)
class AdminSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "is_active", "created_at", "last_activity"]
    list_filter = ["is_active", "created_at", "last_activity"]
    search_fields = ["user__username", "ip_address", "session_key"]
    readonly_fields = ["created_at", "last_activity"]
    date_hierarchy = "created_at"


@admin.register(DataVersion)
class DataVersionAdmin(admin.ModelAdmin):
    list_display = ["content_type", "object_id", "version_number", "changed_by", "changed_at"]
    list_filter = ["content_type", "changed_at"]
    search_fields = ["object_id", "change_reason"]
    readonly_fields = ["changed_at"]
    date_hierarchy = "changed_at"
