"""
Cash Audit Service
Handles audit trail management with hash chain and encryption
"""

import hashlib
import json
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

# Try to import cryptography, but make it optional
try:
    from cryptography.fernet import Fernet

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    Fernet = None

from payments.models import (
    CashAuditLog,
    CashSession,
    CashTransaction,
)


class CashAuditService:
    """Service for audit trail management"""

    def __init__(self):
        # Initialize encryption key (should be stored securely in settings)
        # For production, use settings.CASH_AUDIT_ENCRYPTION_KEY
        if ENCRYPTION_AVAILABLE:
            self.encryption_key = getattr(settings, "CASH_AUDIT_ENCRYPTION_KEY", Fernet.generate_key())
            self.cipher = Fernet(self.encryption_key)
        else:
            self.encryption_key = None
            self.cipher = None

    @transaction.atomic
    def log_action(
        self,
        action_type: str,
        user: User,
        data: Dict[str, Any],
        session: Optional[CashSession] = None,
        transaction_obj: Optional[CashTransaction] = None,
        request=None,
    ) -> Optional[CashAuditLog]:
        """
        Create audit log entry with hash chain

        Args:
            action_type: Type of action being logged
            user: User performing the action
            data: Action data to log
            session: Optional related cash session
            transaction_obj: Optional related cash transaction
            request: Optional HTTP request for IP and user agent

        Returns:
            CashAuditLog entry or None
        """
        try:
            # Get previous log entry hash
            previous_hash = CashAuditLog.get_last_hash()

            # Extract IP address and user agent from request
            ip_address = None
            user_agent = ""

            if request:
                # Get IP address
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(",")[0]
                else:
                    ip_address = request.META.get("REMOTE_ADDR")

                # Get user agent
                user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

            # Encrypt sensitive data
            encrypted_data = self._encrypt_data(data)

            # Create audit log entry
            audit_log = CashAuditLog(
                action_type=action_type,
                user=user,
                session=session,
                transaction=transaction_obj,
                action_data=encrypted_data,
                ip_address=ip_address,
                user_agent=user_agent,
                previous_hash=previous_hash,
            )

            # Calculate and set current hash
            audit_log.current_hash = audit_log.calculate_hash()
            audit_log.save()

            return audit_log

        except Exception as e:
            # Log error but don't fail the main operation
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {str(e)}")
            return None

    def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive data fields

        Args:
            data: Data dictionary to encrypt

        Returns:
            Dictionary with encrypted sensitive fields
        """
        # If encryption is not available, return data as-is
        if not ENCRYPTION_AVAILABLE or not self.cipher:
            return data

        # Fields that should be encrypted
        sensitive_fields = [
            "customer_name",
            "vehicle_plate",
            "phone_number",
            "notes",
        ]

        encrypted_data = data.copy()

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                try:
                    # Convert to string and encrypt
                    value_str = str(encrypted_data[field])
                    encrypted_value = self.cipher.encrypt(value_str.encode())
                    encrypted_data[field] = encrypted_value.decode()
                    encrypted_data[f"{field}_encrypted"] = True
                except Exception:
                    # If encryption fails, keep original value
                    pass

        return encrypted_data

    def _decrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive data fields

        Args:
            data: Data dictionary with encrypted fields

        Returns:
            Dictionary with decrypted fields
        """
        # If encryption is not available, return data as-is
        if not ENCRYPTION_AVAILABLE or not self.cipher:
            return data

        decrypted_data = data.copy()

        for key, value in data.items():
            if key.endswith("_encrypted") and value:
                # Get the field name
                field_name = key.replace("_encrypted", "")
                if field_name in decrypted_data:
                    try:
                        # Decrypt the value
                        encrypted_value = decrypted_data[field_name].encode()
                        decrypted_value = self.cipher.decrypt(encrypted_value)
                        decrypted_data[field_name] = decrypted_value.decode()
                    except Exception:
                        # If decryption fails, keep encrypted value
                        pass

        return decrypted_data

    @staticmethod
    def verify_audit_trail(
        start_date: Optional[timezone.datetime] = None, end_date: Optional[timezone.datetime] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Verify integrity of audit trail hash chain

        Args:
            start_date: Optional start date for verification
            end_date: Optional end date for verification

        Returns:
            Tuple of (is_valid, list of tampered entries)
        """
        # Build query
        logs = CashAuditLog.objects.all()

        if start_date:
            logs = logs.filter(timestamp__gte=start_date)

        if end_date:
            logs = logs.filter(timestamp__lte=end_date)

        logs = logs.order_by("timestamp")

        tampered_entries = []
        previous_hash = ""

        for log in logs:
            # Check if previous hash matches
            if log.previous_hash != previous_hash:
                tampered_entries.append(
                    {
                        "log_id": str(log.id),
                        "timestamp": log.timestamp,
                        "action_type": log.action_type,
                        "expected_previous_hash": previous_hash,
                        "actual_previous_hash": log.previous_hash,
                        "error": "Hash chain broken - previous hash mismatch",
                    }
                )

            # Verify current hash
            calculated_hash = log.calculate_hash()
            if log.current_hash != calculated_hash:
                tampered_entries.append(
                    {
                        "log_id": str(log.id),
                        "timestamp": log.timestamp,
                        "action_type": log.action_type,
                        "expected_hash": calculated_hash,
                        "actual_hash": log.current_hash,
                        "error": "Hash mismatch - entry may have been tampered",
                    }
                )

            # Update previous hash for next iteration
            previous_hash = log.current_hash

        is_valid = len(tampered_entries) == 0

        return is_valid, tampered_entries

    def get_audit_trail(self, filters: Optional[Dict[str, Any]] = None, decrypt: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with filters

        Args:
            filters: Optional filters dictionary
            decrypt: Whether to decrypt sensitive data

        Returns:
            List of audit log entries
        """
        # Build query
        logs = CashAuditLog.objects.all()

        if filters:
            # Apply filters
            if "action_type" in filters:
                logs = logs.filter(action_type=filters["action_type"])

            if "user" in filters:
                logs = logs.filter(user=filters["user"])

            if "session" in filters:
                logs = logs.filter(session=filters["session"])

            if "transaction" in filters:
                logs = logs.filter(transaction=filters["transaction"])

            if "start_date" in filters:
                logs = logs.filter(timestamp__gte=filters["start_date"])

            if "end_date" in filters:
                logs = logs.filter(timestamp__lte=filters["end_date"])

        logs = logs.order_by("-timestamp")

        # Convert to list of dictionaries
        audit_trail = []
        for log in logs:
            entry = {
                "id": str(log.id),
                "action_type": log.get_action_type_display(),
                "action_type_code": log.action_type,
                "user": log.user.get_full_name() if log.user else None,
                "user_username": log.user.username if log.user else None,
                "session_number": log.session.session_number if log.session else None,
                "transaction_number": log.transaction.transaction_number if log.transaction else None,
                "action_data": self._decrypt_data(log.action_data) if decrypt else log.action_data,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp,
                "current_hash": log.current_hash,
                "previous_hash": log.previous_hash,
            }
            audit_trail.append(entry)

        return audit_trail

    @staticmethod
    def get_audit_statistics(
        start_date: Optional[timezone.datetime] = None, end_date: Optional[timezone.datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit trail statistics

        Args:
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with audit statistics
        """
        logs = CashAuditLog.objects.all()

        if start_date:
            logs = logs.filter(timestamp__gte=start_date)

        if end_date:
            logs = logs.filter(timestamp__lte=end_date)

        # Count by action type
        action_counts = {}
        for choice in CashAuditLog.ACTION_TYPE_CHOICES:
            action_type = choice[0]
            count = logs.filter(action_type=action_type).count()
            action_counts[choice[1]] = count

        # Count by user
        user_counts = (
            logs.values("user__username", "user__first_name", "user__last_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Get recent activity
        recent_logs = logs.order_by("-timestamp")[:20]

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "total_entries": logs.count(),
            "action_counts": action_counts,
            "top_users": list(user_counts),
            "recent_activity": [
                {
                    "action_type": log.get_action_type_display(),
                    "user": log.user.get_full_name() if log.user else None,
                    "timestamp": log.timestamp,
                }
                for log in recent_logs
            ],
        }

    @staticmethod
    def get_user_activity(
        user: User, start_date: Optional[timezone.datetime] = None, end_date: Optional[timezone.datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for a specific user

        Args:
            user: The user
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of user's audit log entries
        """
        logs = CashAuditLog.objects.filter(user=user)

        if start_date:
            logs = logs.filter(timestamp__gte=start_date)

        if end_date:
            logs = logs.filter(timestamp__lte=end_date)

        logs = logs.order_by("-timestamp")

        activity = []
        for log in logs:
            activity.append(
                {
                    "action_type": log.get_action_type_display(),
                    "session_number": log.session.session_number if log.session else None,
                    "transaction_number": log.transaction.transaction_number if log.transaction else None,
                    "timestamp": log.timestamp,
                    "ip_address": log.ip_address,
                }
            )

        return activity

    @staticmethod
    def export_audit_trail(start_date: timezone.datetime, end_date: timezone.datetime, format: str = "json") -> str:
        """
        Export audit trail for compliance

        Args:
            start_date: Start date
            end_date: End date
            format: Export format ('json' or 'csv')

        Returns:
            Exported data as string
        """
        logs = CashAuditLog.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date).order_by("timestamp")

        if format == "json":
            # Export as JSON
            export_data = []
            for log in logs:
                export_data.append(
                    {
                        "id": str(log.id),
                        "action_type": log.action_type,
                        "user_id": log.user_id,
                        "user_username": log.user.username if log.user else None,
                        "session_id": str(log.session_id) if log.session_id else None,
                        "transaction_id": str(log.transaction_id) if log.transaction_id else None,
                        "action_data": log.action_data,
                        "ip_address": log.ip_address,
                        "timestamp": log.timestamp.isoformat(),
                        "current_hash": log.current_hash,
                        "previous_hash": log.previous_hash,
                    }
                )

            return json.dumps(export_data, indent=2, default=str)

        elif format == "csv":
            # Export as CSV
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(["ID", "Action Type", "User", "Session", "Transaction", "IP Address", "Timestamp", "Hash"])

            # Write data
            for log in logs:
                writer.writerow(
                    [
                        str(log.id),
                        log.get_action_type_display(),
                        log.user.username if log.user else "",
                        log.session.session_number if log.session else "",
                        log.transaction.transaction_number if log.transaction else "",
                        log.ip_address or "",
                        log.timestamp.isoformat(),
                        log.current_hash,
                    ]
                )

            return output.getvalue()

        return ""


# Import Count for aggregation
from django.db.models import Count
