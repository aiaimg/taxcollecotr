from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.fields import ProfilePictureField
from core.models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with user type selection"""

    USER_TYPE_CHOICES = [
        ("individual", "Particulier (Citoyen)"),
        ("company", "Entreprise/Société"),
        ("public_institution", "Administration Publique et Institution"),
        ("international_organization", "Organisation Internationale"),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        initial="individual",
        widget=forms.Select(attrs={"class": "form-control", "required": True}),
        label="Type d'utilisateur",
        help_text="Sélectionnez le type d'utilisateur qui vous correspond le mieux",
    )

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom (optionnel)"}),
        label="Prénom",
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom (optionnel)"}),
        label="Nom",
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        label="Email",
        help_text="Un email de vérification sera envoyé à cette adresse",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "user_type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for existing fields
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Nom d'utilisateur"})
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control password-input", "placeholder": "Mot de passe"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control password-input", "placeholder": "Confirmer le mot de passe"}
        )

    def save(self, commit=True):
        """Save the user and store user_type for signal processing"""
        user = super().save(commit=False)

        # Store user_type as a temporary attribute for the signal
        user._user_type = self.cleaned_data["user_type"]

        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile including profile picture"""

    # Use custom optimized image field
    profile_picture = ProfilePictureField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        label="Photo de profil",
    )

    class Meta:
        model = UserProfile
        fields = ["profile_picture", "telephone", "langue_preferee"]
        widgets = {
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+261xxxxxxxxx"}),
            "langue_preferee": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {"telephone": "Téléphone", "langue_preferee": "Langue préférée"}


class UserEditForm(forms.ModelForm):
    """Form for editing basic user information"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }
        labels = {"first_name": "Prénom", "last_name": "Nom", "email": "Email"}
