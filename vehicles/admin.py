from django.contrib import admin

from .models import DocumentVehicule, GrilleTarifaire, VehicleType, Vehicule


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ("nom", "description", "est_actif", "ordre_affichage", "created_at")
    list_filter = ("est_actif", "created_at")
    search_fields = ("nom", "description")
    list_editable = ("est_actif", "ordre_affichage")
    ordering = ("ordre_affichage", "nom")

    fieldsets = (
        (None, {"fields": ("nom", "description")}),
        ("Configuration", {"fields": ("est_actif", "ordre_affichage")}),
    )


@admin.register(DocumentVehicule)
class DocumentVehiculeAdmin(admin.ModelAdmin):
    list_display = ("vehicule", "document_type", "verification_status", "uploaded_by", "created_at")
    list_filter = ("document_type", "verification_status", "created_at")
    search_fields = (
        "vehicule__plaque_immatriculation",
        "uploaded_by__username",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("vehicule", "uploaded_by", "document_type", "fichier", "note", "expiration_date")}),
        ("Vérification", {"fields": ("verification_status", "verification_comment")}),
        ("Meta", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = (
        "plaque_immatriculation",
        "proprietaire",
        "type_vehicule",
        "categorie_vehicule",
        "puissance_fiscale_cv",
        "est_actif",
    )
    list_filter = ("type_vehicule", "categorie_vehicule", "source_energie", "est_actif", "created_at")
    search_fields = (
        "plaque_immatriculation",
        "proprietaire__username",
        "proprietaire__first_name",
        "proprietaire__last_name",
    )
    list_editable = ("est_actif",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Informations de base",
            {"fields": ("plaque_immatriculation", "proprietaire", "type_vehicule", "categorie_vehicule")},
        ),
        (
            "Caractéristiques techniques",
            {"fields": ("puissance_fiscale_cv", "cylindree_cm3", "source_energie", "date_premiere_circulation")},
        ),
        ("Spécifications", {"fields": ("specifications_techniques",), "classes": ("collapse",)}),
        ("Statut", {"fields": ("est_actif",)}),
    )


@admin.register(GrilleTarifaire)
class GrilleTarifaireAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "puissance_range",
        "source_energie",
        "age_range",
        "montant_ariary",
        "annee_fiscale",
        "est_active",
    )
    list_filter = ("source_energie", "annee_fiscale", "est_active", "created_at")
    search_fields = ("source_energie", "annee_fiscale")
    list_editable = ("est_active",)
    ordering = ("-annee_fiscale", "puissance_min_cv", "source_energie")

    fieldsets = (
        ("Plage de puissance", {"fields": ("puissance_min_cv", "puissance_max_cv")}),
        ("Plage d'âge", {"fields": ("age_min_annees", "age_max_annees")}),
        ("Tarification", {"fields": ("source_energie", "montant_ariary", "annee_fiscale")}),
        ("Statut", {"fields": ("est_active",)}),
    )
    readonly_fields = ("created_at",)

    def puissance_range(self, obj):
        if obj.puissance_max_cv:
            return f"{obj.puissance_min_cv}-{obj.puissance_max_cv} CV"
        return f"{obj.puissance_min_cv}+ CV"

    puissance_range.short_description = "Puissance"

    def age_range(self, obj):
        if obj.age_max_annees:
            return f"{obj.age_min_annees}-{obj.age_max_annees} ans"
        return f"{obj.age_min_annees}+ ans"

    age_range.short_description = "Âge"
