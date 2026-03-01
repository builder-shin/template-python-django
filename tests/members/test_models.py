import pytest

from apps.members.models import Member


@pytest.mark.django_db
class TestMemberModel:
    def test_create_member(self):
        member = Member.objects.create(user_id="user-1", nickname="Test User")
        assert member.nickname == "Test User"
        assert member.status == Member.Status.ACTIVE
        assert member.bio == ""
        assert member.avatar_url is None

    def test_display_name(self):
        member = Member(user_id="user-1", nickname="Nick")
        assert member.display_name() == "Nick"

    def test_display_name_fallback(self):
        member = Member(user_id="user-1", nickname="")
        assert member.display_name() == "User#user-1"

    def test_is_active(self):
        member = Member(user_id="user-1", nickname="Nick", status=Member.Status.ACTIVE)
        assert member.is_active() is True

    def test_suspend(self):
        member = Member.objects.create(user_id="user-1", nickname="Nick")
        member.suspend()
        member.refresh_from_db()
        assert member.status == Member.Status.SUSPENDED

    def test_withdraw(self):
        member = Member.objects.create(user_id="user-1", nickname="Nick")
        member.withdraw()
        member.refresh_from_db()
        assert member.status == Member.Status.WITHDRAWN

    def test_strip_nickname(self):
        member = Member.objects.create(user_id="user-1", nickname="  spaces  ")
        assert member.nickname == "spaces"


@pytest.mark.django_db
class TestMemberQuerySet:
    def test_active(self):
        Member.objects.create(user_id="u1", nickname="Active", status=Member.Status.ACTIVE)
        Member.objects.create(user_id="u2", nickname="Suspended", status=Member.Status.SUSPENDED)
        assert Member.objects.active().count() == 1

    def test_by_user(self):
        Member.objects.create(user_id="u1", nickname="User1")
        Member.objects.create(user_id="u2", nickname="User2")
        assert Member.objects.by_user("u1").count() == 1

    def test_recent(self):
        Member.objects.create(user_id="u1", nickname="First")
        m2 = Member.objects.create(user_id="u2", nickname="Second")
        results = list(Member.objects.recent())
        assert results[0].pk == m2.pk
