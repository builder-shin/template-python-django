import pytest
from django.contrib.auth.models import User

from apps.members.models import Member


@pytest.mark.django_db
class TestMemberModel:
    def test_create_member(self, auth_user):
        member = Member.objects.create(user=auth_user, nickname="Test User")
        assert member.nickname == "Test User"
        assert member.status == Member.Status.ACTIVE
        assert member.bio == ""
        assert member.avatar_url is None

    def test_strip_nickname(self, auth_user):
        member = Member.objects.create(user=auth_user, nickname="  spaces  ")
        assert member.nickname == "spaces"
