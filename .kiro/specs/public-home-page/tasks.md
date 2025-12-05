# Implementation Plan

- [x] 1. Create base template structure for public pages
  - Create `templates/cms/base_public.html` extending Django base
  - Include Bootstrap 5 (Velzon theme) CSS and JavaScript ( http://127.0.0.1:8000/app/password-reset/ ) for reference
  - Set up i18n template tags and language switching support
  - Add meta tags for SEO and responsive design
  - _Requirements: 6.1, 6.4, 7.2_

- [x] 2. Implement public header component if exist you have to use the existing and check if it well implemented 
  - Create `templates/cms/partials/public_header.html` if not exist
  - Render site logo from HeaderSettings
  - Display navigation menu items from CMS (menu_location="header" or "both")
  - Implement language switcher (FR/MG) with current language indicator
  - Add login/register buttons for unauthenticated users
  - Add user menu for authenticated users
  - Implement mobile-responsive hamburger menu
  - Apply styling from HeaderSettings and ThemeSettings
  - _Requirements: 2.1, 2.3, 2.5, 4.4_

- [x] 3. Implement public footer component if not exit , if exist you have to use the existing and check if it well implemented 
  - Create `templates/cms/partials/public_footer.html` if not exist
  - Display footer menu items from CMS (menu_location="footer" or "both")
  - Render contact information from SiteSettings
  - Display social media links from SiteSettings
  - Show copyright text with dynamic year from FooterSettings
  - Implement multi-column layout for desktop, stacked for mobile
  - Apply styling from FooterSettings
  - _Requirements: 2.2, 2.4, 4.5, 10.1, 10.2, 10.3, 10.4_

- [x] 4. Create PublicHomeView if not exit if exist , check and use it
  - Create view class in `cms/views.py` extending TemplateView
  - Implement get_context_data() to include CMS settings
  - Add homepage sections from CMS Page model
  - Include user authentication status in context
  - Handle language preference from cookie
  - _Requirements: 1.1, 5.1, 5.2, 5.3, 6.2_

- [x] 5. Create public home page template
  - Create `templates/cms/public_home.html` extending base_public.html
  - Include public header component
  - Implement hero section with headline, subheadline, and CTA buttons, use moderne and professional, you have to act as expert in frontend desing,. 
  - Create features section with icons and descriptions
  - Add secondary CTA section
  - Include public footer component
  - Support CMS-managed sections rendering
  - _Requirements: 1.5, 3.1, 9.1, 9.2, 9.3, 9.4, 9.5, 13.1, 13.5_

- [x] 6. Implement CTA button logic
  - Add primary CTA button linking to login page
  - Add secondary CTA button linking to QR verification
  - Implement conditional redirect (dashboard if authenticated, login if not)
  - Apply multilingual button text
  - Style buttons prominently with Velzon theme
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [x] 7. Create custom CSS for public home page
  - Create `static/css/public_home.css`
  - Style hero section with background and typography
  - Style feature cards with hover effects
  - Style CTA buttons with animations
  - Implement responsive breakpoints (mobile, tablet, desktop)
  - Add smooth transitions and animations
  - Ensure accessibility (contrast ratios, focus states)
  - _Requirements: 4.1, 4.2, 4.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8. Create JavaScript for interactive features
  - Create `static/js/public_home.js`
  - Implement language switcher functionality
  - Add mobile menu toggle logic
  - Implement smooth scrolling for anchor links
  - Add CTA button click tracking (optional)
  - Ensure graceful degradation when JavaScript disabled
  - _Requirements: 7.3_

- [x] 9. Add French translations
  - Create/update `locale/fr/LC_MESSAGES/django.po`
  - Translate hero headline and subheadline
  - Translate feature titles and descriptions
  - Translate CTA button text
  - Translate navigation and footer text
  - Compile messages with `compilemessages`
  - _Requirements: 1.2, 1.4, 3.3_

- [x] 10. Add Malagasy translations
  - Create/update `locale/mg/LC_MESSAGES/django.po`
  - Translate hero headline and subheadline
  - Translate feature titles and descriptions
  - Translate CTA button text
  - Translate navigation and footer text
  - Compile messages with `compilemessages`
  - _Requirements: 1.3, 3.3_

- [x] 11. Update CMS page detail template
  - Update `templates/cms/page_detail.html` to use base_public.html
  - Replace old header with public_header.html partial
  - Replace old footer with public_footer.html partial
  - Maintain existing section rendering functionality
  - Ensure responsive design
  - _Requirements: 13.2, 13.3, 13.4, 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 12. Update URL routing
  - Update `cms/urls.py` to use PublicHomeView for root URL
  - Ensure CMS page detail URLs remain functional
  - Test all URL patterns
  - _Requirements: 1.1, 6.5_

- [x] 13. Implement language preference persistence
  - Verify Django i18n middleware is configured
  - Test language cookie setting on language switch
  - Verify cookie persists for 30 days
  - Test fallback to default language when cookie cleared
  - Ensure language preference applies across all pages
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 14. Add accessibility features
  - Add ARIA labels to all interactive elements
  - Implement keyboard navigation support
  - Add alt text to all images
  - Verify proper heading hierarchy (h1, h2, h3)
  - Test color contrast ratios (WCAG 2.1 AA)
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 15. Optimize images and assets
  - Compress hero background image
  - Create WebP versions of images with fallbacks
  - Optimize feature icons
  - Minify CSS and JavaScript files
  - Configure browser caching headers
  - _Requirements: 7.4, 7.5_

- [ ] 16. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 17. Write unit tests for PublicHomeView
  - Test view returns 200 status code
  - Test context contains CMS settings
  - Test authenticated vs unauthenticated user context
  - Test language switching updates context
  - Test missing CMS settings handled gracefully
  - _Requirements: 1.1, 4.1, 5.1, 5.2, 5.3_

- [ ]* 17.1 Write property test for language consistency
  - **Property 1: Language Content Consistency**
  - **Validates: Requirements 1.3, 1.4**

- [ ]* 17.2 Write property test for component presence
  - **Property 2: Header and Footer Presence**
  - **Validates: Requirements 2.1, 2.2**

- [ ]* 17.3 Write property test for CTA redirect logic
  - **Property 3: CTA Redirect Correctness**
  - **Validates: Requirements 3.2, 3.5**

- [ ]* 17.4 Write property test for responsive breakpoints
  - **Property 4: Responsive Layout Adaptation**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ]* 17.5 Write property test for CMS settings propagation
  - **Property 5: CMS Settings Reflection**
  - **Validates: Requirements 5.4, 5.5**

