#!/usr/bin/env python
"""
Test script to verify the user detail view fix
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from payments.models import PaiementTaxe

def test_user_detail_queries():
    """Test that the user detail queries work without FieldError"""
    try:
        # Get a user (assuming user with ID 4 exists)
        users = User.objects.all()
        if not users.exists():
            print("No users found in database")
            return False
            
        user = users.first()
        print(f"Testing with user: {user.username} (ID: {user.id})")
        
        # Test the queries that were causing FieldError
        print("Testing PaiementTaxe queries...")
        
        # This should work now
        payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user)
        print(f"Found {payments.count()} payments for user")
        
        # Test the statistics queries
        total_payments = PaiementTaxe.objects.filter(vehicule_plaque__proprietaire=user).count()
        print(f"Total payments: {total_payments}")
        
        paid_payments = PaiementTaxe.objects.filter(
            vehicule_plaque__proprietaire=user,
            statut='PAYE'
        ).count()
        print(f"Paid payments: {paid_payments}")
        
        print("✅ All queries executed successfully - FieldError is fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False

if __name__ == "__main__":
    test_user_detail_queries()