from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
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


class AdminLoginView(auth_views.LoginView):
    """Custom admin login view with admin-specific validation"""
    template_name = 'administration/auth/admin_login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('administration:dashboard')
    
    def form_valid(self, form):
        """Validate that the user is an admin before logging in"""
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if is_admin_user(user):
                login(self.request, user)
                messages.success(self.request, _('Connexion administrateur réussie'))
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, _('Accès refusé. Seuls les administrateurs peuvent accéder à cette section.'))
                return self.form_invalid(form)
        else:
            messages.error(self.request, _('Nom d\'utilisateur ou mot de passe incorrect'))
            return self.form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect already authenticated admin users"""
        if request.user.is_authenticated and is_admin_user(request.user):
            return redirect(self.get_success_url())
        elif request.user.is_authenticated and not is_admin_user(request.user):
            messages.warning(request, _('Vous devez vous connecter avec un compte administrateur'))
            # Log out the non-admin user
            from django.contrib.auth import logout
            logout(request)
        
        return super().dispatch(request, *args, **kwargs)


class AdminLogoutView(LoginRequiredMixin, TemplateView):
    """Custom admin logout view"""
    template_name = 'administration/auth/admin_logout.html'
    
    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, _('Déconnexion administrateur réussie'))
        return render(request, self.template_name)


@login_required
def admin_required_view(request):
    """View to check admin access and redirect appropriately"""
    if is_admin_user(request.user):
        return redirect('administration:dashboard')
    else:
        messages.error(request, _('Accès refusé. Seuls les administrateurs peuvent accéder à cette section.'))
        return redirect('administration:admin_login')