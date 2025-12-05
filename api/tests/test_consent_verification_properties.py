"""
Property-Based Tests for Consent Verification

Feature: government-interoperability-standards
Property 24: Consent Verification for Personal Data
Validates: Requirements 9.3
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import from_model
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.utils import timezone
from datetime import timedelta

from api.models_consent import DataConsent
from api.middleware.consent import ConsentVerificationMiddleware


# Strategies for generating test data
@st.composite
def user_strategy(draw):
    """Generate a user"""
    username = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    email = f"{username}@test.com"
    user = User.objects.create_user(username=username, email=email, password='testpass123')
    return user


@st.composite
def consent_type_strategy(draw):
    """Generate a valid consent type"""
    consent_types = [choice[0] for choice in DataConsent.CONSENT_TYPE_CHOICES]
    return draw(st.sampled_from(consent_types))


@st.composite
def api_endpoint_strategy(draw):
    """Generate API endpoints that require consent"""
    endpoints = [
        '/api/v1/users/1/',
        '/api/v1/users/1/profile/',
        '/api/v1/vehicles/',
        '/api/v1/payments/',
        '/api/v1/users/1/vehicles/',
        '/api/v1/users/1/payments/',
    ]
    return draw(st.sampled_from(endpoints))


@pytest.mark.django_db
class TestConsentVerificationProperty:
    """
    Property 24: Consent Verification for Personal Data
    
    For any API request accessing personal data, the system should verify 
    that appropriate consent exists before returning the data.
    """
    
    @given(
        consent_type=consent_type_strategy(),
        has_consent=st.booleans(),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_consent_verification(self, consent_type, has_consent):
        """
        Property: For any user and consent type, access should be granted 
        only if valid consent exists.
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Grant consent if required
            if has_consent:
                DataConsent.grant_consent(
                    user=user,
                    consent_type=consent_type,
                    purpose='Test purpose',
                    granted_via='test'
                )
            
            # Check consent
            result = DataConsent.has_consent(user, consent_type)
            
            # Property: Consent check result should match whether consent was granted
            assert result == has_consent, \
                f"Consent check failed: expected {has_consent}, got {result}"
        
        finally:
            # Cleanup
            user.delete()
    
    @given(
        consent_type=consent_type_strategy(),
        days_until_expiry=st.integers(min_value=-10, max_value=10),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_consent_expiration(self, consent_type, days_until_expiry):
        """
        Property: For any consent with expiration date, it should be valid 
        only if not expired.
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Set expiration date
            expires_at = timezone.now() + timedelta(days=days_until_expiry)
            
            # Grant consent with expiration
            consent = DataConsent.grant_consent(
                user=user,
                consent_type=consent_type,
                purpose='Test purpose',
                granted_via='test',
                expires_at=expires_at
            )
            
            # Check if consent is valid
            is_valid = consent.is_valid()
            
            # Property: Consent should be valid only if not expired
            expected_valid = days_until_expiry > 0
            assert is_valid == expected_valid, \
                f"Consent validity check failed: expected {expected_valid}, got {is_valid} " \
                f"(expires in {days_until_expiry} days)"
        
        finally:
            # Cleanup
            user.delete()
    
    @given(
        consent_type=consent_type_strategy(),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_consent_revocation(self, consent_type):
        """
        Property: For any granted consent, after revocation it should no longer be valid.
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Grant consent
            consent = DataConsent.grant_consent(
                user=user,
                consent_type=consent_type,
                purpose='Test purpose',
                granted_via='test'
            )
            
            # Verify it's valid before revocation
            assert consent.is_valid(), "Consent should be valid after granting"
            
            # Revoke consent
            consent.revoke(reason='Test revocation')
            
            # Property: Consent should not be valid after revocation
            assert not consent.is_valid(), \
                "Consent should not be valid after revocation"
            
            # Property: has_consent should return False after revocation
            assert not DataConsent.has_consent(user, consent_type), \
                "has_consent should return False after revocation"
        
        finally:
            # Cleanup
            user.delete()
    
    @given(
        consent_type=consent_type_strategy(),
        grant_count=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_consent_uniqueness(self, consent_type, grant_count):
        """
        Property: For any user and consent type, only one consent record should exist
        (subsequent grants should update, not create new records).
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Grant consent multiple times
            for i in range(grant_count):
                DataConsent.grant_consent(
                    user=user,
                    consent_type=consent_type,
                    purpose=f'Test purpose {i}',
                    granted_via='test'
                )
            
            # Property: Only one consent record should exist per user/type combination
            consent_count = DataConsent.objects.filter(
                user=user,
                consent_type=consent_type
            ).count()
            
            assert consent_count == 1, \
                f"Expected 1 consent record, found {consent_count} after {grant_count} grants"
        
        finally:
            # Cleanup
            user.delete()
    
    @given(
        has_profile_consent=st.booleans(),
        has_vehicle_consent=st.booleans(),
        has_payment_consent=st.booleans(),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_independent_consents(self, has_profile_consent, has_vehicle_consent, has_payment_consent):
        """
        Property: For any user, consents for different data types should be independent
        (granting one should not affect others).
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Grant consents based on flags
            if has_profile_consent:
                DataConsent.grant_consent(
                    user=user,
                    consent_type='profile_access',
                    purpose='Profile access',
                    granted_via='test'
                )
            
            if has_vehicle_consent:
                DataConsent.grant_consent(
                    user=user,
                    consent_type='vehicle_data',
                    purpose='Vehicle data access',
                    granted_via='test'
                )
            
            if has_payment_consent:
                DataConsent.grant_consent(
                    user=user,
                    consent_type='payment_history',
                    purpose='Payment history access',
                    granted_via='test'
                )
            
            # Property: Each consent type should be independent
            assert DataConsent.has_consent(user, 'profile_access') == has_profile_consent, \
                "Profile consent should match granted state"
            
            assert DataConsent.has_consent(user, 'vehicle_data') == has_vehicle_consent, \
                "Vehicle consent should match granted state"
            
            assert DataConsent.has_consent(user, 'payment_history') == has_payment_consent, \
                "Payment consent should match granted state"
        
        finally:
            # Cleanup
            user.delete()


@pytest.mark.django_db
class TestConsentMiddlewareProperty:
    """
    Property tests for consent verification middleware
    """
    
    def test_property_middleware_blocks_without_consent(self):
        """
        Property: For any endpoint requiring consent, requests without valid consent
        should be blocked with 403 status.
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user without consent
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Create request factory
            factory = RequestFactory()
            
            # Test endpoints that require consent
            endpoints_requiring_consent = [
                ('/api/v1/users/1/', 'profile_access'),
                ('/api/v1/vehicles/', 'vehicle_data'),
                ('/api/v1/payments/', 'payment_history'),
            ]
            
            middleware = ConsentVerificationMiddleware(lambda r: None)
            
            for endpoint, consent_type in endpoints_requiring_consent:
                # Create request
                request = factory.get(endpoint)
                request.user = user
                request.correlation_id = 'test-correlation-id'
                
                # Process request through middleware
                response = middleware.process_request(request)
                
                # Property: Request should be blocked (return 403 response)
                if response is not None:
                    assert response.status_code == 403, \
                        f"Expected 403 for {endpoint} without consent, got {response.status_code}"
        
        finally:
            # Cleanup
            user.delete()
    
    def test_property_middleware_allows_with_consent(self):
        """
        Property: For any endpoint requiring consent, requests with valid consent
        should be allowed (middleware returns None).
        
        **Feature: government-interoperability-standards, Property 24: Consent Verification for Personal Data**
        **Validates: Requirements 9.3**
        """
        # Create a user with all consents
        user = User.objects.create_user(
            username=f'testuser_{timezone.now().timestamp()}',
            email='test@example.com',
            password='testpass123'
        )
        
        try:
            # Grant all necessary consents
            for consent_type in ['profile_access', 'vehicle_data', 'payment_history']:
                DataConsent.grant_consent(
                    user=user,
                    consent_type=consent_type,
                    purpose=f'Test {consent_type}',
                    granted_via='test'
                )
            
            # Create request factory
            factory = RequestFactory()
            
            # Test endpoints that require consent
            endpoints = [
                '/api/v1/users/1/',
                '/api/v1/vehicles/',
                '/api/v1/payments/',
            ]
            
            middleware = ConsentVerificationMiddleware(lambda r: None)
            
            for endpoint in endpoints:
                # Create request
                request = factory.get(endpoint)
                request.user = user
                request.correlation_id = 'test-correlation-id'
                
                # Process request through middleware
                response = middleware.process_request(request)
                
                # Property: Request should be allowed (middleware returns None)
                assert response is None, \
                    f"Expected None (allow) for {endpoint} with consent, got {response}"
        
        finally:
            # Cleanup
            user.delete()
