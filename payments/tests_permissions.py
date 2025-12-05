"""
Tests for cash payment permission system
Tests permission groups, decorators, and view access control
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from core.models import User
from payments.decorators import admin_staff_required, agent_partenaire_or_admin_required, agent_partenaire_required
from payments.models import AgentPartenaireProfile


class PermissionGroupsTestCase(TestCase):
    """Test permission groups setup"""

    def setUp(self):
        """Set up test data"""
        # Create groups
        self.agent_group = Group.objects.create(name="Agent Partenaire")
        self.admin_group = Group.objects.create(name="Admin Staff")

        # Create users
        self.agent_user = User.objects.create_user(username="agent1", email="agent1@test.com", password="testpass123")

        self.admin_user = User.objects.create_user(
            username="admin1", email="admin1@test.com", password="testpass123", is_staff=True
        )

        self.superuser = User.objects.create_superuser(
            username="superuser", email="super@test.com", password="testpass123"
        )

        self.regular_user = User.objects.create_user(
            username="regular", email="regular@test.com", password="testpass123"
        )

        # Create agent profile
        self.agent_profile = AgentPartenaireProfile.objects.create(
            user=self.agent_user,
            agent_id="AGT001",
            full_name="Test Agent",
            phone_number="0340000000",
            collection_location="Antananarivo",
            is_active=True,
            created_by=self.admin_user,
        )

        # Assign groups
        self.agent_user.groups.add(self.agent_group)
        self.admin_user.groups.add(self.admin_group)

    def test_agent_group_exists(self):
        """Test that Agent Partenaire group exists"""
        self.assertTrue(Group.objects.filter(name="Agent Partenaire").exists())

    def test_admin_group_exists(self):
        """Test that Admin Staff group exists"""
        self.assertTrue(Group.objects.filter(name="Admin Staff").exists())

    def test_agent_in_group(self):
        """Test that agent user is in Agent Partenaire group"""
        self.assertTrue(self.agent_user.groups.filter(name="Agent Partenaire").exists())

    def test_admin_in_group(self):
        """Test that admin user is in Admin Staff group"""
        self.assertTrue(self.admin_user.groups.filter(name="Admin Staff").exists())


class PermissionDecoratorsTestCase(TestCase):
    """Test permission decorators"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create groups
        self.agent_group = Group.objects.create(name="Agent Partenaire")
        self.admin_group = Group.objects.create(name="Admin Staff")

        # Create users
        self.agent_user = User.objects.create_user(username="agent1", email="agent1@test.com", password="testpass123")

        self.admin_user = User.objects.create_user(
            username="admin1", email="admin1@test.com", password="testpass123", is_staff=True
        )

        self.superuser = User.objects.create_superuser(
            username="superuser", email="super@test.com", password="testpass123"
        )

        self.regular_user = User.objects.create_user(
            username="regular", email="regular@test.com", password="testpass123"
        )

        # Create agent profile
        self.agent_profile = AgentPartenaireProfile.objects.create(
            user=self.agent_user,
            agent_id="AGT001",
            full_name="Test Agent",
            phone_number="0340000000",
            collection_location="Antananarivo",
            is_active=True,
            created_by=self.admin_user,
        )

        # Assign groups
        self.agent_user.groups.add(self.agent_group)
        self.admin_user.groups.add(self.admin_group)

    def _create_request(self, user):
        """Helper to create request with user and messages"""
        request = self.factory.get("/")
        request.user = user
        # Add session and messages
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_agent_decorator_allows_agent(self):
        """Test that agent_partenaire_required allows agent users"""

        @agent_partenaire_required
        def test_view(request):
            return "success"

        request = self._create_request(self.agent_user)
        response = test_view(request)
        self.assertEqual(response, "success")

    def test_agent_decorator_allows_superuser(self):
        """Test that agent_partenaire_required allows superusers"""
        # Create agent profile for superuser
        AgentPartenaireProfile.objects.create(
            user=self.superuser,
            agent_id="AGT999",
            full_name="Super Agent",
            phone_number="0340000001",
            collection_location="Antananarivo",
            is_active=True,
            created_by=self.admin_user,
        )

        @agent_partenaire_required
        def test_view(request):
            return "success"

        request = self._create_request(self.superuser)
        response = test_view(request)
        self.assertEqual(response, "success")

    def test_admin_decorator_allows_admin(self):
        """Test that admin_staff_required allows admin users"""

        @admin_staff_required
        def test_view(request):
            return "success"

        request = self._create_request(self.admin_user)
        response = test_view(request)
        self.assertEqual(response, "success")

    def test_admin_decorator_allows_superuser(self):
        """Test that admin_staff_required allows superusers"""

        @admin_staff_required
        def test_view(request):
            return "success"

        request = self._create_request(self.superuser)
        response = test_view(request)
        self.assertEqual(response, "success")

    def test_combined_decorator_allows_agent(self):
        """Test that agent_partenaire_or_admin_required allows agents"""

        @agent_partenaire_or_admin_required
        def test_view(request):
            return "success"

        request = self._create_request(self.agent_user)
        response = test_view(request)
        self.assertEqual(response, "success")

    def test_combined_decorator_allows_admin(self):
        """Test that agent_partenaire_or_admin_required allows admins"""

        @agent_partenaire_or_admin_required
        def test_view(request):
            return "success"

        request = self._create_request(self.admin_user)
        response = test_view(request)
        self.assertEqual(response, "success")
