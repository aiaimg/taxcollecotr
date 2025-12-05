# CMS App - Content Management System

A comprehensive Content Management System (CMS) for managing the frontend of the Tax Collector platform.

## Features

- **Site Settings**: Manage general site configuration (name, logo, contact info, social media links)
- **Header Management**: Customize header/navigation (logo, colors, menu items, sticky header)
- **Footer Management**: Customize footer (copyright, description, social links)
- **Menu Management**: Create hierarchical menu items for header and footer
- **Page Management**: Create and manage pages with rich content
- **Section Management**: Create reusable page sections (hero, features, testimonials, etc.)
- **Multi-language Support**: Full support for French and Malagasy translations
- **Admin Interface**: Full Django admin integration for easy content management

## Models

### SiteSettings
General site configuration including:
- Site name and tagline
- Logo and favicon
- Contact information
- Social media links

### HeaderSettings
Header/navigation customization:
- Site name (with translations)
- Logo
- Colors (background and text)
- Display options (search, language switcher, sticky header)

### FooterSettings
Footer customization:
- Copyright text (with translations)
- Description (with translations)
- Display options (social links, newsletter)
- Colors (background and text)

### MenuItem
Navigation menu items:
- Title (with translations)
- URL or path
- Icon (Font Awesome)
- Parent-child relationships
- Menu location (header, footer, both)
- Order and visibility

### Page
CMS pages:
- Title and slug (with translations)
- Content (with translations)
- Meta description (with translations)
- Featured image
- Status (draft, published, archived)
- Homepage flag
- Custom template support
- Associated sections

### PageSection
Reusable page sections:
- Section type (hero, features, testimonials, etc.)
- Title and subtitle (with translations)
- Content (with translations)
- Background image and colors
- Text color
- Order and visibility

### SectionItem
Items within sections (e.g., individual features):
- Title and description (with translations)
- Icon or image
- Link URL and text
- Order and visibility

## Usage

### 1. Run Migrations

```bash
python manage.py migrate cms
```

### 2. Migrate Existing Content

To migrate existing frontend content to the CMS:

```bash
python manage.py migrate_frontend_content
```

This command will:
- Create default site settings
- Create header and footer settings
- Create menu items (Home, About, Contact, QR Verification)
- Create homepage sections (hero, features)
- Create default pages (homepage, about, contact)

### 3. Access Admin Interface

1. Go to `/admin/`
2. Navigate to the "CMS" section
3. Manage your content:
   - **Site Settings**: Configure general site information
   - **Header Settings**: Customize the header/navigation
   - **Footer Settings**: Customize the footer
   - **Menu Items**: Manage navigation menu
   - **Pages**: Create and manage pages
   - **Page Sections**: Create reusable sections
   - **Section Items**: Add items to sections

### 4. View CMS Pages

- Homepage: `/cms/`
- Page detail: `/cms/page/<slug>/`

## Templates

### Base Template
`templates/cms/base.html` - Base template with dynamic header and footer

### Page Templates
- `templates/cms/home.html` - Homepage template
- `templates/cms/page_detail.html` - Page detail template
- `templates/cms/section.html` - Reusable section template

## Integration with Existing Views

The CMS can be integrated with existing views by using the `get_cms_context()` helper function:

```python
from cms.views import get_cms_context

def my_view(request):
    context = get_cms_context()
    # Add your view-specific context
    context.update({
        'my_data': 'value',
    })
    return render(request, 'my_template.html', context)
```

## Customization

### Custom Section Types

You can extend the `SECTION_TYPE_CHOICES` in `PageSection` model to add custom section types.

### Custom Templates

Pages can use custom templates by setting the `template_name` field in the Page model.

### Styling

The CMS uses Bootstrap 5 and Velzon theme. You can customize styles by:
- Modifying the inline styles in `templates/cms/base.html`
- Adding custom CSS in the `extra_css` block
- Using the color settings in HeaderSettings and FooterSettings

## Best Practices

1. **Always set translations**: Fill in both French and Malagasy translations for better user experience
2. **Use sections**: Create reusable sections instead of duplicating content
3. **Order matters**: Set proper order values for menu items and sections
4. **Test visibility**: Use the `is_active` flag to control visibility without deleting content
5. **SEO**: Always fill in meta descriptions for pages

## Migration from Existing Content

The migration command (`migrate_frontend_content`) creates:
- Default site settings based on `base_public.html`
- Menu items matching existing navigation
- Homepage with hero and features sections
- About and Contact pages

After migration, you can:
- Update content through the admin interface
- Add more pages and sections
- Customize header and footer
- Add more menu items

## Support

For issues or questions, please refer to the main project documentation or contact the development team.

















