"""
Image optimization utility for converting and compressing images to WebP format.
This utility can be used throughout the application for any image uploads.
"""

import hashlib
import os
import uuid
from datetime import datetime
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image


class ImageOptimizer:
    """
    Utility class for optimizing and converting images to WebP format.
    Handles automatic resizing, compression, and format conversion.
    """

    # Default settings
    DEFAULT_QUALITY = 85
    DEFAULT_MAX_WIDTH = 1920
    DEFAULT_MAX_HEIGHT = 1920

    # Profile picture specific settings
    PROFILE_PICTURE_SIZE = (400, 400)
    PROFILE_PICTURE_QUALITY = 90

    # Document specific settings (CIN, Carte Grise, etc.)
    DOCUMENT_MAX_SIZE = (2048, 2048)
    DOCUMENT_QUALITY = 92

    # Thumbnail settings
    THUMBNAIL_SIZE = (150, 150)
    THUMBNAIL_QUALITY = 80

    @staticmethod
    def generate_unique_filename(original_filename, prefix=""):
        """
        Generate a unique filename using timestamp and UUID.

        Args:
            original_filename: Original file name
            prefix: Optional prefix for the filename

        Returns:
            Unique filename with .webp extension
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]

        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}.webp"
        return f"{timestamp}_{unique_id}.webp"

    @staticmethod
    def optimize_image(
        image_file, max_width=None, max_height=None, quality=None, output_format="WEBP", maintain_aspect_ratio=True
    ):
        """
        Optimize and convert an image to WebP format.

        Args:
            image_file: Django UploadedFile object or file path
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: WebP quality (1-100)
            output_format: Output format (default: WEBP)
            maintain_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            InMemoryUploadedFile object ready for saving
        """
        # Set defaults
        if max_width is None:
            max_width = ImageOptimizer.DEFAULT_MAX_WIDTH
        if max_height is None:
            max_height = ImageOptimizer.DEFAULT_MAX_HEIGHT
        if quality is None:
            quality = ImageOptimizer.DEFAULT_QUALITY

        # Open the image
        try:
            img = Image.open(image_file)
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # Convert RGBA to RGB if necessary
        if img.mode in ("RGBA", "LA", "P"):
            # Create a white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Get original dimensions
        original_width, original_height = img.size

        # Calculate new dimensions
        if maintain_aspect_ratio:
            # Calculate aspect ratio
            aspect_ratio = original_width / original_height

            # Determine new dimensions
            if original_width > max_width or original_height > max_height:
                if aspect_ratio > 1:  # Landscape
                    new_width = min(original_width, max_width)
                    new_height = int(new_width / aspect_ratio)
                else:  # Portrait or square
                    new_height = min(original_height, max_height)
                    new_width = int(new_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height
        else:
            new_width = min(original_width, max_width)
            new_height = min(original_height, max_height)

        # Resize image if needed
        if (new_width, new_height) != (original_width, original_height):
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(
            output, format=output_format, quality=quality, optimize=True, method=6  # Best compression method for WebP
        )
        output.seek(0)

        # Generate unique filename
        original_name = getattr(image_file, "name", "image.jpg")
        new_filename = ImageOptimizer.generate_unique_filename(original_name)

        # Create InMemoryUploadedFile
        optimized_file = InMemoryUploadedFile(
            output, "ImageField", new_filename, f"image/{output_format.lower()}", output.getbuffer().nbytes, None
        )

        return optimized_file

    @staticmethod
    def optimize_profile_picture(image_file):
        """
        Optimize image specifically for profile pictures.
        Creates a square thumbnail with high quality.

        Args:
            image_file: Django UploadedFile object

        Returns:
            Optimized InMemoryUploadedFile
        """
        try:
            img = Image.open(image_file)
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # Convert to RGB if necessary
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Create square crop (center crop)
        width, height = img.size
        min_dimension = min(width, height)

        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension

        img = img.crop((left, top, right, bottom))

        # Resize to profile picture size
        img = img.resize(ImageOptimizer.PROFILE_PICTURE_SIZE, Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format="WEBP", quality=ImageOptimizer.PROFILE_PICTURE_QUALITY, optimize=True, method=6)
        output.seek(0)

        # Generate filename with profile prefix
        new_filename = ImageOptimizer.generate_unique_filename(
            getattr(image_file, "name", "profile.jpg"), prefix="profile"
        )

        # Create InMemoryUploadedFile
        optimized_file = InMemoryUploadedFile(
            output, "ImageField", new_filename, "image/webp", output.getbuffer().nbytes, None
        )

        return optimized_file

    @staticmethod
    def optimize_document(image_file, document_type="document"):
        """
        Optimize image for documents (CIN, Carte Grise, etc.).
        Maintains higher quality and resolution for readability.

        Args:
            image_file: Django UploadedFile object
            document_type: Type of document (cin, carte_grise, etc.)

        Returns:
            Optimized InMemoryUploadedFile
        """
        optimized = ImageOptimizer.optimize_image(
            image_file,
            max_width=ImageOptimizer.DOCUMENT_MAX_SIZE[0],
            max_height=ImageOptimizer.DOCUMENT_MAX_SIZE[1],
            quality=ImageOptimizer.DOCUMENT_QUALITY,
        )

        # Rename with document type prefix
        original_name = optimized.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        new_name = f"{document_type}_{timestamp}_{unique_id}.webp"

        optimized.name = new_name
        return optimized

    @staticmethod
    def create_thumbnail(image_file, size=None):
        """
        Create a thumbnail version of an image.

        Args:
            image_file: Django UploadedFile object or PIL Image
            size: Tuple of (width, height) for thumbnail

        Returns:
            Optimized thumbnail as InMemoryUploadedFile
        """
        if size is None:
            size = ImageOptimizer.THUMBNAIL_SIZE

        try:
            if isinstance(image_file, Image.Image):
                img = image_file
            else:
                img = Image.open(image_file)
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # Convert to RGB if necessary
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format="WEBP", quality=ImageOptimizer.THUMBNAIL_QUALITY, optimize=True, method=6)
        output.seek(0)

        # Generate filename
        new_filename = ImageOptimizer.generate_unique_filename("thumbnail.jpg", prefix="thumb")

        # Create InMemoryUploadedFile
        thumbnail_file = InMemoryUploadedFile(
            output, "ImageField", new_filename, "image/webp", output.getbuffer().nbytes, None
        )

        return thumbnail_file

    @staticmethod
    def get_image_info(image_file):
        """
        Get information about an image file.

        Args:
            image_file: Django UploadedFile object or file path

        Returns:
            Dictionary with image information
        """
        try:
            img = Image.open(image_file)
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.size[0],
                "height": img.size[1],
                "file_size": getattr(image_file, "size", None),
            }
        except Exception as e:
            return {"error": str(e)}


def optimize_model_image_field(instance, field_name, optimize_type="default"):
    """
    Helper function to optimize an image field on a model instance.
    Can be called from any model's save() method.

    Args:
        instance: Model instance
        field_name: Name of the ImageField
        optimize_type: Type of optimization ('default', 'profile', 'document')

    Example usage in a model's save() method:
        from core.utils.image_optimizer import optimize_model_image_field

        def save(self, *args, **kwargs):
            optimize_model_image_field(self, 'cin_image', optimize_type='document')
            optimize_model_image_field(self, 'carte_grise_image', optimize_type='document')
            super().save(*args, **kwargs)
    """
    import logging

    logger = logging.getLogger(__name__)

    field = getattr(instance, field_name, None)

    if field and hasattr(field, "file"):
        try:
            # Check if already optimized
            if field.name and field.name.endswith(".webp"):
                return

            # Choose optimization method
            if optimize_type == "profile":
                optimized = ImageOptimizer.optimize_profile_picture(field)
            elif optimize_type == "document":
                optimized = ImageOptimizer.optimize_document(field, document_type=field_name)
            else:
                optimized = ImageOptimizer.optimize_image(field)

            # Replace the field with optimized version
            setattr(instance, field_name, optimized)

        except Exception as e:
            logger.error(f"Error optimizing {field_name} for {instance}: {str(e)}")
