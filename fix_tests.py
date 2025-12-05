#!/usr/bin/env python
"""Script to fix test plate formats"""
import re

# Read the test file
with open("vehicles/tests.py", "r") as f:
    content = f.read()

# Replace all invalid plate formats with TEMP- format
replacements = [
    ("plaque_immatriculation='MAR-003'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='MAR-004'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='MAR-005'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='MAR-006'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='MAR-007'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='5R-XYZ'", "plaque_immatriculation=self.generate_temp_plate('AIR')"),
    ("plaque_immatriculation='MAR-008'", "plaque_immatriculation=self.generate_temp_plate('MAR')"),
    ("plaque_immatriculation='AMB-001'", "plaque_immatriculation=self.generate_temp_plate('AMB')"),
]

for old, new in replacements:
    content = content.replace(old, new)

# Fix CV values for terrestrial vehicle
content = content.replace(
    "puissance_fiscale_cv=8,\n            cylindree_cm3=1800,",
    "puissance_fiscale_cv=13,\n            cylindree_cm3=1800,",
)

# Fix CV values for maritime vehicles (set to 1 to avoid validation)
content = re.sub(
    r"(vehicle_category='MARITIME'.*?)\n(\s+)puissance_fiscale_cv=0,",
    r"\1\n\2puissance_fiscale_cv=1,",
    content,
    flags=re.DOTALL,
)

# Write back
with open("vehicles/tests.py", "w") as f:
    f.write(content)

print("Fixed test file")
