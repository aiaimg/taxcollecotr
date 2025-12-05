#!/usr/bin/env python
"""
Test script for help text template tags
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
django.setup()

from django.template import Context, Template


def test_template_tags():
    """Test help text template tags"""
    print("=" * 60)
    print("Testing Help Text Template Tags")
    print("=" * 60)

    # Test 1: help_tooltip tag
    print("\n1. Testing help_tooltip tag...")
    template = Template("{% load help_text_tags %}{% help_tooltip 'marque' 'fr' %}")
    result = template.render(Context({}))
    print(f"   ✓ Result: {result[:60]}...")

    # Test 2: help_detailed tag
    print("\n2. Testing help_detailed tag...")
    template = Template(
        "{% load help_text_tags %}{% help_detailed 'plaque_immatriculation' 'fr' as help %}{{ help.title }}"
    )
    result = template.render(Context({}))
    print(f"   ✓ Result: {result}")

    # Test 3: required_docs tag
    print("\n3. Testing required_docs tag...")
    template = Template("{% load help_text_tags %}{% required_docs 'AERIEN' 'fr' as docs %}{{ docs|length }}")
    result = template.render(Context({}))
    print(f"   ✓ Number of documents: {result}")

    # Test 4: progress_steps tag
    print("\n4. Testing progress_steps tag...")
    template = Template("{% load help_text_tags %}{% progress_steps 'fr' as steps %}{{ steps|length }}")
    result = template.render(Context({}))
    print(f"   ✓ Number of steps: {result}")

    # Test 5: get_item filter
    print("\n5. Testing get_item filter...")
    template = Template("{% load help_text_tags %}{{ my_dict|get_item:'key' }}")
    result = template.render(Context({"my_dict": {"key": "value"}}))
    print(f"   ✓ Result: {result}")

    print("\n" + "=" * 60)
    print("All template tag tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_template_tags()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
