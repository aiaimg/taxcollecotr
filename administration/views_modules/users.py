"""
User management views for admin console
"""

import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView

from administration.models import AdminUserProfile, PermissionGroup
from core.models import AuditLog, UserProfile
from payments.models import PaiementTaxe
from vehicles.models import Vehicule

from ..decorators import admin_required
from ..mixins import AdminRequiredMixin, is_admin_user


class UserListView(AdminRequiredMixin, ListView):
    """
    Enhanced user list view for admin console
    Displays users with pagination, search, and filters
    """

    model = User
    template_name = "administration/users/list.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        """Get filtered and searched queryset"""
        queryset = (
            User.objects.select_related("profile")
            .prefetch_related("groups", "custom_permission_groups")
            .order_by("-date_joined")
        )

        # Search functionality
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        # Filter by user type
        user_type = self.request.GET.get("user_type")
        if user_type:
            queryset = queryset.filter(profile__user_type=user_type)

        # Filter by verification status
        verification_status = self.request.GET.get("verification_status")
        if verification_status:
            queryset = queryset.filter(profile__verification_status=verification_status)

        # Filter by active status
        is_active = self.request.GET.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(is_active=True)
        elif is_active == "false":
            queryset = queryset.filter(is_active=False)

        # Filter by staff status
        is_staff = self.request.GET.get("is_staff")
        if is_staff == "true":
            queryset = queryset.filter(is_staff=True)
        elif is_staff == "false":
            queryset = queryset.filter(is_staff=False)

        # Sorting
        sort = self.request.GET.get("sort", "-date_joined")
        valid_sorts = [
            "username",
            "-username",
            "email",
            "-email",
            "date_joined",
            "-date_joined",
            "last_login",
            "-last_login",
        ]
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter options
        context["user_type_choices"] = UserProfile.USER_TYPE_CHOICES
        context["verification_status_choices"] = UserProfile.VERIFICATION_STATUS_CHOICES

        # Preserve current filters
        context["search"] = self.request.GET.get("search", "")
        context["selected_user_type"] = self.request.GET.get("user_type", "")
        context["selected_verification_status"] = self.request.GET.get("verification_status", "")
        context["selected_is_active"] = self.request.GET.get("is_active", "")
        context["selected_is_staff"] = self.request.GET.get("is_staff", "")
        context["current_sort"] = self.request.GET.get("sort", "-date_joined")

        # Add statistics
        context["total_users"] = User.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        context["staff_users"] = User.objects.filter(is_staff=True).count()
        context["verified_users"] = User.objects.filter(profile__verification_status="verified").count()

        # Add user type statistics
        context["individual_users"] = User.objects.filter(profile__user_type="individual").count()
        context["company_users"] = User.objects.filter(profile__user_type="company").count()
        context["public_institution_users"] = User.objects.filter(profile__user_type="public_institution").count()
        context["international_organization_users"] = User.objects.filter(
            profile__user_type="international_organization"
        ).count()

        # Legacy statistics (for backward compatibility during migration)
        context["emergency_users"] = 0  # Deprecated: now part of public_institution
        context["government_users"] = 0  # Deprecated: now part of public_institution
        context["law_enforcement_users"] = 0  # Deprecated: now part of public_institution

        return context


@login_required
@admin_required
def user_detail_view(request, user_id):
    """
    Detailed view of a single user
    Shows profile, vehicles, payments, and activity
    """
    user = get_object_or_404(
        User.objects.select_related("profile").prefetch_related("groups", "custom_permission_groups"), id=user_id
    )

    # Get user's vehicles
    vehicles = Vehicule.objects.filter(proprietaire=user).select_related("proprietaire").order_by("-created_at")[:10]

    # Get user's payments
    payments = (
        PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user)
        .select_related("vehicule_plaque")
        .order_by("-created_at")[:10]
    )

    # Get user's recent activity from audit log
    recent_activity = AuditLog.objects.filter(user=user).order_by("-date_action")[:20]

    # Calculate statistics
    total_vehicles = Vehicule.objects.filter(proprietaire=user).count()
    total_payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user).count()
    total_paid = (
        PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user, statut="PAYE").aggregate(total=Count("*"))[
            "total"
        ]
        or 0
    )

    # Get admin profile if exists
    admin_profile = None
    if hasattr(user, "admin_profile"):
        admin_profile = user.admin_profile

    context = {
        "user_obj": user,
        "vehicles": vehicles,
        "payments": payments,
        "recent_activity": recent_activity,
        "total_vehicles": total_vehicles,
        "total_payments": total_payments,
        "total_paid": total_paid,
        "admin_profile": admin_profile,
    }

    return render(request, "administration/users/detail.html", context)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update user information
    """

    model = User
    template_name = "administration/users/form.html"
    fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
    pk_url_kwarg = "user_id"

    def get_success_url(self):
        return f"/administration/users/{self.object.id}/"

    def form_valid(self, form):
        # Log the change
        user = form.save()

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="UPDATE",
            table_concernee="auth_user",
            objet_id=str(user.id),
            adresse_ip=self.get_client_ip(),
        )

        messages.success(self.request, f"User {user.username} updated successfully.")
        return super().form_valid(form)

    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip


