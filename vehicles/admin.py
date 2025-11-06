from django.contrib import admin
from .models import VehicleType, Vehicule, DocumentVehicule


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'est_actif', 'ordre_affichage', 'created_at')
    list_filter = ('est_actif', 'created_at')
    search_fields = ('nom', 'description')
    list_editable = ('est_actif', 'ordre_affichage')
    ordering = ('ordre_affichage', 'nom')
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'description')
        }),
        ('Configuration', {
            'fields': ('est_actif', 'ordre_affichage')
        }),
    )


@admin.register(DocumentVehicule)
class DocumentVehiculeAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'document_type', 'verification_status', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'verification_status', 'created_at')
    search_fields = (
        'vehicule__plaque_immatriculation',
        'uploaded_by__username',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('vehicule', 'uploaded_by', 'document_type', 'fichier', 'note', 'expiration_date')
        }),
        ('Vérification', {
            'fields': ('verification_status', 'verification_comment')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('plaque_immatriculation', 'proprietaire', 'type_vehicule', 'categorie_vehicule', 'puissance_fiscale_cv', 'est_actif')
    list_filter = ('type_vehicule', 'categorie_vehicule', 'source_energie', 'est_actif', 'created_at')
    search_fields = ('plaque_immatriculation', 'proprietaire__username', 'proprietaire__first_name', 'proprietaire__last_name')
    list_editable = ('est_actif',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('plaque_immatriculation', 'proprietaire', 'type_vehicule', 'categorie_vehicule')
        }),
        ('Caractéristiques techniques', {
            'fields': ('puissance_fiscale_cv', 'cylindree_cm3', 'source_energie', 'date_premiere_circulation')
        }),
        ('Spécifications', {
            'fields': ('specifications_techniques',),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('est_actif',)
        }),
    )
