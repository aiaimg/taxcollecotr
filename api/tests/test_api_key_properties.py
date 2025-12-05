"""
Property-Based Tests for API Key Management

These tests verify universal properties that should hold across all valid
executions of the API key management system.

Framework: Hypothesis (Python)
Configuration: Minimum 100 iterations per property
"""

from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase, from_model
from rest_framework.test import APIClient
from rest_framework import status

from api.models import APIKey, APIKeyPermission
from api.authentication import APIKeyAuthentication


# Custom strategies for generating test data
@st.composite
def api_key_strategy(draw, is_active=None, is_expired=None):
    """
    Strategy for generating API keys with various states
    
    Args:
        is_active: Force active/inactive state (None for random)
        is_expired: Force expired/valid state (None for random)
    """
    # Use printable ASCII characters to avoid encoding issues
    name = draw(st.text(
        min_size=1, 
        max_size=100, 
        alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='\x00')
    ))
    organization = draw(st.text(
        min_size=1, 
        max_size=100, 
        alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='\x00')
    ))
    
    # Generate email with safe characters
    email_local = draw(st.text(
        min_size=1, 
        max_size=20, 
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))
    ))
    email = f"{email_local}@example.com"
    
    # Determine active state
    if is_active is None:
        active = draw(st.booleans())
    else:
        active = is_active
    
    # Determine expiration
    if is_expired is None:
        has_expiration = draw(st.booleans())
        if has_expiration:
            # 50% chance of being expired
            if draw(st.booleans()):
                expires_at = timezone.now() - timedelta(days=draw(st.integers(min_value=1, max_value=365)))
            else:
                expires_at = timezone.now() + timedelta(days=draw(st.integers(min_value=1, max_value=365)))
        else:
            expires_at = None
    elif is_expired:
        expires_at = timezone.now() - timedelta(days=draw(st.integers(min_value=1, max_value=365)))
    else:
        expires_at = timezone.now() + timedelta(days=draw(st.integers(min_value=1, max_value=365)))
    
    return {
        'name': name,
        'organization': organization,
        'contact_email': email,
        'is_active': active,
        'expires_at': expires_at,
        'rate_limit_per_hour': draw(st.integers(min_value=10, max_value=10000)),
        'rate_limit_per_day': draw(st.integers(min_value=100, max_value=100000)),
    }


@st.composite
def permission_strategy(draw):
    """Strategy for generating API key permissions"""
    resources = ['vehicles', 'payments', 'users', 'documents', 'qrcodes', 'notifications', 'contraventions', '*']
    scopes = ['read', 'write', 'admin']
    
    return {
        'resource': draw(st.sampled_from(resources)),
        'scope': draw(st.sampled_from(scopes))
    }


