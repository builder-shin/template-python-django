import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification(self, user_id: int, message: str) -> dict:
    """Example Celery task: send a notification to a user.

    This is a template task demonstrating:
    - shared_task decorator (autodiscovered by config/celery.py)
    - bind=True for self-reference (retries)
    - Retry on transient failure (User.DoesNotExist)
    - Structured return value
    - Logging
    """
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    try:
        user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist as exc:
        raise self.retry(exc=exc) from exc
    logger.info("Sending notification to user %s: %s", user_id, message)
    return {"user_id": user_id, "message": message, "status": "sent"}
