"""
Management command to create test agents for the Tax Collector system
Creates Agent Partenaire and Agent Gouvernement for testing
"""

import random
import string
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from administration.models import AgentVerification
from core.models import UserProfile
from payments.models import AgentPartenaireProfile, CashSystemConfig


class Command(BaseCommand):
    help = "Create test agents (Agent Partenaire and Agent Gouvernement) for testing"

    def add_arguments(self, parser):
        parser.add_argument("--clean", action="store_true", help="Delete existing test agents before creating new ones")
        parser.add_argument("--partenaire", action="store_true", help="Create Agent Partenaire only")
        parser.add_argument("--government", action="store_true", help="Create Agent Gouvernement only")

    def handle(self, *args, **options):
        clean = options["clean"]
        create_partenaire = options["partenaire"]
        create_government = options["government"]

        # If no specific type is requested, create both with multiple agents
        if not create_partenaire and not create_government:
            create_partenaire = True
            create_government = True

        if clean:
            self.stdout.write(self.style.WARNING("Cleaning existing test agents..."))
            self.clean_test_agents()

        # Ensure CashSystemConfig exists
        self.ensure_cash_system_config()

        agents_created = []

        if create_partenaire:
            self.stdout.write(self.style.SUCCESS("\n=== Creating Agent Partenaire ==="))
            # Create multiple agent partenaires
            agent_partenaire1 = self.create_agent_partenaire(
                username="agent_partenaire1",
                password="agentpartenaire123",
                email="agent.partenaire1@taxcollector.mg",
                first_name="Agent",
                last_name="Partenaire 1",
                agent_id_prefix="AP",
                full_name="Agent Partenaire Test 1",
                location="Antananarivo - Analakely",
                commission_rate=Decimal("2.50"),
                use_default=False,
            )
            if agent_partenaire1:
                agents_created.append(("Agent Partenaire 1", agent_partenaire1))

            agent_partenaire2 = self.create_agent_partenaire(
                username="agent_partenaire2",
                password="agentpartenaire123",
                email="agent.partenaire2@taxcollector.mg",
                first_name="Agent",
                last_name="Partenaire 2",
                agent_id_prefix="AP",
                full_name="Agent Partenaire Test 2",
                location="Antananarivo - Ivandry",
                commission_rate=Decimal("3.00"),
                use_default=False,
            )
            if agent_partenaire2:
                agents_created.append(("Agent Partenaire 2", agent_partenaire2))

        if create_government:
            self.stdout.write(self.style.SUCCESS("\n=== Creating Agent Gouvernement ==="))
            # Create multiple agent governments
            agent_government1 = self.create_agent_government(
                username="agent_government1",
                password="agentgov123",
                email="agent.government1@taxcollector.mg",
                first_name="Agent",
                last_name="Gouvernement 1",
                badge_prefix="AG",
                zone="Antananarivo Centre",
            )
            if agent_government1:
                agents_created.append(("Agent Gouvernement 1", agent_government1))

            agent_government2 = self.create_agent_government(
                username="agent_government2",
                password="agentgov123",
                email="agent.government2@taxcollector.mg",
                first_name="Agent",
                last_name="Gouvernement 2",
                badge_prefix="AG",
                zone="Antananarivo - Atsimondrano",
            )
            if agent_government2:
                agents_created.append(("Agent Gouvernement 2", agent_government2))

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("SUMMARY - Test Agents Created"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        for agent_type, agent in agents_created:
            if "Partenaire" in agent_type:
                self.stdout.write(self.style.SUCCESS(f"\n{agent_type}:"))
                self.stdout.write(f"  Username: {agent.user.username}")
                self.stdout.write(f"  Password: agentpartenaire123")
                self.stdout.write(f"  Agent ID: {agent.agent_id}")
                self.stdout.write(f"  Full Name: {agent.full_name}")
                self.stdout.write(f"  Location: {agent.collection_location}")
                self.stdout.write(f"  Commission Rate: {agent.get_commission_rate()}%")
                self.stdout.write(f'  Status: {"Active" if agent.is_active else "Inactive"}')
                self.stdout.write(f"  Login URL: /administration/agent-partenaire/login/")
            elif "Gouvernement" in agent_type:
                self.stdout.write(self.style.SUCCESS(f"\n{agent_type}:"))
                self.stdout.write(f"  Username: {agent.user.username}")
                self.stdout.write(f"  Password: agentgov123")
                self.stdout.write(f"  Badge Number: {agent.numero_badge}")
                self.stdout.write(f"  Zone: {agent.zone_affectation}")
                self.stdout.write(f'  Status: {"Active" if agent.est_actif else "Inactive"}')
                self.stdout.write(f"  Login URL: /administration/agent-government/login/")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("All agents are ready for testing!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

    def clean_test_agents(self):
        """Clean existing test agents"""
        # Delete Agent Partenaire test users
        test_usernames = ["agent_partenaire1", "agent_partenaire2", "agent_government1", "agent_government2"]
        deleted_count = 0
        for username in test_usernames:
            try:
                user = User.objects.get(username=username)
                if hasattr(user, "agent_partenaire_profile"):
                    user.agent_partenaire_profile.delete()
                if hasattr(user, "agent_verification"):
                    user.agent_verification.delete()
                user.delete()
                deleted_count += 1
                self.stdout.write(f"  Deleted test agent: {username}")
            except User.DoesNotExist:
                pass

        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Cleaned {deleted_count} test agents"))
        else:
            self.stdout.write("  No test agents found to clean")

    def ensure_cash_system_config(self):
        """Ensure CashSystemConfig exists"""
        try:
            config = CashSystemConfig.get_config()
            if not config:
                CashSystemConfig.objects.create(
                    default_commission_rate=Decimal("2.00"),
                    dual_verification_threshold=Decimal("500000.00"),
                    reconciliation_tolerance=Decimal("1000.00"),
                )
                self.stdout.write("  Created CashSystemConfig")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Warning: Could not create CashSystemConfig: {e}"))

    def create_agent_partenaire(
        self,
        username="agent_partenaire1",
        password="agentpartenaire123",
        email="agent.partenaire1@taxcollector.mg",
        first_name="Agent",
        last_name="Partenaire",
        agent_id_prefix="AP",
        full_name="Agent Partenaire Test",
        location="Antananarivo - Analakely",
        commission_rate=Decimal("2.50"),
        use_default=False,
        phone="+261341234567",
    ):
        """Create Agent Partenaire"""
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created user: {username}"))
        else:
            # Update password to ensure we know it
            user.set_password(password)
            user.is_active = True
            user.save()
            self.stdout.write(self.style.WARNING(f"  ⚠ User already exists: {username} (password reset)"))

        # Create user profile if it doesn't exist
        if not hasattr(user, "profile"):
            UserProfile.objects.create(
                user=user, user_type="individual", telephone=phone, verification_status="verified"
            )
            self.stdout.write("  ✓ Created user profile")

        # Generate unique agent ID
        while True:
            agent_id = f"{agent_id_prefix}{random.randint(10000, 99999)}"
            if not AgentPartenaireProfile.objects.filter(agent_id=agent_id).exists():
                break

        # Create or get agent profile
        agent, created = AgentPartenaireProfile.objects.get_or_create(
            user=user,
            defaults={
                "agent_id": agent_id,
                "full_name": full_name,
                "phone_number": phone,
                "collection_location": location,
                "commission_rate": commission_rate,
                "use_default_commission": use_default,
                "is_active": True,
                "created_by": user,  # Self-created for test
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created Agent Partenaire: {agent.agent_id}"))
        else:
            # Update to ensure it's active and has correct settings
            agent.is_active = True
            agent.commission_rate = commission_rate
            agent.use_default_commission = use_default
            agent.collection_location = location
            agent.full_name = full_name
            agent.save()
            self.stdout.write(self.style.WARNING(f"  ⚠ Agent Partenaire already exists: {agent.agent_id} (updated)"))

        return agent

    def create_agent_government(
        self,
        username="agent_government1",
        password="agentgov123",
        email="agent.government1@taxcollector.mg",
        first_name="Agent",
        last_name="Gouvernement",
        badge_prefix="AG",
        zone="Antananarivo Centre",
        phone="+261341234568",
    ):
        """Create Agent Gouvernement"""
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created user: {username}"))
        else:
            # Update password to ensure we know it
            user.set_password(password)
            user.is_active = True
            user.save()
            self.stdout.write(self.style.WARNING(f"  ⚠ User already exists: {username} (password reset)"))

        # Create user profile if it doesn't exist
        if not hasattr(user, "profile"):
            UserProfile.objects.create(
                user=user, user_type="government", telephone=phone, verification_status="verified"
            )
            self.stdout.write("  ✓ Created user profile")

        # Generate unique badge number
        while True:
            badge_number = f"{badge_prefix}{random.randint(1000, 9999)}"
            if not AgentVerification.objects.filter(numero_badge=badge_number).exists():
                break

        # Create or get agent verification
        agent, created = AgentVerification.objects.get_or_create(
            user=user, defaults={"numero_badge": badge_number, "zone_affectation": zone, "est_actif": True}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created Agent Gouvernement: {agent.numero_badge}"))
        else:
            # Update to ensure it's active and has correct settings
            agent.est_actif = True
            agent.zone_affectation = zone
            agent.save()
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Agent Gouvernement already exists: {agent.numero_badge} (updated)")
            )

        return agent
