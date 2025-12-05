"""
API Models

Models for API key management, audit logging, webhooks, and versioning.
"""

import secrets
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType



class APIKey(models.Model):
    """
    API Key for system-to-system authentication
    
    Provides secure API access for external systems and partners.
    """
    
    # Identification
    key = models.CharField(
        max_length=128,  # Increased to accommodate tc_ prefix + 48-byte token_urlsafe
        unique=True, 
        db_index=True,
        help_text="Unique API key token"
    )
    name = models.CharField(
        max_length=255, 
        help_text="Descriptive name for the API key"
    )
    organization = models.CharField(
        max_length=255,
        help_text="Organization name"
    )
    contact_email = models.EmailField(
        help_text="Contact email for the API key owner"
    )
    
    # State
    is_active = models.BooleanField(
        default=True, 
        db_index=True,
        help_text="Whether the API key is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_api_keys',
        help_text="User who created this API key"
    )
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Expiration date for the API key"
    )
    last_used_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last time this API key was used"
    )
    
    # Rate limiting
    rate_limit_per_hour = models.IntegerField(
        default=1000,
        help_text="Maximum requests per hour"
    )
    rate_limit_per_day = models.IntegerField(
        default=10000,
        help_text="Maximum requests per day"
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the API key purpose"
    )
    ip_whitelist = models.JSONField(
        default=list, 
        blank=True, 
        help_text="List of allowed IP addresses (empty = all IPs allowed)"
    )
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
    
    def __str__(self):
        return f"{self.name} ({self.organization})"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate key if not provided"""
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_key(cls):
        """Generate a secure API key"""
        return f"tc_{secrets.token_urlsafe(48)}"
    
    def is_expired(self):
        """Check if the API key is expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    def revoke(self, revoked_by=None):
        """
        Revoke the API key immediately
        
        Args:
            revoked_by: User who revoked the key
        """
        self.is_active = False
        self.save(update_fields=['is_active'])
        
        # Log the revocation event
        APIKeyEvent.objects.create(
            api_key=self,
            event_type='REVOKED',
            performed_by=revoked_by,
            details={'revoked_at': timezone.now().isoformat()}
        )
    
    def has_permission(self, resource, scope='read'):
        """
        Check if the API key has permission for a resource and scope
        
        Args:
            resource: Resource name (e.g., 'vehicles', 'payments')
            scope: Permission scope ('read', 'write', 'admin')
        
        Returns:
            bool: True if permission exists
        """
        # Define scope hierarchy: admin > write > read
        scope_hierarchy = {
            'read': ['read', 'write', 'admin'],
            'write': ['write', 'admin'],
            'admin': ['admin']
        }
        
        allowed_scopes = scope_hierarchy.get(scope, [scope])
        
        # Check for wildcard permission
        if self.permissions.filter(resource='*', scope__in=allowed_scopes).exists():
            return True
        
        # Check for specific resource permission
        return self.permissions.filter(
            resource=resource,
            scope__in=allowed_scopes
        ).exists()


class APIKeyPermission(models.Model):
    """
    Permissions associated with an API key
    
    Defines granular access control for API resources.
    """
    
    SCOPE_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read & Write'),
        ('admin', 'Full Admin'),
    ]
    
    RESOURCE_CHOICES = [
        ('vehicles', 'Vehicles'),
        ('payments', 'Payments'),
        ('users', 'Users'),
        ('documents', 'Documents'),
        ('qrcodes', 'QR Codes'),
        ('notifications', 'Notifications'),
        ('contraventions', 'Contraventions'),
        ('*', 'All Resources'),
    ]
    
    api_key = models.ForeignKey(
        APIKey, 
        on_delete=models.CASCADE, 
        related_name='permissions'
    )
    resource = models.CharField(
        max_length=100, 
        choices=RESOURCE_CHOICES,
        help_text="Resource type"
    )
    scope = models.CharField(
        max_length=20, 
        choices=SCOPE_CHOICES,
        help_text="Permission scope"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="User who granted this permission"
    )
    
    class Meta:
        db_table = 'api_key_permissions'
        unique_together = [['api_key', 'resource']]
        verbose_name = 'API Key Permission'
        verbose_name_plural = 'API Key Permissions'
    
    def __str__(self):
        return f"{self.api_key.name} - {self.resource}:{self.scope}"


