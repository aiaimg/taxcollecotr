# Generated migration for extending GrilleTarifaire to support flat rates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0011_add_multi_vehicle_category_support'),
    ]

    operations = [
        # Add grid_type field to distinguish between progressive and flat rate grids
        migrations.AddField(
            model_name='grilletarifaire',
            name='grid_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('PROGRESSIVE', 'Progressive (Terrestre)'),
                    ('FLAT_AERIAL', 'Forfaitaire Aérien'),
                    ('FLAT_MARITIME', 'Forfaitaire Maritime'),
                ],
                default='PROGRESSIVE',
                verbose_name='Type de grille',
                help_text='Type de grille tarifaire (progressive pour terrestres, forfaitaire pour aériens/maritimes)'
            ),
        ),
        
        # Maritime category field for flat maritime rates
        migrations.AddField(
            model_name='grilletarifaire',
            name='maritime_category',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                choices=[
                    ('NAVIRE_PLAISANCE', 'Navire de plaisance ≥7m ou ≥22CV/90kW'),
                    ('JETSKI', 'Jet-ski/moto nautique ≥90kW'),
                    ('AUTRES_ENGINS', 'Autres engins maritimes motorisés'),
                ],
                verbose_name='Catégorie maritime',
                help_text='Catégorie spécifique pour les véhicules maritimes'
            ),
        ),
        
        # Aerial type field for flat aerial rates
        migrations.AddField(
            model_name='grilletarifaire',
            name='aerial_type',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                choices=[
                    ('ALL', 'Tous types d\'aéronefs'),
                    ('AVION', 'Avion'),
                    ('HELICOPTERE', 'Hélicoptère'),
                    ('DRONE', 'Drone'),
                    ('ULM', 'ULM'),
                    ('PLANEUR', 'Planeur'),
                    ('BALLON', 'Ballon'),
                ],
                verbose_name='Type d\'aéronef',
                help_text='Type spécifique d\'aéronef (ALL pour tous types)'
            ),
        ),
        
        # Maritime threshold fields
        migrations.AddField(
            model_name='grilletarifaire',
            name='longueur_min_metres',
            field=models.DecimalField(
                max_digits=6,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Longueur minimale (mètres)',
                help_text='Seuil de longueur minimale pour cette catégorie maritime'
            ),
        ),
        migrations.AddField(
            model_name='grilletarifaire',
            name='puissance_min_cv_maritime',
            field=models.DecimalField(
                max_digits=8,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Puissance minimale (CV)',
                help_text='Seuil de puissance minimale en CV pour cette catégorie maritime'
            ),
        ),
        migrations.AddField(
            model_name='grilletarifaire',
            name='puissance_min_kw_maritime',
            field=models.DecimalField(
                max_digits=8,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Puissance minimale (kW)',
                help_text='Seuil de puissance minimale en kW pour cette catégorie maritime'
            ),
        ),
        
        # Add indexes for performance
        migrations.AddIndex(
            model_name='grilletarifaire',
            index=models.Index(fields=['grid_type'], name='idx_grid_type'),
        ),
        migrations.AddIndex(
            model_name='grilletarifaire',
            index=models.Index(fields=['maritime_category'], name='idx_maritime_category'),
        ),
        migrations.AddIndex(
            model_name='grilletarifaire',
            index=models.Index(fields=['aerial_type'], name='idx_aerial_type'),
        ),
    ]
