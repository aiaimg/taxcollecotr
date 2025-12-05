from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from administration.models import AgentVerification
from core.models import UserProfile
from payments.models import AgentPartenaireProfile


class Command(BaseCommand):
    help = "Reset or create test accounts with known passwords"

    def handle(self, *args, **options):
        users = []

        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        admin.is_superuser = True
        admin.is_staff = True
        admin.set_password("Admin123!")
        admin.first_name = "Admin"
        admin.last_name = "User"
        admin.is_active = True
        admin.save()
        users.append(("admin", "Admin123!"))

        staff, _ = User.objects.get_or_create(username="staff1", defaults={"email": "staff1@example.com"})
        staff.is_staff = True
        staff.set_password("Staff123!")
        staff.first_name = "Staff"
        staff.last_name = "User"
        staff.is_active = True
        staff.save()
        users.append(("staff1", "Staff123!"))

        indiv, _ = User.objects.get_or_create(username="testuser1", defaults={"email": "testuser1@example.com"})
        indiv.set_password("TestPass123!")
        indiv.is_active = True
        indiv.save()
        UserProfile.objects.get_or_create(user=indiv, defaults={"user_type": "individual", "langue_preferee": "fr"})
        users.append(("testuser1", "TestPass123!"))

        company, _ = User.objects.get_or_create(username="company1", defaults={"email": "company1@example.com"})
        company.set_password("Company123!")
        company.is_active = True
        company.save()
        up, created = UserProfile.objects.get_or_create(user=company)
        up.user_type = "company"
        up.langue_preferee = "fr"
        up.save()
        users.append(("company1", "Company123!"))

        agentp, _ = User.objects.get_or_create(username="agentp1", defaults={"email": "agentp1@example.com"})
        agentp.set_password("Agent123!")
        agentp.is_active = True
        agentp.is_staff = True
        agentp.save()
        UserProfile.objects.get_or_create(user=agentp, defaults={"user_type": "individual", "langue_preferee": "fr"})
        AgentPartenaireProfile.objects.get_or_create(
            user=agentp,
            defaults={
                "agent_id": "AGP001",
                "full_name": "Agent Partenaire",
                "phone_number": "+261320000001",
                "collection_location": "Antananarivo",
                "use_default_commission": True,
                "is_active": True,
            },
        )
        users.append(("agentp1", "Agent123!"))

        agentg, _ = User.objects.get_or_create(username="agentg1", defaults={"email": "agentg1@example.com"})
        agentg.set_password("Agent123!")
        agentg.is_active = True
        agentg.is_staff = True
        agentg.save()
        UserProfile.objects.get_or_create(
            user=agentg, defaults={"user_type": "public_institution", "langue_preferee": "fr"}
        )
        AgentVerification.objects.get_or_create(
            user=agentg,
            defaults={
                "numero_badge": "GOV001",
                "zone_affectation": "Antananarivo",
                "est_actif": True,
            },
        )
        users.append(("agentg1", "Agent123!"))

        for u, p in users:
            self.stdout.write(f"{u}:{p}")
