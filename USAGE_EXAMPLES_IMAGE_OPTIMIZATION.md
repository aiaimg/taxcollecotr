# Image Optimization - Usage Examples

## Quick Start

The image optimization system is now active and will automatically convert all uploaded images to WebP format.

## Current Implementation

### ✅ Profile Pictures
Profile pictures are automatically optimized when users upload them through the profile edit page.

**What happens:**
1. User uploads JPG/PNG image
2. System automatically:
   - Crops to square (center crop)
   - Resizes to 400x400 pixels
   - Converts to WebP at 90% quality
   - Saves with unique filename: `profile_20241107_a1b2c3d4.webp`

**No code changes needed** - it's already working!

## How to Add to Other Models

### Example 1: Add CIN (Identity Card) Images

```python
# In your model (e.g., core/models.py)
from django.db import models
from core.utils import optimize_model_image_field

class UserProfile(models.Model):
    # ... existing fields ...
    
    cin_recto = models.ImageField(
        upload_to='documents/cin/',
        blank=True,
        null=True,
        verbose_name="CIN Recto"
    )
    cin_verso = models.ImageField(
        upload_to='documents/cin/',
        blank=True,
        null=True,
        verbose_name="CIN Verso"
    )
    
    def save(self, *args, **kwargs):
        # Optimize CIN images before saving
        optimize_model_image_field(self, 'cin_recto', optimize_type='document')
        optimize_model_image_field(self, 'cin_verso', optimize_type='document')
        super().save(*args, **kwargs)
```

```python
# In your form (e.g., core/forms.py)
from core.fields import DocumentImageField

class UserProfileForm(forms.ModelForm):
    cin_recto = DocumentImageField(
        required=False,
        label='CIN Recto',
        help_text='Photo du recto de votre carte d\'identité'
    )
    cin_verso = DocumentImageField(
        required=False,
        label='CIN Verso',
        help_text='Photo du verso de votre carte d\'identité'
    )
    
    class Meta:
        model = UserProfile
        fields = ['cin_recto', 'cin_verso', ...]
```

### Example 2: Add Carte Grise (Vehicle Registration) Images

```python
# In vehicles/models.py
from django.db import models
from core.utils import optimize_model_image_field

class Vehicule(models.Model):
    # ... existing fields ...
    
    carte_grise_image = models.ImageField(
        upload_to='vehicles/carte_grise/',
        blank=True,
        null=True,
        verbose_name="Carte Grise"
    )
    photo_vehicule = models.ImageField(
        upload_to='vehicles/photos/',
        blank=True,
        null=True,
        verbose_name="Photo du véhicule"
    )
    
    def save(self, *args, **kwargs):
        # Optimize images before saving
        optimize_model_image_field(self, 'carte_grise_image', optimize_type='document')
        optimize_model_image_field(self, 'photo_vehicule', optimize_type='default')
        super().save(*args, **kwargs)
```

```python
# In vehicles/forms.py
from core.fields import DocumentImageField, OptimizedImageField

class VehiculeForm(forms.ModelForm):
    carte_grise_image = DocumentImageField(
        required=False,
        label='Carte Grise',
        help_text='Photo de la carte grise du véhicule'
    )
    photo_vehicule = OptimizedImageField(
        required=False,
        label='Photo du véhicule',
        help_text='Photo du véhicule'
    )
    
    class Meta:
        model = Vehicule
        fields = ['carte_grise_image', 'photo_vehicule', ...]
```

### Example 3: Payment Receipt Images

```python
# In payments/models.py
from django.db import models
from core.utils import optimize_model_image_field

class PaiementTaxe(models.Model):
    # ... existing fields ...
    
    receipt_image = models.ImageField(
        upload_to='payments/receipts/',
        blank=True,
        null=True,
        verbose_name="Reçu de paiement"
    )
    
    def save(self, *args, **kwargs):
        optimize_model_image_field(self, 'receipt_image', optimize_type='document')
        super().save(*args, **kwargs)
```

## Management Commands

### Convert Existing Images

If you already have images in the database, convert them to WebP:

```bash
# See what would be converted (dry run)
python manage.py convert_images_to_webp --dry-run

# Actually convert all profile pictures
python manage.py convert_images_to_webp
```

## Template Usage

### Display Optimized Images

```html
<!-- Profile picture -->
{% if user.profile.profile_picture %}
    <img src="{{ user.profile.profile_picture.url }}" 
         alt="Profile" 
         class="rounded-circle">
{% else %}
    <img src="{% static 'images/default-avatar.jpg' %}" 
         alt="Profile" 
         class="rounded-circle">
{% endif %}

<!-- CIN Image -->
{% if user.profile.cin_recto %}
    <img src="{{ user.profile.cin_recto.url }}" 
         alt="CIN Recto" 
         class="img-fluid">
{% endif %}

<!-- Vehicle Image -->
{% if vehicule.photo_vehicule %}
    <img src="{{ vehicule.photo_vehicule.url }}" 
         alt="Véhicule" 
         class="img-thumbnail">
{% endif %}
```

## Benefits You Get

### 1. Smaller File Sizes
- **Before**: profile.jpg (2.5 MB)
- **After**: profile_20241107_a1b2c3d4.webp (650 KB)
- **Savings**: ~74% reduction

### 2. Faster Page Loads
- Smaller images = faster downloads
- Better user experience
- Lower bandwidth costs

### 3. Consistent Quality
- All images optimized to same standards
- No manual intervention needed
- Automatic processing

### 4. Better Storage
- Less disk space used
- More efficient backups
- Lower storage costs

## Testing

### Test Profile Picture Upload

1. Login to the application
2. Go to Profile page
3. Click "Modifier le Profil"
4. Upload a JPG or PNG image
5. Save
6. Check the media folder - you'll see a `.webp` file!

### Verify Optimization

```python
# In Django shell
python manage.py shell

from core.models import UserProfile
from core.utils import ImageOptimizer

# Get a profile with image
profile = UserProfile.objects.filter(profile_picture__isnull=False).first()

# Check image info
info = ImageOptimizer.get_image_info(profile.profile_picture)
print(info)
# Output: {'format': 'WEBP', 'mode': 'RGB', 'size': (400, 400), ...}
```

## Troubleshooting

### Images not converting?

1. Check Pillow is installed:
   ```bash
   pip install Pillow
   ```

2. Check Django logs for errors

3. Verify the save() method is being called

### Quality issues?

Adjust quality settings in `core/utils/image_optimizer.py`:

```python
# For higher quality documents
DOCUMENT_QUALITY = 95  # Increase from 92

# For smaller profile pictures
PROFILE_PICTURE_QUALITY = 85  # Decrease from 90
```

## Next Steps

1. **Add CIN images** to UserProfile model
2. **Add Carte Grise images** to Vehicule model
3. **Add receipt images** to PaiementTaxe model
4. **Run conversion command** for existing images
5. **Update templates** to display new images

## Questions?

Check the detailed documentation in:
- `core/utils/README_IMAGE_OPTIMIZATION.md`
- `core/utils/image_optimizer.py` (source code with comments)
