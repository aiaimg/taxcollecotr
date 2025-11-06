from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import authenticate
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy


def is_admin_user(user):
    """Check if user is admin or staff"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or hasattr(user, 'adminuserprofile')


class CustomAllauthLoginView(AllauthLoginView):
    """Custom allauth login view that excludes admin users"""
    
    def form_valid(self, form):
        """Override form validation to exclude admin users"""
        # Get the credentials from the form
        login = form.cleaned_data.get('login')
        password = form.cleaned_data.get('password')
        
        # Try to authenticate the user
        user = authenticate(self.request, email=login, password=password)
        if not user:
            # Try with username if email authentication fails
            user = authenticate(self.request, username=login, password=password)
        
        if user is not None:
            # Check if user is an admin
            if is_admin_user(user):
                # Add error message and return form as invalid
                form.add_error(None, _("Utilisateur non trouvé. Veuillez vérifier vos identifiants."))
                return self.form_invalid(form)
        
        # Proceed with normal allauth login process
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        ret = get_next_redirect_url(self.request, None)
        if ret:
            return ret
        return reverse_lazy('core:velzon_dashboard')