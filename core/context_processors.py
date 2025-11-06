"""
Context processors for the core app
"""

def user_role_context(request):
    """
    Add user role information to template context
    """
    context = {
        'is_admin_user': False,
        'user_type': None,
    }
    
    if request.user.is_authenticated:
        # Check if user is admin or staff
        context['is_admin_user'] = request.user.is_staff or request.user.is_superuser
        
        # Get user type from profile if available
        if hasattr(request.user, 'profile'):
            context['user_type'] = request.user.profile.user_type
        else:
            context['user_type'] = 'individual'  # Default
    
    return context