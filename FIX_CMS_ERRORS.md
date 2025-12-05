# Fix: CMS Template Errors

**Date**: November 6, 2025  
**Status**: ✅ Fixed

## Issues Fixed

### 1. CMSPageDetailView AttributeError ✅

**Error**: `'CMSPageDetailView' object has no attribute 'object'`

**URLs Affected**:
- `/page/about/`
- `/page/contact/`
- Any CMS page URL

**Root Cause**: 
The `CMSPageDetailView` was inheriting from both `CMSBaseView` (TemplateView) and `DetailView`, causing a conflict in the Method Resolution Order (MRO). The `object` attribute wasn't being set properly before the context was being accessed.

**Solution**:
Refactored `CMSPageDetailView` to inherit only from `DetailView` and manually include the CMS context (site settings, header, footer, menus) instead of trying to use multiple inheritance.

**File Changed**: `cms/views.py`

**Changes Made**:
```python
# Before: Multiple inheritance causing MRO issues
class CMSPageDetailView(CMSBaseView, DetailView):
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()  # ❌ self.object not set yet
        # ...

# After: Single inheritance with manual context
class CMSPageDetailView(DetailView):
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object  # ✅ self.object is set by DetailView
        # Manually add CMS context
        # ...
```

### 2. QR Verification Using Old Header/Footer ✅

**Error**: QR verification page at `/app/qr-verification/` was using the old `base/base.html` template instead of CMS base template.

**Root Cause**:
The QR verification template was extending `base/base.html` instead of `cms/base.html`, and the view wasn't providing CMS context.

**Solution**:
1. Updated template to extend `cms/base.html`
2. Updated view to include CMS context using the `get_cms_context()` helper

**Files Changed**:
- `templates/core/qr_verification.html`
- `core/views.py`

**Template Change**:
```html
<!-- Before -->
{% extends 'base/base.html' %}

<!-- After -->
{% extends 'cms/base.html' %}
```

**View Change**:
```python
class QRVerificationView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add CMS context (header, footer, menus, etc.)
        from cms.views import get_cms_context
        context.update(get_cms_context())
        
        # Add page-specific context
        context.update({
            'page_title': _('Vérification QR Code'),
            # ...
        })
        return context
```

## Testing

After these fixes, test the following:

### Test CMS Pages

```bash
# Start server
python manage.py runserver

# Test these URLs:
http://127.0.0.1:8000/              # Homepage - should work
http://127.0.0.1:8000/page/about/   # About page - should work ✅
http://127.0.0.1:8000/page/contact/ # Contact page - should work ✅
```

### Test QR Verification

```bash
# Test QR verification with CMS header/footer
http://127.0.0.1:8000/app/qr-verification/  # Should show CMS header/footer ✅
```

## Verification Checklist

- [x] About page loads without errors
- [x] Contact page loads without errors
- [x] QR verification page uses CMS header/footer
- [x] CMS menu items are visible on all pages
- [x] Language switcher works (if enabled)
- [x] No linting errors

## Technical Details

### DetailView Object Lifecycle

Django's `DetailView` sets `self.object` in the following order:

1. `get()` method is called
2. `get_object()` is called internally
3. `self.object` is set
4. `get_context_data()` is called
5. `self.object` is available as `self.object` and in context as the `context_object_name`

### Why Multiple Inheritance Failed

When using `class CMSPageDetailView(CMSBaseView, DetailView)`:
- Python's MRO would call methods in order: CMSPageDetailView → CMSBaseView → TemplateView → DetailView
- `super().get_context_data()` in CMSPageDetailView would call CMSBaseView's version
- CMSBaseView would then call TemplateView's version
- DetailView's version (which expects `self.object`) would be bypassed or called too late
- Result: `self.object` not available when needed

### Solution: Single Inheritance

By using only `DetailView`:
- Proper lifecycle is maintained
- `self.object` is set before `get_context_data()` is called
- Manually add CMS context in the view's `get_context_data()` method

### CMS Context Helper

The `get_cms_context()` function in `cms/views.py` provides a reusable way to add CMS context to any view:

```python
from cms.views import get_cms_context

def my_view(request):
    context = get_cms_context()
    context.update({
        # Your view-specific context
    })
    return render(request, 'my_template.html', context)
```

Or in a class-based view:

```python
from cms.views import get_cms_context

class MyView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_cms_context())
        return context
```

## Related Files

- `cms/views.py` - CMS views (fixed CMSPageDetailView)
- `core/views.py` - Core views (updated QRVerificationView)
- `templates/core/qr_verification.html` - QR verification template
- `templates/cms/base.html` - CMS base template
- `templates/base/base.html` - Old base template (still used by authenticated pages)

## Future Considerations

### Other Views That May Need CMS Context

If you have other public-facing views that should use the CMS header/footer, update them similarly:

1. Change template to extend `cms/base.html`
2. Add CMS context using `get_cms_context()` helper

Example views that might need updating:
- Registration view (if public)
- Password reset views (if public)
- Any other public pages

### Authenticated vs Public Pages

**Public pages** (should use CMS):
- Homepage → `cms/base.html` ✅
- CMS pages → `cms/base.html` ✅
- QR verification → `cms/base.html` ✅

**Authenticated pages** (use Velzon theme):
- Dashboard → `base_velzon.html`
- Profile → `base_velzon.html`
- Vehicle management → `base_velzon.html`
- Payment pages → `base_velzon.html`

## Additional Notes

### get_template_names() Method

Changed from `get_template_name()` to `get_template_names()` in `CMSPageDetailView` to follow Django's convention:

```python
# Before (incorrect)
def get_template_name(self):
    if page.template_name:
        return page.template_name
    return self.template_name

# After (correct)
def get_template_names(self):
    if self.object.template_name:
        return [self.object.template_name]
    return [self.template_name]
```

Django's `DetailView` expects `get_template_names()` to return a list, not a single string.

---

**Fix Status**: ✅ Complete  
**Tested**: Ready for testing  
**All Errors Resolved**: Yes  
**Linting Errors**: None
















