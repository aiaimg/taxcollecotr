from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Vehicule
from .utils import get_conversion_info, get_puissance_fiscale_from_cylindree

class VehiculeForm(forms.ModelForm):
    """Form for creating and editing vehicles"""
    
    class Meta:
        model = Vehicule
        fields = [
            'plaque_immatriculation',
            'puissance_fiscale_cv',
            'cylindree_cm3',
            'source_energie',
            'date_premiere_circulation',
            'categorie_vehicule',
            'type_vehicule',
        ]
        widgets = {
            'plaque_immatriculation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ex: 1234 TAA'),
                'pattern': r'[0-9]{1,4}\s[A-Z]{2,3}',
                'title': _('Format: 1234 TAA')
            }),
            'puissance_fiscale_cv': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': _('Ex: 8')
            }),
            'cylindree_cm3': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': _('Ex: 1600')
            }),
            'source_energie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_premiere_circulation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'categorie_vehicule': forms.Select(attrs={
                'class': 'form-select'
            }),
            'type_vehicule': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'plaque_immatriculation': _('Plaque d\'immatriculation'),
            'puissance_fiscale_cv': _('Puissance fiscale (CV)'),
            'cylindree_cm3': _('Cylindrée (cm³)'),
            'source_energie': _('Source d\'énergie'),
            'date_premiere_circulation': _('Date de première circulation'),
            'categorie_vehicule': _('Catégorie de véhicule'),
            'type_vehicule': _('Type de véhicule'),
        }
        help_texts = {
            'plaque_immatriculation': _('Format requis: 1234 TAA (chiffres + espace + lettres)'),
            'puissance_fiscale_cv': _('Puissance fiscale en chevaux vapeur (CV) - Obligatoire pour le calcul de la taxe'),
            'cylindree_cm3': _('Cylindrée du moteur en cm³ (optionnel) - Si vous la connaissez, nous pouvons vous aider à déterminer les CV'),
            'date_premiere_circulation': _('Date de première mise en circulation du véhicule'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make cylindree_cm3 optional for electric vehicles
        self.fields['cylindree_cm3'].required = False
        
    def clean_plaque_immatriculation(self):
        """Validate license plate format"""
        plaque = self.cleaned_data.get('plaque_immatriculation', '').upper().strip()
        
        if not plaque:
            raise forms.ValidationError(_('La plaque d\'immatriculation est requise'))
        
        # Basic format validation (more detailed validation in model)
        import re
        if not re.match(r'^[0-9]{1,4}\s[A-Z]{2,3}$', plaque):
            raise forms.ValidationError(_('Format invalide. Utilisez le format: 1234 TAA'))
        
        return plaque
    
    def clean(self):
        """Cross-field validation avec suggestion de conversion"""
        cleaned_data = super().clean()
        source_energie = cleaned_data.get('source_energie')
        cylindree_cm3 = cleaned_data.get('cylindree_cm3')
        puissance_fiscale_cv = cleaned_data.get('puissance_fiscale_cv')
        
        # For non-electric vehicles, cylindree is recommended
        if source_energie in ['Essence', 'Diesel', 'Hybride'] and not cylindree_cm3:
            self.add_error('cylindree_cm3', _('La cylindrée est recommandée pour ce type de véhicule'))
        
        # Suggestion intelligente de conversion
        if cylindree_cm3 and not puissance_fiscale_cv:
            conversion_info = get_conversion_info(cylindree_cm3)
            if conversion_info['valid']:
                cv_suggere = conversion_info['cv_suggere']
                plage_description = conversion_info['plage_description']
                message = _(f'Suggestion: Pour {cylindree_cm3}cm³, la puissance fiscale est généralement {plage_description}. Nous suggérons {cv_suggere} CV.')
                # Ajouter un message informatif plutôt qu'une erreur
                if hasattr(self, '_conversion_suggestion'):
                    self._conversion_suggestion = message
                else:
                    self._conversion_suggestion = message
        
        # Validation de cohérence si les deux champs sont remplis
        if cylindree_cm3 and puissance_fiscale_cv:
            conversion_info = get_conversion_info(cylindree_cm3)
            if conversion_info['valid']:
                cv_min = conversion_info['cv_min']
                cv_max = conversion_info['cv_max']
                
                if not (cv_min <= puissance_fiscale_cv <= cv_max):
                    plage_description = conversion_info['plage_description']
                    self.add_error('puissance_fiscale_cv', 
                        _(f'Attention: Pour {cylindree_cm3}cm³, la puissance fiscale est généralement {plage_description}. Vérifiez votre saisie.'))
        
        return cleaned_data
    
    def get_conversion_suggestion(self):
        """Retourne la suggestion de conversion si disponible"""
        return getattr(self, '_conversion_suggestion', None)


class VehiculeSearchForm(forms.Form):
    """Form for searching vehicles"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Rechercher par plaque d\'immatriculation...'),
        }),
        label=_('Recherche')
    )
    
    source_energie = forms.ChoiceField(
        required=False,
        choices=[('', _('Toutes les énergies'))] + Vehicule.SOURCE_ENERGIE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Source d\'énergie')
    )
    
    categorie_vehicule = forms.ChoiceField(
        required=False,
        choices=[('', _('Toutes les catégories'))] + Vehicule.CATEGORIE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Catégorie')
    )
    
    type_vehicule = forms.ChoiceField(
        required=False,
        choices=[('', _('Tous les types'))] + Vehicule.TYPE_VEHICULE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Type de véhicule')
    )