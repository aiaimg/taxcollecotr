from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from core.models import UserProfile


def is_admin_user(user):
    """Check if user is an admin"""
    if not user.is_authenticated:
        return False
    
    # Check if user is superuser
    if user.is_superuser:
        return True
    
    # Check if user has admin profile
    try:
        profile = user.profile
        return profile.user_type == 'government'
    except UserProfile.DoesNotExist:
        return False


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be an admin.
    Redirects to admin login page if not authenticated or not admin.
    """
    login_url = reverse_lazy('administration:admin_login')
    
    def test_func(self):
        """Test if user is an admin"""
        return is_admin_user(self.request.user)
    
    def handle_no_permission(self):
        """Handle cases where user doesn't have permission"""
        if not self.request.user.is_authenticated:
            # User not logged in - redirect to admin login
            return redirect(self.get_login_url())
        else:
            # User logged in but not admin - show error and redirect to admin login
            messages.error(
                self.request, 
                _('Accès refusé. Seuls les administrateurs peuvent accéder à cette section.')
            )
            # Log out the non-admin user for security
            from django.contrib.auth import logout
            logout(self.request)
            return redirect('administration:admin_login')
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to handle admin access control"""
        if not request.user.is_authenticated:
            return redirect('administration:admin_login')
        
        if not is_admin_user(request.user):
            messages.error(
                request, 
                _('Accès refusé. Seuls les administrateurs peuvent accéder à cette section.')
            )
            # Log out the non-admin user for security
            from django.contrib.auth import logout
            logout(request)
            return redirect('administration:admin_login')
        
        return super().dispatch(request, *args, **kwargs)


class AdminLoginRequiredMixin(LoginRequiredMixin):
    """
    Simple mixin that just redirects to admin login if not authenticated.
    Use this for views that don't need the full admin check.
    """
    login_url = reverse_lazy('administration:admin_login')