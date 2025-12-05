# Generated migration for creating aerial vehicle tariff grid

from django.db import migrations
from decimal import Decimal


def create_aerial_tariff_grid(apps, schema_editor):
    """Create the flat rate tariff grid for aerial vehicles"""
    GrilleTarifaire = apps.get_model('vehicles', 'GrilleTarifaire')
    
    # Create aerial tariff grid for fiscal year 2026
    # All aircraft types taxed at 2,000,000 Ariary per year
    GrilleTarifaire.objects.create(
        grid_type='FLAT_AERIAL',
        aerial_type='ALL',
        montant_ariary=Decimal('2000000.00'),
        annee_fiscale=2026,
        est_active=True
    )
    print("✓ Created aerial tariff grid: 2,000,000 Ar for all aircraft types (2026)")


def reverse_aerial_tariff_grid(apps, schema_editor):
    """Remove the aerial tariff grid"""
    GrilleTarifaire = apps.get_model('vehicles', 'GrilleTarifaire')
    
    GrilleTarifaire.objects.filter(
        grid_type='FLAT_AERIAL',
        annee_fiscale=2026
    ).delete()
    print("✓ Removed aerial tariff grid for 2026")


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0014_alter_grilletarifaire_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_aerial_tariff_grid,
            reverse_aerial_tariff_grid
        ),
    ]
