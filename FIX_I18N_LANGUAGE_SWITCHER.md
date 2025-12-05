# Fix: Language Switcher Error

**Date**: November 6, 2025  
**Error**: `Reverse for 'set_language' not found`  
**Status**: ✅ Fixed

## Problem

When accessing CMS pages, the following error occurred:

```
Reverse for 'set_language' not found. 'set_language' is not a valid view function or pattern name.
```

**Error Location**: `templates/cms/base.html`, line 221

## Root Cause

The CMS base template includes a language switcher feature that allows users to switch between French and Malagasy. This feature uses Django's built-in `set_language` view, which is part of Django's internationalization (i18n) system.

However, the i18n URLs were not included in the main URL configuration, causing the template to fail when trying to reverse the `set_language` URL.

## Solution

Added Django's i18n URLs to the main URL configuration.

### File Changed

**`taxcollector_project/urls.py`**

Added this line to the urlpatterns:

```python
# i18n URLs for language switching
path('i18n/', include('django.conf.urls.i18n')),
```

### Complete URL Configuration

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('core.allauth_urls')),
    # Root path now points to CMS for frontend content
    path('', include('cms.urls', namespace='cms')),
    # Core URLs for authenticated user features (dashboard, profile, etc.)
    path('app/', include('core.urls', namespace='core')),
    path('vehicles/', include('vehicles.urls', namespace='vehicles')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('administration/', include('administration.urls', namespace='administration')),
    # Pages app - Velzon template demos only (not CMS-managed, for reference only)
    # Comment out if not needed in production
    path('pages/', include('pages.urls')),
    path('api/', include('core.api_urls')),
    # i18n URLs for language switching
    path('i18n/', include('django.conf.urls.i18n')),  # ← NEW
]
```

## How It Works

### Language Switcher in Template

The CMS base template (`templates/cms/base.html`) includes a language switcher:

```html
{% if header_settings and header_settings.show_language_switcher %}
    <li class="nav-item ms-2">
        <form action="{% url 'set_language' %}" method="post" class="d-inline">
            {% csrf_token %}
            <input type="hidden" name="next" value="{{ request.path }}">
            <select name="language" onchange="this.form.submit()" class="form-select form-select-sm">
                {% get_available_languages as LANGUAGES %}
                {% for lang_code, lang_name in LANGUAGES %}
                    <option value="{{ lang_code }}" {% if lang_code == current_language %}selected{% endif %}>
                        {{ lang_name }}
                    </option>
                {% endfor %}
            </select>
        </form>
    </li>
{% endif %}
```

### Django i18n Configuration

The settings are already properly configured:

**`taxcollector_project/settings.py`**:

```python
# Middleware includes LocaleMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # ← For language switching
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Context processors include i18n
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',  # ← For i18n tags
                # ...
            ],
        },
    },
]

# Language configuration
LANGUAGE_CODE = 'fr-fr'
USE_I18N = True

LANGUAGES = [
    ('fr', 'Français'),
    ('mg', 'Malagasy'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

## What the i18n URLs Provide

Including `django.conf.urls.i18n` provides the following URLs:

- **`/i18n/setlang/`** (name: `set_language`) - Changes the user's language preference
- Handles POST requests with `language` parameter
- Redirects to the `next` URL parameter after setting the language
- Stores language preference in session

## Testing

After the fix, test the language switcher:

1. Start the development server: `python manage.py runserver`
2. Visit the homepage: `http://localhost:8000/`
3. Look for the language switcher in the header (if enabled)
4. Select a different language (Français or Malagasy)
5. The page should reload with the new language

## Enabling/Disabling Language Switcher

The language switcher can be controlled via the CMS admin:

1. Go to `/admin/cms/headersettings/`
2. Find the active HeaderSettings object
3. Check/uncheck the **"Show language switcher"** option
4. Save

When disabled, the language switcher won't appear, and this fix becomes optional (but still recommended).

## Additional Notes

### Language Preference Storage

- Language preference is stored in the user's session
- For authenticated users, you can also store it in the user profile
- Anonymous users' language preference persists while their session is active

### Translation Files

To add translations for your CMS content:

1. Create translation files:
   ```bash
   python manage.py makemessages -l fr
   python manage.py makemessages -l mg
   ```

2. Edit the `.po` files in `locale/fr/LC_MESSAGES/` and `locale/mg/LC_MESSAGES/`

3. Compile translations:
   ```bash
   python manage.py compilemessages
   ```

### CMS Content Translations

The CMS models already have built-in translation fields:
- `title`, `title_fr`, `title_mg`
- `content`, `content_fr`, `content_mg`
- `description`, `description_fr`, `description_mg`

These are managed directly through the Django admin without needing `.po` files.

## Related Documentation

- [Django Internationalization](https://docs.djangoproject.com/en/stable/topics/i18n/)
- [Django Translation](https://docs.djangoproject.com/en/stable/topics/i18n/translation/)
- [CMS Setup Instructions](CMS_SETUP_INSTRUCTIONS.md)

## Troubleshooting

### Issue: Language doesn't change

**Solution**:
1. Check that `LocaleMiddleware` is in `MIDDLEWARE`
2. Verify `USE_I18N = True` in settings
3. Clear browser cache and cookies
4. Check that `LANGUAGES` setting includes the language

### Issue: Translations not showing

**Solution**:
1. Make sure translation fields are filled in the admin
2. Check that `django.template.context_processors.i18n` is in context processors
3. Verify `current_language` is being set correctly in the view context

---

**Fix Status**: ✅ Complete  
**Tested**: Ready for testing  
**Deployment**: No additional changes needed
