- [ ]* 18. Write unit tests for template components
  - Test header component renders with menu items
  - Test footer component renders with copyright
  - Test CTA buttons have correct URLs
  - Test language switcher displays both options
  - Test mobile menu toggle functionality
  - _Requirements: 2.1, 2.2, 2.5, 3.2, 4.4, 4.5_

- [ ]* 18.1 Write property test for template consistency
  - **Property 6: Template Consistency**
  - **Validates: Requirements 13.3, 14.1, 14.2**

- [ ]* 18.2 Write property test for menu item rendering
  - **Property 9: Menu Item Rendering**
  - **Validates: Requirements 2.1, 2.5**

- [ ]* 18.3 Write property test for multilingual menu items
  - **Property 10: Multilingual Menu Items**
  - **Validates: Requirements 1.3, 1.4, 10.5**

- [ ]* 19. Write integration tests
  - Test full page render with CMS data
  - Test language switching end-to-end
  - Test CTA click redirects correctly
  - Test responsive breakpoints with different viewport sizes
  - Test authenticated vs unauthenticated user flows
  - _Requirements: 1.3, 1.4, 3.2, 3.5, 4.1, 4.2, 4.3_

- [ ]* 19.1 Write property test for language preference persistence
  - **Property 7: Language Preference Persistence**
  - **Validates: Requirements 12.1, 12.2, 12.3**

- [ ]* 19.2 Write property test for accessibility compliance
  - **Property 8: Accessibility Compliance**
  - **Validates: Requirements 11.1, 11.2**

- [ ]* 20. Perform browser compatibility testing
  - Test on Chrome (latest 2 versions)
  - Test on Firefox (latest 2 versions)
  - Test on Safari (latest 2 versions)
  - Test on Edge (latest 2 versions)
  - Document any browser-specific issues
  - _Requirements: 7.2_

- [ ]* 21. Perform accessibility testing
  - Run WAVE browser extension checks
  - Test keyboard-only navigation
  - Test with screen reader (NVDA or JAWS)
  - Verify color contrast ratios
  - Validate ARIA labels
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 22. Perform performance testing
  - Measure initial page load time
  - Measure Time to Interactive
  - Run Lighthouse audit (target score > 90)
  - Verify image optimization
  - Check CSS/JS minification
  - _Requirements: 7.1, 7.4, 7.5_

- [ ] 23. Create deployment documentation
  - Document static file collection steps
  - Document translation compilation steps
  - Document cache clearing procedures
  - Create rollback plan
  - Document any configuration changes needed
  - _Requirements: 6.1, 6.4, 6.5_

- [ ] 24. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
