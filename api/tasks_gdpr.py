"""
Celery Tasks for GDPR Data Protection

Implements automated data retention and deletion policies.
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from api.models_consent import DataRetentionPolicy, DataDeletionRequest, DataAccessLog
from api.models import APIAuditLog
from vehicles.models import DocumentVehicule
from payments.models import PaiementTaxe

logger = logging.getLogger(__name__)


@shared_task
def apply_data_retention_policies():
    """
    Apply data retention policies to delete old data
    
    Runs daily to check and delete data that has exceeded retention period.
    Implements GDPR Article 5(1)(e) - storage limitation.
    """
    logger.info("Starting data retention policy application")
    
    policies = DataRetentionPolicy.objects.filter(is_active=True)
    results = {
        'policies_applied': 0,
        'records_deleted': 0,
        'errors': []
    }
    
    for policy in policies:
        try:
            cutoff_date = timezone.now() - timedelta(days=policy.retention_days)
            deleted_count = 0
            
            if policy.data_type == 'audit_logs':
                # Delete old audit logs (except those required for legal compliance)
                # Keep logs for at least 3 years as per requirements
                if policy.retention_days >= 1095:  # 3 years
                    deleted_count = APIAuditLog.objects.filter(
                        timestamp__lt=cutoff_date
                    ).delete()[0]
            
            elif policy.data_type == 'data_access_logs':
                # Delete old data access logs
                deleted_count = DataAccessLog.objects.filter(
                    accessed_at__lt=cutoff_date
                ).delete()[0]
            
            elif policy.data_type == 'expired_documents':
                # Delete expired vehicle documents
                deleted_count = DocumentVehicule.objects.filter(
                    expiration_date__lt=cutoff_date,
                    expiration_date__isnull=False
                ).delete()[0]
            
            results['policies_applied'] += 1
            results['records_deleted'] += deleted_count
            
            logger.info(
                f"Applied retention policy '{policy.data_type}': "
                f"deleted {deleted_count} records older than {policy.retention_days} days"
            )
            
        except Exception as e:
            error_msg = f"Error applying policy '{policy.data_type}': {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    logger.info(f"Data retention policy application completed: {results}")
    return results


@shared_task
def process_deletion_requests():
    """
    Process pending data deletion requests
    
    Runs daily to process GDPR "Right to be Forgotten" requests.
    Implements GDPR Article 17 - Right to erasure.
    """
    logger.info("Starting deletion request processing")
    
    pending_requests = DataDeletionRequest.objects.filter(
        status='pending'
    ).select_related('user')
    
    results = {
        'processed': 0,
        'failed': 0,
        'errors': []
    }
    
    for request_obj in pending_requests:
        try:
            with transaction.atomic():
                # Update status
                request_obj.status = 'in_progress'
                request_obj.save()
                
                user = request_obj.user
                data_types = request_obj.data_types
                deletion_report = {}
                
                # Delete or anonymize based on data types
                if 'all' in data_types or 'profile' in data_types:
                    # Anonymize user profile
                    user.username = f"deleted_{user.id}_{timezone.now().timestamp()}"
                    user.email = f"deleted_{user.id}@anonymized.local"
                    user.first_name = "Deleted"
                    user.last_name = "User"
                    user.is_active = False
                    user.save()
                    deletion_report['profile'] = 'anonymized'
                
                if 'all' in data_types or 'vehicles' in data_types:
                    # Delete vehicle data
                    from vehicles.models import Vehicule
                    vehicle_count = Vehicule.objects.filter(proprietaire=user).delete()[0]
                    deletion_report['vehicles'] = f'{vehicle_count} deleted'
                
                if 'all' in data_types or 'payments' in data_types:
                    # Anonymize payment data (keep for financial records)
                    payment_count = PaiementTaxe.objects.filter(
                        vehicule_plaque__proprietaire=user
                    ).count()
                    deletion_report['payments'] = f'{payment_count} anonymized'
                
                if 'all' in data_types or 'documents' in data_types:
                    # Delete document files
                    doc_count = DocumentVehicule.objects.filter(
                        vehicule__proprietaire=user
                    ).delete()[0]
                    deletion_report['documents'] = f'{doc_count} deleted'
                
                # Update request status
                request_obj.status = 'completed'
                request_obj.processed_at = timezone.now()
                request_obj.deletion_report = deletion_report
                request_obj.save()
                
                results['processed'] += 1
                logger.info(f"Processed deletion request {request_obj.id} for user {user.username}")
                
        except Exception as e:
            error_msg = f"Error processing deletion request {request_obj.id}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['failed'] += 1
            
            # Update request status to show error
            try:
                request_obj.status = 'pending'  # Reset to pending for retry
                request_obj.save()
            except:
                pass
    
    logger.info(f"Deletion request processing completed: {results}")
    return results


@shared_task
def expire_old_consents():
    """
    Expire consents that have passed their expiration date
    
    Runs daily to check and expire old consents.
    """
    logger.info("Starting consent expiration check")
    
    from api.models_consent import DataConsent
    
    expired_count = DataConsent.objects.filter(
        status='granted',
        expires_at__lt=timezone.now()
    ).update(status='expired')
    
    logger.info(f"Expired {expired_count} consents")
    return {'expired_count': expired_count}


@shared_task
def cleanup_old_access_logs():
    """
    Clean up old data access logs (keep last 2 years)
    
    Runs weekly to prevent database bloat while maintaining compliance.
    """
    logger.info("Starting access log cleanup")
    
    cutoff_date = timezone.now() - timedelta(days=730)  # 2 years
    
    deleted_count = DataAccessLog.objects.filter(
        accessed_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Deleted {deleted_count} old access logs")
    return {'deleted_count': deleted_count}


@shared_task
def generate_data_protection_report():
    """
    Generate monthly data protection compliance report
    
    Runs monthly to provide overview of data protection activities.
    """
    logger.info("Generating data protection report")
    
    from api.models_consent import DataConsent
    
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    report = {
        'period': {
            'start': last_month.isoformat(),
            'end': now.isoformat(),
        },
        'consents': {
            'total_active': DataConsent.objects.filter(status='granted').count(),
            'granted_last_month': DataConsent.objects.filter(
                granted_at__gte=last_month,
                status='granted'
            ).count(),
            'revoked_last_month': DataConsent.objects.filter(
                revoked_at__gte=last_month,
                status='revoked'
            ).count(),
        },
        'access_logs': {
            'total_last_month': DataAccessLog.objects.filter(
                accessed_at__gte=last_month
            ).count(),
            'by_type': {}
        },
        'deletion_requests': {
            'pending': DataDeletionRequest.objects.filter(status='pending').count(),
            'completed_last_month': DataDeletionRequest.objects.filter(
                processed_at__gte=last_month,
                status='completed'
            ).count(),
        },
        'generated_at': now.isoformat(),
    }
    
    # Count access logs by type
    for access_type in ['read', 'export', 'modify', 'delete']:
        count = DataAccessLog.objects.filter(
            accessed_at__gte=last_month,
            access_type=access_type
        ).count()
        report['access_logs']['by_type'][access_type] = count
    
    logger.info(f"Data protection report generated: {report}")
    return report
