from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from vehicles.models import Vehicule

from .models import Conducteur, Contestation, Contravention, ContraventionAuditLog, DossierFourriere, TypeInfraction
from .serializers import (
    AgentStatsSerializer,
    ConducteurSerializer,
    ContestationSerializer,
    ContraventionCreateSerializer,
    ContraventionDetailSerializer,
    ContraventionListSerializer,
    ContraventionPaymentSerializer,
    GlobalStatsSerializer,
    QRVerificationSerializer,
    TypeInfractionSerializer,
    VehiculeSummarySerializer,
)


class APIContraventionListView(generics.ListAPIView):
    """
    API endpoint to list contraventions with filtering and pagination
    """

    serializer_class = ContraventionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get_queryset(self):
        queryset = Contravention.objects.select_related(
            "type_infraction", "vehicule", "conducteur", "agent_controleur"
        ).prefetch_related("photos")

        # Filter by status (IMPAYEE, PAYEE, CONTESTEE, ANNULEE)
        statut = self.request.query_params.get("status", None)
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filter by date range
        date_from = self.request.query_params.get("date_from", None)
        date_to = self.request.query_params.get("date_to", None)
        if date_from:
            queryset = queryset.filter(date_heure_infraction__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_heure_infraction__lte=date_to)

        # Filter by agent (for agent-specific views)
        agent_id = self.request.query_params.get("agent_id", None)
        if agent_id:
            queryset = queryset.filter(agent_controleur_id=agent_id)

        # Filter by vehicle
        vehicle_id = self.request.query_params.get("vehicle_id", None)
        if vehicle_id:
            queryset = queryset.filter(vehicule_id=vehicle_id)

        # Filter by driver
        driver_id = self.request.query_params.get("driver_id", None)
        if driver_id:
            queryset = queryset.filter(conducteur_id=driver_id)

        # Search by PV, vehicle plate or driver name
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(numero_pv__icontains=search)
                | Q(vehicule__plaque_immatriculation__icontains=search)
                | Q(conducteur__nom_complet__icontains=search)
            )

        return queryset.order_by("-created_at")


class APIContraventionDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a specific contravention detail
    """

    queryset = Contravention.objects.select_related(
        "type_infraction", "vehicule", "conducteur", "agent_controleur", "dossier_fourriere"
    ).prefetch_related("photos", "contestations")
    serializer_class = ContraventionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "numero_pv"
    throttle_classes = []


class APIContraventionCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new contravention (for mobile agents)
    """

    serializer_class = ContraventionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def perform_create(self, serializer):
        serializer.save()


