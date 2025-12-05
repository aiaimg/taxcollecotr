"""
GDPR-Compliant Serializers for Data Protection APIs
"""

from rest_framework import serializers
from api.models_consent import DataConsent, DataAccessLog, DataDeletionRequest


class DataConsentSerializer(serializers.ModelSerializer):
    """Serializer for data consent"""
    
    consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_valid_flag = serializers.SerializerMethodField()
    
    class Meta:
        model = DataConsent
        fields = [
            'id', 'consent_type', 'consent_type_display', 'status', 'status_display',
            'purpose', 'granted_at', 'revoked_at', 'expires_at',
            'granted_via', 'is_valid_flag'
        ]
        read_only_fields = fields
    
    def get_is_valid_flag(self, obj):
        return obj.is_valid()


class ConsentGrantSerializer(serializers.Serializer):
    """Serializer for granting consent"""
    
    consent_type = serializers.ChoiceField(choices=DataConsent.CONSENT_TYPE_CHOICES)
    purpose = serializers.CharField(max_length=500)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_consent_type(self, value):
        """Validate consent type"""
        valid_types = [choice[0] for choice in DataConsent.CONSENT_TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid consent type. Valid options: {', '.join(valid_types)}")
        return value


class DataAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for data access logs"""
    
    access_type_display = serializers.CharField(source='get_access_type_display', read_only=True)
    accessed_by_username = serializers.CharField(source='accessed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = DataAccessLog
        fields = [
            'id', 'access_type', 'access_type_display', 'data_type',
            'accessed_at', 'accessed_by_username', 'endpoint',
            'consent_verified', 'consent_type'
        ]
        read_only_fields = fields


class DataExportSerializer(serializers.Serializer):
    """Serializer for data export"""
    
    user = serializers.DictField()
    profile = serializers.DictField(allow_null=True)
    vehicles = serializers.ListField(child=serializers.DictField())
    payments = serializers.ListField(child=serializers.DictField())
    qr_codes = serializers.ListField(child=serializers.DictField())
    consents = serializers.ListField(child=serializers.DictField())
    access_logs = serializers.ListField(child=serializers.DictField())
    exported_at = serializers.DateTimeField()


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    """Serializer for data deletion requests"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DataDeletionRequest
        fields = [
            'id', 'requested_at', 'status', 'status_display', 'reason',
            'data_types', 'processed_at', 'rejection_reason'
        ]
        read_only_fields = ['id', 'requested_at', 'status', 'processed_at']
    
    def validate_data_types(self, value):
        """Validate data types"""
        if not value:
            return ['all']
        
        valid_types = ['profile', 'vehicles', 'payments', 'documents', 'all']
        for data_type in value:
            if data_type not in valid_types:
                raise serializers.ValidationError(
                    f"Invalid data type: {data_type}. Valid options: {', '.join(valid_types)}"
                )
        return value
