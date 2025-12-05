"""
Management command to convert existing images to WebP format.
Usage: python manage.py convert_images_to_webp
"""

import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import UserProfile
from core.utils import ImageOptimizer


class Command(BaseCommand):
    help = "Convert existing profile pictures to WebP format"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be converted without actually converting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get all profiles with profile pictures
        profiles = UserProfile.objects.exclude(profile_picture="").exclude(profile_picture__isnull=True)
        total = profiles.count()
        converted = 0
        skipped = 0
        errors = 0

        self.stdout.write(f"Found {total} profiles with profile pictures")

        for profile in profiles:
            try:
                # Skip if already WebP
                if profile.profile_picture.name.endswith(".webp"):
                    self.stdout.write(f"  Skipping {profile.user.username} - already WebP")
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  Would convert: {profile.profile_picture.name}")
                    converted += 1
                else:
                    # Get the current file
                    old_path = profile.profile_picture.path
                    old_name = profile.profile_picture.name

                    # Open and optimize
                    with open(old_path, "rb") as f:
                        optimized = ImageOptimizer.optimize_profile_picture(f)

                    # Save the optimized version
                    profile.profile_picture.save(optimized.name, optimized, save=True)

                    # Delete old file if it exists and is different
                    if os.path.exists(old_path) and old_name != profile.profile_picture.name:
                        os.remove(old_path)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Converted {profile.user.username}: {old_name} → {profile.profile_picture.name}"
                        )
                    )
                    converted += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error converting {profile.user.username}: {str(e)}"))
                errors += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Total profiles: {total}")
        self.stdout.write(self.style.SUCCESS(f"Converted: {converted}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
        self.stdout.write("=" * 50)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nThis was a dry run. Run without --dry-run to actually convert images.")
            )