@login_required
@admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        was_active = user.is_active
        user.is_active = not user.is_active
        user.save()

        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action="UPDATE",
            table_concernee="auth_user",
            objet_id=str(user.id),
            donnees_avant={"is_active": was_active},
            donnees_apres={"is_active": user.is_active},
            adresse_ip=get_client_ip(request),
        )

        # Create notification for user
        try:
            from notifications.services import NotificationService

            langue = "fr"
            if hasattr(user, "profile"):
                langue = user.profile.langue_preferee

            if user.is_active:
                NotificationService.create_account_reactivated_notification(user=user, langue=langue)
            else:
                NotificationService.create_account_deactivated_notification(user=user, langue=langue)
        except Exception as e:
            # Log error but don't fail the operation
            pass

        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")

        return JsonResponse({"success": True, "is_active": user.is_active})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)


@login_required
@admin_required
def user_activity_stats(request, user_id):
    """Get user activity statistics (AJAX endpoint)"""
    user = get_object_or_404(User, id=user_id)

    # Calculate various statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        "total_logins": AuditLog.objects.filter(user=user, action="LOGIN").count(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "total_vehicles": Vehicule.objects.filter(proprietaire=user).count(),
        "total_payments": PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user).count(),
        "payments_this_week": PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=user, created_at__date__gte=week_ago
        ).count(),
        "payments_this_month": PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=user, created_at__date__gte=month_ago
        ).count(),
        "total_actions": AuditLog.objects.filter(user=user).count(),
    }

    return JsonResponse(stats)


@login_required
@admin_required
def user_permissions_view(request, user_id):
    """
    Manage user permissions and group assignments
    """
    user = get_object_or_404(User.objects.prefetch_related("groups", "custom_permission_groups"), id=user_id)

    # Get all available groups
    django_groups = Group.objects.all()
    custom_groups = PermissionGroup.objects.all()

    if request.method == "POST":
        # Handle permission updates
        action = request.POST.get("action")

        if action == "update_django_groups":
            # Update Django groups
            selected_groups = request.POST.getlist("django_groups")
            user.groups.clear()
            for group_id in selected_groups:
                try:
                    group = Group.objects.get(id=group_id)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

            # Log the change
            AuditLog.objects.create(
                user=request.user,
                action="UPDATE",
                table_concernee="auth_user_groups",
                objet_id=str(user.id),
                adresse_ip=get_client_ip(request),
            )

            messages.success(request, "Django groups updated successfully")

        elif action == "update_custom_groups":
            # Update custom permission groups
            selected_groups = request.POST.getlist("custom_groups")
            user.custom_permission_groups.clear()
            for group_id in selected_groups:
                try:
                    group = PermissionGroup.objects.get(id=group_id)
                    user.custom_permission_groups.add(group)
                except PermissionGroup.DoesNotExist:
                    pass

            # Log the change
            AuditLog.objects.create(
                user=request.user,
                action="UPDATE",
                table_concernee="custom_permission_groups",
                objet_id=str(user.id),
                adresse_ip=get_client_ip(request),
            )

            messages.success(request, "Custom permission groups updated successfully")

        elif action == "toggle_staff":
            user.is_staff = not user.is_staff
            user.save()

            # Log the change
            AuditLog.objects.create(
                user=request.user,
                action="UPDATE",
                table_concernee="auth_user",
                objet_id=str(user.id),
                donnees_avant={"is_staff": not user.is_staff},
                donnees_apres={"is_staff": user.is_staff},
                adresse_ip=get_client_ip(request),
            )

            status = "granted" if user.is_staff else "revoked"
            messages.success(request, f"Staff status {status} successfully")

        elif action == "toggle_superuser":
            user.is_superuser = not user.is_superuser
            user.save()

            # Log the change
            AuditLog.objects.create(
                user=request.user,
                action="UPDATE",
                table_concernee="auth_user",
                objet_id=str(user.id),
                donnees_avant={"is_superuser": not user.is_superuser},
                donnees_apres={"is_superuser": user.is_superuser},
                adresse_ip=get_client_ip(request),
            )

            status = "granted" if user.is_superuser else "revoked"
            messages.success(request, f"Superuser status {status} successfully")

        return redirect("administration:user_permissions", user_id=user.id)

    context = {
        "user_obj": user,
        "django_groups": django_groups,
        "custom_groups": custom_groups,
        "user_django_groups": user.groups.all(),
        "user_custom_groups": user.custom_permission_groups.all(),
    }

    return render(request, "administration/users/permissions.html", context)


