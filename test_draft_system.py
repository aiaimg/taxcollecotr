"""
Test script for the draft system implementation
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from datetime import date

from django.contrib.auth.models import User

from vehicles.models import VehicleType, Vehicule


def test_draft_system():
    """Test the draft system functionality"""
    print("Testing Draft System Implementation...")
    print("=" * 60)

    # 1. Test that statut_declaration field exists and has correct choices
    print("\n1. Testing statut_declaration field...")
    assert hasattr(Vehicule, "STATUT_DECLARATION_CHOICES"), "STATUT_DECLARATION_CHOICES not found"
    assert len(Vehicule.STATUT_DECLARATION_CHOICES) == 4, "Should have 4 status choices"
    status_codes = [choice[0] for choice in Vehicule.STATUT_DECLARATION_CHOICES]
    assert "BROUILLON" in status_codes, "BROUILLON status missing"
    assert "SOUMISE" in status_codes, "SOUMISE status missing"
    assert "VALIDEE" in status_codes, "VALIDEE status missing"
    assert "REJETEE" in status_codes, "REJETEE status missing"
    print("   ✓ statut_declaration field configured correctly")

    # 2. Test creating a vehicle with draft status
    print("\n2. Testing vehicle creation with draft status...")
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(username="test_draft_user", defaults={"email": "test@example.com"})
        if created:
            user.set_password("testpass123")
            user.save()

        # Clean up any existing test vehicles
        Vehicule.objects.filter(plaque_immatriculation__startswith="TEMP-").delete()

        # Get or create a vehicle type
        vehicle_type, _ = VehicleType.objects.get_or_create(
            nom="Voiture", defaults={"description": "Voiture de tourisme", "ordre_affichage": 1}
        )

        # Create a draft vehicle
        draft_vehicle = Vehicule.objects.create(
            plaque_immatriculation="TEMP-DRAFT001",
            proprietaire=user,
            nom_proprietaire="Test Owner",
            marque="Toyota",
            modele="Corolla",
            puissance_fiscale_cv=13,
            cylindree_cm3=1800,
            source_energie="Essence",
            date_premiere_circulation=date(2020, 1, 1),
            type_vehicule=vehicle_type,
            vehicle_category="TERRESTRE",
            statut_declaration="BROUILLON",
        )

        assert draft_vehicle.statut_declaration == "BROUILLON", "Draft status not set correctly"
        print(f"   ✓ Draft vehicle created: {draft_vehicle.plaque_immatriculation}")

        # 3. Test querying draft vehicles
        print("\n3. Testing draft vehicle queries...")
        draft_count = Vehicule.objects.filter(proprietaire=user, statut_declaration="BROUILLON").count()
        assert draft_count >= 1, "Draft vehicle not found in query"
        print(f"   ✓ Found {draft_count} draft vehicle(s) for user")

        # 4. Test changing status from draft to submitted
        print("\n4. Testing status change from BROUILLON to SOUMISE...")
        draft_vehicle.statut_declaration = "SOUMISE"
        draft_vehicle.save()
        draft_vehicle.refresh_from_db()
        assert draft_vehicle.statut_declaration == "SOUMISE", "Status not changed to SOUMISE"
        print("   ✓ Status successfully changed to SOUMISE")

        # 5. Test document validation methods
        print("\n5. Testing document validation methods...")
        assert hasattr(
            draft_vehicle, "get_required_documents_by_category"
        ), "get_required_documents_by_category method missing"
        assert hasattr(draft_vehicle, "validate_required_documents"), "validate_required_documents method missing"

        required_docs = draft_vehicle.get_required_documents_by_category()
        assert isinstance(required_docs, list), "Required documents should be a list"
        assert len(required_docs) > 0, "Should have required documents"
        print(f"   ✓ Required documents for TERRESTRE: {', '.join(required_docs)}")

        is_valid, missing_docs = draft_vehicle.validate_required_documents()
        assert isinstance(is_valid, bool), "is_valid should be boolean"
        assert isinstance(missing_docs, list), "missing_docs should be a list"
        print(f"   ✓ Document validation working (valid: {is_valid}, missing: {len(missing_docs)})")

        # 6. Test aerial vehicle draft
        print("\n6. Testing aerial vehicle draft...")
        aerial_type, _ = VehicleType.objects.get_or_create(
            nom="Avion", defaults={"description": "Avion", "ordre_affichage": 100}
        )

        aerial_draft = Vehicule.objects.create(
            plaque_immatriculation="TEMP-AERIAL01",
            proprietaire=user,
            nom_proprietaire="Test Owner",
            marque="Cessna",
            modele="172",
            puissance_fiscale_cv=150,
            cylindree_cm3=5000,
            source_energie="Essence",
            date_premiere_circulation=date(2020, 1, 1),
            type_vehicule=aerial_type,
            vehicle_category="AERIEN",
            immatriculation_aerienne="5R-TEST",
            masse_maximale_decollage_kg=1200,
            statut_declaration="BROUILLON",
        )

        assert aerial_draft.vehicle_category == "AERIEN", "Aerial category not set"
        assert aerial_draft.statut_declaration == "BROUILLON", "Aerial draft status not set"
        aerial_required_docs = aerial_draft.get_required_documents_by_category()
        assert "certificat_navigabilite" in aerial_required_docs, "Aerial required docs incorrect"
        print(f"   ✓ Aerial draft created with required docs: {', '.join(aerial_required_docs)}")

        # 7. Test maritime vehicle draft
        print("\n7. Testing maritime vehicle draft...")
        maritime_type, _ = VehicleType.objects.get_or_create(
            nom="Bateau de plaisance", defaults={"description": "Bateau de plaisance", "ordre_affichage": 200}
        )

        maritime_draft = Vehicule.objects.create(
            plaque_immatriculation="TEMP-MARIT001",
            proprietaire=user,
            nom_proprietaire="Test Owner",
            marque="Yamaha",
            modele="Boat",
            puissance_fiscale_cv=25,
            cylindree_cm3=2000,
            source_energie="Essence",
            date_premiere_circulation=date(2020, 1, 1),
            type_vehicule=maritime_type,
            vehicle_category="MARITIME",
            numero_francisation="FR-TEST-001",
            nom_navire="Test Boat",
            longueur_metres=8.5,
            statut_declaration="BROUILLON",
        )

        assert maritime_draft.vehicle_category == "MARITIME", "Maritime category not set"
        assert maritime_draft.statut_declaration == "BROUILLON", "Maritime draft status not set"
        maritime_required_docs = maritime_draft.get_required_documents_by_category()
        assert "certificat_francisation" in maritime_required_docs, "Maritime required docs incorrect"
        print(f"   ✓ Maritime draft created with required docs: {', '.join(maritime_required_docs)}")

        # Cleanup
        print("\n8. Cleaning up test data...")
        draft_vehicle.delete()
        aerial_draft.delete()
        maritime_draft.delete()
        print("   ✓ Test data cleaned up")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_draft_system()
    exit(0 if success else 1)
