from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import DocumentVehicule, VehicleType, Vehicule
from .utils import get_conversion_info, get_puissance_fiscale_from_cylindree


class VehiculeForm(forms.ModelForm):
    """Form for creating and editing vehicles"""

    proprietaire = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label=_("Select owner"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Vehicle Owner"),
        help_text=_("Select the owner of this vehicle (administrators only)"),
    )

    class Meta:
        model = Vehicule
        fields = [
            "proprietaire",
            "nom_proprietaire",
            "plaque_immatriculation",
            "marque",
            "modele",
            "vin",
            "couleur",
            "puissance_fiscale_cv",
            "cylindree_cm3",
            "source_energie",
            "date_premiere_circulation",
            "categorie_vehicule",
            "type_vehicule",
        ]
        widgets = {
            "proprietaire": forms.Select(attrs={"class": "form-select"}),
            "nom_proprietaire": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Samoela")}),
            "plaque_immatriculation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex: 1234 TAA"),
                    "pattern": r"[0-9]{1,4}\s[A-Z]{2,3}",
                    "title": _("Format: 1234 TAA"),
                }
            ),
            "marque": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: TOYOTA, HONDA, YAMAHA")}),
            "modele": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: COROLLA, CIVIC")}),
            "vin": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: 0RT019968")}),
            "couleur": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Blanc, Noir, Rouge")}),
            "puissance_fiscale_cv": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": _("Ex: 8")}
            ),
            "cylindree_cm3": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": _("Ex: 1600")}
            ),
            "source_energie": forms.Select(attrs={"class": "form-select"}),
            "date_premiere_circulation": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "categorie_vehicule": forms.Select(attrs={"class": "form-select"}),
            "type_vehicule": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nom_proprietaire": _("Nom du propriétaire"),
            "plaque_immatriculation": _("Plaque d'immatriculation"),
            "marque": _("Marque"),
            "modele": _("Modèle"),
            "vin": _("VIN (Numéro de châssis)"),
            "couleur": _("Couleur"),
            "puissance_fiscale_cv": _("Puissance fiscale (CV)"),
            "cylindree_cm3": _("Cylindrée (cm³)"),
            "source_energie": _("Source d'énergie"),
            "date_premiere_circulation": _("Date de première circulation"),
            "categorie_vehicule": _("Catégorie de véhicule"),
            "type_vehicule": _("Type de véhicule"),
        }
        help_texts = {
            "nom_proprietaire": _("Nom complet du propriétaire légal du véhicule (ex: Samoela)"),
            "plaque_immatriculation": _("Format requis: 1234 TAA (chiffres + espace + lettres)"),
            "marque": _("Marque du véhicule (visible sur la carte grise)"),
            "modele": _("Modèle du véhicule (optionnel)"),
            "vin": _("Numéro de châssis / VIN (optionnel, visible sur la carte grise)"),
            "couleur": _("Couleur principale du véhicule (optionnel)"),
            "puissance_fiscale_cv": _(
                "Puissance fiscale en chevaux vapeur (CV) - Obligatoire pour le calcul de la taxe"
            ),
            "cylindree_cm3": _(
                "Cylindrée du moteur en cm³ (optionnel) - Si vous la connaissez, nous pouvons vous aider à déterminer les CV"
            ),
            "date_premiere_circulation": _("Date de première mise en circulation du véhicule"),
        }

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if provided
        user = kwargs.pop("user", None)
        # Store user for validation in clean method
        self._user = user
        super().__init__(*args, **kwargs)

        # Make cylindree_cm3 optional for electric vehicles
        self.fields["cylindree_cm3"].required = False

        # Handle proprietaire field visibility and queryset based on user permissions
        if user:
            from administration.mixins import is_admin_user

            if is_admin_user(user):
                # Admin can select any user as owner
                self.fields["proprietaire"].queryset = User.objects.filter(is_active=True).order_by(
                    "first_name", "last_name", "username"
                )
                self.fields["proprietaire"].required = True
                # Update the help text for admins
                self.fields["proprietaire"].help_text = _("Select the owner of this vehicle")
            else:
                # Non-admin users cannot see or modify the proprietaire field
                del self.fields["proprietaire"]

            # Filter vehicle categories based on user type
            if hasattr(user, "profile") and user.profile:
                allowed_categories = user.profile.get_allowed_vehicle_categories()
                if allowed_categories:
                    # Filter choices to only show allowed categories
                    current_choices = self.fields["categorie_vehicule"].choices
                    filtered_choices = [
                        choice
                        for choice in current_choices
                        if choice[0] in allowed_categories or choice[0] == ""  # Keep empty choice
                    ]
                    self.fields["categorie_vehicule"].choices = filtered_choices
        else:
            # If no user provided, hide the proprietaire field
            del self.fields["proprietaire"]

    def clean_plaque_immatriculation(self):
        """Validate license plate format"""
        plaque = self.cleaned_data.get("plaque_immatriculation", "").upper().strip()

        if not plaque:
            raise forms.ValidationError(_("La plaque d'immatriculation est requise"))

        # Basic format validation (more detailed validation in model)
        import re

        if not re.match(r"^[0-9]{1,4}\s[A-Z]{2,3}$", plaque):
            raise forms.ValidationError(_("Format invalide. Utilisez le format: 1234 TAA"))

        return plaque

    def clean(self):
        """Cross-field validation avec suggestion de conversion"""
        cleaned_data = super().clean()
        source_energie = cleaned_data.get("source_energie")
        cylindree_cm3 = cleaned_data.get("cylindree_cm3")
        puissance_fiscale_cv = cleaned_data.get("puissance_fiscale_cv")
        categorie_vehicule = cleaned_data.get("categorie_vehicule")

        # Validate vehicle category based on user type
        user = getattr(self, "_user", None)
        if user and hasattr(user, "profile") and user.profile and categorie_vehicule:
            allowed_categories = user.profile.get_allowed_vehicle_categories()
            if allowed_categories and categorie_vehicule not in allowed_categories:
                self.add_error(
                    "categorie_vehicule",
                    _(
                        "Cette catégorie de véhicule n'est pas autorisée pour votre type d'utilisateur. Catégories autorisées: %(categories)s"
                    )
                    % {"categories": ", ".join(allowed_categories)},
                )

        # For non-electric vehicles, cylindree is recommended
        if source_energie in ["Essence", "Diesel", "Hybride"] and not cylindree_cm3:
            self.add_error("cylindree_cm3", _("La cylindrée est recommandée pour ce type de véhicule"))

        # Suggestion intelligente de conversion
        if cylindree_cm3 and not puissance_fiscale_cv:
            conversion_info = get_conversion_info(cylindree_cm3)
            if conversion_info["valid"]:
                cv_suggere = conversion_info["cv_suggere"]
                plage_description = conversion_info["plage_description"]
                message = _(
                    f"Suggestion: Pour {cylindree_cm3}cm³, la puissance fiscale est généralement {plage_description}. Nous suggérons {cv_suggere} CV."
                )
                # Ajouter un message informatif plutôt qu'une erreur
                if hasattr(self, "_conversion_suggestion"):
                    self._conversion_suggestion = message
                else:
                    self._conversion_suggestion = message

        # Validation de cohérence si les deux champs sont remplis
        # Skip this validation for aerial and maritime vehicles (only for terrestrial)
        vehicle_category = cleaned_data.get("vehicle_category", "TERRESTRE")
        if cylindree_cm3 and puissance_fiscale_cv and vehicle_category == "TERRESTRE":
            conversion_info = get_conversion_info(cylindree_cm3)
            if conversion_info["valid"]:
                cv_min = conversion_info["cv_min"]
                cv_max = conversion_info["cv_max"]

                if not (cv_min <= puissance_fiscale_cv <= cv_max):
                    plage_description = conversion_info["plage_description"]
                    self.add_error(
                        "puissance_fiscale_cv",
                        _(
                            f"Attention: Pour {cylindree_cm3}cm³, la puissance fiscale est généralement {plage_description}. Vérifiez votre saisie."
                        ),
                    )

        return cleaned_data

    def get_conversion_suggestion(self):
        """Retourne la suggestion de conversion si disponible"""
        return getattr(self, "_conversion_suggestion", None)


