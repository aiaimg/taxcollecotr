from django import forms

from payments.models import StripeConfig


class StripeConfigForm(forms.ModelForm):
    """Form to manage Stripe configuration for a specific environment."""

    environment = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = StripeConfig
        fields = [
            "environment",
            "publishable_key",
            "secret_key",
            "webhook_secret",
            "currency",
            "success_url",
            "cancel_url",
        ]
        widgets = {
            "publishable_key": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "pk_live_... or pk_test_..."}
            ),
            "secret_key": forms.TextInput(attrs={"class": "form-control", "placeholder": "sk_live_... or sk_test_..."}),
            "webhook_secret": forms.TextInput(attrs={"class": "form-control", "placeholder": "whsec_..."}),
            "currency": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., MGA"}),
            "success_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com/payments/success/"}
            ),
            "cancel_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com/payments/cancel/"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure environment is read-only so users don't accidentally change it
        self.fields["environment"].disabled = True
