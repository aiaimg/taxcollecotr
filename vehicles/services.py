"""
Vehicle tax calculation services
"""
from decimal import Decimal
from django.utils import timezone
from .models import GrilleTarifaire


class TaxCalculationService:
    """Service for calculating vehicle taxes"""
    
    def calculate_tax(self, vehicule, year=None):
        """
        Calculate tax information for a vehicle
        
        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)
            
        Returns:
            dict: Tax calculation information
        """
        if year is None:
            year = timezone.now().year
            
        # Check if vehicle is exempt
        if vehicule.est_exonere():
            return {
                'is_exempt': True,
                'amount': Decimal('0.00'),
                'exemption_reason': 'Véhicule exonéré',
                'year': year,
                'grid': None
            }
        
        # Find applicable tax grid
        try:
            tax_grids = GrilleTarifaire.objects.filter(
                annee_fiscale=year,
                est_active=True
            ).order_by('puissance_min_cv')
            
            applicable_grid = None
            for grid in tax_grids:
                if grid.est_applicable(vehicule):
                    applicable_grid = grid
                    break
            
            if applicable_grid:
                return {
                    'is_exempt': False,
                    'amount': applicable_grid.montant_ariary,
                    'exemption_reason': None,
                    'year': year,
                    'grid': applicable_grid
                }
            else:
                return {
                    'is_exempt': False,
                    'amount': None,
                    'exemption_reason': None,
                    'year': year,
                    'grid': None,
                    'error': 'Aucune grille tarifaire applicable trouvée'
                }
                
        except Exception as e:
            return {
                'is_exempt': False,
                'amount': None,
                'exemption_reason': None,
                'year': year,
                'grid': None,
                'error': f'Erreur lors du calcul: {str(e)}'
            }
    
    def get_tax_breakdown(self, vehicule, year=None):
        """
        Get detailed tax breakdown for a vehicle
        
        Args:
            vehicule: Vehicule instance
            year: Tax year (defaults to current year)
            
        Returns:
            dict: Detailed tax breakdown
        """
        tax_info = self.calculate_tax(vehicule, year)
        
        breakdown = {
            'vehicle_info': {
                'plaque': vehicule.plaque_immatriculation,
                'puissance_fiscale': vehicule.puissance_fiscale_cv,
                'source_energie': vehicule.get_source_energie_display(),
                'age': vehicule.get_age_annees(),
                'categorie': vehicule.get_categorie_vehicule_display(),
            },
            'tax_info': tax_info
        }
        
        if tax_info.get('grid'):
            grid = tax_info['grid']
            breakdown['grid_info'] = {
                'puissance_min': grid.puissance_fiscale_min,
                'puissance_max': grid.puissance_fiscale_max,
                'age_min': grid.age_vehicule_min,
                'age_max': grid.age_vehicule_max,
                'source_energie': grid.source_energie,
                'montant': grid.montant_ariary,
            }
        
        return breakdown