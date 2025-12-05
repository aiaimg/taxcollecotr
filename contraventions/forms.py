from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contestation,
    Contravention,
    DossierFourriere,
    TypeInfraction,
)
from contraventions.services.contravention_service import ContraventionService


class ContraventionForm(forms.ModelForm):
    vehicule_plaque = forms.CharField(required=False, max_length=20)
    vehicule_marque = forms.CharField(required=False, max_length=100)
    vehicule_modele = forms.CharField(required=False, max_length=100)

    conducteur_cin = forms.CharField(required=True, max_length=12)
    conducteur_nom = forms.CharField(required=False, max_length=200)
    conducteur_telephone = forms.CharField(required=False, max_length=20)
    conducteur_numero_permis = forms.CharField(required=False, max_length=50)
    conducteur_categorie_permis = forms.CharField(required=False, max_length=20)

    signature_electronique = forms.CharField(required=False, widget=forms.Textarea)
    coordonnees_gps_lat = forms.DecimalField(required=False, max_digits=10, decimal_places=8)
    coordonnees_gps_lon = forms.DecimalField(required=False, max_digits=11, decimal_places=8)

    class Meta:
        model = Contravention
        fields = [
            "type_infraction",
            "date_heure_infraction",
            "lieu_infraction",
            "route_type",
            "route_numero",
            "a_accident_associe",
            "observations",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["type_infraction"].queryset = TypeInfraction.objects.filter(est_actif=True)

        if self.user:
            try:
                agent = AgentControleurProfile.objects.get(user=self.user, est_actif=True)
                self.fields["type_infraction"].queryset = self.fields["type_infraction"].queryset
                if agent.autorite_type:
                    self.fields["type_infraction"].queryset = self.fields["type_infraction"].queryset.filter(
                        est_actif=True
                    )
            except AgentControleurProfile.DoesNotExist:
                pass

        self._est_recidive = False

    def clean_conducteur_cin(self):
        cin = self.cleaned_data.get("conducteur_cin", "").strip()
        if len(cin) != 12 or not cin.isdigit():
            raise ValidationError("Le CIN doit contenir exactement 12 chiffres.")
        return cin

    def clean(self):
        cleaned = super().clean()

        type_infraction = cleaned.get("type_infraction")
        cin = cleaned.get("conducteur_cin")
        if type_infraction and cin:
            conducteur = Conducteur.objects.filter(cin=cin).first()
            if conducteur:
                self._est_recidive = ContraventionService.detecter_recidive(
                    conducteur=conducteur,
                    type_infraction=type_infraction,
                    periode_mois=12,
                )

        date_inf = cleaned.get("date_heure_infraction")
        if date_inf and date_inf > timezone.now():
            self.add_error("date_heure_infraction", "La date de l'infraction ne peut pas être dans le futur.")

        return cleaned

    def save(self, commit=True):
        if not self.user:
            raise ValidationError("Utilisateur requis pour créer une contravention")

        type_infraction = self.cleaned_data["type_infraction"]
        vehicule_plaque = (self.cleaned_data.get("vehicule_plaque") or "").upper().replace(" ", "")
        vehicule_data_manuelle = {
            "marque": self.cleaned_data.get("vehicule_marque", ""),
            "modele": self.cleaned_data.get("vehicule_modele", ""),
        }

        conducteur_data = {
            "cin": self.cleaned_data.get("conducteur_cin"),
            "nom_complet": self.cleaned_data.get("conducteur_nom", ""),
            "telephone": self.cleaned_data.get("conducteur_telephone", ""),
            "numero_permis": self.cleaned_data.get("conducteur_numero_permis", ""),
            "categorie_permis": self.cleaned_data.get("conducteur_categorie_permis", ""),
        }

        lieu_data = {
            "lieu_infraction": self.cleaned_data.get("lieu_infraction", ""),
            "route_type": self.cleaned_data.get("route_type", ""),
            "route_numero": self.cleaned_data.get("route_numero", ""),
        }

        coordonnees_gps = None
        if (
            self.cleaned_data.get("coordonnees_gps_lat") is not None
            or self.cleaned_data.get("coordonnees_gps_lon") is not None
        ):
            coordonnees_gps = {
                "lat": self.cleaned_data.get("coordonnees_gps_lat"),
                "lon": self.cleaned_data.get("coordonnees_gps_lon"),
            }

        contravention = ContraventionService.creer_contravention(
            agent=self.user,
            type_infraction_id=type_infraction.id,
            conducteur_data=conducteur_data,
            lieu_data=lieu_data,
            vehicule_plaque=vehicule_plaque or None,
            vehicule_data_manuelle=vehicule_data_manuelle,
            date_heure_infraction=self.cleaned_data.get("date_heure_infraction"),
            observations=self.cleaned_data.get("observations", ""),
            a_accident_associe=self.cleaned_data.get("a_accident_associe") or False,
            signature_electronique=self.cleaned_data.get("signature_electronique", ""),
            coordonnees_gps=coordonnees_gps,
        )

        return contravention


class ContestationForm(forms.ModelForm):
    documents = forms.FileField(
        required=False, help_text="Télécharger des documents justificatifs (plusieurs fichiers possibles)"
    )

    class Meta:
        model = Contestation
        fields = [
            "contravention",
            "nom_demandeur",
            "email_demandeur",
            "telephone_demandeur",
            "motif",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        motif = cleaned.get("motif", "")
        if motif and len(motif.strip()) < 10:
            self.add_error("motif", "Le motif doit contenir au moins 10 caractères.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.demandeur:
            instance.demandeur = self.user

        instance.save()

        uploaded_docs = []
        files = self.files.getlist("documents") if hasattr(self.files, "getlist") else []
        for f in files:
            path = f"contestations/{instance.numero_contestation}/{f.name}"
            default_storage.save(path, ContentFile(f.read()))
            uploaded_docs.append({"name": f.name, "path": path})

        if uploaded_docs:
            instance.documents_justificatifs = uploaded_docs
            instance.save(update_fields=["documents_justificatifs"])

        return instance


class TypeInfractionForm(forms.ModelForm):
    class Meta:
        model = TypeInfraction
        fields = [
            "nom",
            "article_code",
            "loi_reference",
            "categorie",
            "montant_min_ariary",
            "montant_max_ariary",
            "montant_variable",
            "sanctions_administratives",
            "fourriere_obligatoire",
            "emprisonnement_possible",
            "penalite_accident_ariary",
            "penalite_recidive_pct",
            "est_actif",
        ]

    def clean(self):
        cleaned = super().clean()
        minv = cleaned.get("montant_min_ariary")
        maxv = cleaned.get("montant_max_ariary")
        if minv is not None and maxv is not None and minv > maxv:
            self.add_error("montant_max_ariary", "Le montant maximum doit être supérieur ou égal au minimum.")
        return cleaned


class ConfigurationSystemeForm(forms.ModelForm):
    class Meta:
        model = ConfigurationSysteme
        fields = [
            "delai_paiement_standard_jours",
            "delai_paiement_immediat_jours",
            "penalite_retard_pct",
            "frais_transport_fourriere_ariary",
            "frais_gardiennage_journalier_ariary",
            "duree_minimale_fourriere_jours",
            "duree_minimale_fourriere_perissable_jours",
            "delai_annulation_directe_heures",
            "delai_contestation_jours",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.pk = 1
        if commit:
            instance.save()
        return instance


class DossierFourriereForm(forms.ModelForm):
    class Meta:
        model = DossierFourriere
        fields = [
            "contravention",
            "date_mise_fourriere",
            "lieu_fourriere",
            "adresse_fourriere",
            "type_vehicule",
            "frais_transport_ariary",
            "frais_gardiennage_journalier_ariary",
            "duree_minimale_jours",
            "date_sortie_fourriere",
            "notes",
        ]

    def clean(self):
        cleaned = super().clean()
        date_in = cleaned.get("date_mise_fourriere")
        date_out = cleaned.get("date_sortie_fourriere")
        if date_in and date_out and date_out < date_in:
            self.add_error("date_sortie_fourriere", "La date de sortie doit être postérieure à la mise en fourrière.")
        return cleaned
