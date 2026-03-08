from .base import *  # noqa: F403

DEBUG = False

# Use a sufficiently long SECRET_KEY (>=32 bytes) to silence PyJWT InsecureKeyLengthWarning
SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes-long!"
JWT_AUTH["SIGNING_KEY"] = SECRET_KEY  # noqa: F405

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable throttling in tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Run Celery tasks synchronously in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable Sentry in tests
try:
    import sentry_sdk

    sentry_sdk.init(dsn=None)
except ImportError:
    pass
