# CMS Setup Instructions

This document provides instructions for completing the CMS setup after the frontend refactoring.

## Overview

The frontend has been refactored to ensure all public-facing content is managed through the CMS. The following changes have been made:

### Completed Changes

1. ✅ Removed `templates/core/home.html` (non-CMS frontpage)
2. ✅ Removed `templates/base_public.html` (replaced by CMS base template)
3. ✅ Removed `templates/core/about.html` and `templates/core/contact.html` (should be CMS pages)
4. ✅ Updated `templates/base/base.html` to use CMS URLs
5. ✅ Documented pages app as demo-only
6. ✅ Root URL (`/`) now points to CMS home

### URL Structure

- **CMS Homepage**: `/` → `cms:home`
- **CMS Pages**: `/page/<slug>/` → `cms:page_detail`
- **Authenticated Users**: `/app/` → Core dashboard and features
- **Admin Panel**: `/admin/`
- **Demo Pages**: `/pages/` → Velzon template demos (optional, can be disabled)

## Required Steps to Complete CMS Setup

### 1. Run Migrations

Ensure all CMS migrations are applied:

```bash
python manage.py migrate cms
```

### 2. Create Initial CMS Content

Run the migration command to populate initial CMS content:

```bash
python manage.py migrate_frontend_content
```

This will create:
- Default site settings
- Header and footer settings  
- Menu items (Home, About, Contact, QR Verification)
- Homepage with hero and features sections
- Default pages (homepage, about, contact)

### 3. Create About and Contact Pages via Django Admin

Since we removed the hardcoded about and contact templates, you need to create them as CMS pages:

#### Create About Page

1. Go to `/admin/cms/page/add/`
2. Fill in the details:
   - **Title**: About Us (À propos in French, Momba anay in Malagasy)
   - **Slug**: `about`
   - **Status**: Published
   - **Content**: Add your about page content with rich text
   - **Meta Description**: Add SEO-friendly description
3. Save the page

#### Create Contact Page

1. Go to `/admin/cms/page/add/`
2. Fill in the details:
   - **Title**: Contact Us (Contactez-nous in French, Mifandraisa aminay in Malagasy)
   - **Slug**: `contact`
   - **Content**: Add your contact information, form, etc.
   - **Meta Description**: Add SEO-friendly description
3. Save the page

### 4. Configure Site Settings

1. Go to `/admin/cms/sitesettings/`
2. Update the site settings with your information:
   - Site name
   - Logo and favicon
   - Contact information
   - Social media links

### 5. Configure Header Settings

1. Go to `/admin/cms/headersettings/`
2. Customize your header:
   - Site name (with translations)
   - Logo
   - Colors
   - Display options (search, language switcher, sticky header)

### 6. Configure Footer Settings

1. Go to `/admin/cms/footersettings/`
2. Customize your footer:
   - Copyright text (with translations)
   - Description (with translations)
   - Colors
   - Display options

### 7. Create Menu Items

1. Go to `/admin/cms/menuitem/`
2. Create or update menu items for header and footer navigation
3. Set proper order and parent-child relationships

### 8. Create Homepage Sections

1. Go to `/admin/cms/pagesection/`
2. Create sections for your homepage:
   - Hero section
   - Features section
   - Statistics section
   - Call-to-action section
3. Link sections to your homepage

### 9. Add Section Items

1. Go to `/admin/cms/sectionitem/`
2. Add items to your sections (e.g., individual features, testimonials)
3. Use icons, images, and descriptions

## Testing

After completing the setup:

1. Visit `/` to see your CMS homepage
2. Check `/page/about/` for the about page
3. Check `/page/contact/` for the contact page
4. Test menu navigation in header and footer
5. Test language switching (if enabled)
6. Check responsive design on mobile devices

## Production Checklist

Before deploying to production:

- [ ] All CMS pages are created and published
- [ ] Site settings are configured
- [ ] Header and footer are customized
- [ ] Menu items are properly ordered
- [ ] All translations are complete (French and Malagasy)
- [ ] Meta descriptions are added to all pages for SEO
- [ ] Images are optimized and uploaded
- [ ] Social media links are added
- [ ] Contact information is up to date
- [ ] Test all pages on different devices
- [ ] Comment out `/pages/` URL in `taxcollector_project/urls.py` if not needed

## Migration Notes

### Old URL → New URL Mapping

| Old URL | New URL | Notes |
|---------|---------|-------|
| `/` (core:home) | `/` (cms:home) | Now CMS-managed |
| N/A (hardcoded) | `/page/about/` | Create as CMS page |
| N/A (hardcoded) | `/page/contact/` | Create as CMS page |
| `/app/` | `/app/` | No change (authenticated users) |

### Template Changes

| Old Template | New Template | Status |
|-------------|--------------|--------|
| `base_public.html` | `cms/base.html` | Replaced |
| `core/home.html` | `cms/home.html` | Replaced |
| `core/about.html` | CMS Page | Removed (use CMS) |
| `core/contact.html` | CMS Page | Removed (use CMS) |
| `base/base.html` | `base/base.html` | Updated URLs |

## Troubleshooting

### Issue: About/Contact pages show 404

**Solution**: Make sure you created the CMS pages with slugs `about` and `contact`.

### Issue: Menu items not showing

**Solution**: 
1. Check that menu items are marked as `is_active=True`
2. Check that menu location is set correctly (header/footer/both)
3. Check the order field

### Issue: Translations not working

**Solution**:
1. Make sure you filled in all translation fields (title_fr, title_mg, etc.)
2. Run `python manage.py makemigrations` and `python manage.py migrate`
3. Check language settings in Django settings

### Issue: Images not displaying

**Solution**:
1. Check MEDIA_URL and MEDIA_ROOT settings
2. Make sure images are uploaded via admin
3. Check file permissions

## Support

For more information:
- [CMS App Documentation](cms/README.md)
- [Django Admin Guide](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Velzon Theme Documentation](static/velzon/README.md)

---

**Last Updated**: November 6, 2025
