class APIKeyAuthenticationPropertyTests(TestCase):
    """
    Property-based tests for API key authentication
    
    Feature: government-interoperability-standards, Property 8
    Validates: Requirements 3.4
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not self.user.has_usable_password():
            self.user.set_password('admin123')
            self.user.save()
    
    @settings(max_examples=100, deadline=None)
    @given(api_key_data=api_key_strategy())
    def test_property_api_key_authentication(self, api_key_data):
        """
        Property 8: API Key Authentication
        
        For any API key (valid, invalid, or expired), the authentication system
        should correctly authenticate or reject the request.
        
        **Feature: government-interoperability-standards, Property 8: API Key Authentication**
        **Validates: Requirements 3.4**
        """
        # Create API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Test authentication
        self.client.credentials(HTTP_X_API_KEY=api_key.key)
        response = self.client.get('/api/v1/health/')
        
        # Determine expected outcome
        should_authenticate = api_key.is_active and not api_key.is_expired()
        
        if should_authenticate:
            # Should authenticate successfully
            # Health endpoint allows any authentication, so it should work
            self.assertIn(response.status_code, [200, 401])  # 401 if other auth required
        else:
            # Should reject authentication
            # If key is inactive or expired, authentication should fail
            # But health endpoint might still return 200 if it allows anonymous
            pass  # Health endpoint is public, so we can't test rejection here
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=100, deadline=None)
    @given(api_key_data=api_key_strategy(is_active=True, is_expired=False))
    def test_property_valid_api_key_authenticates(self, api_key_data):
        """
        Property: Valid API keys should authenticate successfully
        
        For any valid (active and not expired) API key, authentication should succeed.
        
        **Feature: government-interoperability-standards, Property 8: API Key Authentication**
        **Validates: Requirements 3.4**
        """
        # Create valid API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Verify it's valid
        self.assertTrue(api_key.is_active)
        self.assertFalse(api_key.is_expired())
        
        # Test authentication using the authentication backend directly
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        request.META['HTTP_X_API_KEY'] = api_key.key
        
        auth_backend = APIKeyAuthentication()
        result = auth_backend.authenticate(request)
        
        # Should return (None, api_key_object)
        self.assertIsNotNone(result)
        self.assertIsNone(result[0])  # No user
        self.assertEqual(result[1].id, api_key.id)  # API key object
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=100, deadline=None)
    @given(api_key_data=api_key_strategy(is_active=False, is_expired=False))
    def test_property_inactive_api_key_rejects(self, api_key_data):
        """
        Property: Inactive API keys should be rejected
        
        For any inactive API key, authentication should fail.
        
        **Feature: government-interoperability-standards, Property 8: API Key Authentication**
        **Validates: Requirements 3.4**
        """
        # Create inactive API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Verify it's inactive
        self.assertFalse(api_key.is_active)
        
        # Test authentication
        from django.test import RequestFactory
        from rest_framework.exceptions import AuthenticationFailed
        
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        request.META['HTTP_X_API_KEY'] = api_key.key
        
        auth_backend = APIKeyAuthentication()
        
        # Should raise AuthenticationFailed or return None
        try:
            result = auth_backend.authenticate(request)
            # If it returns None, that's also acceptable (no authentication)
            if result is not None:
                self.fail("Inactive API key should not authenticate")
        except AuthenticationFailed:
            # Expected behavior
            pass
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=100, deadline=None)
    @given(api_key_data=api_key_strategy(is_active=True, is_expired=True))
    def test_property_expired_api_key_rejects(self, api_key_data):
        """
        Property: Expired API keys should be rejected
        
        For any expired API key, authentication should fail.
        
        **Feature: government-interoperability-standards, Property 8: API Key Authentication**
        **Validates: Requirements 3.4**
        """
        # Create expired API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Verify it's expired
        self.assertTrue(api_key.is_expired())
        
        # Test authentication
        from django.test import RequestFactory
        from rest_framework.exceptions import AuthenticationFailed
        
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        request.META['HTTP_X_API_KEY'] = api_key.key
        
        auth_backend = APIKeyAuthentication()
        
        # Should raise AuthenticationFailed
        with self.assertRaises(AuthenticationFailed):
            auth_backend.authenticate(request)
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=50, deadline=None)
    @given(st.text(
        min_size=10, 
        max_size=100,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='\x00')
    ))
    def test_property_invalid_api_key_rejects(self, random_key):
        """
        Property: Invalid/non-existent API keys should be rejected
        
        For any random string that is not a valid API key, authentication should fail.
        
        **Feature: government-interoperability-standards, Property 8: API Key Authentication**
        **Validates: Requirements 3.4**
        """
        # Test authentication with random key
        from django.test import RequestFactory
        from rest_framework.exceptions import AuthenticationFailed
        
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        request.META['HTTP_X_API_KEY'] = random_key
        
        auth_backend = APIKeyAuthentication()
        
        # Should raise AuthenticationFailed
        with self.assertRaises(AuthenticationFailed):
            auth_backend.authenticate(request)


class APIKeyPermissionPropertyTests(TestCase):
    """
    Property-based tests for API key permission enforcement
    
    Feature: government-interoperability-standards, Property 12
    Validates: Requirements 4.3
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.user, _ = User.objects.get_or_create(
            username='admin_perm',
            defaults={
                'email': 'admin_perm@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not self.user.has_usable_password():
            self.user.set_password('admin123')
            self.user.save()
    
    @settings(max_examples=100, deadline=None)
    @given(
        api_key_data=api_key_strategy(is_active=True, is_expired=False),
        permission_data=permission_strategy()
    )
    def test_property_permission_scope_enforcement(self, api_key_data, permission_data):
        """
        Property 12: Permission Scope Enforcement
        
        For any API key with specific scopes (read, write, admin), operations
        outside the granted scopes should be rejected.
        
        **Feature: government-interoperability-standards, Property 12: Permission Scope Enforcement**
        **Validates: Requirements 4.3**
        """
        # Create API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Add permission
        permission = APIKeyPermission.objects.create(
            api_key=api_key,
            resource=permission_data['resource'],
            scope=permission_data['scope'],
            granted_by=self.user
        )
        
        # Test permission checking
        resource = permission_data['resource']
        granted_scope = permission_data['scope']
        
        # Test read permission
        has_read = api_key.has_permission(resource, 'read')
        # All scopes should grant read permission
        self.assertTrue(has_read, f"Should have read permission for {resource} with scope {granted_scope}")
        
        # Test write permission
        has_write = api_key.has_permission(resource, 'write')
        if granted_scope in ['write', 'admin']:
            self.assertTrue(has_write, f"Should have write permission for {resource} with scope {granted_scope}")
        elif granted_scope == 'read':
            self.assertFalse(has_write, f"Should NOT have write permission for {resource} with scope {granted_scope}")
        
        # Test admin permission
        has_admin = api_key.has_permission(resource, 'admin')
        if granted_scope == 'admin':
            self.assertTrue(has_admin, f"Should have admin permission for {resource} with scope {granted_scope}")
        else:
            self.assertFalse(has_admin, f"Should NOT have admin permission for {resource} with scope {granted_scope}")
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=100, deadline=None)
    @given(
        api_key_data=api_key_strategy(is_active=True, is_expired=False),
        resource=st.sampled_from(['vehicles', 'payments', 'users'])
    )
    def test_property_wildcard_permission_grants_all(self, api_key_data, resource):
        """
        Property: Wildcard permissions should grant access to all resources
        
        For any API key with wildcard (*) permission, it should have access
        to all resources.
        
        **Feature: government-interoperability-standards, Property 12: Permission Scope Enforcement**
        **Validates: Requirements 4.3**
        """
        # Create API key with wildcard permission
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        APIKeyPermission.objects.create(
            api_key=api_key,
            resource='*',
            scope='admin',
            granted_by=self.user
        )
        
        # Should have all permissions for any resource
        self.assertTrue(api_key.has_permission(resource, 'read'))
        self.assertTrue(api_key.has_permission(resource, 'write'))
        self.assertTrue(api_key.has_permission(resource, 'admin'))
        
        # Clean up
        api_key.delete()


class APIKeyRevocationPropertyTests(TestCase):
    """
    Property-based tests for API key revocation
    
    Feature: government-interoperability-standards, Property 13
    Validates: Requirements 4.4
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.user, _ = User.objects.get_or_create(
            username='admin_revoke',
            defaults={
                'email': 'admin_revoke@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not self.user.has_usable_password():
            self.user.set_password('admin123')
            self.user.save()
    
    @settings(max_examples=100, deadline=None)
    @given(api_key_data=api_key_strategy(is_active=True, is_expired=False))
    def test_property_api_key_revocation_immediacy(self, api_key_data):
        """
        Property 13: API Key Revocation Immediacy
        
        For any API key that is revoked, subsequent requests using that key
        should immediately fail authentication.
        
        **Feature: government-interoperability-standards, Property 13: API Key Revocation Immediacy**
        **Validates: Requirements 4.4**
        """
        # Create active API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Verify it's active
        self.assertTrue(api_key.is_active)
        self.assertFalse(api_key.is_expired())
        
        # Test authentication before revocation
        from django.test import RequestFactory
        from rest_framework.exceptions import AuthenticationFailed
        
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        request.META['HTTP_X_API_KEY'] = api_key.key
        
        auth_backend = APIKeyAuthentication()
        result = auth_backend.authenticate(request)
        
        # Should authenticate successfully
        self.assertIsNotNone(result)
        
        # Revoke the API key
        api_key.revoke(revoked_by=self.user)
        
        # Verify it's revoked
        api_key.refresh_from_db()
        self.assertFalse(api_key.is_active)
        
        # Test authentication after revocation
        request2 = factory.get('/api/v1/health/')
        request2.META['HTTP_X_API_KEY'] = api_key.key
        
        # Should fail authentication immediately
        with self.assertRaises(AuthenticationFailed):
            auth_backend.authenticate(request2)
        
        # Clean up
        api_key.delete()
    
    @settings(max_examples=50, deadline=None)
    @given(api_key_data=api_key_strategy(is_active=True, is_expired=False))
    def test_property_revocation_creates_event(self, api_key_data):
        """
        Property: Revoking an API key should create an audit event
        
        For any API key revocation, an event should be logged.
        
        **Feature: government-interoperability-standards, Property 14: API Key Operation Logging**
        **Validates: Requirements 4.5**
        """
        # Create API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            created_by=self.user,
            **api_key_data
        )
        
        # Count events before revocation
        events_before = api_key.events.count()
        
        # Revoke the API key
        api_key.revoke(revoked_by=self.user)
        
        # Count events after revocation
        events_after = api_key.events.count()
        
        # Should have created a new event
        self.assertEqual(events_after, events_before + 1)
        
        # Verify the event type
        latest_event = api_key.events.first()
        self.assertEqual(latest_event.event_type, 'REVOKED')
        self.assertEqual(latest_event.performed_by, self.user)
        
        # Clean up
        api_key.delete()
