"""
API Version 1 Serializers

This module contains all serializers for API version 1.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import serializers

from administration.models import AgentVerification, VerificationQR
from core.models import (  # Legacy profiles (kept for backward compatibility during migration); EmergencyServiceProfile, GovernmentAdminProfile, LawEnforcementProfile,
    CompanyProfile,
    IndividualProfile,
    InternationalOrganizationProfile,
    PublicInstitutionProfile,
    UserProfile,
)
from notifications.models import Notification
from payments.models import AgentPartenaireProfile, PaiementTaxe, QRCode
from vehicles.models import DocumentVehicule, GrilleTarifaire, VehicleType, Vehicule
from api.models import WebhookSubscription, WebhookDelivery
from api.utils.data_minimization import (
    minimize_user_data,
    minimize_vehicle_data,
    minimize_payment_data,
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def to_representation(self, instance):
        """Minimize data based on context"""
        ret = super().to_representation(instance)
        view = self.context.get("view")
        
        if view and hasattr(view, "action"):
            if view.action == "list":
                return minimize_user_data(ret, context="list")
            elif view.action == "retrieve":
                return minimize_user_data(ret, context="detail")
                
        return ret


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "user_type",
            "telephone",
            "verification_status",
            "langue_preferee",
            "est_entreprise",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleTypeSerializer(serializers.ModelSerializer):
    """Vehicle type serializer"""

    class Meta:
        model = VehicleType
        fields = ["id", "nom", "description", "est_actif", "ordre_affichage", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleSerializer(serializers.ModelSerializer):
    """Vehicle serializer"""

    proprietaire = UserSerializer(read_only=True)
    proprietaire_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="proprietaire", write_only=True, required=False
    )
    type_vehicule = VehicleTypeSerializer(read_only=True)
    type_vehicule_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.filter(est_actif=True), source="type_vehicule", write_only=True
    )
    age_annees = serializers.IntegerField(read_only=True)
    est_exonere = serializers.BooleanField(read_only=True)

    class Meta:
        model = Vehicule
        fields = [
            "plaque_immatriculation",
            "proprietaire",
            "proprietaire_id",
            "puissance_fiscale_cv",
            "cylindree_cm3",
            "source_energie",
            "date_premiere_circulation",
            "categorie_vehicule",
            "type_vehicule",
            "type_vehicule_id",
            "specifications_techniques",
            "est_actif",
            "age_annees",
            "est_exonere",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_plaque_immatriculation(self, value):
        """Validate license plate format"""
        import re

        pattern = r"^[0-9]{1,4}\s[A-Z]{2,3}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Format invalide. Format attendu: 1234 TAA")
        return value.upper()

    def create(self, validated_data):
        """Create vehicle with proper owner assignment"""
        request = self.context.get("request")
        if request and request.user:
            validated_data["proprietaire"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Minimize data based on context"""
        ret = super().to_representation(instance)
        view = self.context.get("view")
        
        if view and hasattr(view, "action"):
            if view.action == "list":
                return minimize_vehicle_data(ret, context="list")
            elif view.action == "retrieve":
                return minimize_vehicle_data(ret, context="detail")
                
        return ret


