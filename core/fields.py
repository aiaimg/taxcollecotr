"""
Custom form fields for image optimization.
"""

from django import forms

from core.utils import ImageOptimizer


class OptimizedImageField(forms.ImageField):
    """
    Custom ImageField that automatically optimizes uploaded images to WebP format.
    Can be used for any image upload in the system.
    """

    def __init__(self, *args, **kwargs):
        # Extract custom optimization parameters
        self.max_width = kwargs.pop("max_width", None)
        self.max_height = kwargs.pop("max_height", None)
        self.quality = kwargs.pop("quality", None)
        self.optimize_type = kwargs.pop("optimize_type", "default")  # default, profile, document

        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Override clean to optimize the image before validation.
        """
        file = super().clean(data, initial)

        if file and hasattr(file, "file"):
            try:
                # Choose optimization method based on type
                if self.optimize_type == "profile":
                    optimized_file = ImageOptimizer.optimize_profile_picture(file)
                elif self.optimize_type == "document":
                    optimized_file = ImageOptimizer.optimize_document(file)
                else:
                    optimized_file = ImageOptimizer.optimize_image(
                        file, max_width=self.max_width, max_height=self.max_height, quality=self.quality
                    )

                return optimized_file
            except Exception as e:
                raise forms.ValidationError(f"Erreur lors de l'optimisation de l'image: {str(e)}")

        return file


class ProfilePictureField(OptimizedImageField):
    """
    Specialized field for profile pictures.
    Automatically creates square thumbnails optimized for display.
    """

    def __init__(self, *args, **kwargs):
        kwargs["optimize_type"] = "profile"
        kwargs.setdefault("help_text", "Formats acceptés: JPG, PNG, GIF. Sera automatiquement converti en WebP.")
        super().__init__(*args, **kwargs)


class DocumentImageField(OptimizedImageField):
    """
    Specialized field for document images (CIN, Carte Grise, etc.).
    Maintains higher quality for readability.
    """

    def __init__(self, *args, **kwargs):
        kwargs["optimize_type"] = "document"
        kwargs.setdefault(
            "help_text", "Formats acceptés: JPG, PNG. Sera automatiquement converti en WebP haute qualité."
        )
        super().__init__(*args, **kwargs)
