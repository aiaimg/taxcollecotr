"""
Tests for PublicHomeView
"""
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils.translation import activate

from cms.models import FooterSettings, HeaderSettings, Page, PageSection, SiteSettings, ThemeSettings
from cms.views import PublicHomeView

User = get_user_model()


class PublicHomeViewTests(TestCase):
    """Test suite for PublicHomeView"""

    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.view = PublicHomeView.as_view()

        # Create CMS settings
        self.site_settings = SiteSettings.objects.create(
            site_name="Test Tax Collector",
            contact_email="test@example.com",
            is_active=True,
        )

        self.header_settings = HeaderSettings.objects.create(
            site_name="Test Tax Collector",
            is_active=True,
        )

        self.footer_settings = FooterSettings.objects.create(
            copyright_text="© Test Tax Collector",
            is_active=True,
        )

        self.theme_settings = ThemeSettings.objects.create(
            theme_name="default",
            is_active=True,
        )

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )

        # Create homepage
        self.homepage = Page.objects.create(
            title="Home",
            title_fr="Accueil",
            title_mg="Fandraisana",
            slug="home",
            status="published",
            is_homepage=True,
        )

        # Create page sections
        self.section1 = PageSection.objects.create(
            name="Hero Section",
            section_type="hero",
            title="Welcome",
            title_fr="Bienvenue",
            title_mg="Tonga soa",
            is_active=True,
            order=1,
        )

        self.section2 = PageSection.objects.create(
            name="Features Section",
            section_type="features",
            title="Our Features",
            title_fr="Nos Fonctionnalités",
            title_mg="Ny Toetra",
            is_active=True,
            order=2,
        )

        # Add sections to homepage
        self.homepage.sections.add(self.section1, self.section2)

    def test_view_returns_200_status(self):
        """Test that the view returns 200 status code"""
        request = self.factory.get("/")
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_cms_settings(self):
        """Test that context contains all CMS settings"""
        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check CMS settings are in context
        self.assertIn("site_settings", context)
        self.assertIn("header_settings", context)
        self.assertIn("footer_settings", context)
        self.assertIn("theme_settings", context)
        self.assertIn("header_menu_items", context)
        self.assertIn("footer_menu_items", context)

        # Verify settings are correct
        self.assertEqual(context["site_settings"], self.site_settings)
        self.assertEqual(context["header_settings"], self.header_settings)
        self.assertEqual(context["footer_settings"], self.footer_settings)
        self.assertEqual(context["theme_settings"], self.theme_settings)

    def test_context_contains_homepage_and_sections(self):
        """Test that context contains homepage and its sections"""
        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check homepage is in context
        self.assertIn("homepage", context)
        self.assertEqual(context["homepage"], self.homepage)

        # Check sections are in context
        self.assertIn("sections", context)
        sections = list(context["sections"])
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0], self.section1)
        self.assertEqual(sections[1], self.section2)

    def test_authenticated_user_context(self):
        """Test context for authenticated user"""
        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check authentication status
        self.assertIn("is_authenticated", context)
        self.assertTrue(context["is_authenticated"])

    def test_unauthenticated_user_context(self):
        """Test context for unauthenticated user"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/")
        request.user = AnonymousUser()
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check authentication status
        self.assertIn("is_authenticated", context)
        self.assertFalse(context["is_authenticated"])

    def test_language_in_context(self):
        """Test that current language is in context"""
        activate("fr")
        
        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check language is in context
        self.assertIn("current_language", context)
        self.assertEqual(context["current_language"], "fr")

    def test_missing_cms_settings_handled_gracefully(self):
        """Test that missing CMS settings are handled gracefully"""
        # Delete all settings
        SiteSettings.objects.all().delete()
        HeaderSettings.objects.all().delete()
        FooterSettings.objects.all().delete()
        ThemeSettings.objects.all().delete()

        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check that context still contains keys but with None values
        self.assertIn("site_settings", context)
        self.assertIn("header_settings", context)
        self.assertIn("footer_settings", context)
        self.assertIn("theme_settings", context)
        self.assertIsNone(context["site_settings"])
        self.assertIsNone(context["header_settings"])
        self.assertIsNone(context["footer_settings"])
        self.assertIsNone(context["theme_settings"])

    def test_missing_homepage_handled_gracefully(self):
        """Test that missing homepage is handled gracefully"""
        # Delete homepage
        Page.objects.all().delete()

        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check that homepage is None
        self.assertIn("homepage", context)
        self.assertIsNone(context["homepage"])

        # Check that sections is empty
        self.assertIn("sections", context)
        self.assertEqual(len(list(context["sections"])), 0)

    def test_inactive_sections_not_included(self):
        """Test that inactive sections are not included"""
        # Make section2 inactive
        self.section2.is_active = False
        self.section2.save()

        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check only active section is included
        sections = list(context["sections"])
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], self.section1)

    def test_sections_ordered_correctly(self):
        """Test that sections are ordered by order field"""
        # Create additional section with lower order
        section0 = PageSection.objects.create(
            name="Top Section",
            section_type="hero",
            title="Top",
            is_active=True,
            order=0,
        )
        self.homepage.sections.add(section0)

        request = self.factory.get("/")
        request.user = self.user
        
        view_instance = PublicHomeView()
        view_instance.request = request
        context = view_instance.get_context_data()

        # Check sections are ordered
        sections = list(context["sections"])
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0], section0)
        self.assertEqual(sections[1], self.section1)
        self.assertEqual(sections[2], self.section2)

    def test_premium_layout_structure_present(self):
        request = self.factory.get("/")
        request.user = self.user
        response = self.view(request)
        response.render()
        content = response.content.decode()
        self.assertIn("premium-container", content)
        self.assertIn("premium-workspace", content)
        self.assertIn("premium-utility", content)
        self.assertIn("Entrée", content)
        self.assertIn("Sortie", content)
        self.assertIn("Télécharger la quittance", content)
