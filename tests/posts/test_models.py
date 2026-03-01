import pytest
from django.utils import timezone

from apps.posts.models import Post


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        post = Post.objects.create(title="Test Post", content="Content", user_id="user-1")
        assert post.title == "Test Post"
        assert post.status == Post.Status.DRAFT
        assert post.view_count == 0

    def test_publish(self):
        post = Post.objects.create(title="Draft", content="Content", user_id="user-1")
        assert post.publish() is True
        post.refresh_from_db()
        assert post.status == Post.Status.PUBLISHED
        assert post.published_at is not None

    def test_publish_without_content_fails(self):
        post = Post.objects.create(title="Empty", content="", user_id="user-1")
        assert post.publish() is False

    def test_archive(self):
        post = Post.objects.create(title="Archive Me", content="Content", user_id="user-1")
        assert post.archive() is True
        post.refresh_from_db()
        assert post.status == Post.Status.ARCHIVED

    def test_publishable(self):
        post = Post(title="Draft", content="Content", status=Post.Status.DRAFT)
        assert post.publishable() is True

    def test_not_publishable_when_published(self):
        post = Post(title="Published", content="Content", status=Post.Status.PUBLISHED)
        assert post.publishable() is False

    def test_summary_short(self):
        post = Post(content="Short")
        assert post.summary() == "Short"

    def test_summary_truncated(self):
        post = Post(content="a " * 100)
        s = post.summary(length=10)
        assert s.endswith("...")

    def test_days_since_published(self):
        post = Post(published_at=timezone.now())
        assert post.days_since_published() == 0

    def test_days_since_published_none(self):
        post = Post(published_at=None)
        assert post.days_since_published() is None

    def test_increment_view_count(self):
        post = Post.objects.create(title="Views", content="Content", user_id="user-1")
        post.increment_view_count()
        assert post.view_count == 1

    def test_strip_title(self):
        post = Post.objects.create(title="  spaces  ", content="Content", user_id="user-1")
        assert post.title == "spaces"

    def test_author_name(self):
        post = Post(user_id="user-1")
        assert post.author_name() == "User#user-1"

    def test_comment_count(self):
        post = Post.objects.create(title="With Comments", content="Content", user_id="user-1")
        assert post.comment_count() == 0


@pytest.mark.django_db
class TestPostQuerySet:
    def test_published_only(self):
        Post.objects.create(title="Draft", content="c", user_id="u1", status=Post.Status.DRAFT)
        Post.objects.create(
            title="Published", content="c", user_id="u1", status=Post.Status.PUBLISHED, published_at=timezone.now()
        )
        assert Post.objects.published_only().count() == 1

    def test_by_user(self):
        Post.objects.create(title="Mine", content="c", user_id="u1")
        Post.objects.create(title="Theirs", content="c", user_id="u2")
        assert Post.objects.by_user("u1").count() == 1

    def test_active(self):
        Post.objects.create(title="Active", content="c", user_id="u1")
        Post.objects.create(title="Archived", content="c", user_id="u1", status=Post.Status.ARCHIVED)
        assert Post.objects.active().count() == 1

    def test_statistics(self):
        Post.objects.create(title="D1", content="c", user_id="u1", status=Post.Status.DRAFT)
        Post.objects.create(
            title="P1", content="c", user_id="u1", status=Post.Status.PUBLISHED, published_at=timezone.now()
        )
        stats = Post.objects.statistics()
        assert stats["total"] == 2
        assert stats["published"] == 1
        assert stats["draft"] == 1

    def test_most_popular(self):
        Post.objects.create(
            title="Popular",
            content="c",
            user_id="u1",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
            view_count=100,
        )
        Post.objects.create(
            title="Less",
            content="c",
            user_id="u1",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
            view_count=10,
        )
        results = Post.objects.most_popular(limit=1)
        assert len(results) == 1
        assert results[0].title == "Popular"