@login_required
@admin_required
def reset_user_password(request, user_id):
    """Send password reset email to user"""
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        if not user.email:
            return JsonResponse({"success": False, "error": "User does not have an email address"}, status=400)

        # Generate password reset token and send email
        from django.conf import settings
        from django.contrib.auth.tokens import default_token_generator
        from django.core.mail import send_mail
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset link (adjust domain as needed)
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"

        # Send email
        try:
            send_mail(
                subject="Password Reset Request",
                message=f"Click the following link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action="UPDATE",
                table_concernee="auth_user",
                objet_id=str(user.id),
                adresse_ip=get_client_ip(request),
            )

            return JsonResponse({"success": True, "message": f"Password reset email sent to {user.email}"})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)


@login_required
@admin_required
def user_bulk_operations(request):
    """
    Handle bulk operations on users
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        action = data.get("action")
        user_ids = data.get("items", [])

        if not action or not user_ids:
            return JsonResponse({"success": False, "error": "Missing action or items"}, status=400)

        # Get users
        users = User.objects.filter(id__in=user_ids)
        count = users.count()

        if count == 0:
            return JsonResponse({"success": False, "error": "No users found"}, status=404)

        # Perform action
        if action == "activate":
            users.update(is_active=True)

            # Send notifications
            try:
                from notifications.services import NotificationService

                for user in users:
                    langue = "fr"
                    if hasattr(user, "profile"):
                        langue = user.profile.langue_preferee
                    NotificationService.create_account_reactivated_notification(user=user, langue=langue)
            except Exception:
                pass

            message = f"{count} user(s) activated successfully"

        elif action == "deactivate":
            users.update(is_active=False)

            # Send notifications
            try:
                from notifications.services import NotificationService

                for user in users:
                    langue = "fr"
                    if hasattr(user, "profile"):
                        langue = user.profile.langue_preferee
                    NotificationService.create_account_deactivated_notification(user=user, langue=langue)
            except Exception:
                pass

            message = f"{count} user(s) deactivated successfully"

        elif action == "assign_group":
            group_id = data.get("group_id")
            if not group_id:
                return JsonResponse({"success": False, "error": "Missing group_id"}, status=400)

            try:
                group = PermissionGroup.objects.get(id=group_id)
                for user in users:
                    user.custom_permission_groups.add(group)
                message = f'{count} user(s) assigned to group "{group.name}"'
            except PermissionGroup.DoesNotExist:
                return JsonResponse({"success": False, "error": "Group not found"}, status=404)

        elif action == "send_email":
            subject = data.get("subject", "Message from Administrator")
            body = data.get("body", "")

            if not body:
                return JsonResponse({"success": False, "error": "Email body is required"}, status=400)

            # Send emails
            from django.conf import settings
            from django.core.mail import send_mass_mail

            messages_to_send = []
            for user in users:
                if user.email:
                    messages_to_send.append((subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]))

            try:
                send_mass_mail(messages_to_send, fail_silently=False)
                message = f"Email sent to {len(messages_to_send)} user(s)"
            except Exception as e:
                return JsonResponse({"success": False, "error": f"Failed to send emails: {str(e)}"}, status=500)

        else:
            return JsonResponse({"success": False, "error": "Invalid action"}, status=400)

        # Log the bulk operation
        AuditLog.objects.create(
            user=request.user,
            action="UPDATE",
            table_concernee="auth_user",
            objet_id=f"bulk_{count}_users",
            adresse_ip=get_client_ip(request),
        )

        return JsonResponse({"success": True, "message": message, "count": count})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@admin_required
def user_export(request):
    """
    Export users to CSV or JSON with privacy considerations
    Excludes sensitive fields like passwords and tokens
    """
    export_format = request.GET.get("export", "csv")
    anonymize = request.GET.get("anonymize", "false") == "true"

    # Get filtered queryset (reuse same filters as list view)
    queryset = User.objects.select_related("profile").order_by("-date_joined")

    # Apply filters
    search = request.GET.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    user_type = request.GET.get("user_type")
    if user_type:
        queryset = queryset.filter(profile__user_type=user_type)

    verification_status = request.GET.get("verification_status")
    if verification_status:
        queryset = queryset.filter(profile__verification_status=verification_status)

    is_active = request.GET.get("is_active")
    if is_active == "true":
        queryset = queryset.filter(is_active=True)
    elif is_active == "false":
        queryset = queryset.filter(is_active=False)

    is_staff = request.GET.get("is_staff")
    if is_staff == "true":
        queryset = queryset.filter(is_staff=True)
    elif is_staff == "false":
        queryset = queryset.filter(is_staff=False)

    # Limit to 10,000 records
    queryset = queryset[:10000]

    # Log the export
    AuditLog.objects.create(
        user=request.user,
        action="UPDATE",
        table_concernee="auth_user",
        objet_id=f"export_{export_format}_{queryset.count()}_users",
        adresse_ip=get_client_ip(request),
    )

    if export_format == "csv":
        return export_users_csv(queryset, anonymize)
    elif export_format == "json":
        return export_users_json(queryset, anonymize)
    else:
        return JsonResponse({"error": "Invalid export format"}, status=400)


def export_users_csv(queryset, anonymize=False):
    """Export users to CSV format"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="users_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )

    writer = csv.writer(response)

    # Write header
    headers = [
        "ID",
        "Username",
        "First Name",
        "Last Name",
        "Email",
        "User Type",
        "Verification Status",
        "Is Active",
        "Is Staff",
        "Date Joined",
        "Last Login",
    ]
    writer.writerow(headers)

    # Write data
    for user in queryset:
        if anonymize:
            # Anonymize personal data
            username = f"user_{user.id}"
            first_name = "***"
            last_name = "***"
            email = f"user{user.id}@anonymized.com"
        else:
            username = user.username
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            email = user.email or ""

        user_type = ""
        verification_status = ""
        if hasattr(user, "profile") and user.profile:
            user_type = user.profile.get_user_type_display()
            verification_status = user.profile.get_verification_status_display()

        writer.writerow(
            [
                user.id,
                username,
                first_name,
                last_name,
                email,
                user_type,
                verification_status,
                "Yes" if user.is_active else "No",
                "Yes" if user.is_staff else "No",
                user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never",
            ]
        )

    return response


def export_users_json(queryset, anonymize=False):
    """Export users to JSON format"""
    users_data = []

    for user in queryset:
        if anonymize:
            # Anonymize personal data
            username = f"user_{user.id}"
            first_name = "***"
            last_name = "***"
            email = f"user{user.id}@anonymized.com"
        else:
            username = user.username
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            email = user.email or ""

        user_data = {
            "id": user.id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

        # Add profile data if available
        if hasattr(user, "profile") and user.profile:
            user_data["profile"] = {
                "user_type": user.profile.user_type,
                "verification_status": user.profile.verification_status,
                "langue_preferee": user.profile.langue_preferee,
            }

            # Only include phone if not anonymizing
            if not anonymize:
                user_data["profile"]["telephone"] = user.profile.telephone or ""

        users_data.append(user_data)

    response = HttpResponse(json.dumps(users_data, indent=2), content_type="application/json")
    response["Content-Disposition"] = (
        f'attachment; filename="users_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    )

    return response


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
