from .base import *  # noqa: F403

DEBUG = True

# Development-specific settings
INSTALLED_APPS += [  # noqa: F405
    "django.contrib.staticfiles",
    "debug_toolbar",
    "django_extensions",
]

STATIC_URL = "/static/"

MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405

# Run Celery tasks synchronously in development (no Redis needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Debug-level logging in development (matches Rails development.rb)
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["api"]["level"] = "DEBUG"  # noqa: F405

# Allow unsafe-inline for Swagger UI in development
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
