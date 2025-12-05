"""
Data Anonymization Utilities

Provides utilities for anonymizing personal data while preserving statistical value.
Implements GDPR-compliant data anonymization techniques.
"""

import hashlib
import random
import string
from datetime import datetime, timedelta


def anonymize_email(email):
    """
    Anonymize email address while preserving domain for statistics
    
    Example: john.doe@example.com -> anon_a1b2c3@example.com
    """
    if not email or '@' not in email:
        return "anonymized@deleted.local"
    
    local, domain = email.split('@', 1)
    # Create deterministic hash of local part
    hash_obj = hashlib.md5(local.encode())
    hash_str = hash_obj.hexdigest()[:8]
    
    return f"anon_{hash_str}@{domain}"


def anonymize_phone(phone):
    """
    Anonymize phone number while preserving country code
    
    Example: +261340123456 -> +261XXXXXXXX
    """
    if not phone:
        return ""
    
    # Keep country code, anonymize rest
    if phone.startswith('+'):
        country_code = phone[:4]  # e.g., +261
        return f"{country_code}{'X' * (len(phone) - 4)}"
    
    return 'X' * len(phone)


def anonymize_name(name):
    """
    Anonymize name while preserving first letter for statistics
    
    Example: John Doe -> J*** D***
    """
    if not name:
        return "Anonymized"
    
    parts = name.split()
    anonymized_parts = []
    
    for part in parts:
        if len(part) > 0:
            anonymized_parts.append(part[0] + '*' * (len(part) - 1))
    
    return ' '.join(anonymized_parts) if anonymized_parts else "Anonymized"


def anonymize_nif(nif):
    """
    Anonymize NIF (tax ID) completely
    
    Example: 1234567890123 -> ***********
    """
    if not nif:
        return ""
    
    return '*' * len(str(nif))


def anonymize_address(address):
    """
    Anonymize address while preserving city/region for statistics
    
    Example: 123 Main St, Antananarivo -> [REDACTED], Antananarivo
    """
    if not address:
        return ""
    
    # Try to preserve last part (usually city)
    parts = address.split(',')
    if len(parts) > 1:
        city = parts[-1].strip()
        return f"[REDACTED], {city}"
    
    return "[REDACTED]"


def anonymize_date_of_birth(dob, preserve_year=True):
    """
    Anonymize date of birth while optionally preserving year for age statistics
    
    Example: 1990-05-15 -> 1990-01-01 (if preserve_year=True)
    """
    if not dob:
        return None
    
    if isinstance(dob, str):
        try:
            dob = datetime.fromisoformat(dob.replace('Z', '+00:00'))
        except:
            return None
    
    if preserve_year:
        # Set to January 1st of the same year
        return dob.replace(month=1, day=1)
    
    # Completely anonymize
    return None


def anonymize_ip_address(ip):
    """
    Anonymize IP address while preserving network prefix
    
    Example: 192.168.1.100 -> 192.168.0.0
    """
    if not ip:
        return ""
    
    if ':' in ip:  # IPv6
        parts = ip.split(':')
        return ':'.join(parts[:4]) + '::0'
    else:  # IPv4
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.0.0"
    
    return "0.0.0.0"


def generate_pseudonym(original_value, salt='taxcollector'):
    """
    Generate a consistent pseudonym for a value using hashing
    
    This allows linking records while preventing identification.
    """
    if not original_value:
        return ""
    
    hash_obj = hashlib.sha256(f"{salt}{original_value}".encode())
    return f"pseudo_{hash_obj.hexdigest()[:16]}"


def anonymize_user_profile(user):
    """
    Anonymize a user profile completely
    
    Args:
        user: Django User object
    
    Returns:
        dict: Anonymization report
    """
    report = {
        'user_id': user.id,
        'original_username': user.username,
        'anonymized_at': datetime.now().isoformat(),
        'fields_anonymized': []
    }
    
    # Anonymize username
    user.username = f"deleted_user_{user.id}"
    report['fields_anonymized'].append('username')
    
    # Anonymize email
    if user.email:
        user.email = anonymize_email(user.email)
        report['fields_anonymized'].append('email')
    
    # Anonymize names
    if user.first_name:
        user.first_name = anonymize_name(user.first_name)
        report['fields_anonymized'].append('first_name')
    
    if user.last_name:
        user.last_name = anonymize_name(user.last_name)
        report['fields_anonymized'].append('last_name')
    
    # Deactivate account
    user.is_active = False
    report['fields_anonymized'].append('is_active')
    
    user.save()
    
    return report


def anonymize_vehicle_data(vehicle):
    """
    Anonymize vehicle data while preserving statistical value
    
    Args:
        vehicle: Vehicule object
    
    Returns:
        dict: Anonymization report
    """
    report = {
        'vehicle_id': vehicle.plaque_immatriculation,
        'anonymized_at': datetime.now().isoformat(),
        'fields_anonymized': []
    }
    
    # Keep technical data for statistics, remove identifying info
    # Plaque is kept as it's the primary key, but owner is removed
    
    # Clear specifications that might contain personal info
    if vehicle.specifications_techniques:
        vehicle.specifications_techniques = {}
        report['fields_anonymized'].append('specifications_techniques')
    
    vehicle.save()
    
    return report


def k_anonymize_dataset(queryset, k=5, quasi_identifiers=None):
    """
    Apply k-anonymity to a dataset
    
    K-anonymity ensures that each record is indistinguishable from at least k-1 other records
    with respect to quasi-identifiers.
    
    Args:
        queryset: Django queryset
        k: Minimum group size
        quasi_identifiers: List of field names that are quasi-identifiers
    
    Returns:
        list: Anonymized records
    """
    if not quasi_identifiers:
        quasi_identifiers = []
    
    # Group records by quasi-identifiers
    groups = {}
    for record in queryset:
        key = tuple(getattr(record, field, None) for field in quasi_identifiers)
        if key not in groups:
            groups[key] = []
        groups[key].append(record)
    
    # Filter out groups smaller than k
    anonymized = []
    for group in groups.values():
        if len(group) >= k:
            anonymized.extend(group)
    
    return anonymized


def differential_privacy_noise(value, epsilon=1.0, sensitivity=1.0):
    """
    Add Laplace noise for differential privacy
    
    Args:
        value: Original numeric value
        epsilon: Privacy parameter (smaller = more privacy)
        sensitivity: Sensitivity of the query
    
    Returns:
        float: Noisy value
    """
    import numpy as np
    
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    
    return value + noise


def aggregate_with_privacy(queryset, field, epsilon=1.0):
    """
    Compute aggregate statistics with differential privacy
    
    Args:
        queryset: Django queryset
        field: Field to aggregate
        epsilon: Privacy parameter
    
    Returns:
        dict: Noisy statistics
    """
    from django.db.models import Count, Avg, Sum
    
    # Compute true statistics
    stats = queryset.aggregate(
        count=Count(field),
        avg=Avg(field),
        sum=Sum(field)
    )
    
    # Add noise for privacy
    return {
        'count': int(differential_privacy_noise(stats['count'] or 0, epsilon)),
        'avg': differential_privacy_noise(stats['avg'] or 0, epsilon),
        'sum': differential_privacy_noise(stats['sum'] or 0, epsilon),
    }
