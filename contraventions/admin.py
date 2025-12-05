from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contestation,
    Contravention,
    ContraventionAuditLog,
    DossierFourriere,
    PhotoContravention,
    TypeInfraction,
)


@admin.register(TypeInfraction)
class TypeInfractionAdmin(admin.ModelAdmin):
    list_display = [
        "article_code",
        "nom",
        "categorie",
        "montant_min_ariary",
        "montant_max_ariary",
        "montant_variable",
        "fourriere_obligatoire",
        "est_actif",
    ]
    list_filter = ["categorie", "montant_variable", "fourriere_obligatoire", "est_actif"]
    search_fields = ["nom", "article_code", "sanctions_administratives"]
    list_editable = ["est_actif"]
    ordering = ["categorie", "nom"]

    fieldsets = (
        ("Informations générales", {"fields": ("nom", "article_code", "loi_reference", "categorie")}),
        ("Montants", {"fields": ("montant_min_ariary", "montant_max_ariary", "montant_variable")}),
        ("Sanctions", {"fields": ("sanctions_administratives", "fourriere_obligatoire", "emprisonnement_possible")}),
        ("Pénalités", {"fields": ("penalite_accident_ariary", "penalite_recidive_pct")}),
        ("Statut", {"fields": ("est_actif",)}),
    )


class PhotoContraventionInline(admin.TabularInline):
    model = PhotoContravention
    extra = 0
    readonly_fields = ["thumbnail", "uploaded_by", "created_at"]
    fields = ["fichier", "description", "ordre", "thumbnail", "uploaded_by", "created_at"]

    def thumbnail(self, obj):
        if obj.fichier:
            return format_html('<img src="{}" width="100" height="75" style="object-fit: cover;" />', obj.fichier.url)
        return "Aucune image"

    thumbnail.short_description = "Aperçu"


@admin.register(Contravention)
class ContraventionAdmin(admin.ModelAdmin):
    list_display = [
        "numero_pv",
        "type_infraction",
        "agent_controleur",
        "conducteur",
        "get_vehicle_display",
        "montant_amende_ariary",
        "statut",
        "date_heure_infraction",
        "est_en_retard_display",
    ]
    list_filter = ["statut", "type_infraction__categorie", "agent_controleur", "date_heure_infraction"]
    search_fields = ["numero_pv", "conducteur__nom_complet", "conducteur__cin", "vehicule_plaque_manuelle"]
    readonly_fields = ["numero_pv", "created_at", "updated_at"]
    date_hierarchy = "date_heure_infraction"
    ordering = ["-created_at"]

    inlines = [PhotoContraventionInline]

    fieldsets = (
        (
            "Informations générales",
            {"fields": ("numero_pv", "agent_controleur", "type_infraction", "date_heure_infraction")},
        ),
        (
            "Véhicule",
            {
                "fields": (
                    "vehicule",
                    "vehicule_plaque_manuelle",
                    "vehicule_marque_manuelle",
                    "vehicule_modele_manuelle",
                )
            },
        ),
        ("Conducteur", {"fields": ("conducteur",)}),
        (
            "Lieu et circonstances",
            {"fields": ("lieu_infraction", "route_type", "route_numero", "coordonnees_gps_lat", "coordonnees_gps_lon")},
        ),
        (
            "Montant et paiement",
            {
                "fields": (
                    "montant_amende_ariary",
                    "a_accident_associe",
                    "est_recidive",
                    "statut",
                    "delai_paiement_jours",
                    "date_limite_paiement",
                    "date_paiement",
                )
            },
        ),
        ("Observations", {"fields": ("observations", "signature_electronique_conducteur")}),
        ("QR Code", {"fields": ("qr_code",)}),
    )

    def est_en_retard_display(self, obj):
        if obj.est_en_retard():
            return format_html('<span style="color: red;">⚠️ En retard</span>')
        return format_html('<span style="color: green;">✓ À jour</span>')

    est_en_retard_display.short_description = "Statut paiement"

    def get_vehicle_display(self, obj):
        return obj.get_vehicle_display()

    get_vehicle_display.short_description = "Véhicule"


@admin.register(AgentControleurProfile)
class AgentControleurProfileAdmin(admin.ModelAdmin):
    list_display = [
        "matricule",
        "nom_complet",
        "autorite_type",
        "unite_affectation",
        "grade",
        "est_actif",
        "created_at",
    ]
    list_filter = ["autorite_type", "est_actif", "created_at"]
    search_fields = ["matricule", "nom_complet", "unite_affectation", "juridiction"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Informations personnelles", {"fields": ("user", "matricule", "nom_complet", "telephone")}),
        ("Informations professionnelles", {"fields": ("unite_affectation", "grade", "autorite_type", "juridiction")}),
        ("Statut", {"fields": ("est_actif", "created_at")}),
    )


