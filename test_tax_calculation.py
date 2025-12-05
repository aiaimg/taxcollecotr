#!/usr/bin/env python
"""
Script de test pour vérifier le calcul automatique des taxes
avec la nouvelle grille tarifaire officielle
"""
import os
import sys
from datetime import date

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User

from vehicles.models import GrilleTarifaire, Vehicule
from vehicles.services import TaxCalculationService


def test_tax_calculations():
    """Test le calcul des taxes avec différents scénarios"""
    print("🧪 Test du calcul automatique des taxes avec la grille officielle")
    print("=" * 60)

    # Créer un utilisateur de test s'il n'existe pas
    user, created = User.objects.get_or_create(
        username="test_user", defaults={"email": "test@example.com", "first_name": "Test", "last_name": "User"}
    )
    if created:
        print(f"✅ Utilisateur de test créé : {user.username}")

    # Scénarios de test
    test_scenarios = [
        {
            "name": "Voiture essence récente (3 CV, 2 ans)",
            "plaque": "1234 TAA",
            "puissance": 3,
            "source_energie": "Essence",
            "date_circulation": date(2023, 1, 1),
            "expected_tax": 15000,  # 1-4 CV, Essence, ≤5 ans
        },
        {
            "name": "SUV diesel ancien (12 CV, 8 ans)",
            "plaque": "5678 TBB",
            "puissance": 12,
            "source_energie": "Diesel",
            "date_circulation": date(2017, 1, 1),
            "expected_tax": 105000,  # 10-12 CV, Diesel, 6-10 ans
        },
        {
            "name": "Voiture électrique (8 CV, 3 ans)",
            "plaque": "9012 TCC",
            "puissance": 8,
            "source_energie": "Electrique",
            "date_circulation": date(2022, 1, 1),
            "expected_tax": 10000,  # 5-9 CV, Électrique, ≤5 ans
        },
        {
            "name": "Véhicule hybride puissant (18 CV, 15 ans)",
            "plaque": "3456 TDD",
            "puissance": 18,
            "source_energie": "Hybride",
            "date_circulation": date(2010, 1, 1),
            "expected_tax": 195000,  # >15 CV, Hybride, 11-20 ans
        },
        {
            "name": "Ambulance (exonérée)",
            "plaque": "7890 AMB",
            "puissance": 10,
            "source_energie": "Diesel",
            "date_circulation": date(2020, 1, 1),
            "categorie": "Ambulance",
            "expected_tax": 0,  # Exonérée
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['name']}")
        print("-" * 40)

        # Supprimer le véhicule s'il existe déjà
        Vehicule.objects.filter(plaque_immatriculation=scenario["plaque"]).delete()

        # Créer le véhicule de test
        vehicule = Vehicule.objects.create(
            plaque_immatriculation=scenario["plaque"],
            proprietaire=user,
            puissance_fiscale_cv=scenario["puissance"],
            source_energie=scenario["source_energie"],
            date_premiere_circulation=scenario["date_circulation"],
            categorie_vehicule=scenario.get("categorie", "Personnel"),
        )

        # Calculer la taxe
        tax_service = TaxCalculationService()
        result = tax_service.calculate_tax(vehicule, 2025)

        # Afficher les résultats
        print(f"   Plaque: {vehicule.plaque_immatriculation}")
        print(f"   Puissance: {vehicule.puissance_fiscale_cv} CV")
        print(f"   Énergie: {vehicule.source_energie}")
        print(f"   Âge: {vehicule.get_age_annees()} ans")
        print(f"   Catégorie: {vehicule.categorie_vehicule}")

        if result["is_exempt"]:
            print(f"   ✅ Statut: EXONÉRÉ ({result['exemption_reason']})")
            print(f"   💰 Montant: 0 Ar")
        else:
            print(f"   💰 Montant calculé: {result['amount']} Ar")
            print(f"   📋 Grille appliquée: {result['grid']}")

        # Vérifier si le résultat correspond à l'attendu
        expected = scenario["expected_tax"]
        actual = result["amount"] if result["amount"] is not None else 0

        if actual == expected:
            print(f"   ✅ SUCCÈS: Montant correct ({actual} Ar)")
        else:
            print(f"   ❌ ERREUR: Attendu {expected} Ar, obtenu {actual} Ar")
            if result.get("error"):
                print(f"   🚨 Erreur: {result['error']}")

    print("\n" + "=" * 60)
    print("🎯 Tests terminés !")

    # Nettoyer les données de test
    print("\n🧹 Nettoyage des données de test...")
    for scenario in test_scenarios:
        Vehicule.objects.filter(plaque_immatriculation=scenario["plaque"]).delete()

    if created:
        user.delete()
        print("✅ Utilisateur de test supprimé")


if __name__ == "__main__":
    test_tax_calculations()
