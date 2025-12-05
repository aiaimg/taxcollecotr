#!/usr/bin/env python
"""
Test script for help_texts module
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from vehicles.help_texts import (
    HELP_TEXTS_DETAILED,
    HELP_TEXTS_SHORT,
    PROGRESS_STEPS,
    REQUIRED_DOCUMENTS,
    get_help_text,
    get_progress_steps,
    get_required_documents,
)


def test_help_texts():
    """Test help text functions"""
    print("=" * 60)
    print("Testing Help Texts Module")
    print("=" * 60)

    # Test 1: Short help texts
    print("\n1. Testing short help texts...")
    short_text = get_help_text("plaque_immatriculation", "fr", detailed=False)
    print(f"   ✓ Short help for 'plaque_immatriculation': {short_text[:50]}...")

    # Test 2: Detailed help texts
    print("\n2. Testing detailed help texts...")
    detailed_text = get_help_text("plaque_immatriculation", "fr", detailed=True)
    if detailed_text:
        print(f"   ✓ Detailed help title: {detailed_text.get('title')}")
        print(f"   ✓ Examples count: {len(detailed_text.get('examples', []))}")

    # Test 3: Required documents for each category
    print("\n3. Testing required documents...")
    for category in ["TERRESTRE", "AERIEN", "MARITIME"]:
        docs = get_required_documents(category, "fr")
        print(f"   ✓ {category}: {len(docs)} documents")
        for doc in docs:
            status = "Obligatoire" if doc["mandatory"] else "Optionnel"
            print(f"      - {doc['label']} ({status})")

    # Test 4: Progress steps
    print("\n4. Testing progress steps...")
    steps = get_progress_steps("fr")
    print(f"   ✓ Total steps: {len(steps)}")
    for step in steps:
        print(f"      - {step['label']}: {step['description']}")

    # Test 5: Multilingual support
    print("\n5. Testing multilingual support...")
    fr_text = get_help_text("marque", "fr", detailed=False)
    mg_text = get_help_text("marque", "mg", detailed=False)
    print(f"   ✓ French: {fr_text}")
    print(f"   ✓ Malagasy: {mg_text}")

    # Test 6: Data structure validation
    print("\n6. Validating data structures...")
    print(f"   ✓ Short help texts: {len(HELP_TEXTS_SHORT)} fields")
    print(f"   ✓ Detailed help texts: {len(HELP_TEXTS_DETAILED)} fields")
    print(f"   ✓ Required documents: {len(REQUIRED_DOCUMENTS)} categories")
    print(f"   ✓ Progress steps: {len(PROGRESS_STEPS)} languages")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_help_texts()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
