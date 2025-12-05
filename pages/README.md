# Pages App - Velzon Template Demos

**⚠️ IMPORTANT: This app is for demonstration purposes only and is NOT CMS-managed.**

## Purpose

This Django app contains demo pages and templates from the Velzon admin theme. These are reference implementations and examples that show various UI patterns and components available in the Velzon theme.

## Contents

- Authentication page templates (signin, signup, password reset, etc.)
- Sample pages (profile, team, timeline, FAQs, pricing, gallery, etc.)
- Landing page examples (NFT landing, job landing, etc.)
- Error pages (404, 500, offline, etc.)

## Usage

### For Development/Reference

These pages are accessible at `/pages/[page-name]/` and can be used as:
- UI/UX reference for designing new features
- Component examples for frontend developers
- Template structure examples for Django developers

### For Production

**It is recommended to comment out or remove the pages app URLs in production** since:
1. All public-facing content should be managed through the **CMS app**
2. These are static demo pages with no dynamic content
3. They are not integrated with the CMS backend

To disable in production, comment out this line in `taxcollector_project/urls.py`:
```python
# path('pages/', include('pages.urls')),  # Velzon demos - disabled in production
```

## Difference from CMS

| Feature | Pages App | CMS App |
|---------|-----------|---------|
| Purpose | Static demos | Dynamic content management |
| Content Management | Hardcoded in templates | Editable via admin |
| Multi-language | Template-level only | Full translation support |
| SEO | Limited | Full meta tags, descriptions |
| Customization | Requires code changes | Admin interface |
| Production Use | No | Yes |

## Migration to CMS

If you want to use any of these page designs in production:

1. Create a new CMS Page via Django admin at `/admin/cms/page/`
2. Copy the HTML content from the template
3. Adapt the content to use CMS sections and items
4. Use the CMS page URL instead of the pages app URL

## Related Documentation

- [CMS App Documentation](../cms/README.md)
- [Velzon Theme Documentation](../static/velzon/README.md)

---

**Note**: This app can be safely removed if not needed for reference purposes.
















