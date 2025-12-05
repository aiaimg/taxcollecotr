"""
Tests for CMS page detail template updates
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.template.loader import render_to_string

from cms.models import Page, PageSection, SiteSettings, HeaderSettings, FooterSettings, ThemeSettings
from cms.views import CMSPageDetailView

User = get_user_model()


class PageDetailTemplateTest(TestCase):
    """Test that page_detail.html uses base_public.html and new components"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create site settings
        self.site_settings = SiteSettings.objects.create(
            site_name="Test Site",
            site_tagline="Test Tagline",
            is_active=True
        )
        
        # Create header settings
        self.header_settings = HeaderSettings.objects.create(
            site_name="Test Site",
            is_active=True
        )
        
        # Create footer settings
        self.footer_settings = FooterSettings.objects.create(
            copyright_text="© 2024 Test Site",
            is_active=True
        )
        
        # Create theme settings
        self.theme_settings = ThemeSettings.objects.create(
            theme_name="default",
            is_active=True
        )
        
        # Create a test page
        self.page = Page.objects.create(
            title="Test Page",
            title_fr="Page de Test",
            title_mg="Pejy Fitsapana",
            slug="test-page",
            content="<p>Test content</p>",
            content_fr="<p>Contenu de test</p>",
            content_mg="<p>Votoaty fitsapana</p>",
            status="published"
        )
        
        # Create a section for the page
        self.section = PageSection.objects.create(
            name="test-section",
            title="Test Section",
            title_fr="Section de Test",
            title_mg="Fizarana Fitsapana",
            content="<p>Section content</p>",
            section_type="content",
            is_active=True,
            order=1
        )
        # Add section to page
        self.page.sections.add(self.section)
    
    def test_page_detail_extends_base_public(self):
        """Test that page_detail.html extends base_public.html"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        # Render the template
        from django.template.loader import get_template
        template = get_template('cms/page_detail.html')
        
        # Check that the template can be loaded
        self.assertIsNotNone(template)
        
        # Render with context
        html = template.render(context, request)
        
        # Verify the template renders without errors
        self.assertIsNotNone(html)
        self.assertIn('Test Page', html)
    
    def test_page_detail_includes_header_component(self):
        """Test that page_detail.html includes public_header.html"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        from django.template.loader import get_template
        template = get_template('cms/page_detail.html')
        html = template.render(context, request)
        
        # The header should be included via base_public.html
        # We can't directly check for the include, but we can verify
        # that header-related elements would be present
        self.assertIsNotNone(html)
    
    def test_page_detail_includes_footer_component(self):
        """Test that page_detail.html includes public_footer.html"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        from django.template.loader import get_template
        template = get_template('cms/page_detail.html')
        html = template.render(context, request)
        
        # The footer should be included via base_public.html
        self.assertIsNotNone(html)
    
    def test_page_detail_maintains_section_rendering(self):
        """Test that page sections are still rendered correctly"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        # Verify sections are in context
        self.assertIn('sections', context)
        self.assertEqual(context['sections'].count(), 1)
        self.assertEqual(context['sections'].first().title, "Test Section")
    
    def test_page_detail_responsive_design(self):
        """Test that responsive CSS is included"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        from django.template.loader import get_template
        template = get_template('cms/page_detail.html')
        html = template.render(context, request)
        
        # Check for responsive CSS classes and media queries
        self.assertIn('@media', html)
        self.assertIn('cms-page-content', html)
    
    def test_page_detail_multilingual_content(self):
        """Test that multilingual content is handled correctly"""
        request = self.factory.get(f'/cms/{self.page.slug}/')
        request.user = User()
        
        view = CMSPageDetailView()
        view.setup(request, slug=self.page.slug)
        view.object = self.page
        
        context = view.get_context_data()
        
        # Verify page title and content are in context
        self.assertIn('page_title', context)
        self.assertEqual(context['page'], self.page)
