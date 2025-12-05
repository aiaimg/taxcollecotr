# Generated migration for multi-vehicle category support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0010_bulkeditoperation_bulkeditchange_fleetimportbatch_and_more'),
    ]

    operations = [
        # Add vehicle_category field to distinguish between terrestrial, aerial, and maritime
        migrations.AddField(
            model_name='vehicule',
            name='vehicle_category',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('TERRESTRE', 'Terrestre'),
                    ('AERIEN', 'Aérien'),
                    ('MARITIME', 'Maritime'),
                ],
                default='TERRESTRE',
                verbose_name='Catégorie de véhicule',
                help_text='Type général du véhicule (terrestre, aérien ou maritime)'
            ),
        ),
        
        # Aerial vehicle specific fields
        migrations.AddField(
            model_name='vehicule',
            name='immatriculation_aerienne',
            field=models.CharField(
                max_length=20,
                null=True,
                blank=True,
                verbose_name="Numéro d'immatriculation aérienne",
                help_text="Ex: 5R-ABC pour Madagascar"
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='masse_maximale_decollage_kg',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name='Masse maximale au décollage (kg)',
                help_text='Masse maximale autorisée au décollage en kilogrammes'
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='numero_serie_aeronef',
            field=models.CharField(
                max_length=100,
                null=True,
                blank=True,
                verbose_name="Numéro de série de l'aéronef",
                help_text="Numéro de série constructeur de l'aéronef"
            ),
        ),
        
        # Maritime vehicle specific fields
        migrations.AddField(
            model_name='vehicule',
            name='numero_francisation',
            field=models.CharField(
                max_length=50,
                null=True,
                blank=True,
                verbose_name='Numéro de francisation',
                help_text='Numéro officiel de francisation du navire'
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='nom_navire',
            field=models.CharField(
                max_length=200,
                null=True,
                blank=True,
                verbose_name='Nom du navire',
                help_text='Nom officiel du navire ou de l\'embarcation'
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='longueur_metres',
            field=models.DecimalField(
                max_digits=6,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Longueur (mètres)',
                help_text='Longueur totale du navire en mètres'
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='tonnage_tonneaux',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Tonnage (tonneaux)',
                help_text='Tonnage du navire en tonneaux'
            ),
        ),
        migrations.AddField(
            model_name='vehicule',
            name='puissance_moteur_kw',
            field=models.DecimalField(
                max_digits=8,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Puissance moteur (kW)',
                help_text='Puissance du moteur en kilowatts'
            ),
        ),
        
        # Add indexes for performance
        migrations.AddIndex(
            model_name='vehicule',
            index=models.Index(fields=['vehicle_category'], name='idx_vehicle_category'),
        ),
        migrations.AddIndex(
            model_name='vehicule',
            index=models.Index(fields=['immatriculation_aerienne'], name='idx_immat_aerienne'),
        ),
        migrations.AddIndex(
            model_name='vehicule',
            index=models.Index(fields=['numero_francisation'], name='idx_francisation'),
        ),
    ]
