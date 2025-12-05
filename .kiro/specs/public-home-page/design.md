# Design Document

## Overview

This design document outlines the technical approach for implementing a new public-facing home page for the Tax Collector platform. The solution will replace the existing CMS home page with a modern, bilingual landing page featuring dynamic header and footer components, responsive design, and clear calls-to-action. The design leverages the existing CMS infrastructure while introducing a new, dedicated home page template and ensuring all other CMS pages adopt the new design for consistency.

## Architecture

### High-Level Architecture

The home page implementation follows a layered architecture:

1. **Presentation Layer**: Django templates with Bootstrap 5 (Velzon theme) for responsive UI
2. **View Layer**: Django class-based views extending existing CMS base views
3. **Data Layer**: Existing CMS models (Page, PageSection, HeaderSettings, FooterSettings, MenuItem)
4. **Internationalization Layer**: Django i18n framework with French and Malagasy translations

### Component Interaction Flow

```
Visitor Request (/) 
    ↓
Django URL Router (cms.urls)
    ↓
PublicHomeView (cms.views)
    ↓
get_cms_context() helper
    ↓
Template Rendering (templates/cms/public_home.html)
    ↓
    ├── Header Component (templates/cms/partials/public_header.html)
    ├── Hero Section
    ├── Features Section
    ├── CTA Section
    └── Footer Component (templates/cms/partials/public_footer.html)
```

## Components and Interfaces

### 1. View Components

#### PublicHomeView
- **Type**: Django TemplateView
- **Purpose**: Render the new public home page
- **Template**: `templates/cms/public_home.html`
- **Context Data**:
  - CMS settings (header, footer, site settings, theme)
  - Menu items (header and footer)
  - Homepage sections from CMS
  - Current language
  - User authentication status

#### Updated CMSPageDetailView
- **Type**: Django DetailView (existing, to be updated)
- **Purpose**: Render CMS pages (About, Contact, etc.) with new design
- **Template**: `templates/cms/page_detail.html` (to be updated)
- **Changes**: Use new header/footer partials

### 2. Template Components

#### Public Header Component
- **File**: `templates/cms/partials/public_header.html`
- **Features**:
  - Site logo and branding
  - Navigation menu from CMS
  - Language switcher (FR/MG)
  - Login/Register buttons (if not authenticated)
  - User menu (if authenticated)
  - Mobile-responsive hamburger menu
- **Styling**: Uses HeaderSettings and ThemeSettings from CMS

#### Public Footer Component
- **File**: `templates/cms/partials/public_footer.html`
- **Features**:
  - Footer menu links from CMS
  - Contact information
  - Social media links
  - Copyright notice with dynamic year
  - Multi-column layout (desktop) / stacked (mobile)
- **Styling**: Uses FooterSettings from CMS


### 3. Static Assets

#### CSS Files
- **File**: `static/css/public_home.css`
- **Purpose**: Custom styles for public home page
- **Contents**:
  - Hero section styling
  - Feature cards
  - CTA button styles
  - Responsive breakpoints
  - Animation effects

#### JavaScript Files
- **File**: `static/js/public_home.js`
- **Purpose**: Interactive functionality
- **Contents**:
  - Language switcher logic
  - Mobile menu toggle
  - Smooth scrolling
  - CTA button interactions

## Data Models

### Existing CMS Models (No Changes Required)

#### SiteSettings
- Stores general site configuration
- Fields: site_name, site_tagline, site_logo, contact_email, contact_phone, social media URLs

#### HeaderSettings
- Stores header/navigation configuration
- Fields: site_name (multilingual), logo, colors, display options, sticky behavior

#### FooterSettings
- Stores footer configuration
- Fields: copyright_text (multilingual), description (multilingual), colors, spacing, social links

#### ThemeSettings
- Stores theme and styling configuration
- Fields: theme_name, navbar_style, colors, animations, effects

#### MenuItem
- Stores navigation menu items
- Fields: title (multilingual), url, icon, parent, menu_location, order

#### Page
- Stores CMS pages
- Fields: title (multilingual), slug, content (multilingual), sections, status, is_homepage

#### PageSection
- Stores reusable page sections
- Fields: name, section_type, title (multilingual), content (multilingual), styling

### Data Flow

1. **Page Load**: View queries CMS models for active settings
2. **Context Building**: `get_cms_context()` aggregates all CMS data
3. **Template Rendering**: Templates access context data via Django template language
4. **Language Switching**: Django i18n middleware handles language preference

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Language Content Consistency
*For any* page load with a selected language, all displayed text content should be in the selected language (French or Malagasy), with no mixing of languages within the same page view.
**Validates: Requirements 1.3, 1.4**

### Property 2: Header and Footer Presence
*For any* public page (home or CMS detail page), both the header component and footer component should be rendered and visible in the HTML output.
**Validates: Requirements 2.1, 2.2**