class VehiculeSearchForm(forms.Form):
    """Form for searching vehicles"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Rechercher par plaque, marque, propriétaire..."),
            }
        ),
        label=_("Recherche"),
    )

    marque = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Filtrer par marque..."),
            }
        ),
        label=_("Marque"),
    )

    source_energie = forms.ChoiceField(
        required=False,
        choices=[("", _("Toutes les énergies"))] + Vehicule.SOURCE_ENERGIE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Source d'énergie"),
    )

    categorie_vehicule = forms.ChoiceField(
        required=False,
        choices=[("", _("Toutes les catégories"))] + Vehicule.CATEGORIE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Catégorie"),
    )

    type_vehicule = forms.ChoiceField(
        required=False,
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Type de véhicule"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate type_vehicule choices dynamically
        vehicle_type_choices = [("", _("Tous les types"))]
        for vtype in VehicleType.get_active_types():
            vehicle_type_choices.append((vtype.id, vtype.nom))
        self.fields["type_vehicule"].choices = vehicle_type_choices


class VehicleDocumentUploadForm(forms.ModelForm):
    """Formulaire pour télécharger un document lié à un véhicule"""

    class Meta:
        model = DocumentVehicule
        fields = ["document_type", "fichier", "note", "expiration_date"]
        widgets = {
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "fichier": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "expiration_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "document_type": _("Type de document"),
            "fichier": _("Fichier"),
            "note": _("Note (optionnel)"),
            "expiration_date": _("Date d'expiration (optionnel)"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All fields except file are optional except document_type
        self.fields["note"].required = False
        self.fields["expiration_date"].required = False

    def clean_fichier(self):
        """Validate file size and allowed types (PDF, JPG, JPEG, PNG, WEBP)"""
        fichier = self.cleaned_data.get("fichier")
        if not fichier:
            raise forms.ValidationError(_("Veuillez sélectionner un fichier."))

        # Size limit: 10MB
        max_size_bytes = 10 * 1024 * 1024
        if getattr(fichier, "size", 0) > max_size_bytes:
            raise forms.ValidationError(_("La taille du fichier dépasse 10MB."))

        # Extension check
        import os

        allowed_exts = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
        ext = os.path.splitext(fichier.name)[1].lower()
        if ext not in allowed_exts:
            raise forms.ValidationError(_("Formats autorisés: PDF, JPG, JPEG, PNG, WEBP."))

        # MIME type check (best effort)
        allowed_mimes = {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        }
        content_type = getattr(fichier, "content_type", "")
        if content_type and content_type not in allowed_mimes:
            # Only warn/block if clearly not allowed
            raise forms.ValidationError(_("Type de fichier non supporté."))

        return fichier


class VehicleDocumentUpdateForm(forms.ModelForm):
    """Formulaire pour modifier les métadonnées d'un document"""

    class Meta:
        model = DocumentVehicule
        fields = ["document_type", "note", "expiration_date", "verification_status", "verification_comment"]
        widgets = {
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "expiration_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "verification_status": forms.Select(attrs={"class": "form-select"}),
            "verification_comment": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
        labels = {
            "document_type": _("Type de document"),
            "note": _("Note"),
            "expiration_date": _("Date d'expiration"),
            "verification_status": _("Statut de vérification"),
            "verification_comment": _("Commentaire de vérification"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["note"].required = False
        self.fields["expiration_date"].required = False
        self.fields["verification_comment"].required = False


class FleetImportUploadForm(forms.Form):
    fichier = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}), label=_("Fichier à importer")
    )
    type_fichier = forms.ChoiceField(
        choices=[("csv", "CSV"), ("xlsx", "Excel")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Type de fichier"),
    )


class FleetImportMappingForm(forms.Form):
    mapping_json = forms.CharField(widget=forms.HiddenInput())
    options_json = forms.CharField(widget=forms.HiddenInput(), required=False)


class FleetBulkEditForm(forms.Form):
    est_actif = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=[("", _("Ne pas modifier")), ("true", _("Activer")), ("false", _("Désactiver"))],
            attrs={"class": "form-select"},
        ),
        label=_("Statut actif"),
    )
    source_energie = forms.ChoiceField(
        required=False,
        choices=[("", _("Ne pas modifier"))] + Vehicule.SOURCE_ENERGIE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Source d'énergie"),
    )
    categorie_vehicule = forms.ChoiceField(
        required=False,
        choices=[("", _("Ne pas modifier"))] + Vehicule.CATEGORIE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Catégorie"),
    )
    type_vehicule = forms.ModelChoiceField(
        required=False,
        queryset=VehicleType.get_active_types(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Type de véhicule"),
    )


class VehiculeAerienForm(forms.ModelForm):
    """Formulaire pour véhicules aériens"""

    proprietaire = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label=_("Sélectionner le propriétaire"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Propriétaire du véhicule"),
        help_text=_("Sélectionner le propriétaire de cet aéronef (administrateurs uniquement)"),
    )

    class Meta:
        model = Vehicule
        fields = [
            "proprietaire",
            "nom_proprietaire",
            "immatriculation_aerienne",
            "type_vehicule",
            "marque",
            "modele",
            "numero_serie_aeronef",
            "masse_maximale_decollage_kg",
            "puissance_moteur_kw",
            "cylindree_cm3",  # Include but will be optional
            "source_energie",  # Include for model compatibility
            "date_premiere_circulation",
            "categorie_vehicule",
        ]
        widgets = {
            "nom_proprietaire": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Jean Dupont")}),
            "immatriculation_aerienne": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex: 5R-ABC"),
                    "pattern": r"[0-9][A-Z]-[A-Z]{3}",
                    "title": _("Format: 5R-ABC (pour Madagascar)"),
                }
            ),
            "type_vehicule": forms.Select(attrs={"class": "form-select"}),
            "marque": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Ex: CESSNA, AIRBUS, ROBINSON")}
            ),
            "modele": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: 172, A320, R44")}),
            "numero_serie_aeronef": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: 17280123")}),
            "masse_maximale_decollage_kg": forms.NumberInput(
                attrs={"class": "form-control", "min": "10", "max": "500000", "placeholder": _("Ex: 1200")}
            ),
            "puissance_moteur_kw": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "0.01", "placeholder": _("Ex: 120.5")}
            ),
            "cylindree_cm3": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": _("Optionnel - Non applicable pour aériens")}
            ),
            "source_energie": forms.Select(attrs={"class": "form-select"}),
            "date_premiere_circulation": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "categorie_vehicule": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nom_proprietaire": _("Nom du propriétaire"),
            "immatriculation_aerienne": _("Numéro d'immatriculation aérienne"),
            "type_vehicule": _("Type d'aéronef"),
            "marque": _("Constructeur"),
            "modele": _("Modèle"),
            "numero_serie_aeronef": _("Numéro de série"),
            "masse_maximale_decollage_kg": _("Masse maximale au décollage (kg)"),
            "puissance_moteur_kw": _("Puissance moteur (kW)"),
            "cylindree_cm3": _("Cylindrée (cm³)"),
            "source_energie": _("Source d'énergie"),
            "date_premiere_circulation": _("Date de première mise en service"),
            "categorie_vehicule": _("Catégorie de véhicule"),
        }
        help_texts = {
            "nom_proprietaire": _("Nom complet du propriétaire légal de l'aéronef"),
            "immatriculation_aerienne": _("Numéro d'immatriculation officiel (ex: 5R-ABC pour Madagascar)"),
            "type_vehicule": _("Type d'aéronef (Avion, Hélicoptère, Drone, ULM, etc.)"),
            "marque": _("Constructeur de l'aéronef (ex: CESSNA, AIRBUS, ROBINSON)"),
            "modele": _("Modèle de l'aéronef (ex: 172, A320, R44)"),
            "numero_serie_aeronef": _("Numéro de série constructeur de l'aéronef"),
            "masse_maximale_decollage_kg": _(
                "Masse maximale autorisée au décollage en kilogrammes (10 kg - 500,000 kg)"
            ),
            "puissance_moteur_kw": _("Puissance du moteur en kilowatts"),
            "cylindree_cm3": _("Cylindrée du moteur (optionnel - non applicable pour aériens)"),
            "source_energie": _("Type de carburant ou énergie"),
            "date_premiere_circulation": _("Date de première mise en service de l'aéronef"),
            "categorie_vehicule": _("Catégorie administrative du véhicule"),
        }

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if provided
        user = kwargs.pop("user", None)
        # Store user for validation in clean method
        self._user = user
        super().__init__(*args, **kwargs)

        # Make cylindree_cm3 optional for aerial vehicles (not applicable)
        self.fields["cylindree_cm3"].required = False

        # Make source_energie optional for aerial (will default to 'Essence' or appropriate)
        self.fields["source_energie"].required = False

        # Handle proprietaire field visibility and queryset based on user permissions
        if user:
            from administration.mixins import is_admin_user

            if is_admin_user(user):
                # Admin can select any user as owner
                self.fields["proprietaire"].queryset = User.objects.filter(is_active=True).order_by(
                    "first_name", "last_name", "username"
                )
                self.fields["proprietaire"].required = True
                # Update the help text for admins
                self.fields["proprietaire"].help_text = _("Sélectionner le propriétaire de cet aéronef")
            else:
                # Non-admin users cannot see or modify the proprietaire field
                del self.fields["proprietaire"]

            # Filter vehicle categories based on user type
            if hasattr(user, "profile") and user.profile:
                allowed_categories = user.profile.get_allowed_vehicle_categories()
                if allowed_categories:
                    # Filter choices to only show allowed categories
                    current_choices = self.fields["categorie_vehicule"].choices
                    filtered_choices = [
                        choice
                        for choice in current_choices
                        if choice[0] in allowed_categories or choice[0] == ""  # Keep empty choice
                    ]
                    self.fields["categorie_vehicule"].choices = filtered_choices
        else:
            # If no user provided, hide the proprietaire field
            del self.fields["proprietaire"]

        # Filter type_vehicule to show only aerial types
        aerial_type_names = ["Avion", "Hélicoptère", "Drone", "ULM", "Planeur", "Ballon"]
        self.fields["type_vehicule"].queryset = VehicleType.objects.filter(
            est_actif=True, nom__in=aerial_type_names
        ).order_by("ordre_affichage", "nom")

    def clean_immatriculation_aerienne(self):
        """Valider le format de l'immatriculation aérienne"""
        immat = self.cleaned_data.get("immatriculation_aerienne", "").upper().strip()

        if not immat:
            raise forms.ValidationError(_("Le numéro d'immatriculation aérienne est requis"))

        # Validation format Madagascar: 5R-XXX
        import re

        if not re.match(r"^[0-9][A-Z]-[A-Z]{3}$", immat):
            raise forms.ValidationError(_("Format invalide. Utilisez le format: 5R-ABC (pour Madagascar)"))

        return immat

    def clean_masse_maximale_decollage_kg(self):
        """Valider la masse maximale au décollage"""
        masse = self.cleaned_data.get("masse_maximale_decollage_kg")

        if masse is None:
            raise forms.ValidationError(_("La masse maximale au décollage est requise"))

        if masse < 10:
            raise forms.ValidationError(_("La masse maximale doit être d'au moins 10 kg"))

        if masse > 500000:
            raise forms.ValidationError(_("La masse maximale ne peut pas dépasser 500,000 kg"))

        return masse

    def _post_clean(self):
        """Set vehicle_category before model validation"""
        # Set vehicle_category on the instance before model validation
        self.instance.vehicle_category = "AERIEN"
        # Call parent's _post_clean which will validate the model
        super()._post_clean()

    def clean(self):
        """Validation croisée et auto-définition de vehicle_category"""
        # Don't call VehiculeForm's clean() to avoid form-level cylindree_cm3/CV validation
        # Call ModelForm.clean() directly instead
        cleaned_data = forms.ModelForm.clean(self)

        # Ensure vehicle_category is set in cleaned_data
        cleaned_data["vehicle_category"] = "AERIEN"

        # Valider que type_vehicule est un type aérien
        type_vehicule = cleaned_data.get("type_vehicule")
        if type_vehicule:
            aerial_type_names = ["Avion", "Hélicoptère", "Drone", "ULM", "Planeur", "Ballon"]
            if type_vehicule.nom not in aerial_type_names:
                self.add_error(
                    "type_vehicule",
                    _("Le type de véhicule doit être un type aérien (Avion, Hélicoptère, Drone, ULM, Planeur, Ballon)"),
                )

        # Validate vehicle category based on user type
        user = getattr(self, "_user", None)
        categorie_vehicule = cleaned_data.get("categorie_vehicule")
        if user and hasattr(user, "profile") and user.profile and categorie_vehicule:
            allowed_categories = user.profile.get_allowed_vehicle_categories()
            if allowed_categories and categorie_vehicule not in allowed_categories:
                self.add_error(
                    "categorie_vehicule",
                    _(
                        "Cette catégorie de véhicule n'est pas autorisée pour votre type d'utilisateur. Catégories autorisées: %(categories)s"
                    )
                    % {"categories": ", ".join(allowed_categories)},
                )

        return cleaned_data


