#!/usr/bin/env python
"""
Script pour charger la grille tarifaire officielle de Madagascar 2025
Basé sur le Projet de Loi de Finances 2026 - extraitplf.md
"""
import os
import sys
from decimal import Decimal

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone

from vehicles.models import GrilleTarifaire


def load_official_tax_grid():
    """Charge la grille tarifaire officielle de Madagascar pour 2025"""
    current_year = 2025

    print(f"🚀 Chargement de la grille tarifaire officielle pour l'année {current_year}...")

    # Supprimer les anciennes données d'exemple
    deleted_count = GrilleTarifaire.objects.filter(annee_fiscale=current_year).delete()[0]
    print(f"🗑️  Supprimé {deleted_count} anciens tarifs")

    # Grille tarifaire officielle basée sur extraitplf.md
    tarifs_officiels = [
        # === TRANCHE 1-4 CV (0 à 250 Cm3) ===
        # Véhicules ≤ 5 ans
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Essence",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 15000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Diesel",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 20000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Electrique",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 5000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Hybride",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 10000,
        },
        # Véhicules 6-10 ans
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Essence",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 40000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Diesel",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 45000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Electrique",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 30000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Hybride",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 35000,
        },
        # Véhicules 11-20 ans
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Essence",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 90000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Diesel",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 95000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Electrique",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 80000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Hybride",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 85000,
        },
        # Véhicules > 20 ans
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Essence",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 115000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Diesel",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 120000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Electrique",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 105000,
        },
        {
            "puissance_min_cv": 1,
            "puissance_max_cv": 4,
            "source_energie": "Hybride",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 110000,
        },
        # === TRANCHE 5-9 CV (251 à 500 Cm3) ===
        # Véhicules ≤ 5 ans
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Essence",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 30000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Diesel",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 40000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Electrique",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 10000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Hybride",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 20000,
        },
        # Véhicules 6-10 ans
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Essence",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 55000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Diesel",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 65000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Electrique",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 35000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Hybride",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 45000,
        },
        # Véhicules 11-20 ans
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Essence",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 105000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Diesel",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 115000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Electrique",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 85000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Hybride",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 95000,
        },
        # Véhicules > 20 ans
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Essence",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 130000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Diesel",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 140000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Electrique",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 110000,
        },
        {
            "puissance_min_cv": 5,
            "puissance_max_cv": 9,
            "source_energie": "Hybride",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 120000,
        },
        # === TRANCHE 10-12 CV (501 à 1000 Cm3) ===
        # Véhicules ≤ 5 ans
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Essence",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 60000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Diesel",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 80000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Electrique",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 20000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Hybride",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 40000,
        },
        # Véhicules 6-10 ans
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Essence",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 85000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Diesel",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 105000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Electrique",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 45000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Hybride",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 65000,
        },
        # Véhicules 11-20 ans
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Essence",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 135000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Diesel",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 155000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Electrique",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 95000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Hybride",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 115000,
        },
        # Véhicules > 20 ans
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Essence",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 160000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Diesel",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 180000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Electrique",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 120000,
        },
        {
            "puissance_min_cv": 10,
            "puissance_max_cv": 12,
            "source_energie": "Hybride",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 140000,
        },
        # === TRANCHE 13-15 CV (Supérieure à 1000 Cm3) ===
        # Véhicules ≤ 5 ans
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Essence",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 90000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Diesel",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 120000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Electrique",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 30000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Hybride",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 60000,
        },
        # Véhicules 6-10 ans
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Essence",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 115000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Diesel",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 145000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Electrique",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 55000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Hybride",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 85000,
        },
        # Véhicules 11-20 ans
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Essence",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 165000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Diesel",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 195000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Electrique",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 105000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Hybride",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 135000,
        },
        # Véhicules > 20 ans
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Essence",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 190000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Diesel",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 220000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Electrique",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 130000,
        },
        {
            "puissance_min_cv": 13,
            "puissance_max_cv": 15,
            "source_energie": "Hybride",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 160000,
        },
        # === TRANCHE > 15 CV ===
        # Véhicules ≤ 5 ans
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Essence",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 180000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Diesel",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 240000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Electrique",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 60000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Hybride",
            "age_min_annees": 0,
            "age_max_annees": 5,
            "montant_ariary": 120000,
        },
        # Véhicules 6-10 ans
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Essence",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 205000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Diesel",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 265000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Electrique",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 85000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Hybride",
            "age_min_annees": 6,
            "age_max_annees": 10,
            "montant_ariary": 145000,
        },
        # Véhicules 11-20 ans
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Essence",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 255000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Diesel",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 315000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Electrique",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 135000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Hybride",
            "age_min_annees": 11,
            "age_max_annees": 20,
            "montant_ariary": 195000,
        },
        # Véhicules > 20 ans
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Essence",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 280000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Diesel",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 340000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Electrique",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 160000,
        },
        {
            "puissance_min_cv": 16,
            "puissance_max_cv": None,
            "source_energie": "Hybride",
            "age_min_annees": 21,
            "age_max_annees": None,
            "montant_ariary": 220000,
        },
    ]

    # Insérer les nouveaux tarifs
    created_count = 0
    for tarif_data in tarifs_officiels:
        tarif_data["annee_fiscale"] = current_year
        tarif_data["est_active"] = True

        tarif, created = GrilleTarifaire.objects.get_or_create(**tarif_data)
        if created:
            created_count += 1

    print(f"✅ Créé {created_count} nouveaux tarifs officiels pour l'année {current_year}")

    # Vérification
    total_tarifs = GrilleTarifaire.objects.filter(annee_fiscale=current_year, est_active=True).count()
    print(f"📊 Total des tarifs actifs en base : {total_tarifs}")

    # Affichage d'un échantillon
    print("\n📋 Échantillon des tarifs chargés :")
    sample_tarifs = GrilleTarifaire.objects.filter(annee_fiscale=current_year, est_active=True).order_by(
        "puissance_min_cv", "source_energie", "age_min_annees"
    )[:10]

    for tarif in sample_tarifs:
        print(f"   • {tarif}")

    print(f"\n🎉 Grille tarifaire officielle chargée avec succès !")


if __name__ == "__main__":
    load_official_tax_grid()
