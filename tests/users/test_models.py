import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123", nickname="Test User"
        )
        assert user.nickname == "Test User"
        assert user.status == User.Status.ACTIVE
        assert user.bio == ""
        assert user.avatar_url is None

    def test_strip_nickname(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123", nickname="  spaces  "
        )
        assert user.nickname == "spaces"
