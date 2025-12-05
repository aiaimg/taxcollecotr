import csv
import io
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from payments.models import PaiementTaxe, QRCode
from vehicles.audit import log_action
from vehicles.forms import FleetBulkEditForm, FleetImportMappingForm, FleetImportUploadForm
from vehicles.import_utils import map_row, normalize_vehicle_payload, read_rows, validate_vehicle_payload
from vehicles.models import (
    BulkEditChange,
    BulkEditOperation,
    FleetImportBatch,
    FleetImportRow,
    GrilleTarifaire,
    Vehicule,
)

from .forms import CustomUserCreationForm
from .models import EntrepriseProfile
from allauth.socialaccount.models import SocialAccount


def is_admin_user(user):
    """Check if user is admin or staff"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or hasattr(user, "adminuserprofile")


class CustomLoginView(LoginView):
    """Custom login view that excludes admin users"""

    template_name = "registration/login.html"

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        # Try to authenticate the user
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            # Check if user has verified their email
            if not user.is_active:
                messages.warning(
                    self.request,
                    _("Votre compte n'est pas encore activé. Veuillez vérifier votre email."),
                )
                return redirect("core:resend_verification")

            # Import agent utilities
            from core.utils import is_agent_government, is_agent_partenaire

            # Allow agents even if they're staff (they have their own login but can use this as fallback)
            is_agent = is_agent_partenaire(user) or is_agent_government(user)

            # Block only pure admin users (staff/superuser who are not agents)
            if is_admin_user(user) and not is_agent:
                # Add error message and return form as invalid
                form.add_error(None, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
                return self.form_invalid(form)

            # User exists and is allowed, proceed with normal login
            login(self.request, user)
            
            # Ensure user has a profile (auto-create if missing)
            from core.models import UserProfile
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, user_type='individual')
            
            return super().form_valid(form)
        else:
            # User doesn't exist or wrong credentials
            form.add_error(None, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
            return self.form_invalid(form)

    def get_success_url(self):
        """Redirect based on user role after login"""
        user = self.request.user

        # Import agent utilities
        from core.utils import is_agent_government, is_agent_partenaire

        # Check user role and redirect accordingly
        if user.is_superuser or user.is_staff:
            # Admin users should use admin login, but if they get here, redirect to admin dashboard
            return reverse_lazy("administration:dashboard")
        elif is_agent_partenaire(user):
            # Agent Partenaire -> Cash Dashboard
            return reverse_lazy("payments:cash_dashboard")
        elif is_agent_government(user):
            # Agent Gouvernement -> QR Verification Dashboard
            return reverse_lazy("payments:qr_verification_dashboard")
        elif hasattr(user, "profile"):
            user_type = user.profile.user_type
            if user_type in ["company", "public_institution", "international_organization"]:
                # Fleet managers -> Fleet Dashboard
                return reverse_lazy("core:fleet_dashboard")

        # Regular clients (individual) -> Main Dashboard
        return reverse_lazy("core:velzon_dashboard")


class CustomLogoutView(View):
    """Custom logout view that accepts both GET and POST requests"""

    def get(self, request):
        return self.logout_user(request)

    def post(self, request):
        return self.logout_user(request)

    def logout_user(self, request):
        # Create logout notification before logging out
        if request.user.is_authenticated:
            try:
                from notifications.services import NotificationService

                langue = "fr"
                if hasattr(request.user, "profile"):
                    langue = request.user.profile.langue_preferee

                NotificationService.create_logout_notification(user=request.user, langue=langue)
            except Exception as e:
                # Log error but don't fail logout
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error creating logout notification: {str(e)}")

        # Logout the user
        auth_logout(request)

        # Add success message
        messages.success(request, _("Vous avez été déconnecté avec succès."))

        # Redirect to login page
        return redirect("core:login")


class VelzonDashboardView(LoginRequiredMixin, TemplateView):
    """Velzon-themed dashboard view"""

    template_name = "dashboard.html"
    login_url = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        """Redirect fleet managers to fleet dashboard"""
        user = request.user
        if hasattr(user, "profile"):
            user_type = user.profile.user_type
            if user_type in ["company", "public_institution", "international_organization"]:
                # Fleet managers should use fleet dashboard
                return redirect("core:fleet_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Check if user is admin
        is_admin = is_admin_user(user)

        if is_admin:
            # Admin sees system-wide data
            total_vehicles = Vehicule.objects.count()
            monthly_payments = (
                PaiementTaxe.objects.filter(
                    date_paiement__month=timezone.now().month, date_paiement__year=timezone.now().year, statut="PAYE"
                ).aggregate(total=Sum("montant_paye_ariary"))["total"]
                or 0
            )

            active_users = User.objects.filter(is_active=True).count()

            # Get recent activities (last 10 payments)
            recent_payments = PaiementTaxe.objects.filter(statut="PAYE").order_by("-date_paiement")[:10]

            # Payment method breakdown
            payment_methods = (
                PaiementTaxe.objects.filter(statut="PAYE")
                .values("methode_paiement")
                .annotate(count=Count("*"), total=Sum("montant_paye_ariary"))
                .order_by("-count")
            )

            # Vehicle type breakdown
            vehicle_types = (
                Vehicule.objects.values("type_vehicule")
                .annotate(count=Count("plaque_immatriculation"))
                .order_by("-count")[:5]
            )

        else:
            # Regular user sees only their personal data
            total_vehicles = Vehicule.objects.filter(proprietaire=user).count()
            monthly_payments = (
                PaiementTaxe.objects.filter(
                    vehicule_plaque__proprietaire=user,
                    date_paiement__month=timezone.now().month,
                    date_paiement__year=timezone.now().year,
                    statut="PAYE",
                ).aggregate(total=Sum("montant_paye_ariary"))["total"]
                or 0
            )

            active_users = 1  # Only themselves

            # Get recent activities (last 10 payments for this user)
            recent_payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user, statut="PAYE").order_by(
                "-date_paiement"
            )[:10]

            # Payment method breakdown for this user
            payment_methods = (
                PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user, statut="PAYE")
                .values("methode_paiement")
                .annotate(count=Count("*"), total=Sum("montant_paye_ariary"))
                .order_by("-count")
            )

            # Vehicle type breakdown for this user
            vehicle_types = (
                Vehicule.objects.filter(proprietaire=user)
                .values("type_vehicule")
                .annotate(count=Count("plaque_immatriculation"))
                .order_by("-count")[:5]
            )

        # Monthly revenue trend (last 6 months) for charts
        monthly_revenue = []
        today = timezone.now().date()
        for i in range(6):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            if is_admin:
                # Admin sees all revenue
                revenue = (
                    PaiementTaxe.objects.filter(
                        date_paiement__date__range=[month_start, month_end], statut="PAYE"
                    ).aggregate(Sum("montant_paye_ariary"))["montant_paye_ariary__sum"]
                    or 0
                )
            else:
                # User sees only their revenue
                revenue = (
                    PaiementTaxe.objects.filter(
                        vehicule_plaque__proprietaire=user,
                        date_paiement__date__range=[month_start, month_end],
                        statut="PAYE",
                    ).aggregate(Sum("montant_paye_ariary"))["montant_paye_ariary__sum"]
                    or 0
                )

            monthly_revenue.append({"month": month_start.strftime("%b %Y"), "revenue": float(revenue)})

        monthly_revenue.reverse()

        # Today's statistics
        today = timezone.now().date()
        if is_admin:
            today_payments = PaiementTaxe.objects.filter(date_paiement__date=today, statut="PAYE").count()

            today_revenue = (
                PaiementTaxe.objects.filter(date_paiement__date=today, statut="PAYE").aggregate(
                    Sum("montant_paye_ariary")
                )["montant_paye_ariary__sum"]
                or 0
            )
        else:
            today_payments = PaiementTaxe.objects.filter(
                vehicule_plaque__proprietaire=user, date_paiement__date=today, statut="PAYE"
            ).count()

            today_revenue = (
                PaiementTaxe.objects.filter(
                    vehicule_plaque__proprietaire=user, date_paiement__date=today, statut="PAYE"
                ).aggregate(Sum("montant_paye_ariary"))["montant_paye_ariary__sum"]
                or 0
            )

        # Get payment reminders for user
        unpaid_vehicles = []
        expiring_vehicles = []
        expired_vehicles = []

        if not is_admin:
            # Only show reminders for regular users
            user_vehicles = Vehicule.objects.filter(proprietaire=user, est_actif=True)
            for vehicle in user_vehicles:
                status_info = vehicle.get_current_payment_status()
                vehicle.payment_status = status_info  # Attach for template use

                if status_info["status"] == "unpaid":
                    unpaid_vehicles.append(vehicle)
                elif status_info["status"] == "expiring_soon":
                    expiring_vehicles.append(vehicle)
                elif status_info["status"] == "expired":
                    expired_vehicles.append(vehicle)

        context.update(
            {
                "page_title": _("Tableau de Bord Velzon"),
                "total_vehicles": total_vehicles,
                "monthly_payments": monthly_payments,
                "active_users": active_users,
                "recent_payments": recent_payments,
                "current_month": timezone.now().strftime("%B %Y"),
                "monthly_revenue": monthly_revenue,
                "payment_methods": payment_methods,
                "vehicle_types": vehicle_types,
                "today_payments": today_payments,
                "today_revenue": today_revenue,
                "is_admin": is_admin,
                "unpaid_vehicles": unpaid_vehicles,
                "expiring_vehicles": expiring_vehicles,
                "expired_vehicles": expired_vehicles,
                "current_year": timezone.now().year,
            }
        )

        return context


class QRVerificationView(TemplateView):
    """Public QR code verification page"""

    template_name = "core/qr_verification.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import CMS context helper
        from cms.views import get_cms_context

        # Add CMS context (header, footer, menus, etc.)
        context.update(get_cms_context())

        # Add page-specific context
        context.update(
            {
                "page_title": _("Vérification QR Code"),
                "page_description": _("Vérifiez la validité d'un QR code de paiement de taxe véhicule"),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        """Handle QR code verification via AJAX"""
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            qr_code = request.POST.get("qr_code", "").strip()

            if not qr_code:
                return JsonResponse({"success": False, "message": _("Veuillez saisir un code QR")})

            try:
                # Look up QR code by token (the QR code stores a token, not a code field)
                qr_obj = (
                    QRCode.objects.select_related("vehicule_plaque", "vehicule_plaque__type_vehicule")
                    .prefetch_related("vehicule_plaque__documents")
                    .get(token=qr_code)
                )

                # Check if QR code is valid
                if not qr_obj.est_actif:
                    return JsonResponse({"success": False, "message": _("Ce QR code n'est plus actif")})

                if qr_obj.date_expiration and qr_obj.date_expiration < timezone.now():
                    return JsonResponse({"success": False, "message": _("Ce QR code a expiré")})

                # Get the payment associated with this QR code
                # QRCode doesn't have a direct paiement relationship, so we look it up
                paiement = PaiementTaxe.objects.filter(
                    vehicule_plaque=qr_obj.vehicule_plaque, annee_fiscale=qr_obj.annee_fiscale
                ).first()

                # Check if vehicle has paid the tax
                tax_paid = False
                if paiement:
                    tax_paid = paiement.statut in ["PAYE", "EXONERE"]

                # Increment scan count
                qr_obj.nombre_scans += 1
                qr_obj.derniere_verification = timezone.now()
                qr_obj.save(update_fields=["nombre_scans", "derniere_verification"])

                # Get vehicle documents (assurance and carte grise)
                # Get the most recent document of each type
                from vehicles.models import DocumentVehicule

                assurance_doc = (
                    qr_obj.vehicule_plaque.documents.filter(document_type="assurance").order_by("-created_at").first()
                )

                carte_grise_doc = (
                    qr_obj.vehicule_plaque.documents.filter(document_type="carte_grise").order_by("-created_at").first()
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

                # Check if QR code is expired
                is_expired = qr_obj.date_expiration and qr_obj.date_expiration < timezone.now()

                # Prepare QR code data
                qr_data = {
                    "est_expire": is_expired,
                    "date_generation": qr_obj.date_generation.isoformat() if qr_obj.date_generation else None,
                    "date_expiration": qr_obj.date_expiration.isoformat() if qr_obj.date_expiration else None,
                    "expiration_date": qr_obj.date_expiration.strftime("%d/%m/%Y") if qr_obj.date_expiration else None,
                }

                # Prepare vehicle data with all required information
                vehicule = None
                if qr_obj.vehicule_plaque:
                    vehicule = {
                        "plaque_immatriculation": qr_obj.vehicule_plaque.plaque_immatriculation,
                        "vin": qr_obj.vehicule_plaque.vin or "",
                        "nom_proprietaire": qr_obj.vehicule_plaque.nom_proprietaire or "",
                        "type_vehicule_display": (
                            str(qr_obj.vehicule_plaque.type_vehicule) if qr_obj.vehicule_plaque.type_vehicule else ""
                        ),
                        "puissance_fiscale": qr_obj.vehicule_plaque.puissance_fiscale_cv,
                    }

                # Prepare payment data
                paiement_data = None
                if paiement:
                    paiement_data = {
                        "tax_paid": tax_paid,
                        "statut": paiement.statut,
                        "statut_display": paiement.get_statut_display(),
                        "montant_paye": str(paiement.montant_paye_ariary) if paiement.montant_paye_ariary else "0.00",
                        "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
                        "methode_paiement_display": (
                            paiement.get_methode_paiement_display() if paiement.methode_paiement else None
                        ),
                        "reference_transaction": paiement.transaction_id or None,
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

                # QR code is valid - return comprehensive data
                return JsonResponse(
                    {
                        "success": True,
                        "message": _("QR code valide"),
                        "tax_paid": tax_paid,  # Main answer: has vehicle paid the tax?
                        "expiration_date": (
                            qr_obj.date_expiration.strftime("%d/%m/%Y") if qr_obj.date_expiration else None
                        ),  # When will it expire?
                        "qr_data": qr_data,
                        "vehicule": vehicule,  # Vehicle plaque, VIN, owner name
                        "paiement": paiement_data,  # Payment information
                        "documents": documents,  # Assurance and carte grise documents with image URLs
                    }
                )

            except QRCode.DoesNotExist:
                return JsonResponse({"success": False, "message": _("QR code non trouvé")})
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error verifying QR code: {str(e)}")
                return JsonResponse({"success": False, "message": _("Erreur lors de la vérification")})

        # If not AJAX, redirect to GET
        return self.get(request, *args, **kwargs)


class RegisterView(CreateView):
    """User registration view with email verification"""

    model = User
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("core:registration_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": _("Inscription"),
                "page_description": _("Créez votre compte pour accéder à la plateforme"),
            }
        )
        return context

    def form_valid(self, form):
        # Create user but set as inactive until email is verified
        user = form.save(commit=False)
        user._user_type = form.cleaned_data["user_type"]
        user.is_active = False  # User must verify email before login
        user.save()

        # Send verification email
        self.send_verification_email(user)

        messages.success(
            self.request,
            _("Votre compte a été créé! Veuillez vérifier votre email pour activer votre compte."),
        )
        return redirect(self.success_url)

    def send_verification_email(self, user):
        """Send email verification link to user"""
        from django.contrib.sites.shortcuts import get_current_site
        from django.template.loader import render_to_string
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from administration.email_utils import send_email
        from core.tokens import email_verification_token

        # Generate verification token
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build verification URL
        current_site = get_current_site(self.request)
        verification_url = f"http://{current_site.domain}/verify-email/{uid}/{token}/"

        # Prepare email content
        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": "Tax Collector",
        }

        subject = "Vérification de votre compte Tax Collector"
        message = render_to_string("registration/verification_email.txt", context)
        html_message = render_to_string("registration/verification_email.html", context)

        # Send email
        send_email(
            subject=subject,
            message=message,
            recipient_list=[user.email],
            html_message=html_message,
            email_type="verification",
            fail_silently=False,
        )

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect("core:velzon_dashboard")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""

    template_name = "registration/profile.html"
    login_url = reverse_lazy("core:login")

    def get_template_names(self):
        """Use Velzon template for all users"""
        return ["core/profile.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user profile and type
        user_profile = None
        user_type = None
        user_type_display = None

        if hasattr(user, "profile"):
            user_profile = user.profile
            user_type = user_profile.user_type
            user_type_display = user_profile.get_user_type_display()

        # Get user's vehicles and payments (personal data only)
        user_vehicles = Vehicule.objects.filter(proprietaire=user).order_by("-created_at")[:5]
        user_payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user).order_by("-created_at")[:5]

        # Calculate user stats
        total_vehicles = Vehicule.objects.filter(proprietaire=user).count()
        total_payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user).count()
        current_year = timezone.now().year
        pending_payments = (
            Vehicule.objects.filter(proprietaire=user)
            .exclude(paiements__annee_fiscale=current_year, paiements__statut="PAID")
            .count()
        )

        context.update(
            {
                "page_title": _("Mon Profil"),
                "page_description": _("Gérez vos informations personnelles"),
                "user_profile": user_profile,
                "user_type": user_type,
                "user_type_display": user_type_display,
                "user_vehicles": user_vehicles,
                "user_payments": user_payments,
                "total_vehicles": total_vehicles,
                "total_payments": total_payments,
                "pending_payments": pending_payments,
                "current_year": current_year,
            }
        )
        return context


class ProfileEditView(LoginRequiredMixin, View):
    """User profile edit view with image upload support"""

    template_name = "core/profile_edit.html"
    login_url = reverse_lazy("core:login")

    def get(self, request):
        from core.forms import UserEditForm, UserProfileForm

        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "page_title": _("Modifier le Profil"),
            "page_description": _("Modifiez vos informations personnelles"),
            "user_profile": request.user.profile,
            "user_type_display": request.user.profile.get_user_type_display(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        from core.forms import UserEditForm, UserProfileForm

        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Create notification for profile updated
            from notifications.services import NotificationService

            langue = request.user.profile.langue_preferee

            NotificationService.create_notification(
                user=request.user,
                notification_type="profile_updated",
                titre=_("Profil mis à jour") if langue == "fr" else "Profil mis à jour",
                message=(
                    _("Vos informations de profil ont été mises à jour avec succès.")
                    if langue == "fr"
                    else "Vos informations de profil ont été mises à jour avec succès."
                ),
                langue=langue,
            )

            messages.success(request, _("Votre profil a été mis à jour avec succès."))
            return redirect("core:profile")

        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "page_title": _("Modifier le Profil"),
            "page_description": _("Modifiez vos informations personnelles"),
            "user_profile": request.user.profile,
            "user_type_display": request.user.profile.get_user_type_display(),
        }
        return render(request, self.template_name, context)

    def form_valid(self, form):
        response = super().form_valid(form)

        # Create notification for profile updated
        from notifications.services import NotificationService

        langue = "fr"
        if hasattr(self.request.user, "profile"):
            langue = self.request.user.profile.langue_preferee

        NotificationService.create_profile_updated_notification(user=self.request.user, langue=langue)

        messages.success(self.request, _("Votre profil a été mis à jour avec succès!"))
        return response


# Fleet Manager Views
class FleetManagerMixin(LoginRequiredMixin):
    """Mixin to ensure user has fleet manager access"""

    login_url = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        # Check if user is a company, public_institution, or international_organization (fleet managers)
        if hasattr(request.user, "profile"):
            user_type = request.user.profile.user_type
            if user_type in ["company", "public_institution", "international_organization"]:
                return super().dispatch(request, *args, **kwargs)

        messages.error(request, _("Accès réservé aux gestionnaires de flotte"))
        return redirect("core:velzon_dashboard")


class FleetDashboardView(FleetManagerMixin, TemplateView):
    """Fleet Manager Dashboard"""

    template_name = "fleet/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = timezone.now().year

        # Get all vehicles for this company
        vehicles = Vehicule.objects.filter(proprietaire=user)

        # Calculate statistics
        total_vehicles = vehicles.count()
        paid_vehicles = (
            vehicles.filter(paiements__annee_fiscale=current_year, paiements__statut="PAID").distinct().count()
        )

        pending_payments = vehicles.exclude(paiements__annee_fiscale=current_year, paiements__statut="PAID").count()

        total_amount_due = 0
        total_amount_paid = 0

        category_stats = {
            "TERRESTRE": {
                "count": 0,
                "paid_count": 0,
                "pending_count": 0,
                "amount_due": 0,
                "amount_paid": 0,
            },
            "AERIEN": {
                "count": 0,
                "paid_count": 0,
                "pending_count": 0,
                "amount_due": 0,
                "amount_paid": 0,
            },
            "MARITIME": {
                "count": 0,
                "paid_count": 0,
                "pending_count": 0,
                "amount_due": 0,
                "amount_paid": 0,
            },
        }

        for vehicle in vehicles:
            # Calculate tax for each vehicle
            from vehicles.services import TaxCalculationService

            tax_service = TaxCalculationService()
            tax_info = tax_service.calculate_tax(vehicle, current_year)

            if not tax_info["is_exempt"] and tax_info["amount"]:
                total_amount_due += tax_info["amount"]

                # Check if paid
                payment = PaiementTaxe.objects.filter(
                    vehicule_plaque=vehicle, annee_fiscale=current_year, statut="PAID"
                ).first()

                if payment:
                    total_amount_paid += payment.montant_paye

            cat = vehicle.vehicle_category or "TERRESTRE"
            if cat in category_stats:
                category_stats[cat]["count"] += 1
                if not tax_info["is_exempt"] and tax_info["amount"]:
                    category_stats[cat]["amount_due"] += tax_info["amount"]
                payment = PaiementTaxe.objects.filter(
                    vehicule_plaque=vehicle, annee_fiscale=current_year, statut="PAID"
                ).first()
                if payment:
                    category_stats[cat]["paid_count"] += 1
                    category_stats[cat]["amount_paid"] += payment.montant_paye
                else:
                    category_stats[cat]["pending_count"] += 1

        # Get organization/institution name based on user type
        organization_name = None
        if hasattr(user, "profile"):
            user_type = user.profile.user_type
            if user_type == "company" and hasattr(user, "company_profile"):
                organization_name = user.company_profile.nom_entreprise
            elif user_type == "public_institution" and hasattr(user.profile, "public_institution_profile"):
                organization_name = user.profile.public_institution_profile.institution_name
            elif user_type == "international_organization" and hasattr(
                user.profile, "international_organization_profile"
            ):
                organization_name = user.profile.international_organization_profile.organization_name

        context.update(
            {
                "total_vehicles": total_vehicles,
                "paid_vehicles": paid_vehicles,
                "pending_payments": pending_payments,
                "total_amount_due": total_amount_due,
                "total_amount_paid": total_amount_paid,
                "current_year": current_year,
                "page_title": _("Tableau de Bord Flotte"),
                "organization_name": organization_name,
                "user_type": user.profile.user_type if hasattr(user, "profile") else None,
                "category_stats": category_stats,
                "category_overview": [
                    {
                        "key": "TERRESTRE",
                        "label": "Terrestre",
                        **category_stats["TERRESTRE"],
                    },
                    {
                        "key": "AERIEN",
                        "label": "Aérien",
                        **category_stats["AERIEN"],
                    },
                    {
                        "key": "MARITIME",
                        "label": "Maritime",
                        **category_stats["MARITIME"],
                    },
                ],
            }
        )

        return context


class FleetVehicleListView(FleetManagerMixin, ListView):
    """Fleet vehicle list with batch operations"""

    model = Vehicule
    template_name = "fleet/vehicle_list.html"
    context_object_name = "vehicles"
    paginate_by = 20

    def get_queryset(self):
        queryset = Vehicule.objects.filter(proprietaire=self.request.user).order_by("plaque_immatriculation")

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(plaque_immatriculation__icontains=search)
                | Q(type_vehicule__icontains=search)
                | Q(source_energie__icontains=search)
            )

        # Filter by energy source
        energy = self.request.GET.get("energy")
        if energy:
            queryset = queryset.filter(source_energie=energy)

        # Filter by vehicle type
        vehicle_type = self.request.GET.get("type")
        if vehicle_type:
            try:
                # Convert to integer if it's an ID
                vehicle_type_id = int(vehicle_type)
                queryset = queryset.filter(type_vehicule_id=vehicle_type_id)
            except (ValueError, TypeError):
                # If it's not a valid ID, try to filter by name
                queryset = queryset.filter(type_vehicule__nom__icontains=vehicle_type)

        # Filter by vehicle category (TERRESTRE, AERIEN, MARITIME)
        category = self.request.GET.get("category")
        if category in {"TERRESTRE", "AERIEN", "MARITIME"}:
            queryset = queryset.filter(vehicle_category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicles.models import VehicleType

        # Get active vehicle types as choices (id, nom)
        type_choices = [(vt.id, vt.nom) for vt in VehicleType.get_active_types()]

        # Get selected type and convert to integer if possible for comparison
        selected_type = self.request.GET.get("type", "")
        try:
            selected_type_int = int(selected_type) if selected_type else ""
        except (ValueError, TypeError):
            selected_type_int = selected_type

        context.update(
            {
                "search": self.request.GET.get("search", ""),
                "selected_energy": self.request.GET.get("energy", ""),
                "selected_type": selected_type_int,
                "selected_category": self.request.GET.get("category", ""),
                "energy_choices": Vehicule.SOURCE_ENERGIE_CHOICES,
                "type_choices": type_choices,
                "page_title": _("Gestion de Flotte"),
            }
        )
        return context


class FleetBatchPaymentView(FleetManagerMixin, TemplateView):
    """Batch payment processing for multiple vehicles"""

    template_name = "fleet/batch_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = timezone.now().year

        # Get vehicles that need payment
        vehicles = Vehicule.objects.filter(proprietaire=user).exclude(
            paiements__annee_fiscale=current_year, paiements__statut="PAID"
        )

        # Calculate tax for each vehicle
        vehicle_taxes = []
        total_amount = 0

        from vehicles.services import TaxCalculationService

        tax_service = TaxCalculationService()

        for vehicle in vehicles:
            tax_info = tax_service.calculate_tax(vehicle, current_year)
            if not tax_info["is_exempt"] and tax_info["amount"]:
                vehicle_taxes.append({"vehicle": vehicle, "tax_amount": tax_info["amount"], "is_exempt": False})
                total_amount += tax_info["amount"]
            else:
                vehicle_taxes.append({"vehicle": vehicle, "tax_amount": 0, "is_exempt": True})

        context.update(
            {
                "vehicle_taxes": vehicle_taxes,
                "total_amount": total_amount,
                "current_year": current_year,
                "page_title": _("Paiement en Lot"),
            }
        )

        return context


class FleetExportView(FleetManagerMixin, TemplateView):
    """Export fleet data and accounting reports"""

    template_name = "fleet/export.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": _("Export Comptable"),
            }
        )
        return context


class FleetExportCSVView(FleetManagerMixin, TemplateView):
    """Export fleet vehicles to CSV"""

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="flotte_vehicules.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["Plaque", "Type", "Puissance (CV)", "Source Énergie", "Date Circulation", "Catégorie", "Statut Taxe"]
        )

        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year

        for vehicle in vehicles:
            # Check payment status
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle, annee_fiscale=current_year, statut="PAID"
            ).first()

            status = "Payé" if payment else "Non payé"

            writer.writerow(
                [
                    vehicle.plaque_immatriculation,
                    vehicle.get_type_vehicule_display(),
                    vehicle.puissance_fiscale_cv,
                    vehicle.get_source_energie_display(),
                    vehicle.date_premiere_circulation.strftime("%d/%m/%Y"),
                    vehicle.get_categorie_vehicule_display(),
                    status,
                ]
            )

        return response


class FleetExportExcelView(FleetManagerMixin, TemplateView):
    """Export fleet payments to Excel"""

    def get(self, request, *args, **kwargs):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Paiements Flotte")

        # Define formats
        header_format = workbook.add_format({"bold": True, "bg_color": "#4472C4", "font_color": "white", "border": 1})

        money_format = workbook.add_format({"num_format": '#,##0 "Ar"'})
        date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})

        # Headers
        headers = [
            "Plaque",
            "Type Véhicule",
            "Puissance (CV)",
            "Source Énergie",
            "Montant Taxe",
            "Date Paiement",
            "Statut",
            "Transaction ID",
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Data
        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year
        row = 1

        from vehicles.services import TaxCalculationService

        tax_service = TaxCalculationService()

        for vehicle in vehicles:
            tax_info = tax_service.calculate_tax(vehicle, current_year)
            payment = PaiementTaxe.objects.filter(vehicule_plaque=vehicle, annee_fiscale=current_year).first()

            worksheet.write(row, 0, vehicle.plaque_immatriculation)
            worksheet.write(row, 1, vehicle.get_type_vehicule_display())
            worksheet.write(row, 2, vehicle.puissance_fiscale_cv)
            worksheet.write(row, 3, vehicle.get_source_energie_display())

            if tax_info["is_exempt"]:
                worksheet.write(row, 4, "Exonéré")
                worksheet.write(row, 6, "Exonéré")
            else:
                worksheet.write(row, 4, float(tax_info["amount"] or 0), money_format)
                if payment:
                    worksheet.write(row, 5, payment.date_paiement, date_format)
                    worksheet.write(row, 6, payment.get_statut_display())
                    worksheet.write(row, 7, payment.transaction_id or "")
                else:
                    worksheet.write(row, 6, "Non payé")

            row += 1

        # Auto-adjust column widths
        worksheet.set_column("A:A", 12)  # Plaque
        worksheet.set_column("B:B", 15)  # Type
        worksheet.set_column("C:C", 12)  # Puissance
        worksheet.set_column("D:D", 15)  # Source
        worksheet.set_column("E:E", 15)  # Montant
        worksheet.set_column("F:F", 12)  # Date
        worksheet.set_column("G:G", 12)  # Statut
        worksheet.set_column("H:H", 20)  # Transaction

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="paiements_flotte.xlsx"'

        return response


class FleetExportPDFView(FleetManagerMixin, TemplateView):
    """Export fleet summary to PDF"""

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="rapport_flotte.pdf"'

        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph("Rapport de Flotte", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # Company info
        if hasattr(request.user, "entreprise_profile"):
            company = request.user.entreprise_profile
            company_info = Paragraph(
                f"""
                <b>Entreprise:</b> {company.nom_entreprise}<br/>
                <b>Numéro de contribuable:</b> {company.numero_contribuable}<br/>
                <b>Date du rapport:</b> {timezone.now().strftime('%d/%m/%Y')}
            """,
                styles["Normal"],
            )
            story.append(company_info)
            story.append(Spacer(1, 12))

        # Summary statistics
        vehicles = Vehicule.objects.filter(proprietaire=request.user)
        current_year = timezone.now().year

        total_vehicles = vehicles.count()
        paid_count = vehicles.filter(paiements__annee_fiscale=current_year, paiements__statut="PAID").distinct().count()

        summary = Paragraph(
            f"""
            <b>Résumé:</b><br/>
            • Total véhicules: {total_vehicles}<br/>
            • Véhicules payés: {paid_count}<br/>
            • Véhicules en attente: {total_vehicles - paid_count}
        """,
            styles["Normal"],
        )
        story.append(summary)
        story.append(Spacer(1, 12))

        # Vehicle details table
        data = [["Plaque", "Type", "Puissance", "Énergie", "Statut"]]

        from vehicles.services import TaxCalculationService

        tax_service = TaxCalculationService()

        for vehicle in vehicles:
            payment = PaiementTaxe.objects.filter(
                vehicule_plaque=vehicle, annee_fiscale=current_year, statut="PAID"
            ).first()

            status = "Payé" if payment else "Non payé"

            data.append(
                [
                    vehicle.plaque_immatriculation,
                    vehicle.get_type_vehicule_display(),
                    f"{vehicle.puissance_fiscale_cv} CV",
                    vehicle.get_source_energie_display(),
                    status,
                ]
            )

        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(table)

        doc.build(story)
        return response


class FleetImportView(FleetManagerMixin, TemplateView):
    template_name = "fleet/import.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"upload_form": FleetImportUploadForm(), "page_title": _("Import Flotte")})
        return context

    def post(self, request, *args, **kwargs):
        form = FleetImportUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"upload_form": form, "page_title": _("Import Flotte")})
        file = request.FILES["fichier"]
        file_type = form.cleaned_data["type_fichier"]
        rows = read_rows(file, file_type)
        headers = list(rows[0].keys()) if rows else []
        return render(
            request,
            "fleet/import_preview.html",
            {
                "headers": headers,
                "rows": rows[:20],
                "mapping_form": FleetImportMappingForm(),
                "file_type": file_type,
                "page_title": _("Prévisualisation Import"),
            },
        )


class FleetImportProcessView(FleetManagerMixin, View):
    def post(self, request, *args, **kwargs):
        mapping_form = FleetImportMappingForm(request.POST)
        if not mapping_form.is_valid():
            return JsonResponse({"ok": False, "error": "invalid_mapping"}, status=400)
        try:
            mapping = json.loads(mapping_form.cleaned_data["mapping_json"])
            options = json.loads(mapping_form.cleaned_data.get("options_json") or "{}")
        except Exception:
            return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
        file = request.FILES.get("fichier")
        file_type = request.POST.get("type_fichier")
        rows = read_rows(file, file_type) if file else []
        batch = FleetImportBatch.objects.create(
            utilisateur=request.user,
            nom_fichier=getattr(file, "name", ""),
            type_fichier=file_type or "",
            mapping_colonnes=mapping,
            options=options,
            total_lignes=len(rows),
            statut="PROCESSING",
        )
        log_action(request.user, "IMPORT_START", lot_import=batch, donnees_action={"total": len(rows)})
        success = 0
        failed = 0
        for i, row in enumerate(rows, start=1):
            data = map_row(mapping, row)
            data = normalize_vehicle_payload(data)
            valid, errs = validate_vehicle_payload(data)
            if not valid:
                FleetImportRow.objects.create(lot=batch, numero_ligne=i, donnees=data, erreurs=errs, statut="ERROR")
                log_action(request.user, "IMPORT_ROW_FAIL", lot_import=batch, donnees_action={"row": i, "errors": errs})
                failed += 1
                continue
            try:
                v = Vehicule(
                    proprietaire=request.user,
                    nom_proprietaire=data.get("nom_proprietaire") or "",
                    plaque_immatriculation=data.get("plaque_immatriculation"),
                    marque=data.get("marque") or "",
                    modele=data.get("modele") or "",
                    vin=data.get("vin") or "",
                    couleur=data.get("couleur") or "",
                    puissance_fiscale_cv=data.get("puissance_fiscale_cv") or 1,
                    cylindree_cm3=data.get("cylindree_cm3") or 1000,
                    source_energie=data.get("source_energie"),
                    date_premiere_circulation=data.get("date_premiere_circulation"),
                    categorie_vehicule=data.get("categorie_vehicule") or "Personnel",
                    type_vehicule_id=data.get("type_vehicule") if isinstance(data.get("type_vehicule"), int) else None,
                    est_actif=True,
                )
                v.full_clean()
                v.save()
                FleetImportRow.objects.create(
                    lot=batch, numero_ligne=i, donnees=data, erreurs=[], statut="SUCCESS", vehicule=v
                )
                log_action(request.user, "IMPORT_ROW_SUCCESS", vehicule=v, lot_import=batch, donnees_action={"row": i})
                success += 1
            except Exception as e:
                FleetImportRow.objects.create(lot=batch, numero_ligne=i, donnees=data, erreurs=[str(e)], statut="ERROR")
                log_action(
                    request.user, "IMPORT_ROW_FAIL", lot_import=batch, donnees_action={"row": i, "errors": [str(e)]}
                )
                failed += 1
        batch.reussites = success
        batch.echecs = failed
        batch.statut = "COMPLETED" if failed == 0 else "FAILED"
        batch.save()
        log_action(request.user, "IMPORT_END", lot_import=batch, donnees_action={"success": success, "failed": failed})
        return redirect("core:fleet_import_detail", batch_id=batch.id)


class FleetImportHistoryView(FleetManagerMixin, TemplateView):
    template_name = "fleet/import_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batches = FleetImportBatch.objects.filter(utilisateur=self.request.user).order_by("-cree_le")
        context.update({"batches": batches, "page_title": _("Historique des Imports")})
        return context


class FleetImportDetailView(FleetManagerMixin, TemplateView):
    template_name = "fleet/import_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch_id = self.kwargs.get("batch_id")
        batch = get_object_or_404(FleetImportBatch, id=batch_id, utilisateur=self.request.user)
        rows = batch.lignes.all().order_by("numero_ligne")
        context.update({"batch": batch, "rows": rows, "page_title": _("Détails Import")})
        return context


class FleetImportRollbackView(FleetManagerMixin, View):
    def post(self, request, *args, **kwargs):
        batch_id = kwargs.get("batch_id")
        batch = get_object_or_404(FleetImportBatch, id=batch_id, utilisateur=request.user)
        deleted = 0
        for row in batch.lignes.filter(statut="SUCCESS"):
            if row.vehicule:
                try:
                    row.vehicule.delete()
                    deleted += 1
                except Exception:
                    pass
        batch.statut = "ROLLED_BACK"
        batch.save()
        log_action(request.user, "IMPORT_ROLLBACK", lot_import=batch, donnees_action={"deleted": deleted})
        return redirect("core:fleet_import_detail", batch_id=batch.id)


class FleetBulkEditView(FleetManagerMixin, TemplateView):
    template_name = "fleet/bulk_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ids = self.request.GET.getlist("ids")
        vehicles = Vehicule.objects.filter(proprietaire=self.request.user, plaque_immatriculation__in=ids)
        context.update({"vehicles": vehicles, "form": FleetBulkEditForm(), "page_title": _("Modification en lot")})
        return context

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("ids")
        vehicles = list(Vehicule.objects.filter(proprietaire=request.user, plaque_immatriculation__in=ids))
        form = FleetBulkEditForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"vehicles": vehicles, "form": form, "page_title": _("Modification en lot")},
            )
        op = BulkEditOperation.objects.create(
            utilisateur=request.user, champs_modifies=form.cleaned_data, selection=ids, statut="PENDING"
        )
        changed = 0
        for v in vehicles:
            before = {
                "est_actif": v.est_actif,
                "source_energie": v.source_energie,
                "categorie_vehicule": v.categorie_vehicule,
                "type_vehicule_id": v.type_vehicule_id,
            }
            if form.cleaned_data.get("est_actif") in ["true", "false"]:
                v.est_actif = True if form.cleaned_data["est_actif"] == "true" else False
            if form.cleaned_data.get("source_energie"):
                v.source_energie = form.cleaned_data["source_energie"]
            if form.cleaned_data.get("categorie_vehicule"):
                v.categorie_vehicule = form.cleaned_data["categorie_vehicule"]
            if form.cleaned_data.get("type_vehicule"):
                v.type_vehicule = form.cleaned_data["type_vehicule"]
            v.full_clean()
            v.save()
            after = {
                "est_actif": v.est_actif,
                "source_energie": v.source_energie,
                "categorie_vehicule": v.categorie_vehicule,
                "type_vehicule_id": v.type_vehicule_id,
            }
            BulkEditChange.objects.create(operation=op, vehicule=v, avant=before, apres=after)
            changed += 1
        op.statut = "APPLIED"
        op.applique_le = timezone.now()
        op.save()
        log_action(request.user, "BULK_EDIT_APPLY", operation_modification=op, donnees_action={"changed": changed})
        return redirect("core:fleet_bulk_edit_history")


class FleetBulkEditHistoryView(FleetManagerMixin, TemplateView):
    template_name = "fleet/bulk_edit_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ops = BulkEditOperation.objects.filter(utilisateur=self.request.user).order_by("-cree_le")
        context.update({"operations": ops, "page_title": _("Historique des modifications")})
        return context


class FleetBulkEditRollbackView(FleetManagerMixin, View):
    def post(self, request, *args, **kwargs):
        op_id = kwargs.get("op_id")
        op = get_object_or_404(BulkEditOperation, id=op_id, utilisateur=request.user)
        for ch in op.changements.all():
            v = ch.vehicule
            v.est_actif = ch.avant.get("est_actif", v.est_actif)
            v.source_energie = ch.avant.get("source_energie", v.source_energie)
            v.categorie_vehicule = ch.avant.get("categorie_vehicule", v.categorie_vehicule)
            if ch.avant.get("type_vehicule_id"):
                v.type_vehicule_id = ch.avant["type_vehicule_id"]
            v.full_clean()
            v.save()
        op.statut = "ROLLED_BACK"
        op.save()
        log_action(request.user, "BULK_EDIT_ROLLBACK", operation_modification=op)
        return redirect("core:fleet_bulk_edit_history")


class PaymentListVelzonView(LoginRequiredMixin, TemplateView):
    """Velzon-themed payment list view"""

    template_name = "core/payment_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user's payments with related data
        payments = (
            PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=self.request.user)
            .select_related("vehicule_plaque")
            .order_by("-date_paiement")
        )

        # Calculate statistics
        total_payments = payments.count()
        paid_payments = payments.filter(statut="PAID").count()
        pending_payments = payments.filter(statut="PENDING").count()
        total_amount = payments.filter(statut="PAID").aggregate(total=Sum("montant_paye_ariary"))["total"] or 0

        # Pagination
        paginator = Paginator(payments, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context.update(
            {
                "payments": page_obj,
                "total_payments": total_payments,
                "paid_payments": paid_payments,
                "pending_payments": pending_payments,
                "total_amount": total_amount,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
            }
        )

        return context


class NotificationDemoView(LoginRequiredMixin, TemplateView):
    """Demo page for notification system"""

    template_name = "core/notification_demo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Démonstration des Notifications")
        return context



class RegistrationCompleteView(TemplateView):
    """View shown after successful registration"""

    template_name = "registration/registration_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": _("Inscription réussie"),
                "page_description": _("Vérifiez votre email pour activer votre compte"),
            }
        )
        return context


class EmailVerificationView(View):
    """View to verify email address"""

    def get(self, request, uidb64, token):
        from django.utils.encoding import force_str
        from django.utils.http import urlsafe_base64_decode

        from core.tokens import email_verification_token

        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and email_verification_token.check_token(user, token):
            # Activate user
            user.is_active = True
            user.save()

            # Create welcome notification
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(user, "profile"):
                langue = user.profile.langue_preferee

            NotificationService.create_welcome_notification(user=user, langue=langue)

            messages.success(
                request,
                _("Votre email a été vérifié avec succès! Vous pouvez maintenant vous connecter."),
            )
            return redirect("core:login")
        else:
            messages.error(
                request,
                _("Le lien de vérification est invalide ou a expiré. Veuillez demander un nouveau lien."),
            )
            return redirect("core:resend_verification")


class ResendVerificationView(View):
    """View to resend verification email"""

    template_name = "registration/resend_verification.html"

    def get(self, request):
        return render(request, self.template_name, {"page_title": _("Renvoyer l'email de vérification")})

    def post(self, request):
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, _("Veuillez saisir votre adresse email"))
            return render(request, self.template_name, {"page_title": _("Renvoyer l'email de vérification")})

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                messages.info(request, _("Ce compte est déjà activé. Vous pouvez vous connecter."))
                return redirect("core:login")

            # Send verification email
            self.send_verification_email(request, user)

            messages.success(
                request,
                _("Un nouvel email de vérification a été envoyé à votre adresse."),
            )
            return redirect("core:registration_complete")

        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(
                request,
                _("Si cette adresse email existe dans notre système, un email de vérification a été envoyé."),
            )
            return redirect("core:registration_complete")

    def send_verification_email(self, request, user):
        """Send email verification link to user"""
        from django.contrib.sites.shortcuts import get_current_site
        from django.template.loader import render_to_string
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from administration.email_utils import send_email
        from core.tokens import email_verification_token

        # Generate verification token
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build verification URL
        current_site = get_current_site(request)
        verification_url = f"http://{current_site.domain}/verify-email/{uid}/{token}/"

        # Prepare email content
        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": "Tax Collector",
        }

        subject = "Vérification de votre compte Tax Collector"
        message = render_to_string("registration/verification_email.txt", context)
        html_message = render_to_string("registration/verification_email.html", context)

        # Send email
        send_email(
            subject=subject,
            message=message,
            recipient_list=[user.email],
            html_message=html_message,
            email_type="verification",
            fail_silently=False,
        )


class SocialAccountManageView(LoginRequiredMixin, TemplateView):
    template_name = "core/social_accounts.html"
    login_url = reverse_lazy("core:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        accounts = SocialAccount.objects.filter(user=user).order_by("provider")
        context.update(
            {
                "accounts": accounts,
                "can_disconnect": user.has_usable_password(),
            }
        )
        return context


class SocialAccountUnlinkView(LoginRequiredMixin, TemplateView):
    template_name = "core/social_account_unlink_confirm.html"
    login_url = reverse_lazy("core:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_usable_password():
            messages.error(
                request,
                _("Vous devez définir un mot de passe avant de délier un compte social."),
            )
            return redirect("account_set_password")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sa_id = self.kwargs.get("pk")
        account = get_object_or_404(SocialAccount, id=sa_id, user=self.request.user)
        context.update({"account": account})
        return context

    def post(self, request, *args, **kwargs):
        sa_id = self.kwargs.get("pk")
        account = get_object_or_404(SocialAccount, id=sa_id, user=request.user)
        confirm = request.POST.get("confirm")
        if confirm == "yes":
            try:
                account.delete()
                messages.success(request, _("Compte social délié avec succès."))
            except Exception as e:
                messages.error(request, _("Échec du délien. Veuillez réessayer."))
        else:
            messages.info(request, _("Délien annulé."))
        return redirect("core:social_accounts")
