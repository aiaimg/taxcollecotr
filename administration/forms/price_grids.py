"""
Price Grid Forms for Admin Console
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from vehicles.models import GrilleTarifaire


class PriceGridForm(forms.ModelForm):
    """Form for creating and editing price grids"""
    
    class Meta:
        model = GrilleTarifaire
        fields = [
            'puissance_min_cv', 'puissance_max_cv', 'source_energie',
            'age_min_annees', 'age_max_annees', 'montant_ariary',
            'annee_fiscale', 'est_active'
        ]
        widgets = {
            'puissance_min_cv': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '1',
                'required': True
            }),
            'puissance_max_cv': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '1'
            }),
            'source_energie': forms.Select(attrs={
                'class': 'mdl-textfield__input',
                'required': True
            }),
            'age_min_annees': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '0',
                'value': '0',
                'required': True
            }),
            'age_max_annees': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '0'
            }),
            'montant_ariary': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '0',
                'step': '0.01',
                'required': True
            }),
            'annee_fiscale': forms.NumberInput(attrs={
                'class': 'mdl-textfield__input',
                'min': '2020',
                'required': True
            }),
            'est_active': forms.CheckboxInput(attrs={
                'class': 'mdl-checkbox__input'
            }),
        }
        labels = {
            'puissance_min_cv': 'Minimum Power (CV)',
            'puissance_max_cv': 'Maximum Power (CV)',
            'source_energie': 'Energy Source',
            'age_min_annees': 'Minimum Age (Years)',
            'age_max_annees': 'Maximum Age (Years)',
            'montant_ariary': 'Amount (Ariary)',
            'annee_fiscale': 'Fiscal Year',
            'est_active': 'Active',
        }
        help_texts = {
            'puissance_min_cv': 'Minimum power in CV (horsepower)',
            'puissance_max_cv': 'Maximum power in CV (leave empty for unlimited)',
            'age_min_annees': 'Minimum vehicle age in years',
            'age_max_annees': 'Maximum vehicle age in years (leave empty for unlimited)',
            'montant_ariary': 'Tax amount in Ariary',
            'annee_fiscale': 'Fiscal year for this rate',
        }
    
    def clean_puissance_max_cv(self):
        """Validate that max power is greater than min power"""
        puissance_min = self.cleaned_data.get('puissance_min_cv')
        puissance_max = self.cleaned_data.get('puissance_max_cv')
        
        if puissance_max is not None and puissance_min is not None:
            if puissance_max < puissance_min:
                raise ValidationError(
                    'Maximum power must be greater than or equal to minimum power.'
                )
        
        return puissance_max
    
    def clean_age_max_annees(self):
        """Validate that max age is greater than min age"""
        age_min = self.cleaned_data.get('age_min_annees')
        age_max = self.cleaned_data.get('age_max_annees')
        
        if age_max is not None and age_min is not None:
            if age_max < age_min:
                raise ValidationError(
                    'Maximum age must be greater than or equal to minimum age.'
                )
        
        return age_max
    
    def clean_annee_fiscale(self):
        """Validate that fiscal year is current or future"""
        annee_fiscale = self.cleaned_data.get('annee_fiscale')
        current_year = timezone.now().year
        
        if annee_fiscale is not None:
            if annee_fiscale < current_year:
                raise ValidationError(
                    f'Fiscal year must be {current_year} or later. '
                    f'Historical rates cannot be created or modified.'
                )
        
        return annee_fiscale
    
    def clean_montant_ariary(self):
        """Validate that amount is positive"""
        montant = self.cleaned_data.get('montant_ariary')
        
        if montant is not None and montant <= 0:
            raise ValidationError('Amount must be greater than zero.')
        
        return montant
    
    def clean(self):
        """Additional validation for overlapping price ranges"""
        cleaned_data = super().clean()
        
        puissance_min = cleaned_data.get('puissance_min_cv')
        puissance_max = cleaned_data.get('puissance_max_cv')
        source_energie = cleaned_data.get('source_energie')
        age_min = cleaned_data.get('age_min_annees')
        age_max = cleaned_data.get('age_max_annees')
        annee_fiscale = cleaned_data.get('annee_fiscale')
        
        # Check for overlapping ranges
        if all([puissance_min, source_energie, age_min is not None, annee_fiscale]):
            # Build query to find overlapping grids
            overlapping = GrilleTarifaire.objects.filter(
                source_energie=source_energie,
                annee_fiscale=annee_fiscale
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            # Check power range overlap
            if puissance_max:
                overlapping = overlapping.filter(
                    puissance_min_cv__lte=puissance_max,
                    puissance_max_cv__gte=puissance_min
                ) | overlapping.filter(
                    puissance_min_cv__lte=puissance_max,
                    puissance_max_cv__isnull=True
                )
            else:
                overlapping = overlapping.filter(
                    puissance_min_cv__gte=puissance_min
                )
            
            # Check age range overlap
            if age_max:
                overlapping = overlapping.filter(
                    age_min_annees__lte=age_max,
                    age_max_annees__gte=age_min
                ) | overlapping.filter(
                    age_min_annees__lte=age_max,
                    age_max_annees__isnull=True
                )
            else:
                overlapping = overlapping.filter(
                    age_min_annees__gte=age_min
                )
            
            if overlapping.exists():
                raise ValidationError(
                    'This price grid overlaps with an existing grid for the same '
                    'energy source and fiscal year. Please adjust the power or age ranges.'
                )
        
        return cleaned_data
