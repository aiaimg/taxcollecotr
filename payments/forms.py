from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from core.models import User
from vehicles.models import VehicleType, Vehicule

from .models import AgentPartenaireProfile, CashSession, CashSystemConfig, CashTransaction, PaiementTaxe


class PaiementTaxeForm(forms.ModelForm):
    """Form for creating tax payments"""

    numero_telephone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+261 XX XX XXX XX", "pattern": r"^\+?261[0-9]{9}$"}
        ),
        label="Numéro de téléphone",
        help_text="Requis pour les paiements Mobile Money",
    )

    class Meta:
        model = PaiementTaxe
        fields = ["methode_paiement", "numero_telephone"]

        widgets = {
            "methode_paiement": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

        labels = {
            "methode_paiement": "Méthode de paiement",
        }

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        methode_paiement = cleaned_data.get("methode_paiement")
        numero_telephone = cleaned_data.get("numero_telephone")

        # Phone number is required for Mobile Money payments
        mobile_money_methods = ["mvola", "orange_money", "airtel_money"]

        if methode_paiement in mobile_money_methods:
            if not numero_telephone:
                raise forms.ValidationError(
                    {"numero_telephone": "Le numéro de téléphone est requis pour les paiements Mobile Money"}
                )

            # Validate phone number format for specific providers
            if methode_paiement == "mvola" and not numero_telephone.startswith(("034", "038", "+261 34", "+261 38")):
                raise forms.ValidationError({"numero_telephone": "Les numéros MVola doivent commencer par 034 ou 038"})
            elif methode_paiement == "orange_money" and not numero_telephone.startswith(
                ("032", "037", "+261 32", "+261 37")
            ):
                raise forms.ValidationError(
                    {"numero_telephone": "Les numéros Orange Money doivent commencer par 032 ou 037"}
                )
            elif methode_paiement == "airtel_money" and not numero_telephone.startswith(("033", "+261 33")):
                raise forms.ValidationError({"numero_telephone": "Les numéros Airtel Money doivent commencer par 033"})

        return cleaned_data


# ============================================================================
# CASH PAYMENT SYSTEM FORMS
# ============================================================================


class CashSessionOpenForm(forms.ModelForm):
    """Form for opening a cash collection session"""

    class Meta:
        model = CashSession
        fields = ["opening_balance"]
        widgets = {
            "opening_balance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }
        labels = {
            "opening_balance": _("Solde d'ouverture (Ariary)"),
        }
        help_texts = {
            "opening_balance": _("Montant en espèces avec lequel vous commencez la session"),
        }

    def clean_opening_balance(self):
        """Validate opening balance is non-negative"""
        opening_balance = self.cleaned_data.get("opening_balance")

        if opening_balance is None:
            raise forms.ValidationError(_("Le solde d'ouverture est requis"))

        if opening_balance < 0:
            raise forms.ValidationError(_("Le solde d'ouverture ne peut pas être négatif"))

        return opening_balance


class CashSessionCloseForm(forms.ModelForm):
    """Form for closing a cash collection session"""

    class Meta:
        model = CashSession
        fields = ["closing_balance", "discrepancy_notes"]
        widgets = {
            "closing_balance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "discrepancy_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Expliquez tout écart entre le solde attendu et le solde réel..."),
                }
            ),
        }
        labels = {
            "closing_balance": _("Solde de clôture (Ariary)"),
            "discrepancy_notes": _("Notes sur l'écart"),
        }
        help_texts = {
            "closing_balance": _("Montant total en espèces compté à la fin de la session"),
            "discrepancy_notes": _("Expliquez tout écart si le solde ne correspond pas au montant attendu"),
        }

    def clean_closing_balance(self):
        """Validate closing balance is non-negative"""
        closing_balance = self.cleaned_data.get("closing_balance")

        if closing_balance is None:
            raise forms.ValidationError(_("Le solde de clôture est requis"))

        if closing_balance < 0:
            raise forms.ValidationError(_("Le solde de clôture ne peut pas être négatif"))

        return closing_balance


