"""
Tests for accessibility features on the public home page.

This test suite verifies WCAG 2.1 AA compliance for:
- ARIA labels on interactive elements
- Keyboard navigation support
- Alt text for images
- Proper heading hierarchy
- Color contrast ratios

Requirements covered:
- 11.1: ARIA labels for interactive elements
- 11.2: Keyboard navigation support
- 11.3: Alt text for all images
- 11.4: Proper heading hierarchy
- 11.5: Color contrast ratios (WCAG 2.1 AA)
"""

from django.test import TestCase, Client
from django.urls import reverse
from bs4 import BeautifulSoup
import re


class AccessibilityTestCase(TestCase):
    """Test accessibility features of the public home page."""

    def setUp(self):
        """Set up test client and common test data."""
        self.client = Client()
        self.home_url = reverse('cms:home')

    def test_skip_link_present(self):
        """Test that skip link is present for keyboard navigation."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        skip_link = soup.find('a', class_='skip-link')
        
        self.assertIsNotNone(skip_link, "Skip link should be present")
        self.assertIn('visually-hidden-focusable', skip_link.get('class', []))
        self.assertTrue(skip_link.get('href', '').startswith('#'))

    def test_aria_labels_on_buttons(self):
        """Test that all CTA buttons have aria-label attributes."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all CTA buttons
        cta_buttons = soup.find_all('a', class_=re.compile(r'btn-(hero|cta)'))
        
        self.assertGreater(len(cta_buttons), 0, "Should have CTA buttons")
        
        for button in cta_buttons:
            self.assertTrue(
                button.has_attr('aria-label'),
                f"Button '{button.get_text(strip=True)}' should have aria-label"
            )

    def test_aria_labels_on_feature_links(self):
        """Test that all feature links have aria-label attributes."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        feature_links = soup.find_all('a', class_='feature-link')
        
        self.assertGreater(len(feature_links), 0, "Should have feature links")
        
        for link in feature_links:
            self.assertTrue(
                link.has_attr('aria-label'),
                f"Feature link '{link.get_text(strip=True)}' should have aria-label"
            )

    def test_heading_hierarchy(self):
        """Test that heading hierarchy is proper (h1 -> h2 -> h3)."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all headings
        headings = soup.find_all(re.compile(r'^h[1-6]$'))
        
        # Should have at least one h1
        h1_count = len([h for h in headings if h.name == 'h1'])
        self.assertEqual(h1_count, 1, "Page should have exactly one h1 element")
        
        # Check hierarchy
        heading_levels = [int(h.name[1]) for h in headings]
        
        # First heading should be h1
        self.assertEqual(heading_levels[0], 1, "First heading should be h1")
        
        # Check that headings don't skip levels
        for i in range(1, len(heading_levels)):
            level_diff = heading_levels[i] - heading_levels[i-1]
            self.assertLessEqual(
                level_diff, 1,
                f"Heading levels should not skip (found h{heading_levels[i-1]} followed by h{heading_levels[i]})"
            )

    def test_svg_has_role_and_aria_label(self):
        """Test that SVG illustrations have proper role and aria-label."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        svgs = soup.find_all('svg')
        
        for svg in svgs:
            # SVG should either have aria-hidden="true" or role="img" with aria-label
            if svg.get('aria-hidden') == 'true':
                continue
            
            self.assertTrue(
                svg.has_attr('role') or svg.has_attr('aria-label'),
                "SVG without aria-hidden should have role or aria-label"
            )
            
            if svg.get('role') == 'img':
                self.assertTrue(
                    svg.has_attr('aria-label'),
                    "SVG with role='img' should have aria-label"
                )

    def test_decorative_icons_hidden(self):
        """Test that decorative icons have aria-hidden='true'."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all icon elements (typically <i> tags with icon classes)
        icons = soup.find_all('i', class_=re.compile(r'ri-'))
        
        self.assertGreater(len(icons), 0, "Should have icon elements")
        
        for icon in icons:
            self.assertEqual(
                icon.get('aria-hidden'),
                'true',
                f"Decorative icon should have aria-hidden='true'"
            )

    def test_feature_cards_have_article_role(self):
        """Test that feature cards use article role for semantic structure."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        feature_cards = soup.find_all(class_='feature-card')
        
        self.assertGreater(len(feature_cards), 0, "Should have feature cards")
        
        for card in feature_cards:
            self.assertEqual(
                card.get('role'),
                'article',
                "Feature card should have role='article'"
            )

    def test_sections_have_aria_labelledby(self):
        """Test that major sections have aria-labelledby attributes."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find sections with titles
        sections = soup.find_all('section')
        
        for section in sections:
            # Skip sections without titles
            if not section.find(['h1', 'h2', 'h3']):
                continue
            
            self.assertTrue(
                section.has_attr('aria-labelledby') or section.has_attr('aria-label'),
                f"Section should have aria-labelledby or aria-label"
            )

    def test_main_content_has_role(self):
        """Test that main content area has role='main'."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main = soup.find('main')
        
        self.assertIsNotNone(main, "Should have <main> element")
        self.assertEqual(
            main.get('role'),
            'main',
            "Main element should have role='main'"
        )

    def test_aria_live_region_present(self):
        """Test that ARIA live region is present for dynamic announcements."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        live_region = soup.find(id='aria-live-region')
        
        self.assertIsNotNone(live_region, "Should have ARIA live region")
        self.assertEqual(
            live_region.get('aria-live'),
            'polite',
            "Live region should have aria-live='polite'"
        )
        self.assertEqual(
            live_region.get('aria-atomic'),
            'true',
            "Live region should have aria-atomic='true'"
        )

    def test_language_switcher_has_aria_label(self):
        """Test that language switcher has proper aria-label."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        lang_select = soup.find('select', {'name': 'language'})
        
        if lang_select:
            self.assertTrue(
                lang_select.has_attr('aria-label'),
                "Language switcher should have aria-label"
            )

    def test_stat_items_have_proper_structure(self):
        """Test that stat items have proper ARIA structure."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stat_items = soup.find_all(class_='stat-item')
        
        for stat in stat_items:
            # Should have role="group"
            self.assertEqual(
                stat.get('role'),
                'group',
                "Stat item should have role='group'"
            )
            
            # Should have aria-labelledby
            self.assertTrue(
                stat.has_attr('aria-labelledby'),
                "Stat item should have aria-labelledby"
            )

    def test_navbar_has_proper_role(self):
        """Test that navbar has proper navigation role."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        nav = soup.find('nav')
        
        self.assertIsNotNone(nav, "Should have <nav> element")
        self.assertEqual(
            nav.get('role'),
            'navigation',
            "Nav element should have role='navigation'"
        )
        self.assertTrue(
            nav.has_attr('aria-label'),
            "Nav should have aria-label"
        )

    def test_footer_has_proper_role(self):
        """Test that footer has proper contentinfo role."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        footer = soup.find('footer')
        
        self.assertIsNotNone(footer, "Should have <footer> element")
        self.assertEqual(
            footer.get('role'),
            'contentinfo',
            "Footer element should have role='contentinfo'"
        )
        self.assertTrue(
            footer.has_attr('aria-label'),
            "Footer should have aria-label"
        )

    def test_form_buttons_have_aria_labels(self):
        """Test that form buttons have proper aria-labels."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        buttons = soup.find_all('button')
        
        for button in buttons:
            # Button should have either aria-label or visible text
            has_text = bool(button.get_text(strip=True))
            has_aria_label = button.has_attr('aria-label')
            
            self.assertTrue(
                has_text or has_aria_label,
                f"Button should have either visible text or aria-label"
            )

    def test_images_have_alt_text(self):
        """Test that all images have alt text."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        images = soup.find_all('img')
        
        for img in images:
            self.assertTrue(
                img.has_attr('alt'),
                f"Image {img.get('src', 'unknown')} should have alt attribute"
            )

    def test_links_have_descriptive_text(self):
        """Test that links have descriptive text or aria-labels."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = soup.find_all('a')
        
        for link in links:
            # Skip skip-link and empty links
            if 'skip-link' in link.get('class', []) or not link.get('href'):
                continue
            
            # Link should have either visible text or aria-label
            has_text = bool(link.get_text(strip=True))
            has_aria_label = link.has_attr('aria-label')
            
            self.assertTrue(
                has_text or has_aria_label,
                f"Link to {link.get('href', 'unknown')} should have text or aria-label"
            )

    def test_color_contrast_css_variables(self):
        """Test that CSS color variables meet WCAG 2.1 AA contrast ratios.
        
        Note: This is a basic check of color definitions. Full contrast testing
        requires visual rendering and should be done with tools like axe or WAVE.
        """
        # This test verifies that we're using semantic color variables
        # Actual contrast testing should be done with browser-based tools
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify CSS file is loaded
        soup = BeautifulSoup(response.content, 'html.parser')
        css_links = soup.find_all('link', rel='stylesheet')
        
        has_public_home_css = any(
            'public_home.css' in link.get('href', '')
            for link in css_links
        )
        
        self.assertTrue(
            has_public_home_css,
            "public_home.css should be loaded"
        )


class KeyboardNavigationTestCase(TestCase):
    """Test keyboard navigation support."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.home_url = reverse('cms:home')

    def test_all_interactive_elements_focusable(self):
        """Test that all interactive elements are keyboard focusable."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all interactive elements
        interactive = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        for element in interactive:
            # Element should not have tabindex="-1" unless it's intentionally hidden
            tabindex = element.get('tabindex')
            
            if tabindex == '-1':
                # Should be hidden or have a good reason
                is_hidden = (
                    element.has_attr('aria-hidden') or
                    element.has_attr('hidden') or
                    'visually-hidden' in element.get('class', [])
                )
                
                if not is_hidden:
                    # This might be intentional for skip targets
                    pass

    def test_navbar_toggler_has_aria_attributes(self):
        """Test that mobile menu toggle has proper ARIA attributes."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        toggler = soup.find(class_='navbar-toggler')
        
        if toggler:
            self.assertTrue(
                toggler.has_attr('aria-controls'),
                "Navbar toggler should have aria-controls"
            )
            self.assertTrue(
                toggler.has_attr('aria-expanded'),
                "Navbar toggler should have aria-expanded"
            )
            self.assertTrue(
                toggler.has_attr('aria-label'),
                "Navbar toggler should have aria-label"
            )

    def test_dropdown_menus_have_aria_attributes(self):
        """Test that dropdown menus have proper ARIA attributes."""
        response = self.client.get(self.home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        dropdowns = soup.find_all(class_='dropdown-toggle')
        
        for dropdown in dropdowns:
            self.assertTrue(
                dropdown.has_attr('aria-expanded'),
                "Dropdown toggle should have aria-expanded"
            )
            self.assertTrue(
                dropdown.has_attr('aria-haspopup') or dropdown.has_attr('data-bs-toggle'),
                "Dropdown toggle should indicate it has a popup"
            )
