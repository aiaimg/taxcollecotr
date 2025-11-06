from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_pk_to_url_str
from django.contrib.auth import authenticate
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse


def is_admin_user(user):
    """Check if user is admin or staff"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or hasattr(user, 'adminuserprofile')


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom allauth adapter that prevents admin users from logging in via regular login"""
    
    def authenticate(self, request, **credentials):
        """Override authenticate to exclude admin users"""
        user = authenticate(request, **credentials)
        
        if user is not None and is_admin_user(user):
            # Return None to indicate authentication failed
            return None
            
        return user
    
    def login(self, request, user):
        """Override login to add additional checks"""
        if is_admin_user(user):
            messages.error(request, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
            return None
        
        return super().login(request, user)
    
    def get_login_redirect_url(self, request):
        """Redirect to dashboard after login"""
        return reverse('core:velzon_dashboard')