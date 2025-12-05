# Apply CMS Customization Updates

## Quick Fix

Run this command to apply the database changes:

```bash
./venv/bin/python manage.py migrate cms
```

## What This Does

This applies the new customization fields to your database:

### Header Customization Fields Added:
- Logo height control
- Link colors (normal and hover)
- Dropdown menu colors
- Button colors (background, text, hover)
- Header padding
- Shadow settings (enable/disable, color)
- Border settings (width, color)
- Background opacity/transparency

### Footer Customization Fields Added:
- Background image support
- Background size, repeat, position options
- Background attachment (scroll/fixed)
- Background opacity
- Overlay color and enable/disable
- Link colors (normal and hover)
- Heading color
- Padding (top and bottom)
- Border (top width and color)

## After Migration

1. Restart your development server
2. Go to `/admin/cms/headersettings/`
3. You'll see all the new customization options
4. Go to `/admin/cms/footersettings/`
5. Configure your footer with background images, colors, etc.

## Full Command

If you're in the project directory:

```bash
cd /Users/samoela/Projet/taxcollecotr
./venv/bin/python manage.py migrate cms
```

This will create all the new database columns and you'll be able to access the admin panel without errors.
















