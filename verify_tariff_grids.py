#!/usr/bin/env python
"""
Verification script for tariff grids (aerial and maritime)
This script validates that all required tariff grids have been created correctly.
"""

import os
import sys

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from decimal import Decimal

from vehicles.models import GrilleTarifaire


def verify_aerial_tariff_grid():
    """Verify the aerial tariff grid"""
    print("\n" + "=" * 80)
    print("VERIFYING AERIAL TARIFF GRID")
    print("=" * 80)

    try:
        grid = GrilleTarifaire.objects.get(grid_type="FLAT_AERIAL", annee_fiscale=2026, est_active=True)

        print(f"✓ Aerial tariff grid found")
        print(f"  - Grid Type: {grid.grid_type}")
        print(f"  - Aerial Type: {grid.aerial_type}")
        print(f"  - Amount: {grid.montant_ariary} Ar")
        print(f"  - Fiscal Year: {grid.annee_fiscale}")
        print(f"  - Active: {grid.est_active}")

        # Validate values
        assert grid.aerial_type == "ALL", "Aerial type should be 'ALL'"
        assert grid.montant_ariary == Decimal("2000000.00"), "Amount should be 2,000,000 Ar"
        assert grid.annee_fiscale == 2026, "Fiscal year should be 2026"
        assert grid.est_active == True, "Grid should be active"

        print("\n✓ All aerial tariff grid validations passed!")
        return True

    except GrilleTarifaire.DoesNotExist:
        print("✗ ERROR: Aerial tariff grid not found!")
        return False
    except AssertionError as e:
        print(f"✗ ERROR: Validation failed - {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def verify_maritime_tariff_grids():
    """Verify the maritime tariff grids"""
    print("\n" + "=" * 80)
    print("VERIFYING MARITIME TARIFF GRIDS")
    print("=" * 80)

    all_passed = True

    # Expected grids
    expected_grids = [
        {
            "category": "NAVIRE_PLAISANCE",
            "amount": Decimal("200000.00"),
            "longueur_min": Decimal("7.00"),
            "puissance_min_cv": Decimal("22.00"),
            "puissance_min_kw": Decimal("90.00"),
        },
        {
            "category": "JETSKI",
            "amount": Decimal("200000.00"),
            "longueur_min": None,
            "puissance_min_cv": None,
            "puissance_min_kw": Decimal("90.00"),
        },
        {
            "category": "AUTRES_ENGINS",
            "amount": Decimal("1000000.00"),
            "longueur_min": None,
            "puissance_min_cv": None,
            "puissance_min_kw": None,
        },
    ]

    for expected in expected_grids:
        print(f"\nChecking {expected['category']}...")

        try:
            grid = GrilleTarifaire.objects.get(
                grid_type="FLAT_MARITIME", maritime_category=expected["category"], annee_fiscale=2026, est_active=True
            )

            print(f"✓ {expected['category']} tariff grid found")
            print(f"  - Grid Type: {grid.grid_type}")
            print(f"  - Maritime Category: {grid.maritime_category}")
            print(f"  - Amount: {grid.montant_ariary} Ar")
            print(f"  - Fiscal Year: {grid.annee_fiscale}")
            print(f"  - Active: {grid.est_active}")

            if grid.longueur_min_metres:
                print(f"  - Min Length: {grid.longueur_min_metres} m")
            if grid.puissance_min_cv_maritime:
                print(f"  - Min Power (CV): {grid.puissance_min_cv_maritime} CV")
            if grid.puissance_min_kw_maritime:
                print(f"  - Min Power (kW): {grid.puissance_min_kw_maritime} kW")

            # Validate values
            assert grid.montant_ariary == expected["amount"], f"Amount should be {expected['amount']} Ar"
            assert grid.annee_fiscale == 2026, "Fiscal year should be 2026"
            assert grid.est_active == True, "Grid should be active"

            if expected["longueur_min"]:
                assert (
                    grid.longueur_min_metres == expected["longueur_min"]
                ), f"Min length should be {expected['longueur_min']} m"

            if expected["puissance_min_cv"]:
                assert (
                    grid.puissance_min_cv_maritime == expected["puissance_min_cv"]
                ), f"Min power (CV) should be {expected['puissance_min_cv']} CV"

            if expected["puissance_min_kw"]:
                assert (
                    grid.puissance_min_kw_maritime == expected["puissance_min_kw"]
                ), f"Min power (kW) should be {expected['puissance_min_kw']} kW"

            print(f"✓ All validations passed for {expected['category']}!")

        except GrilleTarifaire.DoesNotExist:
            print(f"✗ ERROR: {expected['category']} tariff grid not found!")
            all_passed = False
        except AssertionError as e:
            print(f"✗ ERROR: Validation failed - {e}")
            all_passed = False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            all_passed = False

    if all_passed:
        print("\n✓ All maritime tariff grid validations passed!")

    return all_passed


def verify_all_grids():
    """Verify all tariff grids"""
    print("\n" + "=" * 80)
    print("TARIFF GRID VERIFICATION SUMMARY")
    print("=" * 80)

    # Count grids by type
    aerial_count = GrilleTarifaire.objects.filter(grid_type="FLAT_AERIAL", annee_fiscale=2026, est_active=True).count()

    maritime_count = GrilleTarifaire.objects.filter(
        grid_type="FLAT_MARITIME", annee_fiscale=2026, est_active=True
    ).count()

    terrestrial_count = GrilleTarifaire.objects.filter(
        grid_type="PROGRESSIVE", annee_fiscale=2026, est_active=True
    ).count()

    print(f"\nActive Tariff Grids for Fiscal Year 2026:")
    print(f"  - Aerial (FLAT_AERIAL): {aerial_count}")
    print(f"  - Maritime (FLAT_MARITIME): {maritime_count}")
    print(f"  - Terrestrial (PROGRESSIVE): {terrestrial_count}")
    print(f"  - TOTAL: {aerial_count + maritime_count + terrestrial_count}")

    # Verify expected counts
    assert aerial_count == 1, "Should have exactly 1 aerial tariff grid"
    assert maritime_count == 3, "Should have exactly 3 maritime tariff grids"

    print("\n✓ Grid counts are correct!")


def main():
    """Main verification function"""
    print("\n" + "=" * 80)
    print("STARTING TARIFF GRID VERIFICATION")
    print("=" * 80)

    aerial_ok = verify_aerial_tariff_grid()
    maritime_ok = verify_maritime_tariff_grids()

    try:
        verify_all_grids()
        summary_ok = True
    except AssertionError as e:
        print(f"\n✗ ERROR: {e}")
        summary_ok = False

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    if aerial_ok and maritime_ok and summary_ok:
        print("\n✓✓✓ ALL VERIFICATIONS PASSED! ✓✓✓")
        print("\nThe following tariff grids have been successfully created:")
        print("  1. Aerial vehicles: 2,000,000 Ar (all aircraft types)")
        print("  2. Maritime - Navire de plaisance: 200,000 Ar (≥7m or ≥22CV or ≥90kW)")
        print("  3. Maritime - Jet-ski: 200,000 Ar (≥90kW)")
        print("  4. Maritime - Autres engins: 1,000,000 Ar (all other motorized)")
        return 0
    else:
        print("\n✗✗✗ SOME VERIFICATIONS FAILED ✗✗✗")
        print("\nPlease check the errors above and fix the issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