### Property 3: CTA Redirect Correctness
*For any* user clicking the primary CTA button, the redirect destination should be the login page if unauthenticated, or the dashboard if authenticated.
**Validates: Requirements 3.2, 3.5**

### Property 4: Responsive Layout Adaptation
*For any* viewport width, the page layout should adapt appropriately: single-column for mobile (<768px), multi-column for tablet (768-1024px), and full layout for desktop (>1024px).
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 5: CMS Settings Reflection
*For any* update to CMS settings (HeaderSettings, FooterSettings, SiteSettings), the changes should be immediately visible on the next page load without requiring code deployment.
**Validates: Requirements 5.4, 5.5**

### Property 6: Template Consistency
*For any* CMS page (home or detail), the page should use the same header and footer components, ensuring visual consistency across the public site.
**Validates: Requirements 13.3, 14.1, 14.2**

### Property 7: Language Preference Persistence
*For any* visitor who selects a language, returning to the site within 30 days should display content in the previously selected language.
**Validates: Requirements 12.1, 12.2, 12.3**

### Property 8: Accessibility Compliance
*For any* interactive element on the page, keyboard navigation should be functional and ARIA labels should be present where appropriate.
**Validates: Requirements 11.1, 11.2**

### Property 9: Menu Item Rendering
*For any* active menu item in the CMS with menu_location="header" or "both", the item should appear in the header navigation menu.
**Validates: Requirements 2.1, 2.5**

### Property 10: Multilingual Menu Items
*For any* menu item with translated titles (title_fr, title_mg), the displayed title should match the current language selection.
**Validates: Requirements 1.3, 1.4, 10.5**

## Error Handling

### View-Level Error Handling

#### Missing CMS Settings
- **Scenario**: No active HeaderSettings or FooterSettings found
- **Handling**: Use default values, log warning, continue rendering
- **User Impact**: Page displays with default styling

#### Missing Homepage Content
- **Scenario**: No Page with is_homepage=True exists
- **Handling**: Display default hero section with hardcoded content
- **User Impact**: Functional page with generic content

#### Invalid Language Code
- **Scenario**: Language cookie contains invalid code
- **Handling**: Reset to default language (French), clear invalid cookie
- **User Impact**: Page displays in French

### Template-Level Error Handling

#### Missing Translations
- **Scenario**: Content not available in selected language
- **Handling**: Fall back to default language content
- **User Impact**: Some content may appear in French even if Malagasy selected

#### Broken Image URLs
- **Scenario**: Logo or section images return 404
- **Handling**: Use CSS to hide broken images, show alt text
- **User Impact**: Text-only branding/sections

### Database-Level Error Handling

#### Database Connection Failure
- **Scenario**: Cannot connect to database
- **Handling**: Django's standard error handling, show 500 page
- **User Impact**: Site unavailable, error logged

## Testing Strategy

### Unit Testing

Unit tests will verify specific functionality and edge cases:

1. **View Tests**
   - Test PublicHomeView returns 200 status
   - Test context contains required CMS data
   - Test authenticated vs unauthenticated user context
   - Test language switching updates context

2. **Template Tests**
   - Test header component renders with menu items
   - Test footer component renders with copyright
   - Test CTA buttons have correct URLs
   - Test language switcher displays both options

3. **Helper Function Tests**
   - Test get_cms_context() returns all required data
   - Test get_cms_context() handles missing settings gracefully
   - Test language preference cookie setting/reading

4. **Integration Tests**
   - Test full page render with CMS data
   - Test language switching end-to-end
   - Test CTA click redirects correctly
   - Test responsive breakpoints

### Property-Based Testing

Property-based tests will verify universal properties across many inputs using Hypothesis (Python PBT library). Each test will run a minimum of 100 iterations.

1. **Property Test: Language Consistency**
   - **Feature: public-home-page, Property 1: Language Content Consistency**
   - Generate random language selections
   - Verify all rendered content matches selected language
   - Validates: Requirements 1.3, 1.4

2. **Property Test: Component Presence**
   - **Feature: public-home-page, Property 2: Header and Footer Presence**
   - Generate random CMS configurations
   - Verify header and footer always present in HTML
   - Validates: Requirements 2.1, 2.2

3. **Property Test: CTA Redirect Logic**
   - **Feature: public-home-page, Property 3: CTA Redirect Correctness**
   - Generate random authenticated/unauthenticated states
   - Verify CTA redirects to correct destination
   - Validates: Requirements 3.2, 3.5

4. **Property Test: Responsive Breakpoints**
   - **Feature: public-home-page, Property 4: Responsive Layout Adaptation**
   - Generate random viewport widths
   - Verify layout adapts correctly for each breakpoint
   - Validates: Requirements 4.1, 4.2, 4.3

