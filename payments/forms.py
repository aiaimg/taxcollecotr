from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PaiementTaxe


class PaiementTaxeForm(forms.ModelForm):
    """Form for creating tax payments"""
    
    numero_telephone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+261 XX XX XXX XX',
            'pattern': r'^\+?261[0-9]{9}$'
        }),
        label='Numéro de téléphone',
        help_text='Requis pour les paiements Mobile Money'
    )
    
    class Meta:
        model = PaiementTaxe
        fields = ['methode_paiement', 'numero_telephone']
        
        widgets = {
            'methode_paiement': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        
        labels = {
            'methode_paiement': 'Méthode de paiement',
        }
        
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        methode_paiement = cleaned_data.get('methode_paiement')
        numero_telephone = cleaned_data.get('numero_telephone')
        
        # Phone number is required for Mobile Money payments
        mobile_money_methods = ['mvola', 'orange_money', 'airtel_money']
        
        if methode_paiement in mobile_money_methods:
            if not numero_telephone:
                raise forms.ValidationError({
                    'numero_telephone': 'Le numéro de téléphone est requis pour les paiements Mobile Money'
                })
            
            # Validate phone number format for specific providers
            if methode_paiement == 'mvola' and not numero_telephone.startswith(('034', '038', '+261 34', '+261 38')):
                raise forms.ValidationError({
                    'numero_telephone': 'Les numéros MVola doivent commencer par 034 ou 038'
                })
            elif methode_paiement == 'orange_money' and not numero_telephone.startswith(('032', '037', '+261 32', '+261 37')):
                raise forms.ValidationError({
                    'numero_telephone': 'Les numéros Orange Money doivent commencer par 032 ou 037'
                })
            elif methode_paiement == 'airtel_money' and not numero_telephone.startswith(('033', '+261 33')):
                raise forms.ValidationError({
                    'numero_telephone': 'Les numéros Airtel Money doivent commencer par 033'
                })
        
        return cleaned_data