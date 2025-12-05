"""
Tests for CMS URL routing
"""
from django.test import TestCase
from django.urls import resolve, reverse

from cms.views import CMSPageDetailView, Home2View, PublicHomeView


class CMSURLTests(TestCase):
    """Test suite for CMS URL routing"""

    def test_root_url_resolves_to_public_home_view(self):
        """Test that root URL resolves to PublicHomeView"""
        url = reverse("cms:home")
        self.assertEqual(url, "/")
        
        resolver = resolve("/")
        self.assertEqual(resolver.func.view_class, PublicHomeView)
        self.assertEqual(resolver.view_name, "cms:home")

    def test_home2_url_resolves_correctly(self):
        """Test that home2 URL resolves correctly"""
        url = reverse("cms:home2")
        self.assertEqual(url, "/home2/")
        
        resolver = resolve("/home2/")
        self.assertEqual(resolver.func.view_class, Home2View)
        self.assertEqual(resolver.view_name, "cms:home2")

    def test_page_detail_url_resolves_correctly(self):
        """Test that page detail URL resolves correctly"""
        url = reverse("cms:page_detail", kwargs={"slug": "about"})
        self.assertEqual(url, "/page/about/")
        
        resolver = resolve("/page/about/")
        self.assertEqual(resolver.func.view_class, CMSPageDetailView)
        self.assertEqual(resolver.view_name, "cms:page_detail")
        self.assertEqual(resolver.kwargs["slug"], "about")

    def test_page_detail_url_with_different_slugs(self):
        """Test that page detail URL works with different slugs"""
        test_slugs = ["contact", "privacy-policy", "terms-of-service", "faq"]
        
        for slug in test_slugs:
            url = reverse("cms:page_detail", kwargs={"slug": slug})
            self.assertEqual(url, f"/page/{slug}/")
            
            resolver = resolve(f"/page/{slug}/")
            self.assertEqual(resolver.func.view_class, CMSPageDetailView)
            self.assertEqual(resolver.kwargs["slug"], slug)

    def test_all_url_patterns_are_named(self):
        """Test that all URL patterns have names"""
        from cms.urls import urlpatterns
        
        for pattern in urlpatterns:
            self.assertIsNotNone(pattern.name, f"URL pattern {pattern.pattern} should have a name")

    def test_url_namespace_is_cms(self):
        """Test that URL namespace is 'cms'"""
        from cms.urls import app_name
        
        self.assertEqual(app_name, "cms")
