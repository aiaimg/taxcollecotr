#!/usr/bin/env python
"""
Script de test pour la fonction de conversion cylindrée → CV
"""

import os
import sys

import django

# Configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

# Import de la fonction de conversion
from vehicles.utils import get_conversion_info, get_puissance_fiscale_from_cylindree


def test_conversion():
    """Test de la fonction de conversion avec différentes valeurs"""

    print("=" * 60)
    print("TEST DE CONVERSION CYLINDRÉE → PUISSANCE FISCALE (CV)")
    print("=" * 60)
    print()

    # Valeurs de test typiques
    test_values = [
        (110, "Scooter"),
        (400, "Moto moyenne"),
        (800, "Petite voiture"),
        (1600, "Voiture moyenne"),
        (2500, "Grosse voiture"),
        (50, "Cyclomoteur"),
        (1200, "Voiture compacte"),
        (3000, "SUV/4x4"),
    ]

    for cylindree, description in test_values:
        print(f"🔧 Test: {cylindree} cm³ ({description})")
        print("-" * 50)

        # Test de la fonction complète
        conversion_info = get_conversion_info(cylindree)

        if conversion_info["valid"]:
            print(f"✅ Conversion réussie:")
            print(f"   • Cylindrée: {conversion_info['cylindree']} cm³")
            print(f"   • Plage CV: {conversion_info['cv_min']}-{conversion_info['cv_max']} CV")
            print(f"   • CV suggéré: {conversion_info['cv_suggere']} CV")
            print(f"   • Description: {conversion_info['plage_description']}")
            print(f"   • Message: {conversion_info['message']}")
            print(f"   • Conseil: {conversion_info['conseil']}")

            if conversion_info["exemples_vehicules"]:
                print(f"   • Exemples: {', '.join(conversion_info['exemples_vehicules'])}")
        else:
            print(f"❌ Erreur: {conversion_info['message']}")

        print()

    print("=" * 60)
    print("TEST DE LA FONCTION SIMPLE")
    print("=" * 60)
    print()

    # Test de la fonction simple
    for cylindree, description in test_values:
        cv_suggere = get_puissance_fiscale_from_cylindree(cylindree)
        print(f"{cylindree:4d} cm³ ({description:15s}) → {cv_suggere:2d} CV")

    print()
    print("=" * 60)
    print("TESTS TERMINÉS")
    print("=" * 60)


if __name__ == "__main__":
    test_conversion()