class CashPaymentForm(forms.Form):
    """Form for processing cash payments (new and existing customers)"""

    # Customer identification
    customer_search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Rechercher par nom, téléphone ou plaque..."),
                "id": "customer-search-input",
            }
        ),
        label=_("Rechercher un client existant"),
    )

    is_new_customer = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "is-new-customer-checkbox",
            }
        ),
        label=_("Nouveau client"),
    )

    # New customer fields
    customer_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Nom complet du client"),
            }
        ),
        label=_("Nom du client"),
    )

    customer_phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("+261 XX XX XXX XX"),
            }
        ),
        label=_("Téléphone"),
    )

    customer_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("email@example.com"),
            }
        ),
        label=_("Email (optionnel)"),
    )

    customer_id_number = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Numéro de CIN"),
            }
        ),
        label=_("Numéro d'identification"),
    )

    # Vehicle fields
    vehicle_plate = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: 1234 TAA"),
            }
        ),
        label=_("Plaque d'immatriculation"),
    )

    has_plate = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=_("Possède une plaque d'immatriculation"),
    )

    vehicle_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.filter(est_actif=True),
        empty_label=_("Sélectionner le type de véhicule"),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=_("Type de véhicule"),
    )

    vehicle_brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: TOYOTA, HONDA"),
            }
        ),
        label=_("Marque"),
    )

    vehicle_model = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: COROLLA, CIVIC"),
            }
        ),
        label=_("Modèle (optionnel)"),
    )

    vehicle_color = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: Blanc, Noir"),
            }
        ),
        label=_("Couleur (optionnel)"),
    )

    engine_power_cv = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: 8"),
                "min": "1",
            }
        ),
        label=_("Puissance fiscale (CV)"),
    )

    engine_capacity_cc = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Ex: 1600"),
                "min": "1",
            }
        ),
        label=_("Cylindrée (cm³)"),
    )

    energy_source = forms.ChoiceField(
        choices=Vehicule.SOURCE_ENERGIE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=_("Source d'énergie"),
    )

    first_circulation_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label=_("Date de première circulation"),
    )

    vehicle_category = forms.ChoiceField(
        choices=Vehicule.CATEGORIE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=_("Catégorie de véhicule"),
    )

    owner_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Nom du propriétaire légal"),
            }
        ),
        label=_("Nom du propriétaire"),
    )

    # Payment fields
    tax_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.HiddenInput(
            attrs={
                "id": "tax-amount-hidden",
            }
        ),
        label=_("Montant de la taxe"),
    )

    amount_tendered = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0.01",
                "id": "amount-tendered-input",
            }
        ),
        label=_("Montant remis (Ariary)"),
    )

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        is_new_customer = cleaned_data.get("is_new_customer", False)
        customer_search = cleaned_data.get("customer_search")
        customer_name = cleaned_data.get("customer_name")
        customer_phone = cleaned_data.get("customer_phone")
        tax_amount = cleaned_data.get("tax_amount")
        amount_tendered = cleaned_data.get("amount_tendered")

        # Validate customer data based on is_new_customer
        if is_new_customer:
            # New customer requires name and phone
            if not customer_name:
                self.add_error("customer_name", _("Le nom du client est requis pour un nouveau client"))
            if not customer_phone:
                self.add_error("customer_phone", _("Le téléphone est requis pour un nouveau client"))
        else:
            # Existing customer requires search
            if not customer_search:
                self.add_error(
                    "customer_search", _('Veuillez rechercher un client existant ou cocher "Nouveau client"')
                )

        # Validate payment amount
        if tax_amount and amount_tendered:
            if amount_tendered < tax_amount:
                self.add_error(
                    "amount_tendered",
                    _("Le montant remis ({}) est insuffisant. Montant requis: {} Ar").format(
                        amount_tendered, tax_amount
                    ),
                )

        return cleaned_data

    def clean_vehicle_plate(self):
        """Normalize and validate vehicle plate"""
        plate = self.cleaned_data.get("vehicle_plate", "").strip().upper()

        if not plate:
            raise forms.ValidationError(_("La plaque d'immatriculation est requise"))

        # Remove spaces for normalization
        plate = plate.replace(" ", "")

        return plate


