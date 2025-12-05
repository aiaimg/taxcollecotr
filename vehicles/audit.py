import hashlib

from django.utils import timezone

from .models import FleetAuditLog


def log_action(
    user,
    action_type,
    vehicule=None,
    lot_import=None,
    operation_modification=None,
    donnees_action=None,
    adresse_ip=None,
    agent_utilisateur=None,
):
    data_str = f"{action_type}|{user.id}|{getattr(vehicule, 'plaque_immatriculation', '')}|{getattr(lot_import, 'id', '')}|{getattr(operation_modification, 'id', '')}|{timezone.now().isoformat()}|{donnees_action or {}}"
    current_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
    previous = FleetAuditLog.objects.order_by("-cree_le").first()
    previous_hash = previous.current_hash if previous else ""
    return FleetAuditLog.objects.create(
        action_type=action_type,
        utilisateur=user,
        vehicule=vehicule,
        lot_import=lot_import,
        operation_modification=operation_modification,
        donnees_action=donnees_action or {},
        adresse_ip=adresse_ip,
        agent_utilisateur=agent_utilisateur or "",
        previous_hash=previous_hash,
        current_hash=current_hash,
    )
