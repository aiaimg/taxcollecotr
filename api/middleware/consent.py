"""
Consent Verification Middleware

Implements GDPR-compliant consent verification for personal data endpoints.
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from api.models_consent import DataConsent, DataAccessLog
import re


# Endpoints that require consent verification
CONSENT_REQUIRED_ENDPOINTS = {
    r'^/api/v1/users/\d+/$': 'profile_access',
    r'^/api/v1/users/\d+/profile/$': 'profile_access',
    r'^/api/v1/vehicles/': 'vehicle_data',
    r'^/api/v1/payments/': 'payment_history',
    r'^/api/v1/users/\d+/vehicles/$': 'vehicle_data',
    r'^/api/v1/users/\d+/payments/$': 'payment_history',
}


class ConsentVerificationMiddleware(MiddlewareMixin):
    """
    Middleware to verify user consent before accessing personal data endpoints
    
    Implements GDPR Article 7 - Conditions for consent
    """
    
    def process_request(self, request):
        """Verify consent before processing request"""
        
        # Skip for non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Skip for unauthenticated requests (handled by authentication)
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Skip for safe methods that don't access personal data
        if request.method in ['OPTIONS', 'HEAD']:
            return None
        
        # Check if endpoint requires consent
        consent_type = self._get_required_consent_type(request.path)
        if not consent_type:
            return None
        
        # Verify consent
        if not DataConsent.has_consent(request.user, consent_type):
            return JsonResponse({
                'type': 'https://api.taxcollector.gov.mg/errors/consent_required',
                'title': 'Consent Required',
                'status': 403,
                'detail': f'User consent required for {consent_type}. Please grant consent before accessing this resource.',
                'consent_type': consent_type,
                'correlation_id': getattr(request, 'correlation_id', 'unknown'),
            }, status=403)
        
        # Log data access
        self._log_data_access(request, consent_type)
        
        return None
    
    def _get_required_consent_type(self, path):
        """Determine if path requires consent and what type"""
        for pattern, consent_type in CONSENT_REQUIRED_ENDPOINTS.items():
            if re.match(pattern, path):
                return consent_type
        return None
    
    def _log_data_access(self, request, consent_type):
        """Log access to personal data"""
        try:
            # Determine access type from HTTP method
            access_type_map = {
                'GET': 'read',
                'POST': 'modify',
                'PUT': 'modify',
                'PATCH': 'modify',
                'DELETE': 'delete',
            }
            access_type = access_type_map.get(request.method, 'read')
            
            # Determine data type from consent type
            data_type_map = {
                'profile_access': 'profile',
                'vehicle_data': 'vehicle',
                'payment_history': 'payment',
            }
            data_type = data_type_map.get(consent_type, 'unknown')
            
            DataAccessLog.objects.create(
                user=request.user,
                accessed_by=request.user,
                access_type=access_type,
                data_type=data_type,
                endpoint=request.path,
                ip_address=request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                consent_verified=True,
                consent_type=consent_type,
                metadata={
                    'method': request.method,
                    'correlation_id': getattr(request, 'correlation_id', None),
                }
            )
        except Exception as e:
            # Don't fail the request if logging fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log data access: {str(e)}")
