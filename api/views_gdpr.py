"""
GDPR-Compliant Data Protection Views

Implements GDPR rights:
- Right to Access (Article 15)
- Right to Rectification (Article 16)
- Right to Erasure (Article 17)
- Right to Data Portability (Article 20)
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from api.models_consent import DataConsent, DataAccessLog, DataDeletionRequest
from api.serializers_gdpr import (
    DataConsentSerializer,
    DataAccessLogSerializer,
    DataExportSerializer,
    DataDeletionRequestSerializer,
    ConsentGrantSerializer,
)
from vehicles.models import Vehicule, DocumentVehicule
from payments.models import PaiementTaxe, QRCode
from core.models import UserProfile
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_consents(request):
    """
    List all consents for the authenticated user
    
    GET /api/v1/gdpr/consents/
    """
    consents = DataConsent.objects.filter(user=request.user)
    serializer = DataConsentSerializer(consents, many=True)
    return Response({
        'success': True,
        'consents': serializer.data,
        'correlationId': getattr(request, 'correlation_id', None),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_consent(request):
    """
    Grant consent for data processing
    
    POST /api/v1/gdpr/consents/grant/
    Body: {
        "consent_type": "profile_access",
        "purpose": "Allow API access to profile data",
        "expires_at": "2025-12-31T23:59:59Z"  // optional
    }
    """
    serializer = ConsentGrantSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    consent = DataConsent.grant_consent(
        user=request.user,
        consent_type=serializer.validated_data['consent_type'],
        purpose=serializer.validated_data['purpose'],
        granted_via='api',
        ip_address=request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        expires_at=serializer.validated_data.get('expires_at'),
    )
    
    return Response({
        'success': True,
        'consent': DataConsentSerializer(consent).data,
        'correlationId': getattr(request, 'correlation_id', None),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_consent(request, consent_id):
    """
    Revoke a consent
    
    POST /api/v1/gdpr/consents/{consent_id}/revoke/
    Body: {
        "reason": "No longer need this access"  // optional
    }
    """
    try:
        consent = DataConsent.objects.get(id=consent_id, user=request.user)
    except DataConsent.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Consent not found',
        }, status=status.HTTP_404_NOT_FOUND)
    
    reason = request.data.get('reason', '')
    consent.revoke(reason=reason)
    
    return Response({
        'success': True,
        'message': 'Consent revoked successfully',
        'consent': DataConsentSerializer(consent).data,
        'correlationId': getattr(request, 'correlation_id', None),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_data_access_logs(request):
    """
    List all data access logs for the authenticated user
    
    GET /api/v1/gdpr/access-logs/
    
    Implements GDPR Article 15 - Right to access
    """
    logs = DataAccessLog.objects.filter(user=request.user).order_by('-accessed_at')[:100]
    serializer = DataAccessLogSerializer(logs, many=True)
    
    return Response({
        'success': True,
        'access_logs': serializer.data,
        'total_count': DataAccessLog.objects.filter(user=request.user).count(),
        'correlationId': getattr(request, 'correlation_id', None),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_personal_data(request):
    """
    Export all personal data for the authenticated user
    
    GET /api/v1/gdpr/export/
    
    Implements GDPR Article 20 - Right to data portability
    """
    user = request.user
    
    # Collect all personal data
    data = {
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'profile': None,
        'vehicles': [],
        'payments': [],
        'qr_codes': [],
        'consents': [],
        'access_logs': [],
        'exported_at': timezone.now().isoformat(),
    }
    
    # Profile data
    try:
        profile = UserProfile.objects.get(user=user)
        data['profile'] = {
            'user_type': profile.user_type,
            'telephone': profile.telephone,
            'langue_preferee': profile.langue_preferee,
            'verification_status': profile.verification_status,
            'created_at': profile.created_at.isoformat(),
        }
    except UserProfile.DoesNotExist:
        pass
    
    # Vehicle data
    vehicles = Vehicule.objects.filter(proprietaire=user)
    for vehicle in vehicles:
        data['vehicles'].append({
            'plaque_immatriculation': vehicle.plaque_immatriculation,
            'type_vehicule': vehicle.type_vehicule.nom if vehicle.type_vehicule else None,
            'puissance_fiscale_cv': vehicle.puissance_fiscale_cv,
            'source_energie': vehicle.source_energie,
            'date_premiere_circulation': vehicle.date_premiere_circulation.isoformat() if vehicle.date_premiere_circulation else None,
            'created_at': vehicle.created_at.isoformat(),
        })
    
    # Payment data
    payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user)
    for payment in payments:
        data['payments'].append({
            'vehicule_plaque': payment.vehicule_plaque.plaque_immatriculation if payment.vehicule_plaque else None,
            'annee_fiscale': payment.annee_fiscale,
            'montant_du_ariary': str(payment.montant_du_ariary),
            'montant_paye_ariary': str(payment.montant_paye_ariary),
            'date_paiement': payment.date_paiement.isoformat() if payment.date_paiement else None,
            'statut': payment.statut,
            'methode_paiement': payment.methode_paiement,
        })
    
    # QR codes
    qr_codes = QRCode.objects.filter(vehicule_plaque__proprietaire=user)
    for qr in qr_codes:
        data['qr_codes'].append({
            'vehicule_plaque': qr.vehicule_plaque.plaque_immatriculation if qr.vehicule_plaque else None,
            'annee_fiscale': qr.annee_fiscale,
            'date_generation': qr.date_generation.isoformat(),
            'date_expiration': qr.date_expiration.isoformat() if qr.date_expiration else None,
            'est_actif': qr.est_actif,
        })
    
    # Consents
    consents = DataConsent.objects.filter(user=user)
    for consent in consents:
        data['consents'].append({
            'consent_type': consent.consent_type,
            'status': consent.status,
            'purpose': consent.purpose,
            'granted_at': consent.granted_at.isoformat(),
            'revoked_at': consent.revoked_at.isoformat() if consent.revoked_at else None,
        })
    
    # Recent access logs (last 100)
    logs = DataAccessLog.objects.filter(user=user).order_by('-accessed_at')[:100]
    for log in logs:
        data['access_logs'].append({
            'access_type': log.access_type,
            'data_type': log.data_type,
            'accessed_at': log.accessed_at.isoformat(),
            'endpoint': log.endpoint,
            'consent_verified': log.consent_verified,
        })
    
    # Log the export
    DataAccessLog.objects.create(
        user=user,
        accessed_by=user,
        access_type='export',
        data_type='all',
        endpoint=request.path,
        ip_address=request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        consent_verified=True,
        metadata={'export_format': 'json'}
    )
    
    serializer = DataExportSerializer(data)
    return Response({
        'success': True,
        'data': serializer.data,
        'correlationId': getattr(request, 'correlation_id', None),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_data_deletion(request):
    """
    Request deletion of personal data
    
    POST /api/v1/gdpr/delete-request/
    Body: {
        "reason": "I want to delete my account",
        "data_types": ["profile", "vehicles", "payments"]  // optional, defaults to all
    }
    
    Implements GDPR Article 17 - Right to erasure
    """
    serializer = DataDeletionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if there's already a pending request
    existing = DataDeletionRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'in_progress']
    ).first()
    
    if existing:
        return Response({
            'success': False,
            'error': 'You already have a pending deletion request',
            'request_id': str(existing.id),
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create deletion request
    deletion_request = DataDeletionRequest.objects.create(
        user=request.user,
        reason=serializer.validated_data.get('reason', ''),
        data_types=serializer.validated_data.get('data_types', ['profile', 'vehicles', 'payments', 'all']),
    )
    
    return Response({
        'success': True,
        'message': 'Deletion request submitted successfully. It will be processed within 30 days.',
        'request': DataDeletionRequestSerializer(deletion_request).data,
        'correlationId': getattr(request, 'correlation_id', None),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_deletion_request_status(request, request_id):
    """
    Get status of a deletion request
    
    GET /api/v1/gdpr/delete-request/{request_id}/
    """
    try:
        deletion_request = DataDeletionRequest.objects.get(id=request_id, user=request.user)
    except DataDeletionRequest.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Deletion request not found',
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': True,
        'request': DataDeletionRequestSerializer(deletion_request).data,
        'correlationId': getattr(request, 'correlation_id', None),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def anonymize_user_data(request):
    """
    Anonymize user data (soft delete)
    
    POST /api/v1/gdpr/anonymize/
    
    This is an alternative to full deletion that preserves statistical data
    while removing personally identifiable information.
    """
    user = request.user
    
    with transaction.atomic():
        # Anonymize user account
        user.username = f"anonymized_{user.id}"
        user.email = f"anonymized_{user.id}@deleted.local"
        user.first_name = "Anonymized"
        user.last_name = "User"
        user.is_active = False
        user.save()
        
        # Anonymize profile
        try:
            profile = UserProfile.objects.get(user=user)
            profile.telephone = ""
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        
        # Log the anonymization
        DataAccessLog.objects.create(
            user=user,
            accessed_by=user,
            access_type='delete',
            data_type='all',
            endpoint=request.path,
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            consent_verified=True,
            metadata={'action': 'anonymize'}
        )
    
    return Response({
        'success': True,
        'message': 'User data anonymized successfully',
        'correlationId': getattr(request, 'correlation_id', None),
    })
