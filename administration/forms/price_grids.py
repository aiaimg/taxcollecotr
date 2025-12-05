"""
Price Grid Forms for Admin Console
"""

from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from vehicles.models import GrilleTarifaire


class PriceGridForm(forms.ModelForm):
    """Form for creating and editing price grids"""

    class Meta:
        model = GrilleTarifaire
        fields = [
            "puissance_min_cv",
            "puissance_max_cv",
            "source_energie",
            "age_min_annees",
            "age_max_annees",
            "montant_ariary",
            "annee_fiscale",
            "est_active",
        ]
        widgets = {
            "puissance_min_cv": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "required": True, "placeholder": "Ex: 5"}
            ),
            "puissance_max_cv": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": "Ex: 10 (leave empty for unlimited)"}
            ),
            "source_energie": forms.Select(attrs={"class": "form-select", "required": True}),
            "age_min_annees": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "value": "0", "required": True, "placeholder": "Ex: 0"}
            ),
            "age_max_annees": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "placeholder": "Ex: 10 (leave empty for unlimited)"}
            ),
            "montant_ariary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "required": True,
                    "placeholder": "Ex: 50000.00",
                }
            ),
            "annee_fiscale": forms.NumberInput(
                attrs={"class": "form-control", "min": "2020", "required": True, "placeholder": "Ex: 2024"}
            ),
            "est_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "puissance_min_cv": "Minimum Power (CV)",
            "puissance_max_cv": "Maximum Power (CV)",
            "source_energie": "Energy Source",
            "age_min_annees": "Minimum Age (Years)",
            "age_max_annees": "Maximum Age (Years)",
            "montant_ariary": "Amount (Ariary)",
            "annee_fiscale": "Fiscal Year",
            "est_active": "Active",
        }
        help_texts = {
            "puissance_min_cv": "Minimum power in CV (horsepower)",
            "puissance_max_cv": "Maximum power in CV (leave empty for unlimited)",
            "age_min_annees": "Minimum vehicle age in years",
            "age_max_annees": "Maximum vehicle age in years (leave empty for unlimited)",
            "montant_ariary": "Tax amount in Ariary",
            "annee_fiscale": "Fiscal year for this rate",
        }

    def clean_puissance_max_cv(self):
        """Validate that max power is greater than min power"""
        puissance_min = self.cleaned_data.get("puissance_min_cv")
        puissance_max = self.cleaned_data.get("puissance_max_cv")

        if puissance_max is not None and puissance_min is not None:
            if puissance_max < puissance_min:
                raise ValidationError("Maximum power must be greater than or equal to minimum power.")

        return puissance_max

    def clean_age_max_annees(self):
        """Validate that max age is greater than min age"""
        age_min = self.cleaned_data.get("age_min_annees")
        age_max = self.cleaned_data.get("age_max_annees")

        if age_max is not None and age_min is not None:
            if age_max < age_min:
                raise ValidationError("Maximum age must be greater than or equal to minimum age.")

        return age_max

    def clean_annee_fiscale(self):
        """Validate that fiscal year is current or future"""
        annee_fiscale = self.cleaned_data.get("annee_fiscale")
        current_year = timezone.now().year

        if annee_fiscale is not None:
            if annee_fiscale < current_year:
                raise ValidationError(
                    f"Fiscal year must be {current_year} or later. " f"Historical rates cannot be created or modified."
                )

        return annee_fiscale

    def clean_montant_ariary(self):
        """Validate that amount is positive"""
        montant = self.cleaned_data.get("montant_ariary")

        if montant is not None and montant <= 0:
            raise ValidationError("Amount must be greater than zero.")

        return montant

    def clean(self):
        """Additional validation for overlapping price ranges"""
        cleaned_data = super().clean()

        puissance_min = cleaned_data.get("puissance_min_cv")
        puissance_max = cleaned_data.get("puissance_max_cv")
        source_energie = cleaned_data.get("source_energie")
        age_min = cleaned_data.get("age_min_annees")
        age_max = cleaned_data.get("age_max_annees")
        annee_fiscale = cleaned_data.get("annee_fiscale")

        # Check for overlapping ranges
        if all([puissance_min, source_energie, age_min is not None, annee_fiscale]):
            # Build query to find overlapping grids
            overlapping = GrilleTarifaire.objects.filter(source_energie=source_energie, annee_fiscale=annee_fiscale)

            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            # Check power range overlap
            if puissance_max:
                overlapping = overlapping.filter(
                    puissance_min_cv__lte=puissance_max, puissance_max_cv__gte=puissance_min
                ) | overlapping.filter(puissance_min_cv__lte=puissance_max, puissance_max_cv__isnull=True)
            else:
                overlapping = overlapping.filter(puissance_min_cv__gte=puissance_min)

            # Check age range overlap
            if age_max:
                overlapping = overlapping.filter(
                    age_min_annees__lte=age_max, age_max_annees__gte=age_min
                ) | overlapping.filter(age_min_annees__lte=age_max, age_max_annees__isnull=True)
            else:
                overlapping = overlapping.filter(age_min_annees__gte=age_min)

            if overlapping.exists():
                raise ValidationError(
                    "This price grid overlaps with an existing grid for the same "
                    "energy source and fiscal year. Please adjust the power or age ranges."
                )

        return cleaned_data