class VehiculeMaritimeForm(forms.ModelForm):
    """Formulaire pour véhicules maritimes"""

    proprietaire = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label=_("Sélectionner le propriétaire"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Propriétaire du véhicule"),
        help_text=_("Sélectionner le propriétaire de ce navire (administrateurs uniquement)"),
    )

    puissance_moteur_unit = forms.ChoiceField(
        choices=[("CV", "CV (Chevaux)"), ("kW", "kW (Kilowatts)")],
        initial="CV",
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Unité de puissance"),
        help_text=_("Choisissez l'unité dans laquelle vous connaissez la puissance"),
    )

    class Meta:
        model = Vehicule
        fields = [
            "proprietaire",
            "nom_proprietaire",
            "numero_francisation",
            "nom_navire",
            "type_vehicule",
            "marque",
            "modele",
            "longueur_metres",
            "tonnage_tonneaux",
            "puissance_fiscale_cv",
            "puissance_moteur_kw",
            "cylindree_cm3",  # Include but will be optional
            "source_energie",  # Include for model compatibility
            "date_premiere_circulation",
            "categorie_vehicule",
        ]
        widgets = {
            "nom_proprietaire": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Jean Dupont")}),
            "numero_francisation": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: FR-12345")}),
            "nom_navire": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: L'Aventurier")}),
            "type_vehicule": forms.Select(attrs={"class": "form-select"}),
            "marque": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Ex: BENETEAU, YAMAHA, SEA-DOO")}
            ),
            "modele": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: Oceanis 40, VX Cruiser")}),
            "longueur_metres": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "400", "step": "0.01", "placeholder": _("Ex: 8.5")}
            ),
            "tonnage_tonneaux": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": _("Ex: 5.2")}
            ),
            "puissance_fiscale_cv": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "0.01", "placeholder": _("Ex: 25")}
            ),
            "puissance_moteur_kw": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "step": "0.01", "placeholder": _("Ex: 18.4")}
            ),
            "cylindree_cm3": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": _("Optionnel - Non applicable pour maritimes"),
                }
            ),
            "source_energie": forms.Select(attrs={"class": "form-select"}),
            "date_premiere_circulation": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "categorie_vehicule": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nom_proprietaire": _("Nom du propriétaire"),
            "numero_francisation": _("Numéro de francisation"),
            "nom_navire": _("Nom du navire"),
            "type_vehicule": _("Type d'embarcation"),
            "marque": _("Constructeur"),
            "modele": _("Modèle"),
            "longueur_metres": _("Longueur (mètres)"),
            "tonnage_tonneaux": _("Tonnage (tonneaux)"),
            "puissance_fiscale_cv": _("Puissance moteur (CV)"),
            "puissance_moteur_kw": _("Puissance moteur (kW)"),
            "cylindree_cm3": _("Cylindrée (cm³)"),
            "source_energie": _("Source d'énergie"),
            "date_premiere_circulation": _("Date de première mise à l'eau"),
            "categorie_vehicule": _("Catégorie de véhicule"),
        }
        help_texts = {
            "nom_proprietaire": _("Nom complet du propriétaire légal du navire"),
            "numero_francisation": _("Numéro officiel de francisation du navire"),
            "nom_navire": _("Nom officiel du navire ou de l'embarcation"),
            "type_vehicule": _("Type d'embarcation (Bateau de plaisance, Yacht, Jet-ski, etc.)"),
            "marque": _("Constructeur du navire (ex: BENETEAU, YAMAHA, SEA-DOO)"),
            "modele": _("Modèle du navire (ex: Oceanis 40, VX Cruiser)"),
            "longueur_metres": _("Longueur totale du navire en mètres (1m - 400m)"),
            "tonnage_tonneaux": _("Tonnage du navire en tonneaux (optionnel)"),
            "puissance_fiscale_cv": _("Puissance du moteur en chevaux (CV)"),
            "puissance_moteur_kw": _("Puissance du moteur en kilowatts (kW)"),
            "cylindree_cm3": _("Cylindrée du moteur (optionnel - non applicable pour maritimes)"),
            "source_energie": _("Type de carburant ou énergie"),
            "date_premiere_circulation": _("Date de première mise à l'eau du navire"),
            "categorie_vehicule": _("Catégorie administrative du véhicule"),
        }

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if provided
        user = kwargs.pop("user", None)
        # Store user for validation in clean method
        self._user = user
        super().__init__(*args, **kwargs)

        # Make both power fields optional initially (one will be required in clean())
        self.fields["puissance_fiscale_cv"].required = False
        self.fields["puissance_moteur_kw"].required = False

        # Make cylindree_cm3 optional for maritime vehicles (not applicable)
        self.fields["cylindree_cm3"].required = False

        # Make source_energie optional for maritime (will default to 'Diesel' or 'Essence')
        self.fields["source_energie"].required = False

        # Handle proprietaire field visibility and queryset based on user permissions
        if user:
            from administration.mixins import is_admin_user

            if is_admin_user(user):
                # Admin can select any user as owner
                self.fields["proprietaire"].queryset = User.objects.filter(is_active=True).order_by(
                    "first_name", "last_name", "username"
                )
                self.fields["proprietaire"].required = True
                # Update the help text for admins
                self.fields["proprietaire"].help_text = _("Sélectionner le propriétaire de ce navire")
            else:
                # Non-admin users cannot see or modify the proprietaire field
                del self.fields["proprietaire"]

            # Filter vehicle categories based on user type
            if hasattr(user, "profile") and user.profile:
                allowed_categories = user.profile.get_allowed_vehicle_categories()
                if allowed_categories:
                    # Filter choices to only show allowed categories
                    current_choices = self.fields["categorie_vehicule"].choices
                    filtered_choices = [
                        choice
                        for choice in current_choices
                        if choice[0] in allowed_categories or choice[0] == ""  # Keep empty choice
                    ]
                    self.fields["categorie_vehicule"].choices = filtered_choices
        else:
            # If no user provided, hide the proprietaire field
            del self.fields["proprietaire"]

        # Filter type_vehicule to show only maritime types
        maritime_type_names = [
            "Bateau de plaisance",
            "Navire de commerce",
            "Yacht",
            "Jet-ski",
            "Voilier",
            "Bateau de pêche",
        ]
        self.fields["type_vehicule"].queryset = VehicleType.objects.filter(
            est_actif=True, nom__in=maritime_type_names
        ).order_by("ordre_affichage", "nom")

    def clean_numero_francisation(self):
        """Valider le format du numéro de francisation"""
        numero = self.cleaned_data.get("numero_francisation", "").upper().strip()

        if not numero:
            raise forms.ValidationError(_("Le numéro de francisation est requis"))

        # Basic format validation (alphanumeric with optional dashes)
        import re

        if not re.match(r"^[A-Z0-9-]+$", numero):
            raise forms.ValidationError(
                _("Format invalide. Le numéro de francisation doit contenir uniquement des lettres, chiffres et tirets")
            )

        return numero

    def clean_longueur_metres(self):
        """Valider la longueur du navire"""
        longueur = self.cleaned_data.get("longueur_metres")

        if longueur is not None:
            if longueur < 1:
                raise forms.ValidationError(_("La longueur doit être d'au moins 1 mètre"))

            if longueur > 400:
                raise forms.ValidationError(_("La longueur ne peut pas dépasser 400 mètres"))

        return longueur

    def clean_tonnage_tonneaux(self):
        """Valider le tonnage"""
        tonnage = self.cleaned_data.get("tonnage_tonneaux")

        if tonnage is not None and tonnage < 0:
            raise forms.ValidationError(_("Le tonnage doit être positif"))

        return tonnage

    def _post_clean(self):
        """Set vehicle_category before model validation"""
        # Set vehicle_category on the instance before model validation
        self.instance.vehicle_category = "MARITIME"
        # Call parent's _post_clean which will validate the model
        super()._post_clean()

    def clean(self):
        """Validation croisée, conversion CV ↔ kW, et auto-définition de vehicle_category"""
        # Don't call VehiculeForm's clean() to avoid form-level cylindree_cm3/CV validation
        # Call ModelForm.clean() directly instead
        cleaned_data = forms.ModelForm.clean(self)

        # Ensure vehicle_category is set in cleaned_data
        cleaned_data["vehicle_category"] = "MARITIME"

        # Get power values
        puissance_cv = cleaned_data.get("puissance_fiscale_cv")
        puissance_kw = cleaned_data.get("puissance_moteur_kw")
        unit = cleaned_data.get("puissance_moteur_unit", "CV")

        # At least one power value must be provided
        if not puissance_cv and not puissance_kw:
            self.add_error("puissance_fiscale_cv", _("Veuillez fournir la puissance du moteur en CV ou en kW"))
            self.add_error("puissance_moteur_kw", _("Veuillez fournir la puissance du moteur en CV ou en kW"))
        else:
            # Import conversion functions
            from decimal import Decimal

            from vehicles.services import convert_cv_to_kw, convert_kw_to_cv, validate_power_conversion

            # If both are provided, validate coherence
            if puissance_cv and puissance_kw:
                is_valid, message = validate_power_conversion(puissance_cv, puissance_kw)
                if not is_valid:
                    self.add_error("puissance_fiscale_cv", message)
                    self.add_error("puissance_moteur_kw", message)
            # If only one is provided, calculate the other
            elif puissance_cv and not puissance_kw:
                cleaned_data["puissance_moteur_kw"] = convert_cv_to_kw(puissance_cv)
            elif puissance_kw and not puissance_cv:
                # Convert kW to CV and store in puissance_fiscale_cv
                cleaned_data["puissance_fiscale_cv"] = int(convert_kw_to_cv(puissance_kw))

        # Validate vehicle category based on user type
        user = getattr(self, "_user", None)
        categorie_vehicule = cleaned_data.get("categorie_vehicule")
        if user and hasattr(user, "profile") and user.profile and categorie_vehicule:
            allowed_categories = user.profile.get_allowed_vehicle_categories()
            if allowed_categories and categorie_vehicule not in allowed_categories:
                self.add_error(
                    "categorie_vehicule",
                    _(
                        "Cette catégorie de véhicule n'est pas autorisée pour votre type d'utilisateur. Catégories autorisées: %(categories)s"
                    )
                    % {"categories": ", ".join(allowed_categories)},
                )

        return cleaned_data

    def get_maritime_classification(self):
        """
        Détermine la catégorie maritime selon les seuils PLFI
        Réutilise la logique de _classify_maritime_vehicle() du service
        """
        if not self.is_valid():
            return None

        # Create a temporary vehicle object with the form data
        from vehicles.models import Vehicule
        from vehicles.services import TaxCalculationService

        # Create temporary vehicle (not saved)
        temp_vehicle = Vehicule(
            longueur_metres=self.cleaned_data.get("longueur_metres"),
            puissance_fiscale_cv=self.cleaned_data.get("puissance_fiscale_cv"),
            puissance_moteur_kw=self.cleaned_data.get("puissance_moteur_kw"),
            type_vehicule=self.cleaned_data.get("type_vehicule"),
        )

        # Use the service to classify
        service = TaxCalculationService()
        classification = service._classify_maritime_vehicle(temp_vehicle)

        return classification