class APIKeyEvent(models.Model):
    """
    Events related to API keys (creation, revocation, etc.)
    
    Provides audit trail for API key lifecycle.
    """
    
    EVENT_TYPES = [
        ('CREATED', 'Created'),
        ('REVOKED', 'Revoked'),
        ('RENEWED', 'Renewed'),
        ('PERMISSIONS_CHANGED', 'Permissions Changed'),
        ('RATE_LIMIT_CHANGED', 'Rate Limit Changed'),
    ]
    
    api_key = models.ForeignKey(
        APIKey, 
        on_delete=models.CASCADE, 
        related_name='events'
    )
    event_type = models.CharField(
        max_length=50, 
        choices=EVENT_TYPES,
        help_text="Type of event"
    )
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="User who performed the action"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        db_index=True
    )
    details = models.JSONField(
        default=dict,
        help_text="Additional event details"
    )
    
    class Meta:
        db_table = 'api_key_events'
        ordering = ['-timestamp']
        verbose_name = 'API Key Event'
        verbose_name_plural = 'API Key Events'
    
    def __str__(self):
        return f"{self.api_key.name} - {self.event_type} at {self.timestamp}"


class APIAuditLog(models.Model):
    """
    Comprehensive audit log for API requests and responses
    """

    correlation_id = models.CharField(max_length=64, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Request metadata
    endpoint = models.CharField(max_length=512, db_index=True)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField(db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    # Actor
    api_key = models.ForeignKey(
        'APIKey', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')

    # Payloads (masked)
    request_headers = models.JSONField(default=dict, blank=True)
    request_body = models.JSONField(default=dict, blank=True)
    response_body = models.JSONField(default=dict, blank=True)

    # Error details
    error_type = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'api_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} [{self.status_code}] ({self.correlation_id})"


class DataChangeLog(models.Model):
    """
    Data change tracking for create/update/delete operations
    """

    OP_CREATE = 'CREATE'
    OP_UPDATE = 'UPDATE'
    OP_DELETE = 'DELETE'
    OP_CHOICES = [
        (OP_CREATE, 'Create'),
        (OP_UPDATE, 'Update'),
        (OP_DELETE, 'Delete'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    correlation_id = models.CharField(max_length=64, blank=True, db_index=True)
    operation = models.CharField(max_length=10, choices=OP_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    object_repr = models.CharField(max_length=255, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='data_change_logs')
    api_key = models.ForeignKey('APIKey', on_delete=models.SET_NULL, null=True, blank=True, related_name='data_change_logs')

    changed_fields = models.JSONField(default=list, blank=True)
    previous_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'data_change_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['operation']),
            models.Index(fields=['content_type']),
        ]

    def __str__(self):
        return f"{self.operation} {self.content_type}#{self.object_id}"


class WebhookSubscription(models.Model):
    """
    Webhook subscription for external systems

    Stores target URL, subscribed event types and shared secret for HMAC signing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    target_url = models.URLField(max_length=500, help_text="Endpoint to POST webhook events")
    is_active = models.BooleanField(default=True, db_index=True)
    event_types = models.JSONField(default=list, blank=True, help_text="List of event types subscribed")
    secret = models.CharField(max_length=128, help_text="Shared secret for HMAC-SHA256 signature")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "webhook_subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} → {self.target_url}"


class WebhookDelivery(models.Model):
    """
    Webhook delivery attempts and status tracking
    """

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField(default=dict)
    signature = models.CharField(max_length=128, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    attempt_count = models.IntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)

    response_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_deliveries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self):
        return f"{self.subscription.name} [{self.event_type}] #{self.attempt_count} → {self.status}"


class APIVersion(models.Model):
    """
    Track API versions and changelog entries

    Stores semantic version, release timestamp, summary, and detailed changes.
    """

    version = models.CharField(max_length=20, db_index=True)
    released_at = models.DateTimeField(default=timezone.now)
    summary = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=list, blank=True, help_text="List of changes for this release")
    deprecated_endpoints = models.JSONField(default=list, blank=True, help_text="List of endpoint patterns deprecated in this release")
    notify_emails = models.JSONField(default=list, blank=True, help_text="Optional list of recipients to notify")

    class Meta:
        db_table = "api_versions"
        ordering = ["-released_at"]

    def __str__(self):
        return f"API v{self.version} ({self.released_at.isoformat()})"


# Import GDPR/Data Protection models
from api.models_consent import (
    DataConsent,
    DataAccessLog,
    DataRetentionPolicy,
    DataDeletionRequest,
)

# Make them available from api.models
__all__ = [
    'APIKey',
    'APIKeyPermission',
    'APIKeyEvent',
    'APIAuditLog',
    'DataChangeLog',
    'WebhookSubscription',
    'WebhookDelivery',
    'APIVersion',
    'DataConsent',
    'DataAccessLog',
    'DataRetentionPolicy',
    'DataDeletionRequest',
]
