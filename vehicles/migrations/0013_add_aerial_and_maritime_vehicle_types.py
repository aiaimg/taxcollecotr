# Generated migration for adding aerial and maritime vehicle types

from django.db import migrations


def create_aerial_vehicle_types(apps, schema_editor):
    """Create aerial vehicle types"""
    VehicleType = apps.get_model('vehicles', 'VehicleType')
    
    aerial_types = [
        {
            'nom': 'Avion',
            'description': 'Aéronef à voilure fixe',
            'ordre_affichage': 100,
            'est_actif': True
        },
        {
            'nom': 'Hélicoptère',
            'description': 'Aéronef à voilure tournante',
            'ordre_affichage': 101,
            'est_actif': True
        },
        {
            'nom': 'Drone',
            'description': 'Aéronef sans pilote (UAV)',
            'ordre_affichage': 102,
            'est_actif': True
        },
        {
            'nom': 'ULM',
            'description': 'Ultra-léger motorisé',
            'ordre_affichage': 103,
            'est_actif': True
        },
        {
            'nom': 'Planeur',
            'description': 'Aéronef sans moteur',
            'ordre_affichage': 104,
            'est_actif': True
        },
        {
            'nom': 'Ballon',
            'description': 'Aérostat (montgolfière, dirigeable)',
            'ordre_affichage': 105,
            'est_actif': True
        },
    ]
    
    for type_data in aerial_types:
        VehicleType.objects.get_or_create(
            nom=type_data['nom'],
            defaults=type_data
        )


def create_maritime_vehicle_types(apps, schema_editor):
    """Create maritime vehicle types"""
    VehicleType = apps.get_model('vehicles', 'VehicleType')
    
    maritime_types = [
        {
            'nom': 'Bateau de plaisance',
            'description': 'Embarcation de loisir (≥7m ou ≥22CV/90kW)',
            'ordre_affichage': 200,
            'est_actif': True
        },
        {
            'nom': 'Navire de commerce',
            'description': 'Navire commercial ou de transport',
            'ordre_affichage': 201,
            'est_actif': True
        },
        {
            'nom': 'Yacht',
            'description': 'Bateau de luxe',
            'ordre_affichage': 202,
            'est_actif': True
        },
        {
            'nom': 'Jet-ski',
            'description': 'Moto nautique / Scooter des mers (≥90kW)',
            'ordre_affichage': 203,
            'est_actif': True
        },
        {
            'nom': 'Voilier',
            'description': 'Bateau à voile',
            'ordre_affichage': 204,
            'est_actif': True
        },
        {
            'nom': 'Bateau de pêche',
            'description': 'Embarcation de pêche professionnelle',
            'ordre_affichage': 205,
            'est_actif': True
        },
        {
            'nom': 'Canot',
            'description': 'Petite embarcation',
            'ordre_affichage': 206,
            'est_actif': True
        },
        {
            'nom': 'Vedette',
            'description': 'Bateau rapide à moteur',
            'ordre_affichage': 207,
            'est_actif': True
        },
    ]
    
    for type_data in maritime_types:
        VehicleType.objects.get_or_create(
            nom=type_data['nom'],
            defaults=type_data
        )


def reverse_aerial_types(apps, schema_editor):
    """Remove aerial vehicle types"""
    VehicleType = apps.get_model('vehicles', 'VehicleType')
    aerial_names = ['Avion', 'Hélicoptère', 'Drone', 'ULM', 'Planeur', 'Ballon']
    VehicleType.objects.filter(nom__in=aerial_names).delete()


def reverse_maritime_types(apps, schema_editor):
    """Remove maritime vehicle types"""
    VehicleType = apps.get_model('vehicles', 'VehicleType')
    maritime_names = [
        'Bateau de plaisance', 'Navire de commerce', 'Yacht', 
        'Jet-ski', 'Voilier', 'Bateau de pêche', 'Canot', 'Vedette'
    ]
    VehicleType.objects.filter(nom__in=maritime_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0012_extend_grilletarifaire_for_flat_rates'),
    ]

    operations = [
        migrations.RunPython(
            create_aerial_vehicle_types,
            reverse_code=reverse_aerial_types
        ),
        migrations.RunPython(
            create_maritime_vehicle_types,
            reverse_code=reverse_maritime_types
        ),
    ]