class VehiculeAerienSerializer(serializers.ModelSerializer):
    """Aerial vehicle serializer"""

    proprietaire = UserSerializer(read_only=True)
    proprietaire_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="proprietaire", write_only=True, required=False
    )
    type_vehicule = VehicleTypeSerializer(read_only=True)
    type_vehicule_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.filter(est_actif=True), source="type_vehicule", write_only=True
    )
    tax_amount = serializers.SerializerMethodField()
    age_annees = serializers.IntegerField(read_only=True)
    est_exonere = serializers.BooleanField(read_only=True)

    class Meta:
        model = Vehicule
        fields = [
            "plaque_immatriculation",
            "proprietaire",
            "proprietaire_id",
            "immatriculation_aerienne",
            "type_vehicule",
            "type_vehicule_id",
            "marque",
            "modele",
            "numero_serie_aeronef",
            "masse_maximale_decollage_kg",
            "puissance_moteur_kw",
            "date_premiere_circulation",
            "categorie_vehicule",
            "vehicle_category",
            "specifications_techniques",
            "est_actif",
            "age_annees",
            "est_exonere",
            "tax_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "vehicle_category"]

    def get_tax_amount(self, obj):
        """Calculate tax amount for aerial vehicle"""
        from django.utils import timezone

        from vehicles.services import TaxCalculationService

        service = TaxCalculationService()
        year = timezone.now().year
        tax_info = service.calculate_aerial_tax(obj, year)

        if tax_info.get("amount"):
            return float(tax_info["amount"])
        return None

    def validate_immatriculation_aerienne(self, value):
        """Validate aerial registration format"""
        if not value:
            raise serializers.ValidationError("L'immatriculation aérienne est requise")
        # Basic format validation (e.g., 5R-XXX for Madagascar)
        import re

        if not re.match(r"^[A-Z0-9]{2,3}-[A-Z0-9]{3,4}$", value.upper()):
            raise serializers.ValidationError("Format d'immatriculation aérienne invalide. Exemple: 5R-ABC")
        return value.upper()

    def validate_masse_maximale_decollage_kg(self, value):
        """Validate maximum takeoff weight"""
        if value and (value < 10 or value > 500000):
            raise serializers.ValidationError("La masse maximale doit être entre 10 kg et 500,000 kg")
        return value

    def create(self, validated_data):
        """Create aerial vehicle with proper category assignment"""
        validated_data["vehicle_category"] = "AERIEN"
        request = self.context.get("request")
        if request and request.user:
            validated_data["proprietaire"] = request.user
        return super().create(validated_data)


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = [
            "id",
            "name",
            "target_url",
            "is_active",
            "event_types",
            "secret",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class WebhookDeliverySerializer(serializers.ModelSerializer):
    subscription = WebhookSubscriptionSerializer(read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "subscription",
            "event_type",
            "payload",
            "signature",
            "status",
            "attempt_count",
            "next_attempt_at",
            "response_code",
            "response_body",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class VehiculeMaritimeSerializer(serializers.ModelSerializer):
    """Maritime vehicle serializer"""

    proprietaire = UserSerializer(read_only=True)
    proprietaire_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="proprietaire", write_only=True, required=False
    )
    type_vehicule = VehicleTypeSerializer(read_only=True)
    type_vehicule_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.filter(est_actif=True), source="type_vehicule", write_only=True
    )
    tax_amount = serializers.SerializerMethodField()
    maritime_classification = serializers.SerializerMethodField()
    age_annees = serializers.IntegerField(read_only=True)
    est_exonere = serializers.BooleanField(read_only=True)

    class Meta:
        model = Vehicule
        fields = [
            "plaque_immatriculation",
            "proprietaire",
            "proprietaire_id",
            "numero_francisation",
            "nom_navire",
            "type_vehicule",
            "type_vehicule_id",
            "marque",
            "modele",
            "longueur_metres",
            "tonnage_tonneaux",
            "puissance_fiscale_cv",
            "puissance_moteur_kw",
            "date_premiere_circulation",
            "categorie_vehicule",
            "vehicle_category",
            "specifications_techniques",
            "est_actif",
            "age_annees",
            "est_exonere",
            "maritime_classification",
            "tax_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "vehicle_category"]

    def get_tax_amount(self, obj):
        """Calculate tax amount for maritime vehicle"""
        from django.utils import timezone

        from vehicles.services import TaxCalculationService

        service = TaxCalculationService()
        year = timezone.now().year
        tax_info = service.calculate_maritime_tax(obj, year)

        if tax_info.get("amount"):
            return float(tax_info["amount"])
        return None

    def get_maritime_classification(self, obj):
        """Get maritime vehicle classification"""
        from vehicles.services import TaxCalculationService

        service = TaxCalculationService()
        return service._classify_maritime_vehicle(obj)

    def validate_numero_francisation(self, value):
        """Validate francisation number format"""
        if not value:
            raise serializers.ValidationError("Le numéro de francisation est requis")
        return value.upper()

    def validate_longueur_metres(self, value):
        """Validate vessel length"""
        if value and (value < 1 or value > 400):
            raise serializers.ValidationError("La longueur doit être entre 1m et 400m")
        return value

    def validate(self, data):
        """Validate maritime vehicle data"""
        # Ensure at least one power measurement is provided
        puissance_cv = data.get("puissance_fiscale_cv")
        puissance_kw = data.get("puissance_moteur_kw")

        if not puissance_cv and not puissance_kw:
            raise serializers.ValidationError(
                {
                    "puissance_fiscale_cv": "Au moins une mesure de puissance (CV ou kW) est requise",
                    "puissance_moteur_kw": "Au moins une mesure de puissance (CV ou kW) est requise",
                }
            )

        # Convert between CV and kW if only one is provided
        if puissance_cv and not puissance_kw:
            from vehicles.services import convert_cv_to_kw

            data["puissance_moteur_kw"] = convert_cv_to_kw(puissance_cv)
        elif puissance_kw and not puissance_cv:
            from vehicles.services import convert_kw_to_cv

            data["puissance_fiscale_cv"] = convert_kw_to_cv(puissance_kw)

        return data

    def create(self, validated_data):
        """Create maritime vehicle with proper category assignment"""
        validated_data["vehicle_category"] = "MARITIME"
        request = self.context.get("request")
        if request and request.user:
            validated_data["proprietaire"] = request.user
        return super().create(validated_data)


class VehicleDocumentSerializer(serializers.ModelSerializer):
    """Vehicle document serializer"""

    vehicule = VehicleSerializer(read_only=True)
    vehicule_plaque = serializers.CharField(source="vehicule.plaque_immatriculation", read_only=True)
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = DocumentVehicule
        fields = [
            "id",
            "vehicule",
            "vehicule_plaque",
            "uploaded_by",
            "document_type",
            "fichier",
            "note",
            "expiration_date",
            "verification_status",
            "verification_comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at", "updated_at"]


class PriceGridSerializer(serializers.ModelSerializer):
    """Price grid (tax rate) serializer"""

    class Meta:
        model = GrilleTarifaire
        fields = [
            "id",
            "puissance_min_cv",
            "puissance_max_cv",
            "source_energie",
            "age_min_annees",
            "age_max_annees",
            "montant_ariary",
            "annee_fiscale",
            "est_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""

    vehicule_plaque = serializers.CharField(source="vehicule_plaque.plaque_immatriculation", read_only=True)
    vehicule_plaque_id = serializers.CharField(source="vehicule_plaque", write_only=True)
    currency_code = serializers.SerializerMethodField()

    class Meta:
        model = PaiementTaxe
        fields = [
            "id",
            "vehicule_plaque",
            "vehicule_plaque_id",
            "annee_fiscale",
            "montant_du_ariary",
            "montant_paye_ariary",
            "date_paiement",
            "statut",
            "transaction_id",
            "methode_paiement",
            "details_paiement",
            "stripe_payment_intent_id",
            "stripe_status",
            "stripe_receipt_url",
            "billing_email",
            "billing_name",
            "currency_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "stripe_payment_intent_id",
            "stripe_status",
            "stripe_receipt_url",
            "created_at",
            "updated_at",
        ]

    def get_currency_code(self, obj):
        try:
            code = (obj.currency_stripe or "MGA").upper()
            return code
        except Exception:
            return "MGA"

    def to_representation(self, instance):
        """Minimize data based on context"""
        ret = super().to_representation(instance)
        view = self.context.get("view")
        
        if view and hasattr(view, "action"):
            if view.action == "list":
                return minimize_payment_data(ret, context="list")
            elif view.action == "retrieve":
                return minimize_payment_data(ret, context="detail")
                
        return ret


class QRCodeSerializer(serializers.ModelSerializer):
    """QR code serializer"""

    vehicule_plaque = serializers.CharField(source="vehicule_plaque.plaque_immatriculation", read_only=True)
    est_valide = serializers.BooleanField(read_only=True)

    class Meta:
        model = QRCode
        fields = [
            "id",
            "vehicule_plaque",
            "annee_fiscale",
            "token",
            "date_generation",
            "date_expiration",
            "est_actif",
            "nombre_scans",
            "derniere_verification",
            "est_valide",
        ]
        read_only_fields = ["id", "token", "date_generation", "nombre_scans", "derniere_verification"]


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "type_notification",
            "titre",
            "contenu",
            "langue",
            "est_lue",
            "date_envoi",
            "date_lecture",
            "metadata",
        ]
        read_only_fields = ["id", "user", "date_envoi"]


class TaxCalculationSerializer(serializers.Serializer):
    """Tax calculation request serializer"""

    plaque_immatriculation = serializers.CharField(required=False)
    puissance_fiscale_cv = serializers.IntegerField(min_value=1)
    cylindree_cm3 = serializers.IntegerField(min_value=1, required=False)
    source_energie = serializers.ChoiceField(choices=Vehicule.SOURCE_ENERGIE_CHOICES)
    date_premiere_circulation = serializers.DateField()
    categorie_vehicule = serializers.ChoiceField(choices=Vehicule.CATEGORIE_CHOICES)
    annee_fiscale = serializers.IntegerField(required=False)

    def validate(self, data):
        """Validate calculation request"""
        # If vehicle exists, validate against it
        plaque = data.get("plaque_immatriculation")
        if plaque:
            try:
                vehicule = Vehicule.objects.get(plaque_immatriculation=plaque)
                # Use vehicle data if not provided
                if "puissance_fiscale_cv" not in data:
                    data["puissance_fiscale_cv"] = vehicule.puissance_fiscale_cv
                if "source_energie" not in data:
                    data["source_energie"] = vehicule.source_energie
                if "date_premiere_circulation" not in data:
                    data["date_premiere_circulation"] = vehicule.date_premiere_circulation
                if "categorie_vehicule" not in data:
                    data["categorie_vehicule"] = vehicule.categorie_vehicule
            except Vehicule.DoesNotExist:
                pass

        return data


class TaxCalculationResponseSerializer(serializers.Serializer):
    """Tax calculation response serializer"""

    montant_du_ariary = serializers.DecimalField(max_digits=12, decimal_places=2)
    annee_fiscale = serializers.IntegerField()
    est_exonere = serializers.BooleanField()
    grille_tarifaire = PriceGridSerializer(required=False)
    details = serializers.DictField()


class LoginSerializer(serializers.Serializer):
    """Login serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Try to authenticate with email
            user = authenticate(username=email, password=password)
            if not user:
                # Try with username if email fails
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                raise serializers.ValidationError("Invalid email or password.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer"""

    refresh = serializers.CharField()


class ConvertCylindreeSerializer(serializers.Serializer):
    """Convert cylindree to CV serializer"""

    cylindree = serializers.IntegerField(min_value=1)

    def validate_cylindree(self, value):
        if value < 1:
            raise serializers.ValidationError("La cylindrée doit être supérieure à 0")
        return value


class AgentPartenaireProfileSerializer(serializers.ModelSerializer):
    """Agent Partenaire profile serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = AgentPartenaireProfile
        fields = [
            "id",
            "user",
            "agent_id",
            "full_name",
            "phone_number",
            "collection_location",
            "commission_rate",
            "use_default_commission",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "agent_id", "created_at", "updated_at"]


class AgentVerificationSerializer(serializers.ModelSerializer):
    """Agent Government verification serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = AgentVerification
        fields = ["id", "user", "numero_badge", "zone_affectation", "est_actif", "date_creation", "date_modification"]
        read_only_fields = ["id", "date_creation", "date_modification"]


class VerificationQRSerializer(serializers.ModelSerializer):
    """QR code verification serializer"""

    agent = AgentVerificationSerializer(read_only=True)
    qr_code = QRCodeSerializer(read_only=True)
    qr_code_token = serializers.CharField(source="qr_code.token", read_only=True)
    vehicle_plate = serializers.CharField(source="qr_code.vehicule_plaque.plaque_immatriculation", read_only=True)
    vehicle_type = serializers.CharField(
        source="qr_code.vehicule_plaque.type_vehicule.nom", read_only=True, allow_null=True
    )
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = VerificationQR
        fields = [
            "id",
            "agent",
            "qr_code",
            "qr_code_token",
            "vehicle_plate",
            "vehicle_type",
            "owner_name",
            "statut_verification",
            "date_verification",
            "localisation_gps",
            "notes",
        ]
        read_only_fields = ["id", "date_verification"]

    def get_owner_name(self, obj):
        if obj.qr_code and obj.qr_code.vehicule_plaque:
            user = obj.qr_code.vehicule_plaque.proprietaire
            return user.get_full_name() or user.username
        return None


class QRCodeVerifySerializer(serializers.Serializer):
    """QR code verification request serializer"""

    token = serializers.CharField(required=True, help_text="QR code token to verify")
    gps_location = serializers.JSONField(required=False, allow_null=True, help_text="GPS location coordinates")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Optional verification notes")


# API Key Management Serializers
from api.models import APIKey, APIKeyPermission, APIKeyEvent


class APIKeyPermissionSerializer(serializers.ModelSerializer):
    """Serializer for API key permissions"""
    
    class Meta:
        model = APIKeyPermission
        fields = ['id', 'resource', 'scope', 'granted_at', 'granted_by']
        read_only_fields = ['id', 'granted_at', 'granted_by']


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys"""
    
    permissions = APIKeyPermissionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_expired_flag = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'key', 'name', 'organization', 'contact_email',
            'is_active', 'created_at', 'created_by_username', 'expires_at',
            'last_used_at', 'rate_limit_per_hour', 'rate_limit_per_day',
            'description', 'ip_whitelist', 'permissions', 'is_expired_flag'
        ]
        read_only_fields = ['id', 'key', 'created_at', 'created_by_username', 'last_used_at']
        extra_kwargs = {
            'key': {'write_only': False}  # Show key only on creation
        }
    
    def get_is_expired_flag(self, obj):
        """Check if API key is expired"""
        return obj.is_expired()
    
    def create(self, validated_data):
        """Create API key with generated key"""
        validated_data['key'] = APIKey.generate_key()
        validated_data['created_by'] = self.context['request'].user
        
        api_key = super().create(validated_data)
        
        # Log creation event
        APIKeyEvent.objects.create(
            api_key=api_key,
            event_type='CREATED',
            performed_by=self.context['request'].user,
            details={
                'organization': api_key.organization,
                'contact_email': api_key.contact_email,
            }
        )
        
        return api_key


class APIKeyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing API keys (without exposing the key)"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_expired_flag = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'organization', 'contact_email',
            'is_active', 'created_at', 'created_by_username', 'expires_at',
            'last_used_at', 'is_expired_flag', 'permission_count'
        ]
        read_only_fields = fields
    
    def get_is_expired_flag(self, obj):
        """Check if API key is expired"""
        return obj.is_expired()
    
    def get_permission_count(self, obj):
        """Get count of permissions"""
        return obj.permissions.count()


class APIKeyRegistrationRequestSerializer(serializers.Serializer):
    """Serializer for API key registration requests"""
    
    name = serializers.CharField(max_length=255, help_text="Descriptive name for the API key")
    organization = serializers.CharField(max_length=255, help_text="Organization name")
    contact_email = serializers.EmailField(help_text="Contact email")
    description = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Detailed description of intended use"
    )
    requested_permissions = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of requested permissions: [{'resource': 'vehicles', 'scope': 'read'}]"
    )
    
    def validate_requested_permissions(self, value):
        """Validate requested permissions format"""
        if not value:
            return []
        
        valid_resources = dict(APIKeyPermission.RESOURCE_CHOICES).keys()
        valid_scopes = dict(APIKeyPermission.SCOPE_CHOICES).keys()
        
        for perm in value:
            if 'resource' not in perm or 'scope' not in perm:
                raise serializers.ValidationError(
                    "Each permission must have 'resource' and 'scope' fields"
                )
            if perm['resource'] not in valid_resources:
                raise serializers.ValidationError(
                    f"Invalid resource: {perm['resource']}. "
                    f"Valid options: {', '.join(valid_resources)}"
                )
            if perm['scope'] not in valid_scopes:
                raise serializers.ValidationError(
                    f"Invalid scope: {perm['scope']}. "
                    f"Valid options: {', '.join(valid_scopes)}"
                )
        
        return value


class APIKeyUsageStatsSerializer(serializers.Serializer):
    """Serializer for API key usage statistics"""
    
    api_key_id = serializers.IntegerField()
    api_key_name = serializers.CharField()
    total_requests = serializers.IntegerField()
    requests_last_24h = serializers.IntegerField()
    requests_last_7d = serializers.IntegerField()
    requests_last_30d = serializers.IntegerField()
    last_used_at = serializers.DateTimeField(allow_null=True)
    avg_response_time_ms = serializers.FloatField(allow_null=True)


class APIKeyEventSerializer(serializers.ModelSerializer):
    """Serializer for API key events"""
    
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = APIKeyEvent
        fields = [
            'id', 'api_key', 'api_key_name', 'event_type',
            'performed_by', 'performed_by_username', 'timestamp', 'details'
        ]
        read_only_fields = fields
