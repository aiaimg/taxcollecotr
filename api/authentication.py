"""
API Authentication Backends

Custom authentication backends for API access.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext as _

from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    """
    Authentication backend for API keys
    
    Authenticates requests using X-API-Key header.
    """
    
    keyword = 'X-API-Key'
    
    def authenticate(self, request):
        """
        Authenticate via API key in X-API-Key header
        
        Args:
            request: HTTP request object
        
        Returns:
            tuple: (None, APIKey) if authenticated, None otherwise
        
        Raises:
            AuthenticationFailed: If API key is invalid or expired
        """
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            # No API key provided, let other authentication methods try
            return None
        
        try:
            key_obj = APIKey.objects.select_related('created_by').prefetch_related('permissions').get(
                key=api_key,
                is_active=True
            )
            
            # Check if key is expired
            if key_obj.is_expired():
                raise AuthenticationFailed(_('API key expired'))
            
            # Check IP whitelist if configured
            if key_obj.ip_whitelist:
                client_ip = self.get_client_ip(request)
                if client_ip not in key_obj.ip_whitelist:
                    raise AuthenticationFailed(_('IP address not whitelisted'))
            
            # Update last used timestamp (async to avoid blocking)
            key_obj.update_last_used()
            
            # Return None as user (API keys don't have associated users)
            # and the API key object as auth
            return (None, key_obj)
            
        except APIKey.DoesNotExist:
            raise AuthenticationFailed(_('Invalid API key'))
    
    def authenticate_header(self, request):
        """
        Return authentication header for 401 responses
        """
        return self.keyword
    
    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        
        Handles X-Forwarded-For header for proxied requests.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