class TransactionApprovalForm(forms.Form):
    """Form for approving or rejecting transactions requiring dual verification"""

    ACTION_CHOICES = [
        ("approve", _("Approuver")),
        ("reject", _("Rejeter")),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=_("Action"),
    )

    approval_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _("Notes d'approbation (optionnel)..."),
            }
        ),
        label=_("Notes"),
    )

    def clean(self):
        """Validate that rejection includes notes"""
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        approval_notes = cleaned_data.get("approval_notes")

        if action == "reject" and not approval_notes:
            self.add_error("approval_notes", _("Veuillez fournir une raison pour le rejet de cette transaction"))

        return cleaned_data


class ReconciliationForm(forms.Form):
    """Form for daily cash reconciliation"""

    reconciliation_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label=_("Date de réconciliation"),
    )

    physical_cash_count = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }
        ),
        label=_("Comptage physique des espèces (Ariary)"),
    )

    reconciliation_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": _("Notes de réconciliation, explications des écarts..."),
            }
        ),
        label=_("Notes de réconciliation"),
    )

    def clean_physical_cash_count(self):
        """Validate physical cash count is non-negative"""
        physical_cash_count = self.cleaned_data.get("physical_cash_count")

        if physical_cash_count is None:
            raise forms.ValidationError(_("Le comptage physique est requis"))

        if physical_cash_count < 0:
            raise forms.ValidationError(_("Le comptage physique ne peut pas être négatif"))

        return physical_cash_count

    def clean_reconciliation_date(self):
        """Validate reconciliation date is not in the future"""
        from django.utils import timezone

        reconciliation_date = self.cleaned_data.get("reconciliation_date")

        if reconciliation_date and reconciliation_date > timezone.now().date():
            raise forms.ValidationError(_("La date de réconciliation ne peut pas être dans le futur"))

        return reconciliation_date


