#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxcollector_project.settings')
django.setup()

from administration.templatetags.currency_filters import format_ariary, format_number_spaces

# Test the format_ariary filter
test_values = [100000, 1500000, 25000, 1000000, 1234567]

print("Testing format_ariary filter:")
for value in test_values:
    result = format_ariary(value)
    print(f"  {value} -> {result}")

print("\nTesting format_number_spaces filter:")
for value in test_values:
    result = format_number_spaces(value)
    print(f"  {value} -> {result}")

print("\nCurrency filter test completed successfully!")