import pytest
from celery.exceptions import MaxRetriesExceededError, Retry
from django.contrib.auth import get_user_model

from apps.core.tasks import send_notification

User = get_user_model()


@pytest.mark.django_db
class TestSendNotification:
    def test_task_executes_synchronously(self, auth_user):
        """CELERY_TASK_ALWAYS_EAGER 환경에서 동기 실행."""
        result = send_notification.delay(user_id=auth_user.id, message="Hello")
        assert result.successful()

    def test_task_returns_expected_payload(self, auth_user):
        """태스크 반환값 구조 검증."""
        result = send_notification.delay(user_id=auth_user.id, message="Hello")
        assert result.result == {
            "user_id": auth_user.id,
            "message": "Hello",
            "status": "sent",
        }

    def test_task_is_registered(self):
        """태스크가 Celery 앱에 등록되어 있는지 확인."""
        from config.celery import app

        assert "apps.core.tasks.send_notification" in app.tasks

    def test_task_retries_on_missing_user(self):
        """존재하지 않는 user_id → retry 시도."""
        with pytest.raises((MaxRetriesExceededError, User.DoesNotExist, Retry)):
            send_notification.apply(args=[99999, "Hello"])

    def test_task_max_retries_config(self):
        """max_retries 설정값 검증."""
        assert send_notification.max_retries == 3