class APIContraventionPaymentView(APIView):
    """
    API endpoint to process contravention payment
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def post(self, request, numero_pv):
        contravention = get_object_or_404(Contravention, numero_pv=numero_pv)

        # Check if already paid
        if contravention.statut == "PAYEE":
            return Response({"error": "Cette contravention est déjà payée"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ContraventionPaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment_method = serializer.validated_data["payment_method"]

            # Process payment based on method
            if payment_method == "mvola":
                # Initiate MVola payment
                return self.process_mvola_payment(contravention, serializer.validated_data)
            elif payment_method == "stripe":
                # Initiate Stripe payment
                return self.process_stripe_payment(contravention)
            elif payment_method == "cash":
                # Record cash payment
                return self.process_cash_payment(contravention, serializer.validated_data)

            return Response({"message": "Paiement initié avec succès"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_mvola_payment(self, contravention, payment_data):
        from contraventions.services.paiement_amende_service import PaiementAmendeService

        number = payment_data.get("mvola_number", "").replace(" ", "")
        if number.startswith("034") or number.startswith("038"):
            customer_msisdn = "261" + number[1:]
        else:
            customer_msisdn = number
        result = PaiementAmendeService.initier_paiement_mvola(
            contravention=contravention, customer_msisdn=customer_msisdn, user=self.request.user
        )
        return Response(
            {
                "message": result["message"],
                "contravention": contravention.numero_pv,
                "montant": contravention.get_montant_total(),
                "transaction_id": result.get("transaction_id"),
                "server_correlation_id": result.get("server_correlation_id"),
            },
            status=status.HTTP_200_OK,
        )

    def process_stripe_payment(self, contravention):
        from contraventions.services.paiement_amende_service import PaiementAmendeService

        result = PaiementAmendeService.initier_paiement_stripe(contravention=contravention, user=self.request.user)
        return Response(
            {
                "message": result["message"],
                "contravention": contravention.numero_pv,
                "client_secret": result.get("client_secret"),
                "payment_intent_id": result.get("payment_intent_id"),
            },
            status=status.HTTP_200_OK,
        )

    def process_cash_payment(self, contravention, payment_data):
        # Cash payments are managed via dedicated cash views/sessions
        return Response(
            {
                "message": "Paiement en espèces à traiter via point de paiement",
                "contravention": contravention.numero_pv,
                "montant": contravention.get_montant_total(),
                "lieu": payment_data.get("cash_location"),
            },
            status=status.HTTP_200_OK,
        )


class APIContestationCreateView(generics.CreateAPIView):
    """
    API endpoint to create a contestation
    """

    queryset = Contestation.objects.all()
    serializer_class = ContestationSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous contestations
    throttle_classes = []

    def perform_create(self, serializer):
        numero_pv = self.kwargs.get("numero_pv")
        if numero_pv:
            contravention = get_object_or_404(Contravention, numero_pv=numero_pv)
            serializer.save(contravention=contravention)
        else:
            super().perform_create(serializer)


class APIPaymentVerificationView(APIView):
    """
    API endpoint to verify payment status
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def post(self, request):
        contravention_numero = request.data.get("contravention_numero")
        transaction_id = request.data.get("transaction_id")

        if not contravention_numero or not transaction_id:
            return Response(
                {"error": "Numéro de contravention et ID de transaction requis"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            contravention = Contravention.objects.get(numero_pv=contravention_numero)

            # Verify payment status with payment provider
            # This would integrate with your payment service

            if contravention.statut == "PAYEE":
                return Response(
                    {
                        "status": "paid",
                        "contravention": contravention.numero_pv,
                        "montant": contravention.get_montant_total(),
                        "date_paiement": contravention.date_paiement,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": "pending",
                        "contravention": contravention.numero_pv,
                        "message": "Paiement en attente de confirmation",
                    },
                    status=status.HTTP_200_OK,
                )

        except Contravention.DoesNotExist:
            return Response({"error": "Contravention non trouvée"}, status=status.HTTP_404_NOT_FOUND)


class APIQRVerificationView(APIView):
    """
    API endpoint to verify QR code
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def post(self, request):
        serializer = QRVerificationSerializer(data=request.data)
        if serializer.is_valid():
            contravention = serializer.context["contravention"]

            return Response(
                {
                    "valid": True,
                    "contravention": {
                        "numero": contravention.numero_pv,
                        "date": contravention.date_heure_infraction,
                        "statut": contravention.statut,
                        "montant": contravention.get_montant_total(),
                        "type_infraction": contravention.type_infraction.nom,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIAgentStatsView(APIView):
    """
    API endpoint to get agent statistics
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        agent_profile = getattr(request.user, "agent_controleur_profile", None)
        agent_id = request.query_params.get("agent_id", agent_profile.id if agent_profile else None)

        date_from = request.query_params.get("date_from", (timezone.now() - timedelta(days=30)).date())
        date_to = request.query_params.get("date_to", timezone.now().date())

        qs = Contravention.objects.all()
        if agent_id:
            qs = qs.filter(agent_controleur_id=agent_id)

        qs = qs.filter(date_heure_infraction__date__gte=date_from, date_heure_infraction__date__lte=date_to)

        agent_stats = qs.aggregate(
            total_contraventions=Count("id"),
            contraventions_actives=Count("id", filter=Q(statut="IMPAYEE")),
            contraventions_payees=Count("id", filter=Q(statut="PAYEE")),
            montant_total=Sum("montant_amende_ariary"),
            montant_percu=Sum("montant_amende_ariary", filter=Q(statut="PAYEE")),
        )

        # Calculate payment rate
        total = agent_stats["total_contraventions"] or 0
        paid = agent_stats["contraventions_payees"] or 0
        agent_stats["taux_paiement"] = (paid / total * 100) if total > 0 else 0

        # Get agent info
        if agent_profile:
            agent_stats["agent_nom"] = agent_profile.nom_complet
        else:
            agent_stats["agent_nom"] = "Agent inconnu"

        serializer = AgentStatsSerializer(agent_stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIVehicleSearchView(APIView):
    """
    API endpoint to search vehicles
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        query = request.query_params.get("q", "")

        if len(query) < 2:
            return Response(
                {"error": "La recherche doit contenir au moins 2 caractères"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Search by plaque or chassis
        vehicles = Vehicule.objects.filter(
            Q(plaque_immatriculation__icontains=query) | Q(numero_chassis__icontains=query)
        ).select_related("proprietaire")[:10]

        serializer = VehiculeSummarySerializer(vehicles, many=True)
        return Response({"success": True, "vehicles": serializer.data}, status=status.HTTP_200_OK)


class APIConducteurSearchView(APIView):
    """
    API endpoint to search drivers
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        query = request.query_params.get("q", "")

        if len(query) < 2:
            return Response(
                {"error": "La recherche doit contenir au moins 2 caractères"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Search by name, first name, or permit number
        conducteurs = Conducteur.objects.filter(
            Q(nom_complet__icontains=query) | Q(cin__icontains=query) | Q(numero_permis__icontains=query)
        )[:10]

        serializer = ConducteurSerializer(conducteurs, many=True)
        return Response({"success": True, "conducteurs": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def check_recidive(request):
    """
    API endpoint to check for récidive
    """
    vehicule_id = request.query_params.get("vehicule_id")
    conducteur_id = request.query_params.get("conducteur_id")
    type_infraction_id = request.query_params.get("type_infraction_id")

    if not vehicule_id and not conducteur_id:
        return Response({"error": "Véhicule ou conducteur requis"}, status=status.HTTP_400_BAD_REQUEST)

    # Check for recent contraventions (last 12 months)
    date_limit = timezone.now() - timedelta(days=365)

    query = Q(date_heure_infraction__gte=date_limit)

    if vehicule_id:
        query &= Q(vehicule_id=vehicule_id)

    if conducteur_id:
        query &= Q(conducteur_id=conducteur_id)

    if type_infraction_id:
        query &= Q(type_infraction_id=type_infraction_id)

    recent_contraventions = Contravention.objects.filter(query).exclude(statut="ANNULEE")
    recidive_count = recent_contraventions.count()

    # Calculate majoration (example: 50% for each récidive)
    majoration = 0
    if recidive_count > 0 and type_infraction_id:
        try:
            type_infraction = TypeInfraction.objects.get(id=type_infraction_id)
            base_amount = type_infraction.montant_min_ariary
            majoration = base_amount * Decimal("0.5") * recidive_count
        except TypeInfraction.DoesNotExist:
            pass

    return Response(
        {
            "success": True,
            "has_recidive": recidive_count > 0,
            "recidive_count": recidive_count,
            "majoration": majoration,
            "message": f"{recidive_count} contravention(s) similaire(s) trouvée(s) dans les 12 derniers mois",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_infraction_details(request):
    """
    API endpoint to get infraction type details
    """
    type_id = request.query_params.get("type_id")

    if not type_id:
        return Response({"error": "ID du type d'infraction requis"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        type_infraction = TypeInfraction.objects.get(id=type_id)

        return Response(
            {
                "success": True,
                "montant": type_infraction.montant_min_ariary,
                "montant_base": type_infraction.montant_min_ariary,
                "montant_variable": type_infraction.montant_variable,
                "fourriere_obligatoire": type_infraction.fourriere_obligatoire,
                "sanctions_administratives": type_infraction.sanctions_administratives,
            },
            status=status.HTTP_200_OK,
        )

    except TypeInfraction.DoesNotExist:
        return Response({"error": "Type d'infraction non trouvé"}, status=status.HTTP_404_NOT_FOUND)