@admin.register(Conducteur)
class ConducteurAdmin(admin.ModelAdmin):
    list_display = ["nom_complet", "cin", "numero_permis", "telephone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["nom_complet", "cin", "numero_permis", "telephone"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Informations personnelles", {"fields": ("cin", "nom_complet", "date_naissance", "adresse", "telephone")}),
        ("Permis de conduire", {"fields": ("numero_permis", "categorie_permis", "date_delivrance_permis")}),
        ("Métadonnées", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(DossierFourriere)
class DossierFourriereAdmin(admin.ModelAdmin):
    list_display = [
        "numero_dossier",
        "contravention",
        "date_mise_fourriere",
        "statut",
        "frais_totaux_ariary",
        "peut_etre_restitue_display",
    ]
    list_filter = ["statut", "date_mise_fourriere"]
    search_fields = ["numero_dossier", "contravention__numero_pv"]
    readonly_fields = ["numero_dossier", "created_at", "frais_totaux_ariary"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Informations générales", {"fields": ("numero_dossier", "contravention", "date_mise_fourriere")}),
        ("Lieu de fourrière", {"fields": ("lieu_fourriere", "adresse_fourriere")}),
        (
            "Frais",
            {
                "fields": (
                    "type_vehicule",
                    "frais_transport_ariary",
                    "frais_gardiennage_journalier_ariary",
                    "duree_minimale_jours",
                    "frais_totaux_ariary",
                )
            },
        ),
        ("Sortie", {"fields": ("date_sortie_fourriere", "bon_sortie_numero", "statut")}),
        ("Notes", {"fields": ("notes",)}),
    )

    def peut_etre_restitue_display(self, obj):
        peut, msg = obj.peut_etre_restitue()
        if peut:
            return format_html('<span style="color: green;">✓ Oui</span>')
        return format_html('<span style="color: red;">✗ Non - {}</span>', msg)

    peut_etre_restitue_display.short_description = "Peut être restitué"


@admin.register(PhotoContravention)
class PhotoContraventionAdmin(admin.ModelAdmin):
    list_display = ["contravention", "description", "ordre", "uploaded_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["contravention__numero_pv", "description"]
    readonly_fields = ["thumbnail", "hash_fichier", "created_at"]
    ordering = ["contravention", "ordre"]

    def thumbnail(self, obj):
        if obj.fichier:
            return format_html('<img src="{}" width="200" height="150" style="object-fit: cover;" />', obj.fichier.url)
        return "Aucune image"

    thumbnail.short_description = "Aperçu"


@admin.register(Contestation)
class ContestationAdmin(admin.ModelAdmin):
    list_display = ["numero_contestation", "contravention", "nom_demandeur", "statut", "date_soumission", "date_examen"]
    list_filter = ["statut", "date_soumission", "date_examen"]
    search_fields = ["numero_contestation", "contravention__numero_pv", "nom_demandeur"]
    readonly_fields = ["numero_contestation", "date_soumission"]
    ordering = ["-date_soumission"]

    fieldsets = (
        ("Informations générales", {"fields": ("numero_contestation", "contravention", "date_soumission")}),
        ("Demandeur", {"fields": ("demandeur", "nom_demandeur", "email_demandeur", "telephone_demandeur")}),
        ("Contestation", {"fields": ("motif", "documents_justificatifs")}),
        ("Décision", {"fields": ("statut", "examine_par", "date_examen", "decision_motif")}),
    )


@admin.register(ContraventionAuditLog)
class ContraventionAuditLogAdmin(admin.ModelAdmin):
    list_display = ["action_type", "user", "contravention", "timestamp", "ip_address"]
    list_filter = ["action_type", "timestamp"]
    search_fields = ["user__username", "contravention__numero_pv", "action_data"]
    readonly_fields = [
        "action_type",
        "user",
        "contravention",
        "action_data",
        "ip_address",
        "user_agent",
        "previous_hash",
        "current_hash",
        "timestamp",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConfigurationSysteme)
class ConfigurationSystemeAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return ConfigurationSysteme.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ("Délais de paiement", {"fields": ("delai_paiement_standard_jours", "delai_paiement_immediat_jours")}),
        ("Pénalités", {"fields": ("penalite_retard_pct",)}),
        (
            "Frais de fourrière",
            {
                "fields": (
                    "frais_transport_fourriere_ariary",
                    "frais_gardiennage_journalier_ariary",
                    "duree_minimale_fourriere_jours",
                    "duree_minimale_fourriere_perissable_jours",
                )
            },
        ),
        ("Délais administratifs", {"fields": ("delai_annulation_directe_heures", "delai_contestation_jours")}),
        ("Métadonnées", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ["created_at", "updated_at"]
