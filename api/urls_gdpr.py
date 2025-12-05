"""
URL Configuration for GDPR Data Protection APIs

Implements GDPR-compliant endpoints for data access, modification, and deletion.
"""

from django.urls import path
from api import views_gdpr

app_name = 'gdpr'

urlpatterns = [
    # Consent Management
    path('consents/', views_gdpr.list_consents, name='list-consents'),
    path('consents/grant/', views_gdpr.grant_consent, name='grant-consent'),
    path('consents/<uuid:consent_id>/revoke/', views_gdpr.revoke_consent, name='revoke-consent'),
    
    # Data Access (GDPR Article 15)
    path('access-logs/', views_gdpr.list_data_access_logs, name='access-logs'),
    path('export/', views_gdpr.export_personal_data, name='export-data'),
    
    # Data Deletion (GDPR Article 17)
    path('delete-request/', views_gdpr.request_data_deletion, name='request-deletion'),
    path('delete-request/<uuid:request_id>/', views_gdpr.get_deletion_request_status, name='deletion-status'),
    path('anonymize/', views_gdpr.anonymize_user_data, name='anonymize-data'),
]
