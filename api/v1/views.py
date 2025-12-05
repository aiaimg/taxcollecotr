"""
API Version 1 Views

Comprehensive RESTful API endpoints for Tax Collector application.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from rest_framework import generics, status, viewsets
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from administration.models import AgentVerification, VerificationQR
from administration.permissions import IsAgentGovernment, IsAgentPartenaire
from contraventions.models import Conducteur, Contravention, PhotoContravention
from contraventions.serializers import ContraventionDetailSerializer, ContraventionListSerializer
from core.models import UserProfile
from core.utils import is_agent_government, is_agent_partenaire
from notifications.models import Notification
from payments.models import AgentPartenaireProfile, PaiementTaxe, QRCode
from vehicles.models import DocumentVehicule, GrilleTarifaire, VehicleType, Vehicule
from api.models import WebhookSubscription, WebhookDelivery
from vehicles.services import TaxCalculationService
from vehicles.utils import get_conversion_info

from .exceptions import NotFoundError, APIValidationError
from .pagination import StandardResultsSetPagination
from .permissions import IsAdminOrReadOnly, IsOwner, IsOwnerOrReadOnly, IsVerifiedUser
from .serializers import (
    AgentPartenaireProfileSerializer,
    AgentVerificationSerializer,
    ConvertCylindreeSerializer,
    LoginSerializer,
    NotificationSerializer,
    PaymentSerializer,
    PriceGridSerializer,
    QRCodeSerializer,
    QRCodeVerifySerializer,
    RefreshTokenSerializer,
    TaxCalculationResponseSerializer,
    TaxCalculationSerializer,
    UserProfileSerializer,
    UserSerializer,
    VehicleDocumentSerializer,
    VehicleSerializer,
    VehicleTypeSerializer,
    VehiculeAerienSerializer,
    VehiculeMaritimeSerializer,
    VerificationQRSerializer,
    WebhookSubscriptionSerializer,
    WebhookDeliverySerializer,
)
from .throttling import (
    AnonBurstThrottle,
    AnonSustainedThrottle,
    AuthThrottle,
    PaymentThrottle,
    UserBurstThrottle,
    UserSustainedThrottle,
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring and load balancers
    """

    permission_classes = [AllowAny]
    throttle_classes = []

    @extend_schema(
        summary="Health check",
        responses={
            200: OpenApiResponse(description="Healthy"),
            503: OpenApiResponse(description="Unhealthy"),
        },
        tags=["Health"],
    )
    def get(self, request):
        """
        Returns API health status
        """
        from django.core.cache import cache
        from django.db import connection

        health_data = {"status": "healthy", "timestamp": timezone.now().isoformat(), "version": "1.0.0", "checks": {}}

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data["checks"]["database"] = "ok"
        except Exception as e:
            health_data["checks"]["database"] = f"error: {str(e)}"
            health_data["status"] = "unhealthy"

        # Cache check
        try:
            cache.set("health_check", "ok", 10)
            cache.get("health_check")
            health_data["checks"]["cache"] = "ok"
        except Exception as e:
            health_data["checks"]["cache"] = f"error: {str(e)}"
            health_data["status"] = "unhealthy"

        status_code = status.HTTP_200_OK if health_data["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response({"success": health_data["status"] == "healthy", "data": health_data}, status=status_code)


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def post(self, request):
        from contraventions.models import ContraventionAuditLog

        try:
            payload = request.data
            contravention_id = None
            if isinstance(payload, dict):
                contravention_id = payload.get("resourceId") or payload.get("contravention")
            contravention = None
            if contravention_id:
                try:
                    contravention = Contravention.objects.get(id=contravention_id)
                except Contravention.DoesNotExist:
                    contravention = None

            log = ContraventionAuditLog.objects.create(
                action_type="UPDATE",
                user=request.user,
                contravention=contravention,
                action_data=payload if isinstance(payload, dict) else {},
            )
            return Response({"success": True, "data": {"id": str(log.id)}}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Audit log error: {str(e)}")
            return Response(
                {"success": False, "error": {"code": "internal_error", "message": "Failed to store audit log"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication endpoints
    """

    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    @extend_schema(
        summary="Login",
        responses={
            200: OpenApiResponse(description="Login success"),
            400: OpenApiResponse(description="Invalid credentials"),
            429: OpenApiResponse(description="Too many requests"),
        },
        tags=["Authentication"],
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """
        Login endpoint - returns JWT tokens
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "success": True,
                    "data": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": UserSerializer(user).data,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "error": {"code": "validation_error", "message": _("Invalid credentials"), "details": serializer.errors},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Refresh token",
        responses={
            200: OpenApiResponse(description="Refresh success"),
            400: OpenApiResponse(description="Invalid refresh token"),
        },
        tags=["Authentication"],
    )
    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh_token(self, request):
        """
        Refresh JWT token endpoint
        """
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh = RefreshToken(serializer.validated_data["refresh"])

            return Response(
                {
                    "success": True,
                    "data": {
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "error": {"code": "validation_error", "message": _("Invalid refresh token"), "details": serializer.errors},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout endpoint - blacklists refresh token
        """
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                try:
                    # Try to blacklist if token_blacklist is installed
                    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

                    token.blacklist()
                except ImportError:
                    # If token_blacklist is not installed, just invalidate the token
                    pass

            return Response({"success": True, "message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"success": False, "error": {"code": "logout_error", "message": "Error during logout"}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User endpoints - read-only for security
    """

    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Users can only see their own profile or admin can see all
        """
        if self.request.user.is_staff or self.request.user.is_superuser:
            return User.objects.filter(is_active=True)
        return User.objects.filter(id=self.request.user.id)

    @extend_schema(
        summary="Current user",
        responses={200: OpenApiResponse(description="User profile")},
        tags=["Users"],
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user profile
        """
        serializer = self.get_serializer(request.user)
        return Response({"success": True, "data": serializer.data})


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    User profile endpoints
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Users can only see their own profile or admin can see all
        """
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user profile
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response({"success": True, "data": serializer.data})


class VehicleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vehicle type endpoints - read-only
    """

    queryset = VehicleType.objects.filter(est_actif=True)
    serializer_class = VehicleTypeSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [AnonBurstThrottle, AnonSustainedThrottle]


class VehicleViewSet(viewsets.ModelViewSet):
    """
    Vehicle endpoints
    """

    queryset = Vehicule.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]
    lookup_field = "plaque_immatriculation"

    def get_queryset(self):
        """
        Filter vehicles by owner or show all for admin
        """
        queryset = Vehicule.objects.select_related("proprietaire", "type_vehicule")

        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.filter(proprietaire=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on vehicle category
        """
        # Check request data for vehicle_category
        if self.request.method in ["POST", "PUT", "PATCH"]:
            vehicle_category = self.request.data.get("vehicle_category")
            if vehicle_category == "AERIEN":
                return VehiculeAerienSerializer
            elif vehicle_category == "MARITIME":
                return VehiculeMaritimeSerializer

        # For GET requests on detail view, check the object's category
        if self.action == "retrieve" and hasattr(self, "get_object"):
            try:
                obj = self.get_object()
                if obj.vehicle_category == "AERIEN":
                    return VehiculeAerienSerializer
                elif obj.vehicle_category == "MARITIME":
                    return VehiculeMaritimeSerializer
            except:
                pass

        # Default to terrestrial vehicle serializer
        return VehicleSerializer

    def perform_create(self, serializer):
        """
        Automatically assign vehicle to current user
        """
        serializer.save(proprietaire=self.request.user)

    @extend_schema(
        summary="Get tax info",
        responses={
            200: OpenApiResponse(description="Tax info"),
            400: OpenApiResponse(description="Invalid year"),
            404: OpenApiResponse(description="Vehicle not found"),
            500: OpenApiResponse(description="Server error"),
        },
        tags=["Tax Calculations"],
    )
    @action(detail=True, methods=["get"])
    def tax_info(self, request, plaque_immatriculation=None):
        """
        Get tax information for a vehicle
        """
        try:
            vehicule = self.get_object()
            year = request.query_params.get("year", timezone.now().year)

            try:
                year = int(year)
            except ValueError:
                raise APIValidationError("Invalid year format")

            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicule, year)

            return Response(
                {"success": True, "data": {"vehicule": VehicleSerializer(vehicule).data, "tax_info": tax_info}}
            )
        except Vehicule.DoesNotExist:
            raise NotFoundError("Vehicle not found")

    @extend_schema(
        summary="Calculate tax",
        responses={
            200: OpenApiResponse(description="Calculation success"),
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Vehicle not found"),
            500: OpenApiResponse(description="Server error"),
        },
        tags=["Tax Calculations"],
    )
    @action(detail=True, methods=["get"], url_path="calculate-tax")
    def calculate_tax(self, request, plaque_immatriculation=None):
        """
        Calculate tax for a specific vehicle
        Accepts optional 'year' parameter (defaults to current year)
        """
        try:
            vehicule = self.get_object()
            year = request.query_params.get("year")

            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response(
                        {"success": False, "error": {"code": "validation_error", "message": "Invalid year format"}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                year = timezone.now().year

            # Calculate tax using the service
            service = TaxCalculationService()
            tax_info = service.calculate_tax(vehicule, year)

            # Prepare response data
            response_data = {
                "vehicle_category": vehicule.vehicle_category,
                "year": year,
                "amount": float(tax_info["amount"]) if tax_info.get("amount") else None,
                "is_exempt": tax_info.get("is_exempt", False),
                "exemption_reason": tax_info.get("exemption_reason"),
                "calculation_method": tax_info.get("calculation_method"),
            }

            # Add grid information if available
            if tax_info.get("grid"):
                response_data["grid"] = {
                    "id": tax_info["grid"].id,
                    "grid_type": tax_info["grid"].grid_type,
                    "amount": float(tax_info["grid"].montant_ariary),
                }

            # Add maritime-specific information
            if vehicule.vehicle_category == "MARITIME" and tax_info.get("maritime_category"):
                response_data["maritime_category"] = tax_info["maritime_category"]

            # Add error if present
            if tax_info.get("error"):
                response_data["error"] = tax_info["error"]

            return Response({"success": True, "data": response_data})

        except Vehicule.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Vehicle not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": {"code": "internal_error", "message": "An error occurred while calculating tax"},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Vehicle payments",
        responses={200: OpenApiResponse(description="Payments list")},
        tags=["Payments"],
    )
    @action(detail=True, methods=["get"])
    def payments(self, request, plaque_immatriculation=None):
        """
        Get all payments for a vehicle
        """
        vehicule = self.get_object()
        payments = PaiementTaxe.objects.filter(vehicule_plaque=vehicule)

        serializer = PaymentSerializer(payments, many=True)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        summary="Vehicle documents",
        responses={200: OpenApiResponse(description="Documents list")},
        tags=["Vehicles"],
    )
    @action(detail=True, methods=["get"])
    def documents(self, request, plaque_immatriculation=None):
        """
        Get all documents for a vehicle
        """
        vehicule = self.get_object()
        documents = DocumentVehicule.objects.filter(vehicule=vehicule)

        serializer = VehicleDocumentSerializer(documents, many=True)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        summary="Vehicles by category",
        responses={
            200: OpenApiResponse(description="Vehicles list"),
            400: OpenApiResponse(description="Invalid category"),
        },
        tags=["Vehicles"],
    )
    @action(detail=False, methods=["get"], url_path="by-category")
    def by_category(self, request):
        """
        Filter vehicles by category (TERRESTRE/AERIEN/MARITIME)
        """
        category = request.query_params.get("category", "TERRESTRE")

        # Validate category
        valid_categories = ["TERRESTRE", "AERIEN", "MARITIME"]
        if category.upper() not in valid_categories:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "validation_error",
                        "message": f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get base queryset (respects user permissions)
        queryset = self.get_queryset()

        # Filter by category
        queryset = queryset.filter(vehicle_category=category.upper())

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Use appropriate serializer based on category
            if category.upper() == "AERIEN":
                serializer = VehiculeAerienSerializer(page, many=True, context={"request": request})
            elif category.upper() == "MARITIME":
                serializer = VehiculeMaritimeSerializer(page, many=True, context={"request": request})
            else:
                serializer = VehicleSerializer(page, many=True, context={"request": request})

            return self.get_paginated_response({"success": True, "data": serializer.data})

        # No pagination
        if category.upper() == "AERIEN":
            serializer = VehiculeAerienSerializer(queryset, many=True, context={"request": request})
        elif category.upper() == "MARITIME":
            serializer = VehiculeMaritimeSerializer(queryset, many=True, context={"request": request})
        else:
            serializer = VehicleSerializer(queryset, many=True, context={"request": request})

        return Response({"success": True, "data": serializer.data, "count": queryset.count()})


class VehicleDocumentViewSet(viewsets.ModelViewSet):
    """
    Vehicle document endpoints
    """

    queryset = DocumentVehicule.objects.all()
    serializer_class = VehicleDocumentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Filter documents by vehicle owner
        """
        queryset = DocumentVehicule.objects.select_related("vehicule", "uploaded_by")

        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.filter(vehicule__proprietaire=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign document to current user
        """
        serializer.save(uploaded_by=self.request.user)


class PriceGridViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Price grid (tax rate) endpoints - read-only
    """

    queryset = GrilleTarifaire.objects.filter(est_active=True)
    serializer_class = PriceGridSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [AnonBurstThrottle, AnonSustainedThrottle]

    def get_queryset(self):
        """
        Filter by year if provided
        """
        queryset = super().get_queryset()
        year = self.request.query_params.get("year")
        if year:
            try:
                queryset = queryset.filter(annee_fiscale=int(year))
            except ValueError:
                pass
        return queryset


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Payment endpoints
    """

    queryset = PaiementTaxe.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [PaymentThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Filter payments by vehicle owner
        """
        queryset = PaiementTaxe.objects.select_related("vehicule_plaque")

        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.filter(vehicule_plaque__proprietaire=self.request.user)

    @extend_schema(
        summary="Verify payment",
        responses={
            200: OpenApiResponse(description="Payment verified"),
            403: OpenApiResponse(description="Only administrators can verify payments"),
        },
        tags=["Payments"],
    )
    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """
        Verify a payment (admin only)
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {
                    "success": False,
                    "error": {"code": "permission_denied", "message": "Only administrators can verify payments"},
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        payment = self.get_object()
        payment.statut = "PAYE"
        payment.save()

        return Response({"success": True, "data": PaymentSerializer(payment).data})


class QRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    QR code endpoints - read-only for security
    """

    queryset = QRCode.objects.filter(est_actif=True)
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Filter QR codes by vehicle owner
        """
        queryset = QRCode.objects.select_related("vehicule_plaque")

        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.filter(vehicule_plaque__proprietaire=self.request.user)

    @extend_schema(
        summary="Verify QR code",
        responses={
            200: OpenApiResponse(description="QR verified"),
            400: OpenApiResponse(description="Invalid token or expired"),
            404: OpenApiResponse(description="QR code not found"),
            500: OpenApiResponse(description="Server error"),
        },
        tags=["Payments"],
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def verify(self, request):
        """
        Verify QR code token (public endpoint for scanning)
        Returns comprehensive vehicle and payment information
        """
        token = request.data.get("token")
        if not token:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": _("Token is required")}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Look up QR code with related data
            qr_code = (
                QRCode.objects.select_related("vehicule_plaque", "vehicule_plaque__type_vehicule")
                .prefetch_related("vehicule_plaque__documents")
                .get(token=token, est_actif=True)
            )

            # Check if QR code is expired
            if qr_code.date_expiration and qr_code.date_expiration < timezone.now():
                return Response(
                    {"success": False, "error": {"code": "invalid_qr", "message": _("QR code is invalid or expired")}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the payment associated with this QR code
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=qr_code.vehicule_plaque, annee_fiscale=qr_code.annee_fiscale
            ).first()

            # Check if vehicle has paid the tax
            tax_paid = False
            if payment:
                tax_paid = payment.statut in ["PAYE", "EXONERE"]

            # Increment scan count
            qr_code.increment_scan_count()

            # Get vehicle documents (assurance and carte grise)
            # Get the most recent document of each type
            assurance_doc = (
                qr_code.vehicule_plaque.documents.filter(document_type="assurance").order_by("-created_at").first()
            )

            carte_grise_doc = (
                qr_code.vehicule_plaque.documents.filter(document_type="carte_grise").order_by("-created_at").first()
            )

            # Prepare document URLs
            assurance_url = None
            carte_grise_url = None

            try:
                if assurance_doc and assurance_doc.fichier:
                    assurance_url = request.build_absolute_uri(assurance_doc.fichier.url)
            except (ValueError, AttributeError):
                # File might not exist or URL building failed
                assurance_url = None

            try:
                if carte_grise_doc and carte_grise_doc.fichier:
                    carte_grise_url = request.build_absolute_uri(carte_grise_doc.fichier.url)
            except (ValueError, AttributeError):
                # File might not exist or URL building failed
                carte_grise_url = None

            # Prepare QR code data
            qr_data = {
                "est_expire": qr_code.date_expiration < timezone.now() if qr_code.date_expiration else False,
                "date_generation": qr_code.date_generation.isoformat() if qr_code.date_generation else None,
                "date_expiration": qr_code.date_expiration.isoformat() if qr_code.date_expiration else None,
                "expiration_date": qr_code.date_expiration.strftime("%d/%m/%Y") if qr_code.date_expiration else None,
            }

            # Prepare vehicle data with all required information
            vehicule_data = {
                "plaque_immatriculation": qr_code.vehicule_plaque.plaque_immatriculation,
                "vin": qr_code.vehicule_plaque.vin or "",
                "nom_proprietaire": qr_code.vehicule_plaque.nom_proprietaire or "",
                "type_vehicule_display": (
                    str(qr_code.vehicule_plaque.type_vehicule) if qr_code.vehicule_plaque.type_vehicule else ""
                ),
                "puissance_fiscale": qr_code.vehicule_plaque.puissance_fiscale_cv,
            }

            # Prepare payment data
            if payment:
                paiement_data = {
                    "tax_paid": tax_paid,
                    "statut": payment.statut,
                    "statut_display": payment.get_statut_display(),
                    "montant_paye": str(payment.montant_paye_ariary) if payment.montant_paye_ariary else "0.00",
                    "date_paiement": payment.date_paiement.isoformat() if payment.date_paiement else None,
                    "methode_paiement_display": (
                        payment.get_methode_paiement_display() if payment.methode_paiement else None
                    ),
                    "reference_transaction": payment.transaction_id or None,
                }
            else:
                # No payment record found
                paiement_data = {
                    "tax_paid": False,
                    "statut": "IMPAYE",
                    "statut_display": "Impayé",
                }

            # Prepare documents data
            documents = {
                "assurance": {
                    "present": assurance_doc is not None,
                    "url": assurance_url,
                    "expiration_date": (
                        assurance_doc.expiration_date.strftime("%d/%m/%Y")
                        if assurance_doc and assurance_doc.expiration_date
                        else None
                    ),
                    "verification_status": assurance_doc.verification_status if assurance_doc else None,
                    "verification_status_display": (
                        assurance_doc.get_verification_status_display() if assurance_doc else None
                    ),
                },
                "carte_grise": {
                    "present": carte_grise_doc is not None,
                    "url": carte_grise_url,
                    "verification_status": carte_grise_doc.verification_status if carte_grise_doc else None,
                    "verification_status_display": (
                        carte_grise_doc.get_verification_status_display() if carte_grise_doc else None
                    ),
                },
            }

            # Return comprehensive data
            return Response(
                {
                    "success": True,
                    "message": "QR code valide",
                    "tax_paid": tax_paid,  # Main answer: has vehicle paid the tax?
                    "expiration_date": (
                        qr_code.date_expiration.strftime("%d/%m/%Y") if qr_code.date_expiration else None
                    ),  # When will it expire?
                    "qr_data": qr_data,
                    "vehicule": vehicule_data,  # Vehicle plaque, VIN, owner name
                    "paiement": paiement_data,  # Payment information
                    "documents": documents,  # Assurance and carte grise documents with image URLs
                    "scanned_at": timezone.now().isoformat(),
                }
            )

        except QRCode.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "QR code not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error verifying QR code: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": {"code": "server_error", "message": "An error occurred while verifying the QR code"},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification endpoints
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        """
        Filter notifications by user
        """
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        Mark notification as read
        """
        notification = self.get_object()
        notification.marquer_comme_lue()

        return Response({"success": True, "data": NotificationSerializer(notification).data})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        """
        count = Notification.objects.filter(user=request.user, est_lue=False).update(est_lue=True)

        return Response({"success": True, "message": f"{count} notifications marked as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Get count of unread notifications
        """
        count = Notification.objects.filter(user=request.user, est_lue=False).count()

        return Response({"success": True, "data": {"count": count}})


class TaxCalculationViewSet(viewsets.ViewSet):
    """
    Tax calculation endpoints
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    @extend_schema(
        summary="Calculate tax",
        responses={
            200: OpenApiResponse(description="Tax calculated"),
            400: OpenApiResponse(description="Invalid input"),
            403: OpenApiResponse(description="Permission denied"),
        },
        tags=["Tax Calculations"],
    )
    @action(detail=False, methods=["post"])
    def calculate(self, request):
        """
        Calculate tax for vehicle data
        """
        serializer = TaxCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "validation_error",
                        "message": "Invalid input data",
                        "details": serializer.errors,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        year = data.get("annee_fiscale", timezone.now().year)

        # Try to get vehicle if plaque provided
        vehicule = None
        if data.get("plaque_immatriculation"):
            try:
                vehicule = Vehicule.objects.get(plaque_immatriculation=data["plaque_immatriculation"])
                # Check ownership
                if vehicule.proprietaire != request.user and not (request.user.is_staff or request.user.is_superuser):
                    return Response(
                        {
                            "success": False,
                            "error": {
                                "code": "permission_denied",
                                "message": "You do not have permission to access this vehicle",
                            },
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Vehicule.DoesNotExist:
                pass

        # Create temporary vehicle object for calculation
        if not vehicule:
            from datetime import datetime

            vehicule = Vehicule(
                plaque_immatriculation=data.get("plaque_immatriculation", "TEMP"),
                puissance_fiscale_cv=data["puissance_fiscale_cv"],
                cylindree_cm3=data.get("cylindree_cm3", 1000),
                source_energie=data["source_energie"],
                date_premiere_circulation=data["date_premiere_circulation"],
                categorie_vehicule=data["categorie_vehicule"],
                type_vehicule=VehicleType.objects.first(),  # Temporary
            )

        # Calculate tax
        service = TaxCalculationService()
        tax_info = service.calculate_tax(vehicule, year)

        response_data = {
            "montant_du_ariary": float(tax_info["amount"]) if tax_info.get("amount") else None,
            "annee_fiscale": year,
            "est_exonere": tax_info.get("is_exempt", False),
            "grille_tarifaire": PriceGridSerializer(tax_info["grid"]).data if tax_info.get("grid") else None,
            "details": {
                "exemption_reason": tax_info.get("exemption_reason"),
                "error": tax_info.get("error"),
            },
        }

        return Response({"success": True, "data": response_data})


class DashboardViewSet(viewsets.ViewSet):
    """
    Dashboard/analytics endpoints
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get dashboard statistics
        """
        user = request.user
        is_admin = user.is_staff or user.is_superuser

        # Vehicle stats
        if is_admin:
            total_vehicles = Vehicule.objects.count()
            user_vehicles = Vehicule.objects.filter(proprietaire=user).count()
        else:
            total_vehicles = Vehicule.objects.filter(proprietaire=user).count()
            user_vehicles = total_vehicles

        # Payment stats
        if is_admin:
            payments = PaiementTaxe.objects.all()
        else:
            payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user)

        total_payments = payments.filter(statut="PAYE").count()
        pending_payments = payments.filter(statut="EN_ATTENTE").count()
        total_amount = payments.filter(statut="PAYE").aggregate(total=Sum("montant_paye_ariary"))["total"] or Decimal(
            "0.00"
        )

        # Notification stats
        unread_notifications = Notification.objects.filter(user=user, est_lue=False).count()

        return Response(
            {
                "success": True,
                "data": {
                    "vehicles": {"total": total_vehicles, "user_total": user_vehicles},
                    "payments": {
                        "total": total_payments,
                        "pending": pending_payments,
                        "total_amount": float(total_amount),
                    },
                    "notifications": {"unread": unread_notifications},
                },
            }
        )


class ConvertCylindreeView(APIView):
    """
    Convert cylindree to CV endpoint
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstThrottle, AnonSustainedThrottle]

    @extend_schema(
        summary="Convert cylindree to CV",
        responses={
            200: OpenApiResponse(description="Conversion success"),
            400: OpenApiResponse(description="Invalid input"),
        },
        tags=["Vehicles"],
    )
    def post(self, request):
        """
        Convert cylindree to CV
        """
        serializer = ConvertCylindreeSerializer(data=request.data)
        if serializer.is_valid():
            cylindree = serializer.validated_data["cylindree"]
            conversion_info = get_conversion_info(cylindree)

            if conversion_info.get("valid"):
                return Response({"success": True, "data": conversion_info})
            else:
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "conversion_error",
                            "message": conversion_info.get("message", "Invalid cylindree"),
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "success": False,
                "error": {"code": "validation_error", "message": "Invalid input", "details": serializer.errors},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Convert cylindree to CV (GET)",
        responses={
            200: OpenApiResponse(description="Conversion success"),
            400: OpenApiResponse(description="Invalid input"),
        },
        tags=["Vehicles"],
    )
    def get(self, request):
        """
        GET version of convert cylindree
        """
        cylindree_str = request.query_params.get("cylindree")
        if not cylindree_str:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": "cylindree parameter is required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cylindree = int(cylindree_str)
        except ValueError:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": "cylindree must be an integer"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversion_info = get_conversion_info(cylindree)

        if conversion_info.get("valid"):
            return Response({"success": True, "data": conversion_info})
        else:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "conversion_error",
                        "message": conversion_info.get("message", "Invalid cylindree"),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class AgentPartenaireViewSet(viewsets.ViewSet):
    """
    API endpoints for Agent Partenaire operations
    """

    permission_classes = [IsAuthenticated, IsAgentPartenaire]
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    @action(detail=False, methods=["get"])
    def profile(self, request):
        """
        Get current agent partenaire profile
        """
        agent = request.user.agent_partenaire_profile
        serializer = AgentPartenaireProfileSerializer(agent)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def my_sessions(self, request):
        """
        Get current agent's cash sessions
        """
        try:
            from payments.cash_views import CashSessionService
            from payments.models import CashSession

            agent = request.user.agent_partenaire_profile
            sessions = CashSession.objects.filter(agent=agent).order_by("-opening_time")

            # Serialize sessions
            sessions_data = []
            for session in sessions:
                sessions_data.append(
                    {
                        "id": str(session.id),
                        "session_number": session.session_number,
                        "opening_time": session.opening_time.isoformat() if session.opening_time else None,
                        "closing_time": session.closing_time.isoformat() if session.closing_time else None,
                        "opening_balance": float(session.opening_balance) if session.opening_balance else 0,
                        "closing_balance": float(session.closing_balance) if session.closing_balance else None,
                        "status": session.status,
                        "transaction_count": session.transactions.count() if hasattr(session, "transactions") else 0,
                        "total_collected": float(session.total_collected) if hasattr(session, "total_collected") else 0,
                        "total_commission": (
                            float(session.total_commission) if hasattr(session, "total_commission") else 0
                        ),
                    }
                )

            return Response({"success": True, "data": sessions_data})
        except ImportError:
            return Response(
                {
                    "success": False,
                    "error": {"code": "feature_not_available", "message": "Cash session feature is not available"},
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class WebhookSubscriptionViewSet(viewsets.ModelViewSet):
    """
    Webhook subscription management (CRUD)
    """

    queryset = WebhookSubscription.objects.all().order_by("-created_at")
    serializer_class = WebhookSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return WebhookSubscription.objects.all().order_by("-created_at")
        return WebhookSubscription.objects.filter(is_active=True).order_by("-created_at")

    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            return Response(
                {"success": False, "error": {"code": "forbidden", "message": "Admin required"}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"success": False, "error": {"code": "forbidden", "message": "Admin required"}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"success": False, "error": {"code": "forbidden", "message": "Admin required"}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Webhook delivery logs
    """

    queryset = WebhookDelivery.objects.all().order_by("-created_at")
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get agent statistics
        """
        agent = request.user.agent_partenaire_profile
        today = timezone.now().date()

        # Get today's payments
        today_payments = PaiementTaxe.objects.filter(collected_by=agent, date_paiement__date=today)

        # Get statistics
        today_stats = {
            "transaction_count": today_payments.count(),
            "total_collected": float(today_payments.aggregate(total=Sum("montant_paye_ariary"))["total"] or 0),
            "commission_earned": 0,  # Calculate based on commission rate
        }

        # Calculate commission
        commission_rate = agent.get_commission_rate()
        if today_stats["total_collected"] > 0:
            today_stats["commission_earned"] = float(today_stats["total_collected"] * Decimal(commission_rate) / 100)

        return Response(
            {
                "success": True,
                "data": {
                    "today": today_stats,
                    "agent": {
                        "agent_id": agent.agent_id,
                        "commission_rate": float(commission_rate),
                    },
                },
            }
        )


class AgentGovernmentViewSet(viewsets.ViewSet):
    """
    API endpoints for Agent Gouvernement operations
    """

    permission_classes = [IsAuthenticated, IsAgentGovernment]
    throttle_classes = [UserBurstThrottle, UserSustainedThrottle]

    @action(detail=False, methods=["get"])
    def profile(self, request):
        """
        Get current agent government profile
        """
        agent = request.user.agent_verification
        serializer = AgentVerificationSerializer(agent)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["post"])
    def verify_qr_code(self, request):
        """
        Verify QR code (agent government only)
        """
        serializer = QRCodeVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": {"code": "validation_error", "message": "Invalid input", "details": serializer.errors},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        gps_location = serializer.validated_data.get("gps_location")
        notes = serializer.validated_data.get("notes", "")

        try:
            qr_code = QRCode.objects.select_related(
                "vehicule_plaque", "vehicule_plaque__proprietaire", "vehicule_plaque__type_vehicule"
            ).get(token=token)

            agent = request.user.agent_verification

            # Determine status
            now = timezone.now()
            if not qr_code.est_actif:
                statut = "invalide"
            elif qr_code.date_expiration < now.date():
                statut = "expire"
            else:
                statut = "valide"

            # Create verification log
            verification = VerificationQR.objects.create(
                agent=agent,
                qr_code=qr_code,
                statut_verification=statut,
                localisation_gps=gps_location,
                notes=notes or "Vérification via API",
            )

            # Update QR code
            qr_code.nombre_scans += 1
            qr_code.derniere_verification = now
            qr_code.save(update_fields=["nombre_scans", "derniere_verification"])

            # Get payment
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=qr_code.vehicule_plaque, annee_fiscale=qr_code.annee_fiscale
            ).first()

            # Serialize response
            verification_data = VerificationQRSerializer(verification).data

            response_data = {
                "success": True,
                "data": {
                    "verification": verification_data,
                    "qr_code": {
                        "token": qr_code.token,
                        "vehicle_plate": qr_code.vehicule_plaque.plaque_immatriculation,
                        "vehicle_type": (
                            qr_code.vehicule_plaque.type_vehicule.nom if qr_code.vehicule_plaque.type_vehicule else None
                        ),
                        "owner": qr_code.vehicule_plaque.proprietaire.get_full_name()
                        or qr_code.vehicule_plaque.proprietaire.username,
                        "expiration_date": qr_code.date_expiration.isoformat(),
                        "is_valid": qr_code.est_actif and qr_code.date_expiration >= now.date(),
                        "scan_count": qr_code.nombre_scans,
                    },
                },
            }

            if payment:
                response_data["data"]["payment"] = {
                    "amount": float(payment.montant_paye_ariary) if payment.montant_paye_ariary else None,
                    "status": payment.statut,
                    "date": payment.date_paiement.isoformat() if payment.date_paiement else None,
                }

            return Response(response_data)

        except QRCode.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "qr_code_not_found", "message": "QR code not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error verifying QR code: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": {"code": "internal_error", "message": "An error occurred while verifying the QR code"},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def my_verifications(self, request):
        """
        Get current agent's verifications
        """
        agent = request.user.agent_verification

        # Get pagination parameters
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        # Get verifications
        verifications = (
            VerificationQR.objects.filter(agent=agent)
            .select_related(
                "qr_code",
                "qr_code__vehicule_plaque",
                "qr_code__vehicule_plaque__type_vehicule",
                "qr_code__vehicule_plaque__proprietaire",
            )
            .order_by("-date_verification")
        )

        # Paginate
        total = verifications.count()
        start = (page - 1) * page_size
        end = start + page_size
        verifications_page = verifications[start:end]

        # Serialize
        serializer = VerificationQRSerializer(verifications_page, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "pages": (total + page_size - 1) // page_size,
                },
            }
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get agent statistics
        """
        agent = request.user.agent_verification
        today = timezone.now().date()

        # Get today's verifications
        today_verifications = VerificationQR.objects.filter(agent=agent, date_verification__date=today)

        # Get this week's verifications
        week_start = today - timedelta(days=today.weekday())
        week_verifications = VerificationQR.objects.filter(agent=agent, date_verification__date__gte=week_start)

        # Get status counts
        status_counts = today_verifications.values("statut_verification").annotate(count=Count("id"))

        stats = {
            "today": {
                "total": today_verifications.count(),
                "valid": today_verifications.filter(statut_verification="valide").count(),
                "invalid": today_verifications.filter(statut_verification="invalide").count(),
                "expired": today_verifications.filter(statut_verification="expire").count(),
                "status_breakdown": list(status_counts),
            },
            "week": {
                "total": week_verifications.count(),
                "valid": week_verifications.filter(statut_verification="valide").count(),
            },
            "agent": {
                "badge_number": agent.numero_badge,
                "zone": agent.zone_affectation,
                "is_active": agent.est_actif,
            },
        }

        return Response({"success": True, "data": stats})

    @action(detail=False, methods=["get"], url_path="contraventions")
    def list_contraventions(self, request):
        qs = (
            Contravention.objects.select_related("type_infraction", "vehicule", "conducteur", "agent_controleur")
            .prefetch_related("photos")
            .order_by("-created_at")
        )

        status_filter = request.query_params.get("status")
        search = request.query_params.get("search")
        date_from = request.query_params.get("fromDate") or request.query_params.get("date_from")
        date_to = request.query_params.get("toDate") or request.query_params.get("date_to")
        department = request.query_params.get("department")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 20))

        if status_filter:
            qs = qs.filter(statut=status_filter.upper())
        if date_from:
            qs = qs.filter(date_heure_infraction__gte=date_from)
        if date_to:
            qs = qs.filter(date_heure_infraction__lte=date_to)
        if department:
            qs = qs.filter(agent_controleur__service__icontains=department)
        if search:
            qs = qs.filter(
                Q(numero_pv__icontains=search)
                | Q(vehicule__numero_plaque__icontains=search)
                | Q(conducteur__nom_complet__icontains=search)
            )

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        serializer = ContraventionListSerializer(qs[start:end], many=True)
        return Response(
            {
                "success": True,
                "data": {
                    "results": serializer.data,
                    "count": total,
                },
            }
        )

    @action(detail=False, methods=["get"], url_path="contraventions/(?P<id>[^/.]+)")
    def contravention_detail(self, request, id=None):
        try:
            contravention = (
                Contravention.objects.select_related("type_infraction", "vehicule", "conducteur", "agent_controleur")
                .prefetch_related("photos", "dossierfourriere", "contestations")
                .get(id=id)
            )
        except Contravention.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Contravention not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ContraventionDetailSerializer(contravention)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["post"], url_path="contraventions/create")
    def create_contravention(self, request):
        try:
            payload = request.data or {}
            offender_id = payload.get("offenderId")
            offense_details = payload.get("offenseDetails") or ""
            timestamp = payload.get("timestamp")
            location = payload.get("location") or {}

            contravention = Contravention()
            contravention.numero_pv = contravention.generate_numero_pv()
            contravention.observations = offense_details
            if timestamp:
                try:
                    contravention.date_heure_infraction = timezone.datetime.fromisoformat(timestamp)
                except Exception:
                    contravention.date_heure_infraction = timezone.now()
            contravention.lieu_infraction = location.get("address") or ""
            lat = location.get("latitude")
            lon = location.get("longitude")
            contravention.coordonnees_gps_lat = lat if lat is not None else None
            contravention.coordonnees_gps_lon = lon if lon is not None else None

            # Link offender by vehicle plate or driver if possible
            if offender_id:
                try:
                    veh = Vehicule.objects.filter(numero_plaque=offender_id).first()
                    if veh:
                        contravention.vehicule = veh
                    else:
                        cond = Conducteur.objects.filter(Q(numero_permis=offender_id) | Q(id=offender_id)).first()
                        if cond:
                            contravention.conducteur = cond
                        else:
                            contravention.vehicule_plaque_manuelle = offender_id
                except Exception:
                    contravention.vehicule_plaque_manuelle = offender_id

            # Assign agent controller if available
            agent_ctrl = getattr(request.user, "agent_controleur_profile", None)
            if agent_ctrl:
                contravention.agent_controleur = agent_ctrl

            # Default fine amount to 0 until fully processed
            from decimal import Decimal

            contravention.montant_amende_ariary = Decimal("0.00")
            contravention.date_limite_paiement = contravention.calculer_date_limite()
            contravention.save()

            serializer = ContraventionDetailSerializer(contravention)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating contravention: {str(e)}")
            return Response(
                {"success": False, "error": {"code": "internal_error", "message": "Error creating contravention"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["put", "patch"], url_path="contraventions/(?P<id>[^/.]+)/update")
    def update_contravention(self, request, id=None):
        try:
            contravention = Contravention.objects.get(id=id)
        except Contravention.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Contravention not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        allowed_fields = {"observations", "statut", "lieu_infraction"}
        for key, value in request.data.items():
            if key in allowed_fields:
                setattr(contravention, key, value)
        contravention.save()
        serializer = ContraventionDetailSerializer(contravention)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["post"], url_path="contraventions/(?P<id>[^/.]+)/void")
    def void_contravention(self, request, id=None):
        try:
            contravention = Contravention.objects.get(id=id)
        except Contravention.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Contravention not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        contravention.statut = "ANNULEE"
        contravention.save(update_fields=["statut"])

        try:
            from contraventions.models import ContraventionAuditLog

            ContraventionAuditLog.objects.create(
                action_type="CANCEL",
                user=request.user,
                contravention=contravention,
                action_data={"reason": request.data.get("reason")},
            )
        except Exception as e:
            logger.warning(f"Audit log create failed: {str(e)}")

        return Response({"success": True})

    @action(detail=False, methods=["post"], url_path="contraventions/(?P<id>[^/.]+)/evidence")
    def upload_evidence(self, request, id=None):
        try:
            contravention = Contravention.objects.get(id=id)
        except Contravention.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Contravention not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": "No file provided"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        photo = PhotoContravention.objects.create(
            contravention=contravention,
            fichier=file,
            uploaded_by=request.user,
        )
        return Response({"success": True, "data": {"id": str(photo.id)}}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="offender/verify")
    def verify_offender(self, request):
        identifier = request.data.get("identifier")
        if not identifier:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": "Identifier required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        veh = Vehicule.objects.filter(Q(numero_plaque=identifier) | Q(id=identifier)).first()
        cond = Conducteur.objects.filter(Q(numero_permis=identifier) | Q(id=identifier)).first()
        data = {}
        if veh:
            data["vehicle"] = {
                "id": veh.id,
                "numero_plaque": veh.numero_plaque,
                "marque": veh.marque,
                "modele": veh.modele,
                "annee_fabrication": veh.annee_fabrication,
            }
        if cond:
            data["driver"] = {
                "id": cond.id,
                "nom": cond.nom,
                "prenom": cond.prenom,
                "numero_permis": cond.numero_permis,
            }
        return Response({"success": True, "data": {"exists": bool(veh or cond), **data}})



class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for API key management (admin only)
    
    Provides CRUD operations for API keys, registration requests,
    revocation, and usage statistics.
    """
    
    permission_classes = [IsAdminUser]
    throttle_classes = [AuthThrottle]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get API keys with related data"""
        return APIKey.objects.select_related('created_by').prefetch_related('permissions')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return APIKeyListSerializer
        elif self.action == 'register_request':
            return APIKeyRegistrationRequestSerializer
        elif self.action == 'usage_stats':
            return APIKeyUsageStatsSerializer
        return APIKeySerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new API key"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.save()
        
        # Add permissions if provided
        permissions_data = request.data.get('permissions', [])
        for perm_data in permissions_data:
            APIKeyPermission.objects.create(
                api_key=api_key,
                resource=perm_data['resource'],
                scope=perm_data['scope'],
                granted_by=request.user
            )
        
        # Reload to include permissions
        api_key.refresh_from_db()
        output_serializer = APIKeySerializer(api_key)
        
        return Response(
            {
                'success': True,
                'message': 'API key created successfully',
                'data': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def list(self, request, *args, **kwargs):
        """List all API keys"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by status if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by organization
        organization = request.query_params.get('organization')
        if organization:
            queryset = queryset.filter(organization__icontains=organization)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific API key"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """Update an API key"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Don't allow updating the key itself
        if 'key' in request.data:
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'validation_error',
                        'message': _('Cannot update API key value')
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log the update
        APIKeyEvent.objects.create(
            api_key=instance,
            event_type='PERMISSIONS_CHANGED' if 'permissions' in request.data else 'RATE_LIMIT_CHANGED',
            performed_by=request.user,
            details={'updated_fields': list(request.data.keys())}
        )
        
        return Response({
            'success': True,
            'message': _('API key updated successfully'),
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete an API key (soft delete by revoking)"""
        instance = self.get_object()
        instance.revoke(revoked_by=request.user)
        
        return Response({
            'success': True,
            'message': 'API key revoked successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='register-request')
    def register_request(self, request):
        """
        Submit an API key registration request
        
        This endpoint allows users to request an API key.
        Admin approval is required before the key is created.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real implementation, this would create a pending request
        # For now, we'll just return success with instructions
        return Response({
            'success': True,
            'message': 'API key registration request submitted successfully',
            'data': {
                'status': 'pending',
                'instructions': 'Your request will be reviewed by an administrator. '
                               'You will receive an email once your API key is approved.',
                'request_details': serializer.validated_data
            }
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke an API key immediately
        
        This action cannot be undone. The API key will be deactivated
        and all subsequent requests using this key will fail.
        """
        api_key = self.get_object()
        
        if not api_key.is_active:
            return Response({
                'success': False,
                'error': {
                    'code': 'already_revoked',
                    'message': 'API key is already revoked'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        api_key.revoke(revoked_by=request.user)
        
        return Response({
            'success': True,
            'message': 'API key revoked successfully',
            'data': {
                'api_key_id': api_key.id,
                'revoked_at': timezone.now().isoformat()
            }
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a revoked API key
        
        This will re-enable a previously revoked API key.
        """
        api_key = self.get_object()
        
        if api_key.is_active:
            return Response({
                'success': False,
                'error': {
                    'code': 'already_active',
                    'message': 'API key is already active'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        api_key.is_active = True
        api_key.save(update_fields=['is_active'])
        
        # Log the activation
        APIKeyEvent.objects.create(
            api_key=api_key,
            event_type='RENEWED',
            performed_by=request.user,
            details={'activated_at': timezone.now().isoformat()}
        )
        
        return Response({
            'success': True,
            'message': 'API key activated successfully',
            'data': {
                'api_key_id': api_key.id,
                'activated_at': timezone.now().isoformat()
            }
        })
    
    @action(detail=True, methods=['get'], url_path='usage-stats')
    def usage_stats(self, request, pk=None):
        """
        Get usage statistics for an API key
        
        Returns request counts and performance metrics.
        """
        api_key = self.get_object()
        
        # In a real implementation, this would query the audit log
        # For now, return mock data structure
        stats = {
            'api_key_id': api_key.id,
            'api_key_name': api_key.name,
            'total_requests': 0,
            'requests_last_24h': 0,
            'requests_last_7d': 0,
            'requests_last_30d': 0,
            'last_used_at': api_key.last_used_at,
            'avg_response_time_ms': None
        }
        
        # TODO: Implement actual statistics from audit logs when available
        
        return Response({
            'success': True,
            'data': stats
        })
    
    @action(detail=True, methods=['post'], url_path='add-permission')
    def add_permission(self, request, pk=None):
        """
        Add a permission to an API key
        
        Request body:
        {
            "resource": "vehicles",
            "scope": "read"
        }
        """
        api_key = self.get_object()
        
        resource = request.data.get('resource')
        scope = request.data.get('scope')
        
        if not resource or not scope:
            return Response({
                'success': False,
                'error': {
                    'code': 'validation_error',
                    'message': 'Both resource and scope are required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if permission already exists
        if api_key.permissions.filter(resource=resource).exists():
            return Response({
                'success': False,
                'error': {
                    'code': 'permission_exists',
                    'message': f'Permission for resource "{resource}" already exists'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create permission
        permission = APIKeyPermission.objects.create(
            api_key=api_key,
            resource=resource,
            scope=scope,
            granted_by=request.user
        )
        
        # Log the event
        APIKeyEvent.objects.create(
            api_key=api_key,
            event_type='PERMISSIONS_CHANGED',
            performed_by=request.user,
            details={
                'action': 'added',
                'resource': resource,
                'scope': scope
            }
        )
        
        serializer = APIKeyPermissionSerializer(permission)
        return Response({
            'success': True,
            'message': 'Permission added successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='remove-permission/(?P<permission_id>[^/.]+)')
    def remove_permission(self, request, pk=None, permission_id=None):
        """
        Remove a permission from an API key
        """
        api_key = self.get_object()
        
        try:
            permission = api_key.permissions.get(id=permission_id)
        except APIKeyPermission.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'not_found',
                    'message': 'Permission not found'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        resource = permission.resource
        scope = permission.scope
        permission.delete()
        
        # Log the event
        APIKeyEvent.objects.create(
            api_key=api_key,
            event_type='PERMISSIONS_CHANGED',
            performed_by=request.user,
            details={
                'action': 'removed',
                'resource': resource,
                'scope': scope
            }
        )
        
        return Response({
            'success': True,
            'message': 'Permission removed successfully'
        })


# Import API models at the end to avoid circular imports
from api.models import APIKey, APIKeyPermission, APIKeyEvent
from .serializers import (
    APIKeySerializer, APIKeyListSerializer, APIKeyRegistrationRequestSerializer,
    APIKeyUsageStatsSerializer, APIKeyPermissionSerializer
)
