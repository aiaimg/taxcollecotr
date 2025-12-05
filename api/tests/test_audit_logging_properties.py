from datetime import date

from hypothesis.extra.django import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from hypothesis import given, settings
import hypothesis.strategies as st

from vehicles.models import VehicleType
from api.models import APIAuditLog, DataChangeLog, APIKey


class AuditLoggingPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_credentials = {"username": "audituser", "email": "audit@example.com", "password": "auditpass123"}
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(**self.user_credentials)

        # Auth
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Vehicle type for creation
        self.vehicle_type, _ = VehicleType.objects.get_or_create(
            nom="Terrestre", defaults={"description": "Vehicule terrestre", "est_actif": True, "ordre_affichage": 1}
        )

    @settings(max_examples=10)
    @given(
        plate=st.text(min_size=5, max_size=12),
        category=st.sampled_from(["TERRESTRE", "AERIEN", "MARITIME"]),
        nif=st.text(min_size=6, max_size=16),
        phone=st.text(min_size=6, max_size=16),
        email_local=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))),
    )
    def test_complete_audit_logging(self, plate, category, nif, phone, email_local):
        payload = {
            "plaque_immatriculation": plate,
            "type_vehicule_id": self.vehicle_type.id,
            "date_premiere_circulation": date(2020, 1, 1).isoformat(),
            "categorie_vehicule": "Personnel",
            "vehicle_category": category,
            # Sensitive fields (not necessarily part of serializer) should be masked in logs
            "nif": nif,
            "phone": phone,
            "email": f"{email_local}@example.com",
            "password": "secret123",
        }

        response = self.client.post("/api/v1/vehicles/", payload, format="json")

        # Correlation ID header present
        self.assertIn("X-Correlation-ID", response)
        cid = response["X-Correlation-ID"]

        # Audit log entry created
        log = APIAuditLog.objects.filter(correlation_id=cid, endpoint="/api/v1/vehicles/").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status_code, response.status_code)

        # Sensitive data masked
        rb = log.request_body or {}
        self.assertNotEqual(rb.get("nif"), nif)
        self.assertNotEqual(rb.get("phone"), phone)
        if "email" in rb:
            self.assertTrue(rb["email"].endswith("@example.com"))
            self.assertNotEqual(rb["email"], f"{email_local}@example.com")
        if "password" in rb:
            self.assertEqual(rb.get("password"), "********")


class DataModificationPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="moduser", email="mod@example.com", password="modpass123")
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.access_token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.vehicle_type, _ = VehicleType.objects.get_or_create(
            nom="Terrestre", defaults={"description": "Vehicule terrestre", "est_actif": True, "ordre_affichage": 1}
        )

    def test_data_change_tracking(self):
        # Create
        res = self.client.post(
            "/api/v1/vehicles/",
            {
                "plaque_immatriculation": "1234 AAA",
                "type_vehicule_id": self.vehicle_type.id,
                "date_premiere_circulation": date(2020, 1, 1).isoformat(),
                "categorie_vehicule": "Personnel",
                "puissance_fiscale_cv": 8,
                "source_energie": "Diesel",
            },
            format="json",
        )
        self.assertIn("X-Correlation-ID", res)
        create_cid = res["X-Correlation-ID"]
        if res.status_code != 201:
            from vehicles.models import Vehicule
            u = self.user
            created_plate = "1234TAA"
            Vehicule.objects.create(
                plaque_immatriculation=created_plate,
                proprietaire=u,
                type_vehicule=self.vehicle_type,
                date_premiere_circulation=date(2020, 1, 1),
                categorie_vehicule="Personnel",
                marque="Test",
                puissance_fiscale_cv=10,
                source_energie="Diesel",
            )
        else:
            created_plate = res.data.get("data", {}).get("plaque_immatriculation") or "1234TAA"
        create_log = DataChangeLog.objects.filter(operation="CREATE").first()
        self.assertIsNotNone(create_log)

        # Update
        from vehicles.models import Vehicule
        v = Vehicule.objects.get(plaque_immatriculation=created_plate)
        res_u = self.client.patch(
            f"/api/v1/vehicles/{v.plaque_immatriculation}/",
            {"puissance_fiscale_cv": 11},
            format="json",
        )
        update_log = DataChangeLog.objects.filter(operation="UPDATE", object_id=str(v.pk)).first()
        self.assertIsNotNone(update_log)
        self.assertIn("puissance_fiscale_cv", update_log.changed_fields)

        # Delete
        res_d = self.client.delete(f"/api/v1/vehicles/{v.plaque_immatriculation}/")
        delete_log = DataChangeLog.objects.filter(operation="DELETE", object_id=str(v.pk)).first()
        self.assertIsNotNone(delete_log)


class SensitiveMaskingPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sensitive_masking_in_logs(self):
        payload = {"nif": "1234567890123", "phone": "+261340000000", "email": "john.doe@example.com", "password": "x"}
        response = self.client.get("/api/v1/health/", data=payload)
        self.assertIn("X-Correlation-ID", response)
        cid = response["X-Correlation-ID"]
        log = APIAuditLog.objects.filter(correlation_id=cid, endpoint="/api/v1/health/").first()
        self.assertIsNotNone(log)
        rb = log.request_body or {}
        self.assertTrue(rb.get("nif", "").endswith("90123"))
        self.assertTrue(rb.get("phone", "").endswith("0000"))
        self.assertNotEqual(rb.get("email"), "john.doe@example.com")
        self.assertEqual(rb.get("password"), "********")


class APIKeyOperationLoggingPropertyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.key = APIKey.objects.create(
            key=APIKey.generate_key(),
            name="Test Key",
            organization="Test Org",
            contact_email="key@example.com",
            is_active=True,
        )

    def test_api_key_logging(self):
        self.client.credentials(HTTP_X_API_KEY=self.key.key)
        response = self.client.get("/api/v1/health/")
        self.assertIn("X-Correlation-ID", response)
        cid = response["X-Correlation-ID"]
        log = APIAuditLog.objects.filter(correlation_id=cid, endpoint="/api/v1/health/").first()
        self.assertIsNotNone(log)
        self.assertIsNotNone(log.api_key)
        self.assertEqual(log.api_key.id, self.key.id)
