"""
Data Minimization Utilities

Implements GDPR Article 5(1)(c) - data minimization principle.
Ensures only necessary data is exposed in API responses.
"""

from rest_framework import serializers


class MinimalUserSerializer(serializers.Serializer):
    """
    Minimal user serializer that only exposes necessary fields
    
    Use this instead of full UserSerializer when detailed user info is not needed.
    """
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    
    def to_representation(self, instance):
        """Only return id and username"""
        return {
            'id': instance.id,
            'username': instance.username,
        }


class MinimalVehicleSerializer(serializers.Serializer):
    """
    Minimal vehicle serializer for list views
    
    Exposes only essential vehicle information.
    """
    plaque_immatriculation = serializers.CharField(read_only=True)
    type_vehicule = serializers.CharField(source='type_vehicule.nom', read_only=True)
    est_actif = serializers.BooleanField(read_only=True)
    
    def to_representation(self, instance):
        """Only return essential fields"""
        return {
            'plaque_immatriculation': instance.plaque_immatriculation,
            'type_vehicule': instance.type_vehicule.nom if instance.type_vehicule else None,
            'est_actif': instance.est_actif,
        }


class MinimalPaymentSerializer(serializers.Serializer):
    """
    Minimal payment serializer for list views
    
    Exposes only essential payment information without sensitive details.
    """
    id = serializers.IntegerField(read_only=True)
    annee_fiscale = serializers.IntegerField(read_only=True)
    montant_du_ariary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    statut = serializers.CharField(read_only=True)
    date_paiement = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Only return essential fields, exclude sensitive payment details"""
        return {
            'id': instance.id,
            'annee_fiscale': instance.annee_fiscale,
            'montant_du_ariary': str(instance.montant_du_ariary),
            'statut': instance.statut,
            'date_paiement': instance.date_paiement.isoformat() if instance.date_paiement else None,
        }


def minimize_user_data(user_data, context='list'):
    """
    Minimize user data based on context
    
    Args:
        user_data: User data dict
        context: Context of use ('list', 'detail', 'public')
    
    Returns:
        dict: Minimized user data
    """
    if context == 'list':
        # For list views, only return id and username
        return {
            'id': user_data.get('id'),
            'username': user_data.get('username'),
        }
    elif context == 'public':
        # For public views, return even less
        return {
            'id': user_data.get('id'),
        }
    elif context == 'detail':
        # For detail views, return more but still minimize
        return {
            'id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),  # Only if user owns the data
            'full_name': user_data.get('full_name'),
        }
    
    return user_data


def minimize_vehicle_data(vehicle_data, context='list'):
    """
    Minimize vehicle data based on context
    
    Args:
        vehicle_data: Vehicle data dict
        context: Context of use ('list', 'detail', 'public')
    
    Returns:
        dict: Minimized vehicle data
    """
    if context == 'list':
        return {
            'plaque_immatriculation': vehicle_data.get('plaque_immatriculation'),
            'type_vehicule': vehicle_data.get('type_vehicule'),
            'est_actif': vehicle_data.get('est_actif'),
        }
    elif context == 'public':
        # For public views, only return plaque
        return {
            'plaque_immatriculation': vehicle_data.get('plaque_immatriculation'),
        }
    elif context == 'detail':
        # For detail views, exclude sensitive technical specs
        excluded_fields = ['specifications_techniques']
        return {k: v for k, v in vehicle_data.items() if k not in excluded_fields}
    
    return vehicle_data


def minimize_payment_data(payment_data, context='list'):
    """
    Minimize payment data based on context
    
    Args:
        payment_data: Payment data dict
        context: Context of use ('list', 'detail', 'public')
    
    Returns:
        dict: Minimized payment data
    """
    if context == 'list':
        return {
            'id': payment_data.get('id'),
            'annee_fiscale': payment_data.get('annee_fiscale'),
            'montant_du_ariary': payment_data.get('montant_du_ariary'),
            'statut': payment_data.get('statut'),
        }
    elif context == 'public':
        # For public views, only return status
        return {
            'statut': payment_data.get('statut'),
        }
    elif context == 'detail':
        # For detail views, exclude sensitive payment details
        excluded_fields = [
            'stripe_payment_intent_id',
            'billing_email',
            'billing_name',
            'details_paiement',
        ]
        return {k: v for k, v in payment_data.items() if k not in excluded_fields}
    
    return payment_data


def remove_sensitive_fields(data, sensitive_fields=None):
    """
    Remove sensitive fields from data dict
    
    Args:
        data: Data dict
        sensitive_fields: List of field names to remove
    
    Returns:
        dict: Data with sensitive fields removed
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password',
            'nif',
            'numero_nif',
            'tax_id',
            'identity_number',
            'numero_contribuable',
            'stripe_payment_intent_id',
            'stripe_secret',
            'api_key',
            'secret',
        ]
    
    if isinstance(data, dict):
        return {
            k: remove_sensitive_fields(v, sensitive_fields)
            for k, v in data.items()
            if k not in sensitive_fields
        }
    elif isinstance(data, list):
        return [remove_sensitive_fields(item, sensitive_fields) for item in data]
    
    return data


def apply_field_level_permissions(data, user, resource_owner):
    """
    Apply field-level permissions based on user relationship to data
    
    Args:
        data: Data dict
        user: Requesting user
        resource_owner: Owner of the resource
    
    Returns:
        dict: Data with appropriate fields based on permissions
    """
    if user == resource_owner:
        # User owns the data, return all fields
        return data
    elif user.is_staff:
        # Staff can see most fields
        return remove_sensitive_fields(data, ['password', 'api_key', 'secret'])
    else:
        # Other users see minimal data
        return minimize_user_data(data, context='public')


class DataMinimizationMixin:
    """
    Mixin for serializers to apply data minimization
    
    Usage:
        class MySerializer(DataMinimizationMixin, serializers.ModelSerializer):
            minimal_fields = ['id', 'name']  # Fields to include in minimal view
            
            class Meta:
                model = MyModel
                fields = '__all__'
    """
    
    minimal_fields = []
    
    def to_representation(self, instance):
        """Apply data minimization based on context"""
        data = super().to_representation(instance)
        
        # Check if minimal view is requested
        request = self.context.get('request')
        if request and request.query_params.get('view') == 'minimal':
            if self.minimal_fields:
                return {k: v for k, v in data.items() if k in self.minimal_fields}
        
        # Check if user has permission to see all fields
        if request and hasattr(instance, 'proprietaire'):
            if request.user != instance.proprietaire and not request.user.is_staff:
                # Apply minimization for non-owners
                return minimize_vehicle_data(data, context='public')
        
        return data
