from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with user type selection"""
    
    USER_TYPE_CHOICES = [
        ('individual', 'Particulier (Citoyen)'),
        ('company', 'Entreprise/Société'),
        ('emergency', 'Service d\'urgence'),
        ('government', 'Administration publique'),
        ('law_enforcement', 'Forces de l\'ordre'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        initial='individual',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label="Type d'utilisateur",
        help_text="Sélectionnez le type d'utilisateur qui vous correspond le mieux"
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom (optionnel)'
        }),
        label="Prénom"
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom (optionnel)'
        }),
        label="Nom"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (optionnel)'
        }),
        label="Email"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for existing fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control password-input',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control password-input',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def save(self, commit=True):
        """Save the user and store user_type for signal processing"""
        user = super().save(commit=False)
        
        # Store user_type as a temporary attribute for the signal
        user._user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
        
        return user