class AerialTariffForm(forms.ModelForm):
    """Form for creating and editing aerial vehicle tariff grids"""

    class Meta:
        model = GrilleTarifaire
        fields = ["aerial_type", "montant_ariary", "annee_fiscale", "est_active"]
        widgets = {
            "aerial_type": forms.Select(attrs={"class": "form-select", "required": True}),
            "montant_ariary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "required": True,
                    "placeholder": "Ex: 2000000.00",
                }
            ),
            "annee_fiscale": forms.NumberInput(
                attrs={"class": "form-control", "min": "2020", "required": True, "placeholder": "Ex: 2026"}
            ),
            "est_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "aerial_type": "Type d'aéronef",
            "montant_ariary": "Montant (Ariary)",
            "annee_fiscale": "Année fiscale",
            "est_active": "Actif",
        }
        help_texts = {
            "aerial_type": "Type d'aéronef concerné (ALL pour tous types)",
            "montant_ariary": "Montant forfaitaire de la taxe en Ariary",
            "annee_fiscale": "Année fiscale pour ce tarif",
            "est_active": "Activer cette grille tarifaire",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default value for aerial_type
        if not self.instance.pk:
            self.initial["aerial_type"] = "ALL"
            self.initial["montant_ariary"] = Decimal("2000000.00")

    def clean_annee_fiscale(self):
        """Validate that fiscal year is current or future"""
        annee_fiscale = self.cleaned_data.get("annee_fiscale")
        current_year = timezone.now().year

        if annee_fiscale is not None:
            if annee_fiscale < current_year:
                raise ValidationError(f"L'année fiscale doit être {current_year} ou ultérieure.")

        return annee_fiscale

    def clean_montant_ariary(self):
        """Validate that amount is positive"""
        montant = self.cleaned_data.get("montant_ariary")

        if montant is not None and montant <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.")

        return montant

    def save(self, commit=True):
        """Auto-set grid_type to FLAT_AERIAL"""
        instance = super().save(commit=False)
        instance.grid_type = "FLAT_AERIAL"

        if commit:
            instance.save()

        return instance


class MaritimeTariffForm(forms.ModelForm):
    """Form for creating and editing maritime vehicle tariff grids"""

    class Meta:
        model = GrilleTarifaire
        fields = [
            "maritime_category",
            "longueur_min_metres",
            "puissance_min_cv_maritime",
            "puissance_min_kw_maritime",
            "montant_ariary",
            "annee_fiscale",
            "est_active",
        ]
        widgets = {
            "maritime_category": forms.Select(attrs={"class": "form-select", "required": True}),
            "longueur_min_metres": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "Ex: 7.00"}
            ),
            "puissance_min_cv_maritime": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "Ex: 22.00"}
            ),
            "puissance_min_kw_maritime": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "Ex: 90.00"}
            ),
            "montant_ariary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "required": True,
                    "placeholder": "Ex: 200000.00",
                }
            ),
            "annee_fiscale": forms.NumberInput(
                attrs={"class": "form-control", "min": "2020", "required": True, "placeholder": "Ex: 2026"}
            ),
            "est_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "maritime_category": "Catégorie maritime",
            "longueur_min_metres": "Longueur minimale (m)",
            "puissance_min_cv_maritime": "Puissance minimale (CV)",
            "puissance_min_kw_maritime": "Puissance minimale (kW)",
            "montant_ariary": "Montant (Ariary)",
            "annee_fiscale": "Année fiscale",
            "est_active": "Actif",
        }
        help_texts = {
            "maritime_category": "Catégorie de véhicule maritime",
            "longueur_min_metres": "Longueur minimale en mètres (optionnel selon catégorie)",
            "puissance_min_cv_maritime": "Puissance minimale en CV (optionnel selon catégorie)",
            "puissance_min_kw_maritime": "Puissance minimale en kW (optionnel selon catégorie)",
            "montant_ariary": "Montant forfaitaire de la taxe en Ariary",
            "annee_fiscale": "Année fiscale pour ce tarif",
            "est_active": "Activer cette grille tarifaire",
        }

    def clean_annee_fiscale(self):
        """Validate that fiscal year is current or future"""
        annee_fiscale = self.cleaned_data.get("annee_fiscale")
        current_year = timezone.now().year

        if annee_fiscale is not None:
            if annee_fiscale < current_year:
                raise ValidationError(f"L'année fiscale doit être {current_year} ou ultérieure.")

        return annee_fiscale

    def clean_montant_ariary(self):
        """Validate that amount is positive"""
        montant = self.cleaned_data.get("montant_ariary")

        if montant is not None and montant <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.")

        return montant

    def clean(self):
        """Validate thresholds based on category"""
        cleaned_data = super().clean()
        maritime_category = cleaned_data.get("maritime_category")
        longueur_min = cleaned_data.get("longueur_min_metres")
        puissance_cv = cleaned_data.get("puissance_min_cv_maritime")
        puissance_kw = cleaned_data.get("puissance_min_kw_maritime")

        # Validate thresholds for NAVIRE_PLAISANCE
        if maritime_category == "NAVIRE_PLAISANCE":
            if not any([longueur_min, puissance_cv, puissance_kw]):
                raise ValidationError(
                    "Pour la catégorie Navire de plaisance, au moins un seuil "
                    "(longueur, puissance CV ou puissance kW) doit être défini."
                )

        # Validate thresholds for JETSKI
        elif maritime_category == "JETSKI":
            if not puissance_kw:
                raise ValidationError("Pour la catégorie Jet-ski, la puissance minimale en kW doit être définie.")

        # AUTRES_ENGINS doesn't require thresholds

        return cleaned_data

    def save(self, commit=True):
        """Auto-set grid_type to FLAT_MARITIME"""
        instance = super().save(commit=False)
        instance.grid_type = "FLAT_MARITIME"

        if commit:
            instance.save()

        return instance