class AgentPartenaireForm(forms.ModelForm):
    """Form for creating and editing Agent Partenaire profiles"""

    # User selection for new agents
    username = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Nom d'utilisateur"),
            }
        ),
        label=_("Nom d'utilisateur"),
        help_text=_("Créer un nouveau compte utilisateur pour cet agent"),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("email@example.com"),
            }
        ),
        label=_("Email de l'utilisateur"),
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Mot de passe"),
            }
        ),
        label=_("Mot de passe"),
    )

    class Meta:
        model = AgentPartenaireProfile
        fields = [
            "agent_id",
            "full_name",
            "phone_number",
            "collection_location",
            "use_default_commission",
            "commission_rate",
            "is_active",
        ]
        widgets = {
            "agent_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex: AGT001"),
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Nom complet de l'agent"),
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("+261 XX XX XXX XX"),
                }
            ),
            "collection_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex: Antananarivo Centre"),
                }
            ),
            "use_default_commission": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "id": "use-default-commission",
                }
            ),
            "commission_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                    "id": "commission-rate-input",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "agent_id": _("ID Agent"),
            "full_name": _("Nom complet"),
            "phone_number": _("Numéro de téléphone"),
            "collection_location": _("Lieu de collecte"),
            "use_default_commission": _("Utiliser le taux de commission par défaut"),
            "commission_rate": _("Taux de commission personnalisé (%)"),
            "is_active": _("Actif"),
        }
        help_texts = {
            "agent_id": _("Identifiant unique pour cet agent"),
            "commission_rate": _("Laissez vide pour utiliser le taux par défaut du système"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing existing agent, hide user creation fields
        if self.instance and self.instance.pk:
            self.fields["username"].widget = forms.HiddenInput()
            self.fields["email"].widget = forms.HiddenInput()
            self.fields["password"].widget = forms.HiddenInput()

    def clean_agent_id(self):
        """Validate agent_id is unique"""
        agent_id = self.cleaned_data.get("agent_id")

        if not agent_id:
            raise forms.ValidationError(_("L'ID agent est requis"))

        # Check uniqueness (excluding current instance if editing)
        queryset = AgentPartenaireProfile.objects.filter(agent_id=agent_id)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(_("Cet ID agent existe déjà"))

        return agent_id

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        use_default_commission = cleaned_data.get("use_default_commission")
        commission_rate = cleaned_data.get("commission_rate")

        # If not using default, commission_rate is required
        if not use_default_commission and not commission_rate:
            self.add_error(
                "commission_rate", _("Le taux de commission est requis si vous n'utilisez pas le taux par défaut")
            )

        # For new agents, validate user creation fields
        if not self.instance.pk:
            username = cleaned_data.get("username")
            email = cleaned_data.get("email")
            password = cleaned_data.get("password")

            if not username:
                self.add_error("username", _("Le nom d'utilisateur est requis pour un nouvel agent"))
            else:
                # Check if username already exists
                if User.objects.filter(username=username).exists():
                    self.add_error("username", _("Ce nom d'utilisateur existe déjà"))

            if not email:
                self.add_error("email", _("L'email est requis pour un nouvel agent"))

            if not password:
                self.add_error("password", _("Le mot de passe est requis pour un nouvel agent"))
            elif len(password) < 8:
                self.add_error("password", _("Le mot de passe doit contenir au moins 8 caractères"))

        return cleaned_data

    def save(self, commit=True):
        """Save agent profile and create user if needed"""
        agent = super().save(commit=False)

        # Create user for new agents
        if not self.instance.pk:
            username = self.cleaned_data.get("username")
            email = self.cleaned_data.get("email")
            password = self.cleaned_data.get("password")

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=agent.full_name.split()[0] if agent.full_name else "",
                last_name=" ".join(agent.full_name.split()[1:]) if agent.full_name else "",
            )

            # Set user as staff (so they can access admin interface)
            user.is_staff = True
            user.save()

            agent.user = user

        if commit:
            agent.save()

        return agent


class CashSystemConfigForm(forms.ModelForm):
    """Form for editing cash system configuration"""

    class Meta:
        model = CashSystemConfig
        fields = [
            "default_commission_rate",
            "dual_verification_threshold",
            "reconciliation_tolerance",
            "session_timeout_hours",
            "void_time_limit_minutes",
            "receipt_footer_text",
        ]
        widgets = {
            "default_commission_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "dual_verification_threshold": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "reconciliation_tolerance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "session_timeout_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "void_time_limit_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "receipt_footer_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Texte personnalisé pour le pied de page des reçus..."),
                }
            ),
        }
        labels = {
            "default_commission_rate": _("Taux de commission par défaut (%)"),
            "dual_verification_threshold": _("Seuil de double vérification (Ariary)"),
            "reconciliation_tolerance": _("Tolérance de réconciliation (Ariary)"),
            "session_timeout_hours": _("Délai d'expiration de session (heures)"),
            "void_time_limit_minutes": _("Délai d'annulation (minutes)"),
            "receipt_footer_text": _("Texte de pied de page du reçu"),
        }
        help_texts = {
            "default_commission_rate": _("Taux de commission par défaut pour tous les agents"),
            "dual_verification_threshold": _("Montant au-dessus duquel une approbation admin est requise"),
            "reconciliation_tolerance": _("Écart acceptable lors de la réconciliation"),
            "session_timeout_hours": _("Nombre d'heures avant qu'une session ouverte expire"),
            "void_time_limit_minutes": _("Temps maximum pour annuler une transaction"),
            "receipt_footer_text": _("Texte personnalisé affiché en bas des reçus"),
        }

    def clean_default_commission_rate(self):
        """Validate commission rate is reasonable"""
        rate = self.cleaned_data.get("default_commission_rate")

        if rate is not None and rate > 100:
            raise forms.ValidationError(_("Le taux de commission ne peut pas dépasser 100%"))

        return rate

    def clean_dual_verification_threshold(self):
        """Validate threshold is positive"""
        threshold = self.cleaned_data.get("dual_verification_threshold")

        if threshold is not None and threshold < 0:
            raise forms.ValidationError(_("Le seuil ne peut pas être négatif"))

        return threshold

    def clean_reconciliation_tolerance(self):
        """Validate tolerance is positive"""
        tolerance = self.cleaned_data.get("reconciliation_tolerance")

        if tolerance is not None and tolerance < 0:
            raise forms.ValidationError(_("La tolérance ne peut pas être négative"))

        return tolerance
