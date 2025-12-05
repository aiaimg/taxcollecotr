# Image Optimization System

This system automatically converts and optimizes all uploaded images to WebP format for better performance and storage efficiency.

## Features

- **Automatic WebP Conversion**: All images are automatically converted to WebP format
- **Smart Compression**: Optimizes file size while maintaining quality
- **Unique Filenames**: Generates unique filenames with timestamps to prevent conflicts
- **Multiple Optimization Profiles**: Different settings for profiles, documents, and general images
- **Reusable**: Can be used throughout the entire application

## Usage

### 1. For Profile Pictures

The system is already integrated into the user profile. Profile pictures are automatically:
- Cropped to square (center crop)
- Resized to 400x400 pixels
- Converted to WebP at 90% quality
- Given a unique filename like `profile_20241107_a1b2c3d4.webp`

### 2. For Forms (CIN, Carte Grise, etc.)

Use the custom form fields in your forms:

```python
from core.fields import DocumentImageField, ProfilePictureField

class MyForm(forms.ModelForm):
    cin_image = DocumentImageField(
        required=False,
        label='Photo CIN'
    )
    
    carte_grise = DocumentImageField(
        required=False,
        label='Carte Grise'
    )
    
    profile_pic = ProfilePictureField(
        required=False,
        label='Photo de profil'
    )
```

### 3. For Models

Add optimization to your model's save method:

```python
from core.utils import optimize_model_image_field

class MyModel(models.Model):
    cin_image = models.ImageField(upload_to='documents/cin/')
    carte_grise = models.ImageField(upload_to='documents/carte_grise/')
    
    def save(self, *args, **kwargs):
        # Optimize images before saving
        optimize_model_image_field(self, 'cin_image', optimize_type='document')
        optimize_model_image_field(self, 'carte_grise', optimize_type='document')
        super().save(*args, **kwargs)
```

### 4. Manual Optimization

You can also manually optimize images:

```python
from core.utils import ImageOptimizer

# For profile pictures
optimized = ImageOptimizer.optimize_profile_picture(uploaded_file)

# For documents (high quality)
optimized = ImageOptimizer.optimize_document(uploaded_file, document_type='cin')

# Custom optimization
optimized = ImageOptimizer.optimize_image(
    uploaded_file,
    max_width=1920,
    max_height=1920,
    quality=85
)

# Create thumbnail
thumbnail = ImageOptimizer.create_thumbnail(uploaded_file, size=(150, 150))
```

## Optimization Profiles

### Profile Pictures
- **Size**: 400x400 pixels (square, center-cropped)
- **Quality**: 90%
- **Format**: WebP
- **Use case**: User avatars, profile photos

### Documents (CIN, Carte Grise, etc.)
- **Max Size**: 2048x2048 pixels
- **Quality**: 92% (higher for readability)
- **Format**: WebP
- **Use case**: Identity cards, vehicle registration, official documents

### General Images
- **Max Size**: 1920x1920 pixels
- **Quality**: 85%
- **Format**: WebP
- **Use case**: General purpose images

### Thumbnails
- **Size**: 150x150 pixels
- **Quality**: 80%
- **Format**: WebP
- **Use case**: Image previews, galleries

## Management Commands

### Convert Existing Images

Convert all existing images to WebP format:

```bash
# Dry run (see what would be converted)
python manage.py convert_images_to_webp --dry-run

# Actually convert
python manage.py convert_images_to_webp
```

## Benefits

1. **Reduced Storage**: WebP files are typically 25-35% smaller than JPEG/PNG
2. **Faster Loading**: Smaller files = faster page loads
3. **Better Quality**: WebP provides better quality at smaller file sizes
4. **Consistent Format**: All images in the same format simplifies handling
5. **Automatic Processing**: No manual intervention needed

## Technical Details

### Supported Input Formats
- JPEG/JPG
- PNG
- GIF (converted to static image)
- BMP
- TIFF

### Output Format
- WebP (always)

### Image Processing
- Uses Pillow (PIL) library
- LANCZOS resampling for high-quality resizing
- Automatic RGBA to RGB conversion
- White background for transparent images
- Method 6 compression (best quality/size ratio)

## Examples

### Example 1: Vehicle Document Upload

```python
# models.py
from django.db import models
from core.utils import optimize_model_image_field

class Vehicle(models.Model):
    carte_grise = models.ImageField(upload_to='vehicles/carte_grise/')
    photo_vehicle = models.ImageField(upload_to='vehicles/photos/')
    
    def save(self, *args, **kwargs):
        optimize_model_image_field(self, 'carte_grise', optimize_type='document')
        optimize_model_image_field(self, 'photo_vehicle', optimize_type='default')
        super().save(*args, **kwargs)
```

### Example 2: User Identity Documents

```python
# forms.py
from django import forms
from core.fields import DocumentImageField

class IdentityVerificationForm(forms.Form):
    cin_recto = DocumentImageField(
        label='CIN Recto',
        help_text='Photo du recto de votre CIN'
    )
    cin_verso = DocumentImageField(
        label='CIN Verso',
        help_text='Photo du verso de votre CIN'
    )
```

## Configuration

Default settings can be modified in `core/utils/image_optimizer.py`:

```python
# Profile picture settings
PROFILE_PICTURE_SIZE = (400, 400)
PROFILE_PICTURE_QUALITY = 90

# Document settings
DOCUMENT_MAX_SIZE = (2048, 2048)
DOCUMENT_QUALITY = 92

# General settings
DEFAULT_QUALITY = 85
DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1920
```

## Troubleshooting

### Images not being optimized
- Check that Pillow is installed: `pip install Pillow`
- Verify the image field has `upload_to` parameter
- Check Django logs for optimization errors

### Quality issues
- Increase quality parameter (max 100)
- Use 'document' optimize_type for text-heavy images
- Check original image quality

### File size still large
- Verify WebP conversion is working (check file extension)
- Consider reducing max dimensions
- Lower quality setting if acceptable

## Future Enhancements

- [ ] Automatic thumbnail generation
- [ ] Multiple size variants (responsive images)
- [ ] Lazy loading integration
- [ ] CDN integration
- [ ] Batch processing API
- [ ] Image metadata preservation
- [ ] AVIF format support