5. **Property Test: CMS Settings Propagation**
   - **Feature: public-home-page, Property 5: CMS Settings Reflection**
   - Generate random CMS setting updates
   - Verify changes appear on next page load
   - Validates: Requirements 5.4, 5.5

### Browser Compatibility Testing

Manual testing across browsers:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

Test scenarios:
- Page load and rendering
- Language switching
- CTA button clicks
- Mobile menu toggle
- Responsive layout

### Accessibility Testing

Tools and methods:
- WAVE browser extension for automated checks
- Keyboard-only navigation testing
- Screen reader testing (NVDA/JAWS)
- Color contrast verification
- ARIA label validation

### Performance Testing

Metrics to verify:
- Initial page load < 2 seconds (broadband)
- Time to Interactive < 3 seconds
- Lighthouse score > 90
- Image optimization (WebP format, compression)
- CSS/JS minification

## Implementation Notes

### URL Routing

The home page will be accessible at the root URL ("/") via the CMS app URLs:

```python
# cms/urls.py
urlpatterns = [
    path('', PublicHomeView.as_view(), name='home'),
    path('<slug:slug>/', CMSPageDetailView.as_view(), name='page_detail'),
]
```

### Language Switching Implementation

Language switching will use Django's built-in i18n framework:

1. Language switcher form posts to `/i18n/setlang/`
2. Django sets language cookie
3. Middleware applies language to subsequent requests
4. Templates use `{% trans %}` and `{% blocktrans %}` tags

### CMS Integration

The implementation will reuse existing CMS infrastructure:

1. **No database migrations required** - uses existing models
2. **Leverages get_cms_context()** - existing helper function
3. **Extends CMSBaseView** - inherits CMS functionality
4. **Uses existing admin interface** - no new admin views needed

### Static File Organization

```
static/
├── css/
│   └── public_home.css          # New file
├── js/
│   └── public_home.js           # New file
└── images/
    └── home/                    # New directory for home page images
        ├── hero-bg.jpg
        └── feature-icons/
```

### Template Organization

```
templates/
└── cms/
    ├── public_home.html         # New file (replaces home.html)
    ├── page_detail.html         # Updated to use new partials
    ├── base_public.html         # New base template for public pages
    └── partials/
        ├── public_header.html   # New file
        └── public_footer.html   # New file
```

### Backward Compatibility

To ensure smooth transition:

1. **Old home.html preserved** as `home_old.html` for reference
2. **Gradual rollout** - can toggle between old/new via settings
3. **CMS pages unchanged** - only template updates, no data changes
4. **Existing URLs maintained** - no URL structure changes

### Security Considerations

1. **CSRF Protection**: All forms include CSRF tokens
2. **XSS Prevention**: All user-generated content escaped in templates
3. **SQL Injection**: Using Django ORM (parameterized queries)
4. **Clickjacking**: X-Frame-Options header set
5. **HTTPS**: Enforce HTTPS in production (existing configuration)

### Internationalization Details

Translation files structure:

```
locale/
├── fr/
│   └── LC_MESSAGES/
│       └── django.po            # French translations
└── mg/
    └── LC_MESSAGES/
        └── django.po            # Malagasy translations
```

Key phrases to translate:
- Hero headline and subheadline
- Feature titles and descriptions
- CTA button text
- Footer links and copyright
- Navigation menu items (via CMS)

### Performance Optimization

1. **Database Query Optimization**
   - Use `select_related()` for foreign keys
   - Use `prefetch_related()` for many-to-many (menu items)
   - Cache CMS settings (Redis/Memcached)

2. **Static Asset Optimization**
   - Minify CSS and JavaScript
   - Use WebP images with fallbacks
   - Implement lazy loading for images
   - Enable browser caching headers

3. **Template Optimization**
   - Use template fragment caching for header/footer
   - Minimize template logic
   - Use template inheritance efficiently

### Deployment Considerations

1. **Static Files**: Run `collectstatic` to gather new CSS/JS
2. **Translations**: Compile message files with `compilemessages`
3. **Cache Clearing**: Clear template cache after deployment
4. **Database**: No migrations needed (uses existing models)
5. **Rollback Plan**: Keep old templates for quick rollback if needed

## Dependencies

### Python Packages (Existing)
- Django 5.2+
- django-modeltranslation (for CMS model translations)
- Pillow (for image handling)

### Frontend Libraries (Existing)
- Bootstrap 5.3+ (Velzon theme)
- Font Awesome 6+ (icons)
- jQuery 3+ (for Bootstrap components)

### Testing Libraries
- pytest-django (unit tests)
- hypothesis (property-based tests)
- selenium (browser automation tests)
- coverage.py (code coverage)

No new dependencies required - all existing packages support the implementation.
