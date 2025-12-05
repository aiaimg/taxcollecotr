"""
Data Protection and Consent Management Models

This module implements GDPR-compliant consent tracking and data protection features.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class DataConsent(models.Model):
    """
    Tracks user consent for personal data processing
    
    Implements GDPR Article 7 requirements for consent management.
    """
    
    CONSENT_TYPE_CHOICES = [
        ('profile_access', 'Profile Data Access'),
        ('vehicle_data', 'Vehicle Data Access'),
        ('payment_history', 'Payment History Access'),
        ('location_tracking', 'Location Tracking'),
        ('marketing', 'Marketing Communications'),
        ('data_sharing', 'Data Sharing with Third Parties'),
        ('api_access', 'API Data Access'),
    ]
    
    CONSENT_STATUS_CHOICES = [
        ('granted', 'Granted'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_consents')
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=CONSENT_STATUS_CHOICES, default='granted', db_index=True)
    
    # Consent details
    purpose = models.TextField(help_text="Purpose of data processing")
    granted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")
    
    # Audit trail
    granted_via = models.CharField(max_length=100, help_text="How consent was granted (web, api, mobile)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'api_data_consent'
        verbose_name = 'Data Consent'
        verbose_name_plural = 'Data Consents'
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'consent_type', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
        unique_together = [['user', 'consent_type']]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_consent_type_display()} ({self.status})"
    
    def is_valid(self):
        """Check if consent is currently valid"""
        if self.status != 'granted':
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            # Auto-expire if past expiration date
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        
        return True
    
    def revoke(self, reason=None):
        """Revoke consent"""
        self.status = 'revoked'
        self.revoked_at = timezone.now()
        if reason:
            self.metadata['revocation_reason'] = reason
        self.save(update_fields=['status', 'revoked_at', 'metadata'])
    
    @classmethod
    def has_consent(cls, user, consent_type):
        """Check if user has valid consent for a specific type"""
        try:
            consent = cls.objects.get(user=user, consent_type=consent_type)
            return consent.is_valid()
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def grant_consent(cls, user, consent_type, purpose, granted_via='web', ip_address=None, user_agent='', expires_at=None):
        """Grant or update consent"""
        consent, created = cls.objects.update_or_create(
            user=user,
            consent_type=consent_type,
            defaults={
                'status': 'granted',
                'purpose': purpose,
                'granted_via': granted_via,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at,
                'revoked_at': None,
            }
        )
        return consent


class DataAccessLog(models.Model):
    """
    Logs all access to personal data for GDPR compliance
    
    Implements GDPR Article 30 requirements for records of processing activities.
    """
    
    ACCESS_TYPE_CHOICES = [
        ('read', 'Read'),
        ('export', 'Export'),
        ('modify', 'Modify'),
        ('delete', 'Delete'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_access_logs')
    accessed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='data_accesses_performed',
        help_text="User or system that accessed the data"
    )
    
    # Access details
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, db_index=True)
    data_type = models.CharField(max_length=100, help_text="Type of data accessed (profile, vehicle, payment)")
    accessed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Context
    endpoint = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Consent verification
    consent_verified = models.BooleanField(default=False)
    consent_type = models.CharField(max_length=50, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'api_data_access_log'
        verbose_name = 'Data Access Log'
        verbose_name_plural = 'Data Access Logs'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['accessed_by', 'accessed_at']),
            models.Index(fields=['access_type', 'data_type']),
        ]
    
    def __str__(self):
        return f"{self.access_type} - {self.data_type} - {self.user.username} at {self.accessed_at}"


class DataRetentionPolicy(models.Model):
    """
    Defines data retention policies for different data types
    
    Implements GDPR Article 5(1)(e) - storage limitation principle.
    """
    
    data_type = models.CharField(max_length=100, unique=True, db_index=True)
    retention_days = models.IntegerField(help_text="Number of days to retain data")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Legal basis
    legal_basis = models.TextField(help_text="Legal justification for retention period")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_data_retention_policy'
        verbose_name = 'Data Retention Policy'
        verbose_name_plural = 'Data Retention Policies'
        ordering = ['data_type']
    
    def __str__(self):
        return f"{self.data_type} - {self.retention_days} days"


class DataDeletionRequest(models.Model):
    """
    Tracks GDPR "Right to be Forgotten" deletion requests
    
    Implements GDPR Article 17 - Right to erasure.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deletion_requests')
    
    # Request details
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    reason = models.TextField(blank=True)
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='deletion_requests_processed'
    )
    
    # Data types to delete
    data_types = models.JSONField(
        default=list,
        help_text="List of data types to delete: ['profile', 'vehicles', 'payments']"
    )
    
    # Audit
    deletion_report = models.JSONField(default=dict, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'api_data_deletion_request'
        verbose_name = 'Data Deletion Request'
        verbose_name_plural = 'Data Deletion Requests'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'requested_at']),
        ]
    
    def __str__(self):
        return f"Deletion request for {self.user.username} - {self.status}"
