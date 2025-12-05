# Generated migration for creating maritime vehicle tariff grids

from django.db import migrations
from decimal import Decimal


def create_maritime_tariff_grids(apps, schema_editor):
    """Create the flat rate tariff grids for maritime vehicles"""
    GrilleTarifaire = apps.get_model('vehicles', 'GrilleTarifaire')
    
    # 1. Navire de plaisance (200,000 Ar)
    # Threshold: longueur ≥ 7m OR puissance ≥ 22 CV OR puissance ≥ 90 kW
    GrilleTarifaire.objects.create(
        grid_type='FLAT_MARITIME',
        maritime_category='NAVIRE_PLAISANCE',
        longueur_min_metres=Decimal('7.00'),
        puissance_min_cv_maritime=Decimal('22.00'),
        puissance_min_kw_maritime=Decimal('90.00'),
        montant_ariary=Decimal('200000.00'),
        annee_fiscale=2026,
        est_active=True
    )
    print("✓ Created maritime tariff grid: NAVIRE_PLAISANCE - 200,000 Ar (≥7m or ≥22CV or ≥90kW)")
    
    # 2. Jet-ski/moto nautique (200,000 Ar)
    # Threshold: puissance ≥ 90 kW
    GrilleTarifaire.objects.create(
        grid_type='FLAT_MARITIME',
        maritime_category='JETSKI',
        puissance_min_kw_maritime=Decimal('90.00'),
        montant_ariary=Decimal('200000.00'),
        annee_fiscale=2026,
        est_active=True
    )
    print("✓ Created maritime tariff grid: JETSKI - 200,000 Ar (≥90kW)")
    
    # 3. Autres engins maritimes motorisés (1,000,000 Ar)
    # No thresholds - applies to all other motorized maritime vehicles
    GrilleTarifaire.objects.create(
        grid_type='FLAT_MARITIME',
        maritime_category='AUTRES_ENGINS',
        montant_ariary=Decimal('1000000.00'),
        annee_fiscale=2026,
        est_active=True
    )
    print("✓ Created maritime tariff grid: AUTRES_ENGINS - 1,000,000 Ar (all other motorized maritime vehicles)")


def reverse_maritime_tariff_grids(apps, schema_editor):
    """Remove the maritime tariff grids"""
    GrilleTarifaire = apps.get_model('vehicles', 'GrilleTarifaire')
    
    deleted_count = GrilleTarifaire.objects.filter(
        grid_type='FLAT_MARITIME',
        annee_fiscale=2026
    ).delete()[0]
    print(f"✓ Removed {deleted_count} maritime tariff grids for 2026")


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0015_create_aerial_tariff_grid'),
    ]

    operations = [
        migrations.RunPython(
            create_maritime_tariff_grids,
            reverse_maritime_tariff_grids
        ),
    ]
