from django.test import RequestFactory, TestCase

from cms.context_processors import cms_context
from cms.models import FooterSettings, HeaderSettings, SiteSettings, ThemeSettings


class CMSContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_cms_context_defaults(self):
        """Test that context processor returns None or defaults when no settings exist."""
        context = cms_context(self.request)
        self.assertIn("header_settings", context)
        self.assertIn("footer_settings", context)
        self.assertIn("site_settings", context)
        self.assertIn("theme_settings", context)
        # Depending on implementation, these might be None or default objects
        # Based on get_cms_context implementation, they might be None if not found

    def test_cms_context_with_data(self):
        """Test that context processor returns correct data when settings exist."""
        header = HeaderSettings.objects.create(site_name="Test Site", is_active=True)
        footer = FooterSettings.objects.create(copyright_text="Test Copyright", is_active=True)

        context = cms_context(self.request)
        self.assertEqual(context["header_settings"], header)
        self.assertEqual(context["footer_settings"], footer)
        self.assertEqual(context["header_settings"].site_name, "Test Site")
        self.assertEqual(context["footer_settings"].copyright_text, "Test Copyright")
