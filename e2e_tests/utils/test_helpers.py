"""
Test helper utilities for E2E tests
"""

import random
import string
from datetime import datetime, timedelta


def generate_license_plate() -> str:
    """Generate a random Madagascar license plate format: 1234 ABC"""
    numbers = "".join(random.choices(string.digits, k=4))
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    return f"{numbers} {letters}"


def generate_test_user_data(user_type: str = "individual") -> dict:
    """
    Generate test user data for registration

    Args:
        user_type: Type of user ('individual', 'company', 'public_institution', 'international_organization')

    Returns:
        Dictionary with user registration data
    """
    email_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    base_data = {
        "email": f"test_{email_suffix}@example.com",
        "password": "TestPass123!@#",
        "password_confirm": "TestPass123!@#",
        "first_name": "Test",
        "last_name": "User",
        "user_type": user_type,
    }

    if user_type == "company":
        base_data.update(
            {
                "company_name": f"Test Company {email_suffix[:4].upper()}",
                "company_registration": f"REG{random.randint(100000, 999999)}",
                "tax_id": f"TAX{random.randint(100000, 999999)}",
            }
        )
    elif user_type == "public_institution":
        base_data.update(
            {
                "institution_name": f"Test Institution {email_suffix[:4].upper()}",
                "institution_type": "autre",
            }
        )
    elif user_type == "international_organization":
        base_data.update(
            {
                "organization_name": f"Test Organization {email_suffix[:4].upper()}",
                "organization_type": "organisation_internationale",
            }
        )

    return base_data


def generate_test_vehicle_data(category: str = "Personnel") -> dict:
    """
    Generate test vehicle data

    Args:
        category: Vehicle category ('Personnel', 'Commercial', 'Ambulance', etc.)

    Returns:
        Dictionary with vehicle data
    """
    return {
        "license_plate": generate_license_plate(),
        "fiscal_power_cv": random.choice([4, 5, 6, 7, 8, 9, 10]),
        "engine_size_cm3": random.choice([1200, 1500, 1800, 2000, 2500]),
        "energy_source": random.choice(["Essence", "Diesel", "Hybride"]),
        "first_registration_date": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d"),
        "categorie_vehicule": category,
        "vehicle_type": "Terrestre",
        "terrestrial_subtype": "voiture",
        "vehicle_brand": "Toyota",
        "vehicle_model": "Corolla",
    }


def generate_test_contravention_data() -> dict:
    """Generate test contravention data"""
    return {
        "infraction_type": "Excès de vitesse",
        "location": "Avenue de l'Indépendance, Antananarivo",
        "fine_amount": 200000,  # Ariary
        "description": "Vitesse constatée: 85 km/h, Limite: 50 km/h",
    }


def calculate_expected_tax(vehicle_data: dict) -> int:
    """
    Calculate expected tax amount based on vehicle data
    This mirrors the logic in the actual application

    Args:
        vehicle_data: Dictionary with vehicle information

    Returns:
        Expected tax amount in Ariary
    """
    # Exempt categories
    exempt_categories = ["Ambulance", "Sapeurs-pompiers", "Administratif", "Convention_internationale"]
    if vehicle_data.get("categorie_vehicule") in exempt_categories:
        return 0

    # This is a simplified version - actual calculation is more complex
    # based on fiscal power, age, and energy source
    fiscal_power = vehicle_data.get("fiscal_power_cv", 5)

    # Simplified tax grid
    if fiscal_power <= 4:
        base_tax = 20000
    elif fiscal_power <= 7:
        base_tax = 50000
    elif fiscal_power <= 10:
        base_tax = 100000
    else:
        base_tax = 150000

    return base_tax


class TestDataGenerator:
    """Helper class for generating test data"""

    @staticmethod
    def create_test_users(count: int = 5) -> list:
        """Create multiple test users with different types"""
        users = []
        user_types = ["individual", "company", "public_institution"]

        for i in range(count):
            user_type = user_types[i % len(user_types)]
            users.append(generate_test_user_data(user_type))

        return users

    @staticmethod
    def create_test_vehicles(count: int = 10) -> list:
        """Create multiple test vehicles with various categories"""
        vehicles = []
        categories = ["Personnel", "Commercial", "Transport", "Ambulance", "Administratif"]

        for i in range(count):
            category = categories[i % len(categories)]
            vehicles.append(generate_test_vehicle_data(category))

        return vehicles
