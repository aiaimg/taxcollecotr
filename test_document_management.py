#!/usr/bin/env python
"""
Test script for document management functionality (Task 8)
Tests the new methods added to the Vehicule model
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from django.contrib.auth import get_user_model

from vehicles.models import DocumentVehicule, VehicleType, Vehicule

User = get_user_model()


def test_get_required_documents_by_category():
    """Test that get_required_documents_by_category returns correct documents"""
    print("\n" + "=" * 70)
    print("TEST: get_required_documents_by_category()")
    print("=" * 70)

    # Get or create a test user
    user, _ = User.objects.get_or_create(username="test_doc_user", defaults={"email": "test@example.com"})

    # Get a vehicle type
    vehicle_type = VehicleType.objects.first()
    if not vehicle_type:
        print("❌ No vehicle types found. Please run migrations first.")
        return False

    # Test TERRESTRE
    print("\n1. Testing TERRESTRE vehicle:")
    vehicule_terrestre = Vehicule(
        plaque_immatriculation="TEST001",
        proprietaire=user,
        vehicle_category="TERRESTRE",
        type_vehicule=vehicle_type,
        puissance_fiscale_cv=5,
        cylindree_cm3=1000,
        source_energie="Essence",
        date_premiere_circulation="2020-01-01",
    )
    required_docs = vehicule_terrestre.get_required_documents_by_category()
    expected_terrestre = ["carte_grise", "assurance", "controle_technique"]

    if required_docs == expected_terrestre:
        print(f"   ✓ TERRESTRE: {required_docs}")
    else:
        print(f"   ❌ TERRESTRE: Expected {expected_terrestre}, got {required_docs}")
        return False

    # Test AERIEN
    print("\n2. Testing AERIEN vehicle:")
    vehicule_aerien = Vehicule(
        plaque_immatriculation="TEST002",
        proprietaire=user,
        vehicle_category="AERIEN",
        type_vehicule=vehicle_type,
        puissance_fiscale_cv=100,
        cylindree_cm3=5000,
        source_energie="Essence",
        date_premiere_circulation="2020-01-01",
        immatriculation_aerienne="5R-ABC",
        masse_maximale_decollage_kg=1500,
    )
    required_docs = vehicule_aerien.get_required_documents_by_category()
    expected_aerien = ["certificat_navigabilite", "certificat_immatriculation_aerienne", "assurance_aerienne"]

    if required_docs == expected_aerien:
        print(f"   ✓ AERIEN: {required_docs}")
    else:
        print(f"   ❌ AERIEN: Expected {expected_aerien}, got {required_docs}")
        return False

    # Test MARITIME
    print("\n3. Testing MARITIME vehicle:")
    vehicule_maritime = Vehicule(
        plaque_immatriculation="TEST003",
        proprietaire=user,
        vehicle_category="MARITIME",
        type_vehicule=vehicle_type,
        puissance_fiscale_cv=25,
        cylindree_cm3=3000,
        source_energie="Diesel",
        date_premiere_circulation="2020-01-01",
        numero_francisation="FR-12345",
        nom_navire="Test Boat",
        longueur_metres=8.5,
    )
    required_docs = vehicule_maritime.get_required_documents_by_category()
    expected_maritime = ["certificat_francisation", "permis_navigation", "assurance_maritime"]

    if required_docs == expected_maritime:
        print(f"   ✓ MARITIME: {required_docs}")
    else:
        print(f"   ❌ MARITIME: Expected {expected_maritime}, got {required_docs}")
        return False

    print("\n✅ All get_required_documents_by_category tests passed!")
    return True


def test_validate_required_documents():
    """Test that validate_required_documents correctly identifies missing documents"""
    print("\n" + "=" * 70)
    print("TEST: validate_required_documents()")
    print("=" * 70)

    # Get or create a test user
    user, _ = User.objects.get_or_create(username="test_doc_user2", defaults={"email": "test2@example.com"})

    # Get a vehicle type
    vehicle_type = VehicleType.objects.first()
    if not vehicle_type:
        print("❌ No vehicle types found. Please run migrations first.")
        return False

    # Test with existing vehicle if available, or create a simple test
    print("\n1. Testing validation logic with TERRESTRE vehicle (no documents):")

    # Create a simple vehicle object (not saved to DB)
    vehicule = Vehicule(
        plaque_immatriculation="1234TAA",
        proprietaire=user,
        vehicle_category="TERRESTRE",
        type_vehicule=vehicle_type,
        marque="TOYOTA",
        modele="COROLLA",
        puissance_fiscale_cv=11,
        cylindree_cm3=1000,
        source_energie="Essence",
        date_premiere_circulation="2020-01-01",
    )

    # Save to DB to test validation
    try:
        vehicule.save()
    except Exception as e:
        print(f"   ⚠️  Could not save vehicle: {e}")
        print("   ℹ️  Testing logic without DB persistence...")

    # Test validation
    is_valid, missing_docs = vehicule.validate_required_documents()

    if not is_valid and len(missing_docs) == 3:
        print(f"   ✓ Correctly identified {len(missing_docs)} missing documents:")
        for doc in missing_docs:
            print(f"      - {doc['name']} ({doc['code']})")
    else:
        print(f"   ❌ Expected 3 missing documents, got {len(missing_docs)}")
        if vehicule.pk:
            vehicule.delete()
        return False

    print("\n2. Testing validation logic with AERIEN vehicle (no documents):")
    vehicule_aerien = Vehicule(
        plaque_immatriculation="5678XYZ",
        proprietaire=user,
        vehicle_category="AERIEN",
        type_vehicule=vehicle_type,
        marque="CESSNA",
        modele="172",
        puissance_fiscale_cv=100,
        cylindree_cm3=5000,
        source_energie="Essence",
        date_premiere_circulation="2020-01-01",
        immatriculation_aerienne="5R-ABC",
        masse_maximale_decollage_kg=1500,
    )

    try:
        vehicule_aerien.save()
    except Exception:
        pass

    is_valid, missing_docs = vehicule_aerien.validate_required_documents()

    if not is_valid and len(missing_docs) == 3:
        print(f"   ✓ Correctly identified {len(missing_docs)} missing documents:")
        for doc in missing_docs:
            print(f"      - {doc['name']} ({doc['code']})")
    else:
        print(f"   ❌ Expected 3 missing documents for AERIEN, got {len(missing_docs)}")
        if vehicule_aerien.pk:
            vehicule_aerien.delete()
        if vehicule.pk:
            vehicule.delete()
        return False

    print("\n3. Testing validation logic with MARITIME vehicle (no documents):")
    vehicule_maritime = Vehicule(
        plaque_immatriculation="9012ABC",
        proprietaire=user,
        vehicle_category="MARITIME",
        type_vehicule=vehicle_type,
        marque="YAMAHA",
        modele="BOAT",
        puissance_fiscale_cv=25,
        cylindree_cm3=3000,
        source_energie="Diesel",
        date_premiere_circulation="2020-01-01",
        numero_francisation="FR-12345",
        nom_navire="Test Boat",
        longueur_metres=8.5,
    )

    try:
        vehicule_maritime.save()
    except Exception:
        pass

    is_valid, missing_docs = vehicule_maritime.validate_required_documents()

    if not is_valid and len(missing_docs) == 3:
        print(f"   ✓ Correctly identified {len(missing_docs)} missing documents:")
        for doc in missing_docs:
            print(f"      - {doc['name']} ({doc['code']})")
    else:
        print(f"   ❌ Expected 3 missing documents for MARITIME, got {len(missing_docs)}")
        if vehicule_maritime.pk:
            vehicule_maritime.delete()
        if vehicule_aerien.pk:
            vehicule_aerien.delete()
        if vehicule.pk:
            vehicule.delete()
        return False

    # Clean up
    if vehicule_maritime.pk:
        vehicule_maritime.delete()
    if vehicule_aerien.pk:
        vehicule_aerien.delete()
    if vehicule.pk:
        vehicule.delete()

    print("\n✅ All validate_required_documents tests passed!")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("DOCUMENT MANAGEMENT TESTS (Task 8)")
    print("=" * 70)

    all_passed = True

    # Test 1: get_required_documents_by_category
    if not test_get_required_documents_by_category():
        all_passed = False

    # Test 2: validate_required_documents
    if not test_validate_required_documents():
        all_passed = False

    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
