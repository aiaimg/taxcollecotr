from rest_framework import serializers

from vehicles.models import Vehicule

from .models import (
    AgentControleurProfile,
    Conducteur,
    Contestation,
    Contravention,
    ContraventionAuditLog,
    DossierFourriere,
    PhotoContravention,
    TypeInfraction,
)


class TypeInfractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeInfraction
        fields = [
            "id",
            "article_code",
            "nom",
            "categorie",
            "loi_reference",
            "montant_min_ariary",
            "montant_max_ariary",
            "montant_variable",
            "fourriere_obligatoire",
            "sanctions_administratives",
            "emprisonnement_possible",
            "penalite_accident_ariary",
            "penalite_recidive_pct",
            "est_actif",
        ]


class AgentControleurProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AgentControleurProfile
        fields = [
            "id",
            "user",
            "matricule",
            "nom_complet",
            "unite_affectation",
            "grade",
            "autorite_type",
            "juridiction",
            "telephone",
            "est_actif",
            "created_at",
        ]


class ConducteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conducteur
        fields = [
            "id",
            "cin",
            "nom_complet",
            "date_naissance",
            "adresse",
            "telephone",
            "numero_permis",
            "categorie_permis",
            "date_delivrance_permis",
            "created_at",
            "updated_at",
        ]


class VehiculeSummarySerializer(serializers.ModelSerializer):
    proprietaire_nom = serializers.CharField(source="proprietaire.nom_complet", read_only=True)

    class Meta:
        model = Vehicule
        fields = ["id", "plaque_immatriculation", "marque", "modele", "numero_chassis", "proprietaire_nom"]


class PhotoContraventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoContravention
        fields = ["id", "fichier", "description", "ordre", "created_at"]


class DossierFourriereSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierFourriere
        fields = [
            "id",
            "numero_dossier",
            "contravention",
            "date_mise_fourriere",
            "lieu_fourriere",
            "adresse_fourriere",
            "type_vehicule",
            "frais_transport_ariary",
            "frais_gardiennage_journalier_ariary",
            "duree_minimale_jours",
            "date_sortie_fourriere",
            "frais_totaux_ariary",
            "statut",
            "bon_sortie_numero",
            "notes",
            "created_at",
        ]


class ContestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestation
        fields = [
            "id",
            "contravention",
            "numero_contestation",
            "demandeur",
            "nom_demandeur",
            "email_demandeur",
            "telephone_demandeur",
            "motif",
            "date_soumission",
            "statut",
            "examine_par",
            "date_examen",
            "decision_motif",
            "documents_justificatifs",
            "created_at",
        ]


class ContraventionListSerializer(serializers.ModelSerializer):
    type_infraction = TypeInfractionSerializer(read_only=True)
    vehicule = VehiculeSummarySerializer(read_only=True)
    conducteur = ConducteurSerializer(read_only=True)
    agent_nom = serializers.CharField(source="agent_controleur.nom_complet", read_only=True)
    a_photos = serializers.SerializerMethodField()
    a_fourriere = serializers.SerializerMethodField()
    montant_total = serializers.SerializerMethodField()

    class Meta:
        model = Contravention
        fields = [
            "id",
            "numero_pv",
            "date_heure_infraction",
            "lieu_infraction",
            "type_infraction",
            "vehicule",
            "conducteur",
            "montant_total",
            "statut",
            "agent_nom",
            "created_at",
            "a_photos",
            "a_fourriere",
        ]

    def get_a_photos(self, obj):
        return obj.photos.exists()

    def get_a_fourriere(self, obj):
        return hasattr(obj, "dossier_fourriere")

    def get_montant_total(self, obj):
        return obj.get_montant_total()


class ContraventionDetailSerializer(serializers.ModelSerializer):
    type_infraction = TypeInfractionSerializer(read_only=True)
    vehicule = VehiculeSummarySerializer(read_only=True)
    conducteur = ConducteurSerializer(read_only=True)
    agent_nom = serializers.CharField(source="agent_controleur.nom_complet", read_only=True)
    photos = PhotoContraventionSerializer(many=True, read_only=True)
    fourriere = DossierFourriereSerializer(source="dossier_fourriere", read_only=True)
    contestations = ContestationSerializer(many=True, read_only=True)
    montant_total = serializers.SerializerMethodField()

    class Meta:
        model = Contravention
        fields = [
            "id",
            "numero_pv",
            "date_heure_infraction",
            "lieu_infraction",
            "type_infraction",
            "vehicule",
            "conducteur",
            "observations",
            "montant_total",
            "statut",
            "agent_nom",
            "created_at",
            "updated_at",
            "photos",
            "fourriere",
            "contestations",
        ]

    def get_montant_total(self, obj):
        return obj.get_montant_total()


