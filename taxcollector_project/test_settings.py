from .settings import *

# Minimal app set for focused audit logging tests
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    # Third-party
    "modeltranslation",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "multiselectfield",
    # Local apps needed by tests
    "core.apps.CoreConfig",
    "vehicles.apps.VehiclesConfig",
    "payments.apps.PaymentsConfig",
    "contraventions.apps.ContraventionsConfig",
    "administration.apps.AdministrationConfig",
    "api",
]

# Use SQLite for tests to avoid external DB dependencies
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",
    }
}

ROOT_URLCONF = "taxcollector_project.test_urls"

TEST_RUNNER = "taxcollector_project.test_runner.NoCheckTestRunner"

# Relax DRF throttling for tests
REST_FRAMEWORK = REST_FRAMEWORK.copy()
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

# Silence request warnings during property tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "django.request": {
            "handlers": [],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
