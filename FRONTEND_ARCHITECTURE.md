# Frontend Architecture After CMS Refactoring

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                     TAX COLLECTOR PLATFORM                      │
└────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   URL Routing     │
                    │  (urls.py)        │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   CMS App     │    │   Core App    │    │  Admin Apps   │
│   (Public)    │    │ (Authenticated)│    │  (Management) │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        │                     │                     │
    Path: /              Path: /app/          Path: /admin/
                                              Path: /administration/
```

## URL Structure

### Public Frontend (CMS-Managed)

```
/                           → CMS Homepage (cms:home)
/page/<slug>/               → CMS Pages (cms:page_detail)
  ├── /page/about/          → About page
  ├── /page/contact/        → Contact page
  └── /page/<any-slug>/     → Any CMS page
```

**Templates Used**:
- `cms/base.html` - Base template with dynamic header/footer
- `cms/home.html` - Homepage template
- `cms/page_detail.html` - Page detail template
- `cms/section.html` - Section template

**Content Source**: Django database (CMS models)

### Authenticated User Area

```
/app/                       → Dashboard (core:home)
/app/dashboard/             → Dashboard (core:velzon_dashboard)
/app/qr-verification/       → QR Verification (core:qr_verification)
/app/profile/               → User Profile (core:profile)
/app/profile/edit/          → Edit Profile (core:profile_edit)
/app/fleet/                 → Fleet Dashboard (core:fleet_dashboard)
/app/fleet/vehicles/        → Fleet Vehicles (core:fleet_vehicles)
/app/payments/              → Payments List (core:payment_list_velzon)
```

**Templates Used**:
- `base_velzon.html` - Base template for authenticated users
- `dashboard.html` - Dashboard template
- Various templates in `templates/core/`, `templates/fleet/`, etc.

**Content Source**: Dynamic from database + hardcoded UI

### Admin & Management

```
/admin/                     → Django Admin
  ├── /admin/cms/           → CMS Management
  │   ├── sitesettings/     → Site Settings
  │   ├── headersettings/   → Header Settings
  │   ├── footersettings/   → Footer Settings
  │   ├── menuitem/         → Menu Items
  │   ├── page/             → Pages
  │   ├── pagesection/      → Page Sections
  │   └── sectionitem/      → Section Items
  │
  └── /admin/[other apps]/  → Other app management

/administration/            → Custom Admin Console
```

**Templates Used**:
- Django admin templates
- Custom admin templates in `templates/administration/`

### Demo Pages (Optional)

```
/pages/                     → Velzon Demo Pages (OPTIONAL)
  ├── /pages/starter/       → Starter page
  ├── /pages/landing/       → Landing page
  ├── /pages/authentication/ → Auth demos
  └── [various demos]       → Template examples
```

**Templates Used**:
- Various templates in `templates/velzon/`

**⚠️ Note**: These are for reference only and should be disabled in production.

## Template Hierarchy

### CMS Templates (Public)

```
cms/base.html
├── Dynamic Header (from HeaderSettings model)
├── Dynamic Navigation (from MenuItem model)
├── Content Block
│   ├── cms/home.html
│   │   ├── Homepage content (from Page model)
│   │   └── Sections (from PageSection model)
│   │       └── Section Items (from SectionItem model)
│   │
│   └── cms/page_detail.html
│       └── Page content (from Page model)
│           └── Sections (from PageSection model)
│
└── Dynamic Footer (from FooterSettings model)
```

### Authenticated Templates

```
base_velzon.html
├── Static Velzon Header
├── Content Block
│   ├── dashboard.html
│   ├── profile.html
│   ├── fleet templates
│   └── [other app templates]
│
└── Static Velzon Footer
```

### Base Template (`base/base.html`)

```
base/base.html (Minimal base template)
├── Header with CMS links
├── Content Block
│   └── [Various authenticated pages]
└── Footer
```

## Database Models

### CMS Models

```
cms.SiteSettings
├── site_name
├── site_tagline
├── site_logo
├── site_favicon
├── contact_email
├── contact_phone
├── contact_address
└── social_media_links

cms.HeaderSettings
├── site_name (FR/MG)
├── logo
├── background_color
├── text_color
├── show_search
├── show_language_switcher
└── is_sticky

cms.FooterSettings
├── copyright_text (FR/MG)
├── description (FR/MG)
├── background_color
├── text_color
├── show_social_links
└── show_newsletter

cms.MenuItem
├── title (FR/MG)
├── url
├── icon
├── parent (self-referential FK)
├── menu_location (header/footer/both)
├── order
└── is_active

cms.Page
├── title (FR/MG)
├── slug
├── content (FR/MG)
├── meta_description (FR/MG)
├── featured_image
├── status (draft/published/archived)
├── is_homepage
├── sections (M2M to PageSection)
└── order