class ContraventionCreateSerializer(serializers.ModelSerializer):
    vehicule_id = serializers.IntegerField(required=False, allow_null=True)
    conducteur_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Contravention
        fields = [
            "type_infraction",
            "vehicule_id",
            "conducteur_id",
            "lieu_infraction",
            "date_heure_infraction",
            "observations",
        ]

    def validate(self, data):
        if not data.get("vehicule_id") and not data.get("conducteur_id"):
            raise serializers.ValidationError("Vous devez spécifier un véhicule ou un conducteur")
        if data.get("vehicule_id"):
            try:
                data["vehicule"] = Vehicule.objects.get(id=data["vehicule_id"])
            except Vehicule.DoesNotExist:
                raise serializers.ValidationError("Le véhicule spécifié n'existe pas")
        if data.get("conducteur_id"):
            try:
                data["conducteur"] = Conducteur.objects.get(id=data["conducteur_id"])
            except Conducteur.DoesNotExist:
                raise serializers.ValidationError("Le conducteur spécifié n'existe pas")
        return data

    def create(self, validated_data):
        vehicule_id = validated_data.pop("vehicule_id", None)
        conducteur_id = validated_data.pop("conducteur_id", None)
        if vehicule_id:
            validated_data["vehicule"] = Vehicule.objects.get(id=vehicule_id)
        if conducteur_id:
            validated_data["conducteur"] = Conducteur.objects.get(id=conducteur_id)
        validated_data["agent_controleur"] = self.context["request"].user.agent_controleur_profile
        return super().create(validated_data)


class ContraventionPaymentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=[("mvola", "MVola"), ("stripe", "Stripe"), ("cash", "Espèces")])
    mvola_number = serializers.CharField(required=False, allow_blank=True)
    cash_location = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        payment_method = data.get("payment_method")

        if payment_method == "mvola":
            if not data.get("mvola_number"):
                raise serializers.ValidationError("Le numéro MVola est requis pour le paiement par MVola")

            # Validate MVola number format (should start with 034 or 038 and be 10 digits)
            mvola_number = data["mvola_number"].replace(" ", "")
            if not (mvola_number.startswith("034") or mvola_number.startswith("038")) or len(mvola_number) != 10:
                raise serializers.ValidationError(
                    "Le numéro MVola doit commencer par 034 ou 038 et contenir 10 chiffres"
                )

        elif payment_method == "cash":
            if not data.get("cash_location"):
                raise serializers.ValidationError("Le lieu de paiement est requis pour le paiement en espèces")

        return data


class QRVerificationSerializer(serializers.Serializer):
    qr_code_data = serializers.CharField()

    def validate_qr_code_data(self, value):
        from payments.models import QRCode

        try:
            parts = value.split("|")
            numero_pv = parts[0].strip()
            contravention = Contravention.objects.filter(numero_pv=numero_pv).first()
            if not contravention:
                raise serializers.ValidationError("Contravention non trouvée")

            # Validate against stored QRCode when available
            qr = contravention.qr_code or QRCode.objects.filter(code=numero_pv, type_code="CONTRAVENTION").first()
            if not qr:
                raise serializers.ValidationError("QR code non enregistré pour cette contravention")

            self.context["contravention"] = contravention
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Erreur lors de la vérification du code QR: {str(e)}")
        return value


class ContraventionAuditLogSerializer(serializers.ModelSerializer):
    user_nom = serializers.CharField(source="user.get_full_name", read_only=True)
    action_type_display = serializers.CharField(source="get_action_type_display", read_only=True)

    class Meta:
        model = ContraventionAuditLog
        fields = [
            "id",
            "contravention",
            "user",
            "user_nom",
            "action_type",
            "action_type_display",
            "action_data",
            "ip_address",
            "user_agent",
            "previous_hash",
            "current_hash",
            "timestamp",
        ]


class AgentStatsSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    agent_nom = serializers.CharField()
    total_contraventions = serializers.IntegerField()
    contraventions_actives = serializers.IntegerField()
    contraventions_payees = serializers.IntegerField()
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    montant_percu = serializers.DecimalField(max_digits=10, decimal_places=2)
    taux_paiement = serializers.FloatField()


class GlobalStatsSerializer(serializers.Serializer):
    total_contraventions = serializers.IntegerField()
    contraventions_actives = serializers.IntegerField()
    contraventions_payees = serializers.IntegerField()
    contraventions_contestees = serializers.IntegerField()
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    montant_percu = serializers.DecimalField(max_digits=10, decimal_places=2)
    taux_paiement_global = serializers.FloatField()
    contraventions_ce_mois = serializers.IntegerField()
    montant_ce_mois = serializers.DecimalField(max_digits=10, decimal_places=2)
