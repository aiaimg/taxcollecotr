"""
Django settings for testing environment

This settings file is specifically for running tests including E2E tests.
It uses a separate test database and disables certain features for faster testing.
"""

from .settings import *  # noqa

# Test database configuration - use SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa
    }
}

# Disable email sending in tests (output to console instead)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use in-memory file storage for tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"

# Simplified password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# MVola test mode
MVOLA_TEST_MODE = True
MVOLA_API_KEY = "test-api-key"
MVOLA_API_SECRET = "test-api-secret"
MVOLA_MERCHANT_NUMBER = "0000000000"

# Disable HTTPS requirement in tests
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable debug toolbar and other development tools
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
}

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable Celery tasks in tests (run synchronously)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Test-specific settings
TESTING = True

# Disable migrations for faster tests (optional)
# Uncomment if you want to speed up tests
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# 
# MIGRATION_MODULES = DisableMigrations()

# Static files
STATIC_ROOT = BASE_DIR / "test_staticfiles"  # noqa
MEDIA_ROOT = BASE_DIR / "test_media"  # noqa

# Logging configuration for tests (less verbose)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",  # Only show warnings and errors
    },
}