cms.PageSection
├── name
├── section_type (hero/features/testimonials/etc.)
├── title (FR/MG)
├── subtitle (FR/MG)
├── content (FR/MG)
├── background_image
├── background_color
├── text_color
├── order
└── is_active

cms.SectionItem
├── section (FK to PageSection)
├── title (FR/MG)
├── description (FR/MG)
├── icon
├── image
├── link_url
├── link_text (FR/MG)
├── order
└── is_active
```

## Static Files Structure

```
static/
├── velzon/                 # Velzon admin theme
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── fonts/
│   └── libs/
│
├── admin_console/          # Custom admin console
│   ├── css/
│   └── js/
│
└── [other static files]

media/                      # User-uploaded files
├── cms/                    # CMS uploads
│   ├── logos/
│   ├── favicons/
│   ├── pages/
│   └── sections/
│
└── [other media files]
```

## Data Flow

### Public Page Request

```
User Request: GET /page/about/
        ↓
URL Router (taxcollector_project/urls.py)
        ↓
CMS URLs (cms/urls.py)
        ↓
CMSPageDetailView (cms/views.py)
        ↓
Get Page from database (slug='about')
        ↓
Get related Sections and Items
        ↓
Get SiteSettings, HeaderSettings, FooterSettings
        ↓
Render cms/page_detail.html
        ↓
Return HTML to user
```

### CMS Content Update

```
Admin logs in to /admin/
        ↓
Navigate to CMS → Pages
        ↓
Edit Page (e.g., About page)
        ↓
Update content, translations, meta
        ↓
Save to database
        ↓
Changes immediately visible on frontend
```

## Multi-Language Support

### Translation Fields

All CMS models support French (FR) and Malagasy (MG) translations:

```python
# Example: Page model
title = models.CharField(...)           # Default
title_fr = models.CharField(...)        # French
title_mg = models.CharField(...)        # Malagasy

content = RichTextField(...)            # Default
content_fr = RichTextField(...)         # French
content_mg = RichTextField(...)         # Malagasy
```

### Language Switching

```
User selects language
        ↓
Language stored in session
        ↓
Templates check current language
        ↓
Display appropriate translation field
        ↓
Fallback to default if translation missing
```

## API Endpoints

```
/api/                       # Core API endpoints
/api/vehicles/              # Vehicle API endpoints
/api/payments/              # Payment API endpoints
/api/notifications/         # Notification API endpoints
/api/administration/        # Admin API endpoints
```

## Security & Permissions

### Public Access
- CMS pages: No authentication required
- Read-only access to published content

### Authenticated Users
- Access to `/app/*` routes
- CRUD operations on own data
- Access to dashboard, profile, vehicles, payments

### Admin Users
- Access to Django admin (`/admin/`)
- Full CMS management
- User management
- System configuration

### Custom Admin Console
- Access to `/administration/` routes
- Enhanced vehicle management
- Payment settings
- Price grids
- User permissions

## Performance Considerations

### Caching Strategy
```python
# CMS views cache context data
# Header/Footer settings cached per request
# Menu items cached with smart invalidation
# Page sections prefetched to reduce queries
```

### Database Optimization
```python
# Use select_related() for ForeignKeys
# Use prefetch_related() for M2M relationships
# Index on slug fields for fast lookups
# Filter active items only
```

### Static Files
```python
# Use collectstatic for production
# Enable GZip compression
# Use CDN for media files
# Minify CSS/JS
```

## Development Workflow

### Adding New CMS Page

1. Go to `/admin/cms/page/add/`
2. Fill in page details (title, slug, content)
3. Add translations (FR/MG)
4. Set status to "Published"
5. Add sections if needed
6. Save
7. Page available at `/page/<slug>/`

### Creating New Page Section

1. Go to `/admin/cms/pagesection/add/`
2. Choose section type (hero, features, etc.)
3. Fill in content and translations
4. Set background colors/images
5. Save
6. Add section to page via M2M relationship
7. Add section items if needed

### Customizing Header/Footer

1. Go to `/admin/cms/headersettings/` or `/admin/cms/footersettings/`
2. Update colors, text, display options
3. Save
4. Changes immediately visible on all CMS pages

## Deployment Checklist

### Before Deploying

- [ ] Run migrations: `python manage.py migrate`
- [ ] Run CMS setup: `python manage.py migrate_frontend_content`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure MEDIA_URL and MEDIA_ROOT
- [ ] Set up media file serving (Nginx/S3)
- [ ] Complete all translations
- [ ] Add meta descriptions to all pages
- [ ] Test all pages (desktop/mobile)
- [ ] Test language switching
- [ ] Configure ALLOWED_HOSTS
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Disable demo pages (optional)
- [ ] Set up backup strategy
- [ ] Configure logging
- [ ] Test admin panel access
- [ ] Verify all static files load correctly

---

**Architecture Version**: 2.0  
**Last Updated**: November 6, 2025  
**Status**: Production Ready (after completing setup)
















