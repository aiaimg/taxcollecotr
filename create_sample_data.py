#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxcollector_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from vehicles.models import GrilleTarifaire

def create_sample_data():
    """Create sample tax grid data for the current year"""
    current_year = timezone.now().year
    
    # Sample tax rates for different vehicle types and power ranges
    tarifs_sample = [
        # Cars - Essence
        {'puissance_min_cv': 1, 'puissance_max_cv': 5, 'source_energie': 'Essence', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 50000},
        {'puissance_min_cv': 6, 'puissance_max_cv': 10, 'source_energie': 'Essence', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 75000},
        {'puissance_min_cv': 11, 'puissance_max_cv': 15, 'source_energie': 'Essence', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 100000},
        {'puissance_min_cv': 16, 'puissance_max_cv': None, 'source_energie': 'Essence', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 150000},
        
        # Cars - Diesel
        {'puissance_min_cv': 1, 'puissance_max_cv': 5, 'source_energie': 'Diesel', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 60000},
        {'puissance_min_cv': 6, 'puissance_max_cv': 10, 'source_energie': 'Diesel', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 85000},
        {'puissance_min_cv': 11, 'puissance_max_cv': 15, 'source_energie': 'Diesel', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 120000},
        {'puissance_min_cv': 16, 'puissance_max_cv': None, 'source_energie': 'Diesel', 'age_min_annees': 0, 'age_max_annees': 5, 'montant_ariary': 180000},
        
        # Electric vehicles (reduced rates)
        {'puissance_min_cv': 1, 'puissance_max_cv': 10, 'source_energie': 'Electrique', 'age_min_annees': 0, 'age_max_annees': None, 'montant_ariary': 25000},
        {'puissance_min_cv': 11, 'puissance_max_cv': None, 'source_energie': 'Electrique', 'age_min_annees': 0, 'age_max_annees': None, 'montant_ariary': 40000},
        
        # Hybrid vehicles
        {'puissance_min_cv': 1, 'puissance_max_cv': 10, 'source_energie': 'Hybride', 'age_min_annees': 0, 'age_max_annees': None, 'montant_ariary': 35000},
        {'puissance_min_cv': 11, 'puissance_max_cv': None, 'source_energie': 'Hybride', 'age_min_annees': 0, 'age_max_annees': None, 'montant_ariary': 55000},
        
        # Older vehicles (higher rates)
        {'puissance_min_cv': 1, 'puissance_max_cv': 10, 'source_energie': 'Essence', 'age_min_annees': 6, 'age_max_annees': None, 'montant_ariary': 80000},
        {'puissance_min_cv': 11, 'puissance_max_cv': None, 'source_energie': 'Essence', 'age_min_annees': 6, 'age_max_annees': None, 'montant_ariary': 120000},
        {'puissance_min_cv': 1, 'puissance_max_cv': 10, 'source_energie': 'Diesel', 'age_min_annees': 6, 'age_max_annees': None, 'montant_ariary': 90000},
        {'puissance_min_cv': 11, 'puissance_max_cv': None, 'source_energie': 'Diesel', 'age_min_annees': 6, 'age_max_annees': None, 'montant_ariary': 140000},
    ]
    
    created_count = 0
    for tarif_data in tarifs_sample:
        tarif_data['annee_fiscale'] = current_year
        tarif_data['est_active'] = True
        
        tarif, created = GrilleTarifaire.objects.get_or_create(**tarif_data)
        if created:
            created_count += 1
    
    print(f"Created {created_count} new tax rates for year {current_year}")
    print("Sample data population completed successfully!")

if __name__ == '__main__':
    create_sample_data()