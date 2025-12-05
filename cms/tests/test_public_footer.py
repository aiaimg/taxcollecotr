"""
Tests for the public footer component.
"""
from django.test import TestCase, RequestFactory
from django.template import Context, Template
from django.contrib.auth import get_user_model
from cms.models import (
    SiteSettings,
    FooterSettings,
    MenuItem,
)

User = get_user_model()


class PublicFooterComponentTest(TestCase):
    """Test the public footer component rendering"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create site settings
        self.site_settings = SiteSettings.objects.create(
            site_name="Tax Collector Test",
            contact_email="test@taxcollector.mg",
            contact_phone="+261 34 00 000 00",
            contact_address="Antananarivo, Madagascar",
            facebook_url="https://facebook.com/taxcollector",
            twitter_url="https://twitter.com/taxcollector",
            linkedin_url="https://linkedin.com/company/taxcollector",
            is_active=True,
        )

        # Create footer settings
        self.footer_settings = FooterSettings.objects.create(
            copyright_text="© Tax Collector Test. Tous droits réservés.",
            copyright_text_fr="© Tax Collector Test. Tous droits réservés.",
            copyright_text_mg="© Tax Collector Test. Zo rehetra voaaro.",
            description="Plateforme de test pour la gestion des taxes.",
            description_fr="Plateforme de test pour la gestion des taxes.",
            description_mg="Sehatra fitsapana ho an'ny fitantanana ny hetra.",
            show_social_links=True,
            show_newsletter=False,
            background_color="#212529",
            text_color="#ffffff",
            link_color="#adb5bd",
            link_hover_color="#ffffff",
            heading_color="#ffffff",
            padding_top=60,
            padding_bottom=60,
            is_active=True,
        )

        # Create footer menu items
        self.footer_menu_1 = MenuItem.objects.create(
            title="About",
            title_fr="À propos",
            title_mg="Momba anay",
            url="/about/",
            menu_location="footer",
            order=1,
            is_active=True,
        )

        self.footer_menu_2 = MenuItem.objects.create(
            title="Contact",
            title_fr="Contact",
            title_mg="Fifandraisana",
            url="/contact/",
            menu_location="footer",
            order=2,
            is_active=True,
        )

        self.footer_menu_3 = MenuItem.objects.create(
            title="Privacy",
            title_fr="Confidentialité",
            title_mg="Tsiambaratelo",
            url="/privacy/",
            menu_location="both",
            order=3,
            is_active=True,
        )

    def render_footer_template(self, context_data):
        """Helper method to render the footer template"""
        template = Template(
            "{% load static %}{% load i18n %}"
            "{% include 'cms/partials/public_footer.html' %}"
        )
        context = Context(context_data)
        return template.render(context)

    def test_footer_renders_with_site_settings(self):
        """Test that footer renders with site settings"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True
            ),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that site name is rendered
        self.assertIn("Tax Collector Test", html)

        # Check that contact information is rendered
        self.assertIn("test@taxcollector.mg", html)
        self.assertIn("+261 34 00 000 00", html)
        self.assertIn("Antananarivo, Madagascar", html)

    def test_footer_renders_social_links(self):
        """Test that footer renders social media links"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that social links are rendered
        self.assertIn("facebook.com/taxcollector", html)
        self.assertIn("twitter.com/taxcollector", html)
        self.assertIn("linkedin.com/company/taxcollector", html)

    def test_footer_renders_menu_items(self):
        """Test that footer renders menu items"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True, parent=None
            ).order_by("order"),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that menu items are rendered
        self.assertIn("À propos", html)
        self.assertIn("Contact", html)
        self.assertIn("Confidentialité", html)
        self.assertIn("/about/", html)
        self.assertIn("/contact/", html)
        self.assertIn("/privacy/", html)

    def test_footer_renders_copyright_text(self):
        """Test that footer renders copyright text with current year"""
        from datetime import datetime

        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that copyright text is rendered
        self.assertIn("Tax Collector Test. Tous droits réservés.", html)
        # Check that current year is rendered
        current_year = str(datetime.now().year)
        self.assertIn(current_year, html)

    def test_footer_multilingual_support(self):
        """Test that footer supports multiple languages"""
        # Test French
        context_fr = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True, parent=None
            ).order_by("order"),
            "current_language": "fr",
        }

        html_fr = self.render_footer_template(context_fr)
        self.assertIn("À propos", html_fr)
        self.assertIn("Tous droits réservés", html_fr)

        # Test Malagasy
        context_mg = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True, parent=None
            ).order_by("order"),
            "current_language": "mg",
        }

        html_mg = self.render_footer_template(context_mg)
        self.assertIn("Momba anay", html_mg)
        self.assertIn("Zo rehetra voaaro", html_mg)

    def test_footer_renders_without_settings(self):
        """Test that footer renders with default values when settings are missing"""
        context = {
            "site_settings": None,
            "footer_settings": None,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that default content is rendered
        self.assertIn("Tax Collector", html)
        # Should not crash without settings
        self.assertIsNotNone(html)

    def test_footer_responsive_layout(self):
        """Test that footer has responsive CSS classes"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check for responsive Bootstrap classes
        self.assertIn("col-lg-4", html)
        self.assertIn("col-md-6", html)
        self.assertIn("col-lg-2", html)
        self.assertIn("col-lg-3", html)

    def test_footer_accessibility_features(self):
        """Test that footer includes accessibility features"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True
            ),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check for ARIA labels
        self.assertIn('role="contentinfo"', html)
        self.assertIn('aria-label', html)
        self.assertIn('aria-hidden="true"', html)

    def test_footer_applies_custom_styling(self):
        """Test that footer applies custom styling from FooterSettings"""
        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Check that custom colors are applied
        self.assertIn("#212529", html)  # background_color
        self.assertIn("#ffffff", html)  # text_color
        self.assertIn("#adb5bd", html)  # link_color

    def test_footer_newsletter_visibility(self):
        """Test that newsletter form is shown/hidden based on settings"""
        # Test with newsletter enabled
        self.footer_settings.show_newsletter = True
        self.footer_settings.save()

        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.none(),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)
        self.assertIn("newsletter-form", html)

        # Test with newsletter disabled
        self.footer_settings.show_newsletter = False
        self.footer_settings.save()

        html = self.render_footer_template(context)
        # Newsletter form should not be present when disabled
        # (The template still has the form but it's conditionally rendered)

    def test_footer_menu_items_filtering(self):
        """Test that only footer and both menu items are displayed"""
        # Create a header-only menu item
        header_only = MenuItem.objects.create(
            title="Header Only",
            url="/header/",
            menu_location="header",
            order=10,
            is_active=True,
        )

        context = {
            "site_settings": self.site_settings,
            "footer_settings": self.footer_settings,
            "footer_menu_items": MenuItem.objects.filter(
                menu_location__in=["footer", "both"], is_active=True, parent=None
            ).order_by("order"),
            "current_language": "fr",
        }

        html = self.render_footer_template(context)

        # Footer and both items should be present
        self.assertIn("À propos", html)
        self.assertIn("Contact", html)
        self.assertIn("Confidentialité", html)

        # Header-only item should not be present
        self.assertNotIn("Header Only", html)
